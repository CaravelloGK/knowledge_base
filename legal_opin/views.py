from django.views.generic import ListView, DetailView, UpdateView, CreateView, View, DeleteView, FormView
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.base import TemplateResponseMixin
from django.urls import reverse_lazy, reverse
from .models import (LegalEntity, Deal, ExecutiveBody, Participant, DealParticipant, Risk_help,
                     Collegial_governing_bodies, DealParticipant, Collateral, Risk_DealParticipant)
from .forms import (LegalEntityForm, CollateralForm, ExecutiveBodyForm, ParticipantForm, Risk_DealParticipantForm,
                    Collegial_governing_bodiesForm, DealForm, DealParticipantForm, BaseCollegialBodiesFormSet)
from django.forms import inlineformset_factory, model_to_dict, modelformset_factory, formset_factory
from django import forms
from django.db import transaction
from django.db.models import Q
from collections import defaultdict
import re, os
from risk.models import Risk, Subject, Direction
from datetime import date
from datetime import datetime
from django.conf import settings
from django.http import JsonResponse
from legal_opin.util import EgrulDownloader, EgripParser, Converter, Date_Converter, compare_formset_data, Risk_analiz
from django.contrib import messages


def remove_non_printable(s):
    if s is None:
        return ''
    # Удаляем все непечатаемые символы, кроме пробелов и видимых
    return re.sub(r'[^\x20-\x7Eа-яА-ЯёЁ0-9 .,\-_/\\]', '', str(s))


# БЛОК Юридического лица (список, карточка, создание, редактирование)
class LegalEntityListView(ListView):
    # класс выводит список юриков
    model = LegalEntity
    template_name = 'list.html'
    context_object_name = 'legal_entities'
    ordering = ['-created_at']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['id_app'] = 'legal_opin'  # ВАЖНО! Идентификатор приложения!
        return context


class LegalEntityDetailView(DetailView):
    # класс выводит карточку юрика
    model = LegalEntity
    template_name = 'legal_opin/detail.html'
    context_object_name = 'entity'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity = self.get_object()
        context['executive_bodies'] = entity.executive_bodies.all()
        # Сортируем участников по доле от большей к меньшей
        participants = entity.participants.all()

        # Преобразуем доли в числа для сортировки, обрабатываем разные форматы
        def parse_share(participant):
            if not participant.share:
                return 0
            share_str = str(participant.share).replace('%', '').replace(',', '.').strip()
            try:
                return float(share_str)
            except (ValueError, TypeError):
                return 0

        context['participants'] = sorted(participants, key=parse_share, reverse=True)
        context['bankrot'] = entity.bankrot
        context['zakup'] = entity.zakup
        context['SEM'] = entity.SEM
        context['reorganization'] = entity.reorganization
        # Получаем сделки с дополнительной информацией о заемщиках и ролях
        deals = Deal.objects.filter(participants__legal_entity=entity).distinct()
        deals_with_data = []
        for deal in deals:
            # Получаем всех заемщиков для данной сделки
            borrowers = DealParticipant.objects.filter(
                deal=deal,
                role=1
            ).select_related('legal_entity')

            # Получаем роли текущего юр.лица в данной конкретной сделке
            current_entity_roles = DealParticipant.objects.filter(
                deal=deal,
                legal_entity=entity
            )

            # Добавляем к сделке список заемщиков и ролей
            deal.borrowers = [dp.legal_entity for dp in borrowers]
            deal.current_entity_roles = [dp.role for dp in current_entity_roles]
            deals_with_data.append(deal)

        context['deals'] = deals_with_data
        return context


def check_inn_file(request):
    # функция по получению выписки и массива при создании
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        inn = request.POST.get('inn', '')
        entity_id = request.POST.get('entity_id', None)

        if not re.match(r'^\d{10}$', inn):  # Проверяем формат ИНН (10 цифр)
            return JsonResponse(
                {'error': 'ИНН должен содержать 10 цифр'})  # если формат некорректный - возвращаем сообщение об ошибке

        # Проверяем, существует ли юр. лицо с таким ИНН в БД
        existing_entity = LegalEntity.objects.filter(inn=inn).first()
        if existing_entity and not entity_id:
            # Если ЮЛ найдено - возвращаем в карточку ЮЛ
            url = reverse_lazy('legal_opin:legal_entity_detail', kwargs={'pk': existing_entity.pk})
            return JsonResponse({
                'status': 'success_DB',
                'message': 'ЮЛ имеется в БД',
                'entity_url': url
            })

        egrul = EgrulDownloader(inn)
        egrul_vipiska = egrul.download()
        if egrul_vipiska == 'Ошибка':
            return JsonResponse({
                'status': 'searching',
                'message': 'Ошибка запроса к сайту. Повторите запрос через 5 минут'
            })
        else:
            parser = EgripParser(egrul_vipiska)
            itog = parser.parse()
            conv = Converter(itog)
            new_mass = conv.itog()
            if new_mass[0]['legal_form'] == 'АО' or new_mass[0]['legal_form'] == 'ООО' or new_mass[0][
                'legal_form'] == 'ПАО' or new_mass[0]['legal_form'] == 'ЗАО' or new_mass[0]['legal_form'] == 'ОАО':
                # Сохраняем данные в сессии

                request.session['legal_entity_data'] = {
                    'legal_entity': new_mass[0],
                    'executive_bodies': new_mass[1],
                    'participants': new_mass[2]
                }
                return JsonResponse({
                    'status': 'success',
                    'message': 'Данные успешно получены'
                })
            else:
                return JsonResponse({'error': 'Иная организационно-правовая форма'})

    return JsonResponse({'error': 'Неверный запрос'}, status=400)


class LegalEntityCreateView(CreateView):
    """
        класс отвечает за создание нового ЮЛ
    """
    model = LegalEntity
    form_class = LegalEntityForm
    template_name = 'legal_opin/legal_entity_form.html'
    success_url = reverse_lazy('legal_opin:legal_entity_list')

    def get(self, request, *args, **kwargs):
        # Очищаем сессию при загрузке формы (на случай старых данных)
        # self._cleanup_session_data()
        return super().get(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        data = self.request.session.get('legal_entity_data')
        if data:
            initial.update(data['legal_entity'])
        inf = data['legal_entity']
        initial['legal_form'] = inf['legal_form']
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session_data = self.request.session.get('legal_entity_data')

        if session_data:
            exec_info = session_data.get('executive_bodies', [])
            part_info = session_data.get('participants', [])
            context['is_create'] = True

            context['executive_formset'] = self.get_executive_formset(initial=exec_info)
            context['participant_formset'] = self.get_participant_formset(initial=part_info)
            context['сollegial_governing_bodies_formset'] = self.get_collegial_governing_bodies_formset()
        else:
            context['executive_formset'] = self.get_executive_formset()
            context['participant_formset'] = self.get_participant_formset()
            context['сollegial_governing_bodies_formset'] = self.get_collegial_governing_bodies_formset()

        return context

    def get_executive_formset(self, initial=None):
        ExecutiveBodyFormSet = forms.formset_factory(
            form=ExecutiveBodyForm,
            extra=0 if initial else 1,
            can_delete=False
        )
        return ExecutiveBodyFormSet(
            prefix='executive',
            initial=initial or []
        )

    def get_collegial_governing_bodies_formset(self, data=None, initial=None):
        CollegialFormSet = inlineformset_factory(
            LegalEntity,
            Collegial_governing_bodies,
            form=Collegial_governing_bodiesForm,
            extra=2,
            max_num=2,
            can_delete=True
        )
        if self.object:
            return CollegialFormSet(data, instance=self.object, prefix='collegial')
        else:
            return CollegialFormSet(data, initial=initial, prefix='collegial')

    def get_participant_formset(self, initial=None):
        ParticipantFormSet = forms.formset_factory(
            form=ParticipantForm,
            extra=0 if initial else 1,
            can_delete=False
        )
        return ParticipantFormSet(
            prefix='participant',
            initial=initial or []
        )

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()

        # Получаем КЛАССЫ формсетов (не экземпляры)
        ExecutiveBodyFormSet = forms.formset_factory(
            ExecutiveBodyForm,
            extra=0,
            can_delete=False
        )
        ParticipantFormSet = forms.formset_factory(
            ParticipantForm,
            extra=0,
            can_delete=True
        )
        CollegialFormSet = inlineformset_factory(
            LegalEntity, Collegial_governing_bodies,
            form=Collegial_governing_bodiesForm,
            extra=0,
            can_delete=True,
            formset=BaseCollegialBodiesFormSet
        )

        # Создаем экземпляры формсетов с POST-данными
        executive_formset = ExecutiveBodyFormSet(
            request.POST,
            prefix='executive'
        )
        participant_formset = ParticipantFormSet(
            request.POST,
            prefix='participant'
        )
        collegial_formset = CollegialFormSet(
            request.POST,
            instance=self.object,
            prefix='collegial'
        )

        if all([form.is_valid(), executive_formset.is_valid(), participant_formset.is_valid(),
                collegial_formset.is_valid()]):
            return self.form_valid(form, executive_formset, participant_formset, collegial_formset)
        return self.form_invalid(form, executive_formset, participant_formset, collegial_formset)

    def form_valid(self, form, executive_formset, participant_formset, collegial_formset):
        inn = form.cleaned_data.get('inn')
        if inn and LegalEntity.objects.filter(inn=inn).exists():
            # Очищаем сессию
            if 'legal_entity_data' in self.request.session:
                del self.request.session['legal_entity_data']
            # Очищаем сессию
            self._cleanup_session_data()
            # Добавляем сообщение об ошибке
            messages.error(self.request, f'Юридическое лицо с ИНН {inn} уже существует в базе данных.')

            # Перенаправляем на список
            return redirect('legal_opin:legal_entity_list')
        main_obj = form.save()

        # Сохраняем исполнительные органы
        for exec_form in executive_formset:
            if exec_form.has_changed():
                exec_body = exec_form.save(commit=False)
                exec_body.legal_entity = main_obj
                exec_body.save()

        # Сохраняем участников
        for part_form in participant_formset:
            if part_form.has_changed():
                participant = part_form.save(commit=False)
                participant.legal_entity = main_obj
                participant.save()

        # Сохраняем коллегиальные органы через inlineformset (включая новые и удаленные)
        collegial_formset.instance = main_obj
        objs = collegial_formset.save(commit=False)
        for obj in objs:
            obj.legal_entity = main_obj
            obj.save()
        for obj in getattr(collegial_formset, 'deleted_objects', []):
            obj.delete()

        # Очищаем сессию
        if 'legal_entity_data' in self.request.session:
            del self.request.session['legal_entity_data']
        # Очищаем сессию
        self._cleanup_session_data()
        return redirect('legal_opin:legal_entity_detail', pk=main_obj.pk)

    def form_invalid(self, form, executive_formset, participant_formset, collegial_formset):
        # Очищаем сессию при ошибках валидации
        self._cleanup_session_data()
        return self.render_to_response(
            self.get_context_data(
                form=form,
                executive_formset=executive_formset,
                participant_formset=participant_formset,
                collegial_formset=collegial_formset
            )
        )

    def _cleanup_session_data(self):
        """Очистка данных сессии связанных с созданием/редактированием ЮЛ"""
        session_keys = ['legal_entity_data']
        for key in session_keys:
            if key in self.request.session:
                del self.request.session[key]


class LegalEntityUpdateView(UpdateView):
    """
        класс отвечает за функцию редактирование
    """
    model = LegalEntity
    form_class = LegalEntityForm
    template_name = 'legal_opin/legal_entity_form.html'

    def get_success_url(self):
        return reverse_lazy('legal_opin:legal_entity_detail', kwargs={'pk': self.object.pk})

    def get_initial(self):
        initial = super().get_initial()
        data = self.request.session.get('legal_entity_data')
        if data:
            initial.update(data['legal_entity'])
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['executive_formset'] = self.get_executive_formset(self.request.POST)
            context['participant_formset'] = self.get_participant_formset(self.request.POST)
            context['сollegial_governing_bodies_formset'] = self.get_collegial_formset(self.request.POST)
        else:
            context['executive_formset'] = self.get_executive_formset()
            context['participant_formset'] = self.get_participant_formset()
            context['сollegial_governing_bodies_formset'] = self.get_collegial_formset()
        context['is_create'] = False
        context['changed_fields'] = ''
        return context

    def get_executive_formset(self, data=None):
        ExecutiveBodyFormSet = inlineformset_factory(
            LegalEntity, ExecutiveBody, form=ExecutiveBodyForm, extra=0, can_delete=False
        )
        return ExecutiveBodyFormSet(data, instance=self.object, prefix='executives')

    def get_participant_formset(self, data=None):
        ParticipantFormSet = inlineformset_factory(
            LegalEntity, Participant, form=ParticipantForm, extra=0, can_delete=False
        )
        return ParticipantFormSet(data, instance=self.object, prefix='participants')

    def get_collegial_formset(self, data=None):
        existing_count = self.object.governing_bodies.count() if self.object else 0
        extra_forms = max(0, 2 - existing_count)
        CollegialFormSet = inlineformset_factory(
            LegalEntity, Collegial_governing_bodies,
            form=Collegial_governing_bodiesForm,
            extra=extra_forms,
            max_num=2,
            can_delete=True,
            formset=BaseCollegialBodiesFormSet
        )
        return CollegialFormSet(data, instance=self.object, prefix='collegial')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        executive_formset = self.get_executive_formset(request.POST)
        participant_formset = self.get_participant_formset(request.POST)
        collegial_formset = self.get_collegial_formset(request.POST)

        if form.is_valid():
            if executive_formset.is_valid():
                if participant_formset.is_valid():
                    if collegial_formset.is_valid():
                        return self.form_valid(form, executive_formset, participant_formset, collegial_formset)
                    else:
                        print("форма по КОУ валидация не пройдена")
                else:
                    print('форма по участникам валидация не пройдена')
            else:
                print('форма по ЕИО валидация не пройдена')
        else:
            return self.form_invalid(form, executive_formset, participant_formset, collegial_formset)

    def form_valid(self, form, executive_formset, participant_formset, collegial_formset):
        with transaction.atomic():
            self.object = form.save()
            executive_formset.instance = self.object
            executive_formset.save()
            participant_formset.instance = self.object
            participant_formset.save()
            collegial_formset.instance = self.object
            objs = collegial_formset.save(commit=False)
            for obj in objs:
                obj.legal_entity = self.object
                obj.save()
            for obj in getattr(collegial_formset, 'deleted_objects', []):
                obj.delete()
        return redirect(self.get_success_url())

    def form_invalid(self, form, executive_formset, participant_formset, collegial_formset):
        return self.render_to_response(self.get_context_data(
            form=form,
            executive_formset=executive_formset,
            participant_formset=participant_formset,
            collegial_formset=collegial_formset
        ))


class LegalEntityUpdateFromEGRULView(UpdateView):
    """
        класс отвечает за редактирование с вапиской
    """
    model = LegalEntity
    form_class = LegalEntityForm
    template_name = 'legal_opin/legal_entity_form.html'

    def get_success_url(self):
        # получаем url после успешного редактирования
        return reverse_lazy('legal_opin:legal_entity_detail', kwargs={'pk': self.object.pk})

    def get_initial(self):
        initial = {}
        new_data = self.request.session.get('legal_entity_data')
        if new_data:
            initial.update(new_data['legal_entity'])
        inf = new_data['legal_entity']
        initial['legal_form'] = inf['legal_form']
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = self.request.session.get('legal_entity_data')

        # Сравнение данных основной формы
        changed_fields = {}
        if data:
            new_entity_data = data['legal_entity']
            for field, value in new_entity_data.items():
                old_value = getattr(self.object, field, None)
                if field == 'info_ustav':
                    value_to_compare = remove_non_printable(value)
                    old_value_to_compare = remove_non_printable(old_value)
                elif field == 'info_ustav_doc':
                    value_to_compare = remove_non_printable(value)
                    old_value_to_compare = remove_non_printable(old_value)
                else:
                    value_to_compare = value or ''
                    old_value_to_compare = old_value or ''
                if value_to_compare != old_value_to_compare:
                    changed_fields[field] = {'new': value, 'old': old_value}
        context['is_update_from_egrul'] = True
        entity = self.get_object()

        session_data = self.request.session.get('legal_entity_data')
        exec_info = session_data.get('executive_bodies', [])
        part_info = session_data.get('participants', [])

        # Сравнение полей ЕИО
        executive_changes = []
        current_executives = list(entity.executive_bodies.all())
        new_executives = exec_info

        # Поля, которые нужно сравнивать
        executive_fields = ['name', 'inn', 'job_title', 'date_of_authority']

        # Для каждого нового ЕИО ищем соответствующий старый по ИНН
        for new_exec in new_executives:
            changes = {}
            # Ищем существующего ЕИО с таким же ИНН
            old_exec = next((x for x in current_executives if x.inn == new_exec.get('inn')), None)
            if old_exec:
                # Сравниваем только указанные поля
                for field in executive_fields:
                    new_value = new_exec.get(field)
                    old_value = getattr(old_exec, field, None)
                    # Для date_of_authority преобразуем строку в дату
                    if field == 'date_of_authority' and new_value:
                        from datetime import datetime
                        try:
                            new_value = datetime.strptime(new_value, '%Y-%m-%d').date()
                        except (ValueError, TypeError):
                            continue
                    if (new_value or '') != (old_value or ''):
                        changes[field] = {'old': old_value, 'new': new_value}
            else:
                # Если это новый ЕИО, помечаем все поля как новые
                changes = {field: {'old': None, 'new': new_exec.get(field)}
                           for field in executive_fields if new_exec.get(field)}

            if changes:  # Если есть изменения
                executive_changes.append({
                    'inn': new_exec.get('inn'),
                    'changes': changes
                })

        # Сравнение полей участники
        part_changes = []
        current_part = list(entity.participants.all())
        new_part = part_info

        # Поля, которые нужно сравнивать
        executive_fields = ['name', 'inn', 'share', 'share_info', 'address']

        # Для каждого нового участника ищем соответствующий старый по ИНН
        for new_par in new_part:
            changes = {}
            # Ищем существующего участника с таким же ИНН
            old_part = next((x for x in current_part if x.inn == new_par.get('inn')), None)
            if old_part:
                # Сравниваем только указанные поля
                for field in executive_fields:
                    new_value = new_par.get(field)
                    old_value = getattr(old_part, field, None)
                    # Для date_of_authority преобразуем строку в дату
                    if field == 'date_of_authority' and new_value:
                        from datetime import datetime
                        try:
                            new_value = datetime.strptime(new_value, '%Y-%m-%d').date()
                        except (ValueError, TypeError):
                            continue
                    if (new_value or '') != (old_value or ''):
                        changes[field] = {'old': old_value, 'new': new_value}
            else:
                # Если это новый участник, помечаем все поля как новые
                changes = {field: {'old': None, 'new': new_par.get(field)}
                           for field in executive_fields if new_par.get(field)}

            if changes:  # Если есть изменения
                part_changes.append({
                    'inn': new_par.get('inn'),
                    'changes': changes
                })

        context['changed_fields'] = changed_fields
        context['executive_changes'] = executive_changes
        context['part_changes'] = part_changes

        initial_executives = []
        initial_part = []
        for new_exec in new_executives:
            # Ищем существующего ЕИО с таким же ИНН
            old_exec = next((x for x in current_executives if x.inn == new_exec.get('inn')), None)
            exec_data = {}
            if old_exec:
                # Берем все поля из старого ЕИО
                for field in old_exec._meta.fields:
                    if not field.primary_key:
                        exec_data[field.name] = getattr(old_exec, field.name)
                # Обновляем только те поля, которые пришли в новых данных
                for k in ['name', 'inn', 'job_title', 'date_of_authority']:
                    if k in new_exec and new_exec[k] is not None:
                        exec_data[k] = new_exec[k]
            else:
                # Если это новый ЕИО, заполняем только теми полями, что есть в массиве
                exec_data = {k: v for k, v in new_exec.items() if v is not None}
                if 'legal_entity' in exec_data:
                    del exec_data['legal_entity']
            initial_executives.append(exec_data)

        # по Участникам
        for new_parter in new_part:
            # Ищем существующего участника с таким же ИНН
            old_part = next((x for x in current_part if x.inn == new_parter.get('inn')), None)
            part_data = {}
            if old_part:
                # Берем все поля из старого участника
                for field in old_part._meta.fields:
                    if not field.primary_key:
                        part_data[field.name] = getattr(old_part, field.name)
                # Обновляем только те поля, которые пришли в новых данных
                for k in ['name', 'inn', 'share', 'share_info', 'address']:
                    if k in new_parter and new_parter[k] is not None:
                        part_data[k] = new_parter[k]
            else:
                # Если это новый участник, заполняем только теми полями, что есть в массиве
                part_data = {k: v for k, v in new_parter.items() if v is not None}
            if 'legal_entity' in part_data:
                del part_data['legal_entity']
            initial_part.append(part_data)

        context['executive_formset'] = self.get_executive_formset(initial=initial_executives)

        context['participant_formset'] = self.get_participant_formset(initial=initial_part)
        context['сollegial_governing_bodies_formset'] = self.get_collegial_formset()

        context['is_update_from_egrul'] = True
        return context

    def get_executive_formset(self, data=None, initial=None):
        ExecutiveBodyFormSet = forms.formset_factory(
            form=ExecutiveBodyForm,
            extra=0 if initial else 1,
            can_delete=False
        )
        if data:
            return ExecutiveBodyFormSet(data, prefix='executive')
        return ExecutiveBodyFormSet(initial=initial or [], prefix='executive')

    def get_participant_formset(self, initial=None):
        ParticipantFormSet = forms.formset_factory(
            form=ParticipantForm,
            extra=0 if initial else 1,
            can_delete=False
        )
        return ParticipantFormSet(
            prefix='participant',
            initial=initial or []
        )

    def get_collegial_formset(self, data=None):
        existing_count = self.object.governing_bodies.count() if self.object else 0
        extra_forms = max(0, 2 - existing_count)
        CollegialFormSet = inlineformset_factory(
            LegalEntity, Collegial_governing_bodies,
            form=Collegial_governing_bodiesForm,
            extra=extra_forms,
            max_num=2,
            can_delete=True,
            formset=BaseCollegialBodiesFormSet
        )
        return CollegialFormSet(data, instance=self.object, prefix='collegial')

    def post(self, request, *args, **kwargs):

        self.object = self.get_object()
        form = self.get_form()

        # Получаем КЛАССЫ формсетов (не экземпляры)
        ExecutiveBodyFormSet = forms.formset_factory(
            ExecutiveBodyForm,
            extra=0,
            can_delete=False
        )
        ParticipantFormSet = forms.formset_factory(
            ParticipantForm,
            extra=0,
            can_delete=True
        )
        CollegialFormSet = inlineformset_factory(
            LegalEntity, Collegial_governing_bodies,
            form=Collegial_governing_bodiesForm,
            extra=0,
            can_delete=True,
            formset=BaseCollegialBodiesFormSet
        )

        # Создаем экземпляры формсетов с POST-данными
        executive_formset = ExecutiveBodyFormSet(
            request.POST,
            prefix='executive'
        )
        participant_formset = ParticipantFormSet(
            request.POST,
            prefix='participant'
        )
        collegial_formset = CollegialFormSet(
            request.POST,
            instance=self.object,
            prefix='collegial'
        )

        if form.is_valid():
            if executive_formset.is_valid():
                if participant_formset.is_valid():
                    if collegial_formset.is_valid():
                        return self.form_valid(form, executive_formset, participant_formset, collegial_formset)
                    else:
                        print("форма по КОУ валидация не пройдена")
                else:
                    print('форма по участникам валидация не пройдена')
            else:
                print('форма по ЕИО валидация не пройдена')
        else:
            print('Основная форма, валидация не пройднеа')

        # if all([form.is_valid(), executive_formset.is_valid(), participant_formset.is_valid(), collegial_formset.is_valid()]):
        #     return self.form_valid(form, executive_formset, participant_formset, collegial_formset)
        return self.form_invalid(form, executive_formset, participant_formset, collegial_formset)

    def form_valid(self, form, executive_formset, participant_formset, collegial_formset):
        main_obj = form.save()

        # Сохраняем исполнительные органы: полная синхронизация с формсетом
        executives_to_save = []
        for exec_form in executive_formset:
            if not exec_form.cleaned_data:
                continue
            exec_body = exec_form.save(commit=False)
            exec_body.legal_entity = main_obj
            executives_to_save.append(exec_body)
        ExecutiveBody.objects.filter(legal_entity=main_obj).delete()
        for exec_body in executives_to_save:
            exec_body.pk = None
            exec_body.save()

        # Сохраняем участников: полная синхронизация с формсетом
        participants_to_save = []
        for part_form in participant_formset:
            if not part_form.cleaned_data:
                continue
            if part_form.cleaned_data.get('DELETE'):
                continue
            participant = part_form.save(commit=False)
            participant.legal_entity = main_obj
            participants_to_save.append(participant)
        Participant.objects.filter(legal_entity=main_obj).delete()
        for participant in participants_to_save:
            participant.pk = None
            participant.save()

        # Сохраняем коллегиальные органы через inlineformset (включая новые и удаленные)
        collegial_formset.instance = main_obj
        objs = collegial_formset.save(commit=False)
        for obj in objs:
            obj.legal_entity = main_obj
            obj.save()
        for obj in getattr(collegial_formset, 'deleted_objects', []):
            obj.delete()

        # Очищаем сессию
        if 'legal_entity_data' in self.request.session:
            del self.request.session['legal_entity_data']

        # Очищаем сессию ПОСЛЕ успешного сохранения
        self._cleanup_session_data()
        return redirect('legal_opin:legal_entity_detail', pk=main_obj.pk)

    def form_invalid(self, form, executive_formset, participant_formset, collegial_formset):
        return self.render_to_response(
            self.get_context_data(
                form=form,
                executive_formset=executive_formset,
                participant_formset=participant_formset,
                collegial_formset=collegial_formset
            )
        )

    def _cleanup_session_data(self):
        """Очистка данных сессии связанных с созданием/редактированием ЮЛ"""
        session_keys = ['legal_entity_data']
        for key in session_keys:
            if key in self.request.session:
                del self.request.session[key]


def start_update_from_egrul(request, pk):
    # функкия для получения массива в рамках функционала редактирование с выпиской
    legal_entity = get_object_or_404(LegalEntity, pk=pk)
    egrul = EgrulDownloader(legal_entity.inn)
    egrul_vipiska = egrul.download()
    if egrul_vipiska == 'Ошибка' or egrul_vipiska == 'На сайте требуется капча':
        return JsonResponse({
            'status': 'searching',
            'message': 'Ошибка запроса к сайту. Повторите запрос через 5 минут'
        })
    else:
        parser = EgripParser(egrul_vipiska)
        itog = parser.parse()
        conv = Converter(itog)
        new_mass = conv.itog()
        # Сохраняем данные в сессии
        request.session['legal_entity_data'] = {
            'legal_entity': new_mass[0],
            'executive_bodies': new_mass[1],
            'participants': new_mass[2]
        }
        return redirect('legal_opin:legal_entity_update_from_egrul', pk=pk)


# БЛОК Сделки(список, карточка, создание, редактирование)
class DealListView(ListView):
    """
        класс отвечает за список сделок
    """
    model = Deal
    template_name = 'list.html'
    context_object_name = 'deals'
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related('participants__legal_entity')

        # Фильтрация
        company_group = self.request.GET.get('company_group')
        credit_product = self.request.GET.get('credit_product')

        if company_group:
            queryset = queryset.filter(company_group__icontains=company_group)

        if credit_product:
            queryset = queryset.filter(credit_product_type__icontains=credit_product)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Передаем параметры фильтрации обратно в шаблон для отображения
        context['filter_company_group'] = self.request.GET.get('company_group', '')
        context['filter_credit_product'] = self.request.GET.get('credit_product', '')
        context['id_app'] = 'legal_opin_deal'  # ВАЖНО! Идентификатор приложения!
        return context


class DealCreateView(CreateView):
    """
        класс отвечает за создание сделки
    """
    model = Deal
    form_class = DealForm
    template_name = 'legal_opin/deal_form.html'

    def form_valid(self, form):
        # Присваиваем автора сделки текущему пользователю
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        # Перенаправляем на карточку созданной сделки
        return reverse_lazy('legal_opin:deal_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = True
        return context


class DealDetailView(DetailView):
    """
        класс отвечает за карточку сделки
    """
    model = Deal
    template_name = 'legal_opin/detail_deal.html'
    context_object_name = 'deal'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        deal = self.get_object()
        # Получаем всех участников и обеспечения для отображения во вкладках
        context['participants'] = deal.participants.select_related('legal_entity').all()
        # Получить связанные Collateral
        collaterals = deal.Collateral.select_related('owner').all()  # <-- исправили здесь

        context['collaterals'] = collaterals  # просто список для шаблона


        participants_with_risks = []
        total_risks_count = 0

        for participant in deal.participants.all():
            # ВСЕ риски участника
            all_risks = Risk_DealParticipant.objects.filter(
                deal=deal,
                owner=participant.legal_entity
            )

            risk_count = all_risks.count()
            total_risks_count += risk_count

            participants_with_risks.append({
                'participant': participant,
                'all_risks': all_risks,  # ВСЕ риски
                'risk_count': risk_count,
                'has_risks': risk_count > 0
            })

        context.update({
            'participants_with_risks': participants_with_risks,
            'total_risks_count': total_risks_count,
            'has_risks': total_risks_count > 0
        })
        return context


class DealUpdateView(UpdateView):
    """
        класс отвечает за функцию редактирование условий сделки
    """
    model = Deal
    form_class = DealForm
    template_name = 'legal_opin/deal_form.html'

    def get_success_url(self):
        return reverse_lazy('legal_opin:deal_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = False
        return context


def add_participant_by_inn(request, deal_pk):
    # функция отвечает за поиск ЮЛ при добавлении участника в сделке
    if request.method == 'POST':
        inn = request.POST.get('inn')
        if not inn or not inn.isdigit():
            return JsonResponse({'status': 'error', 'message': 'ИНН должен состоять из цифр.'}, status=400)
        try:
            legal_entity = LegalEntity.objects.get(inn=inn)
            # Юр. лицо найдено, генерируем URL для перехода на форму информации об участнике
            redirect_url = reverse('legal_opin:deal_participant_form',
                                   kwargs={'deal_pk': deal_pk, 'le_pk': legal_entity.pk})
            return JsonResponse({'status': 'found', 'redirect_url': redirect_url})
        except LegalEntity.DoesNotExist:
            # Юр. лицо не найдено
            return JsonResponse({'status': 'not_found', 'inn': inn})

    return JsonResponse({'status': 'error', 'message': 'Неверный метод запроса.'}, status=405)


class DealParticipantCreateView(CreateView):
    """
        класс отвечает за создание участника сделки
        Обработчик на ситуацию: Заемщик не может быть Поручителем!

    """
    model = DealParticipant
    form_class = DealParticipantForm
    template_name = 'legal_opin/deal_participant_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем сделку и юр. лицо из URL для отображения в шаблоне
        context['deal'] = get_object_or_404(Deal, pk=self.kwargs['deal_pk'])
        context['legal_entity'] = get_object_or_404(LegalEntity, pk=self.kwargs['le_pk'])

        context['is_create'] = True
        return context

    def form_valid(self, form):
        # Привязываем участника к сделке и юр. лицу перед сохранением
        deal = get_object_or_404(Deal, pk=self.kwargs['deal_pk'])
        legal_entity = get_object_or_404(LegalEntity, pk=self.kwargs['le_pk'])
        role = form.cleaned_data['role']
        if str(role.name) == 'Заемщик':
            if DealParticipant.objects.filter(deal=deal, role=role).exists():
                form.add_error(None, 'Заемщик в качестве участников уже есть')
                return self.form_invalid(form)
            if DealParticipant.objects.filter(deal=deal, legal_entity=legal_entity, ).exists():
                for j in DealParticipant.objects.filter(deal=deal, legal_entity=legal_entity):
                    if j.role.name == 'Поручитель':
                        form.add_error(None, 'Одно и то же ЮЛ не может быть Заемщиком и Поручителем')
                        return self.form_invalid(form)

        if str(role.name) == 'Поручитель':
            if DealParticipant.objects.filter(deal=deal, legal_entity=legal_entity, ).exists():
                for j in DealParticipant.objects.filter(deal=deal, legal_entity=legal_entity):
                    if j.role.name == 'Заемщик':
                        form.add_error(None, 'Одно и то же ЮЛ не может быть Поручителем и Заемщиком')
                        return self.form_invalid(form)

        if DealParticipant.objects.filter(deal=deal, legal_entity=legal_entity, role=role).exists():
            form.add_error(None, 'Этот участник с такой ролью для данной сделки уже существует.')
            return self.form_invalid(form)
        form.instance.deal = deal
        form.instance.legal_entity = legal_entity
        return super().form_valid(form)

    def get_success_url(self):
        # Возвращаемся на карточку сделки
        return reverse_lazy('legal_opin:deal_detail', kwargs={'pk': self.kwargs['deal_pk']})


class DealParticipantUpdateView(UpdateView):
    """
    Класс отвечает за редактирование участника сделки
    """
    model = DealParticipant
    form_class = DealParticipantForm
    template_name = 'legal_opin/deal_participant_form.html'
    context_object_name = 'participant'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # self.object здесь - это экземпляр DealParticipant
        context['deal'] = self.object.deal
        context['legal_entity'] = self.object.legal_entity
        context['is_create'] = False
        return context

    def get_success_url(self):
        return reverse('legal_opin:deal_detail', kwargs={'pk': self.object.deal.pk})


class DealParticipantDeleteView(DeleteView):
    model = DealParticipant
    template_name = 'confirm_delete.html'  # или ваш шаблон подтверждения

    def get_success_url(self):
        # Возвращаем на страницу сделки после удаления
        deal_id = self.object.deal.id
        return reverse_lazy('legal_opin:deal_detail', kwargs={'pk': deal_id})


# Базовый класс для работы с формсетом обеспечений
class CollateralFormsetView(TemplateResponseMixin, View):
    template_name = 'legal_opin/collateral_form.html'
    title = ""  # Заголовок страницы
    success_message = ""
    extra = 0  # Добавьте значение по умолчанию
    can_delete = False  # Добавьте значение по умолчанию

    def get_deal(self):
        # Получаем объект сделки из URL
        deal_id = self.kwargs.get('deal_id')
        return get_object_or_404(Deal, pk=deal_id)

    def get_formset(self, **kwargs):
        # Создаем фабрику формсета с нужными параметрами
        kwargs['can_delete'] = self.can_delete
        return inlineformset_factory(
            parent_model=Deal,
            model=Collateral,
            form=CollateralForm,
            **kwargs)

    def get(self, request, *args, **kwargs):
        # Обработка GET-запроса: показываем пустые или существующие формы
        deal = self.get_deal()
        FormSet = self.get_formset(extra=self.extra, can_delete=self.can_delete)
        formset = FormSet(instance=deal)
        return self.render_to_response(self.get_context_data(deal=deal, formset=formset))

    def post(self, request, *args, **kwargs):
        deal = self.get_deal()
        FormSet = self.get_formset(extra=self.extra, can_delete=self.can_delete)
        formset = FormSet(request.POST, instance=deal)
        if formset.is_valid():
            # Сохраняем - это обработает удаление автоматически
            instances = formset.save()
            messages.success(request, self.success_message)
            return redirect('legal_opin:deal_detail', pk=deal.pk)
        else:
            print("Formset validation failed")
            return self.render_to_response(self.get_context_data(deal=deal, formset=formset))

    def get_context_data(self, **kwargs):
        # Добавляем переменные в контекст шаблона
        kwargs.setdefault('title', self.title)
        return kwargs


# Представление для создания обеспечений
class CollateralCreateView(CollateralFormsetView):
    title = "Добавить обеспечения"
    success_message = "Обеспечения успешно созданы."
    extra = 1  # Начинаем с одной пустой формы
    can_delete = True  # Позволяем удалять даже новые, еще не сохраненные формы


# Представление для редактирования обеспечений
class CollateralUpdateView(CollateralFormsetView):
    title = "Редактировать обеспечения"
    success_message = "Обеспечения успешно обновлены."
    extra = 1  # Всегда даем одну дополнительную пустую форму для добавления
    can_delete = True  # Разрешаем удаление существующих записей


# Представление для удаления обеспечений
class DealCollateralDeleteView(DeleteView):
    model = Collateral
    template_name = 'confirm_delete.html'  # или ваш шаблон подтверждения

    def get_success_url(self):
        # Возвращаем на страницу сделки после удаления
        deal_id = self.object.deal.id
        return reverse_lazy('legal_opin:deal_detail', kwargs={'pk': deal_id})


# РИСКИ
class RiskAnalysisView(FormView):
    template_name = 'legal_opin/risk_participant.html'
    form_class = Risk_DealParticipantForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        deal_id = self.kwargs['deal_id']
        deal = get_object_or_404(Deal, id=deal_id)
        is_edit = self.kwargs.get('is_edit', False)

        # Получаем всех участников сделки
        participants = deal.participants.all()

        participants_with_risks = []
        for participant in participants:
            if is_edit:
                # РЕЖИМ РЕДАКТИРОВАНИЯ: получаем ВСЕ существующие риски участника
                existing_risks = Risk_DealParticipant.objects.filter(
                    deal=deal,
                    owner=participant.legal_entity
                )

                # Создаем формы для всех существующих рисков
                forms = []
                for risk in existing_risks:
                    form = Risk_DealParticipantForm(instance=risk)
                    forms.append(form)

                participants_with_risks.append({
                    'participant': participant,
                    'risks': list(existing_risks),  # Все риски
                    'forms': forms,
                    'form_count': existing_risks.count(),
                    'is_edit': True
                })
            else:
                # РЕЖИМ СОЗДАНИЯ: определяем автоматические риски
                risk = Risk_analiz(participant)
                test = risk.main()
                # automatic_risks = self.get_risks_for_participant(participant)
                automatic_risks = test

                # Проверяем, какие автоматические риски уже сохранены в БД
                existing_risks = Risk_DealParticipant.objects.filter(
                    deal=deal,
                    owner=participant.legal_entity
                )

                # Создаем формы для автоматических рисков
                forms = []
                for risk_data in automatic_risks:
                    # Проверяем, существует ли уже такой риск по содержанию
                    existing_risk = None
                    for er in existing_risks:
                        if er.risk == risk_data['risk_obj'].risk:
                            existing_risk = er
                            break

                    if existing_risk:
                        form = Risk_DealParticipantForm(instance=existing_risk)
                    else:
                        form = Risk_DealParticipantForm(initial={
                            'risk': risk_data['risk_obj'].risk,
                            'negative_consequences': risk_data['risk_obj'].negative_consequences,
                            'owner': participant.legal_entity,
                            'deal': deal
                        })

                    forms.append(form)

                participants_with_risks.append({
                    'participant': participant,
                    'risks': automatic_risks,
                    'forms': forms,
                    'form_count': len(automatic_risks),
                    'is_edit': False
                })

        # Получаем риски из альбома для модального окна
        album_risks = Risk.objects.filter(direction=2)
        subjects = Subject.objects.filter(risk__in=album_risks).distinct()

        context.update({
            'deal': deal,
            'participants_with_risks': participants_with_risks,
            'album_risks': album_risks,
            'subjects': subjects,
            'is_edit': is_edit
        })
        return context

    def get_forms_for_existing_risks(self, risks):
        """Создаем формы для существующих рисков"""
        forms = []
        for risk in risks:
            form = Risk_DealParticipantForm(instance=risk)
            forms.append(form)
        return forms


    def get_forms_for_participant(self, participant, risks):
        """Создаем формы для рисков участника"""
        forms = []
        for risk_data in risks:
            risk_obj = risk_data['risk_obj']
            form = Risk_DealParticipantForm(initial={
                'risk': risk_obj.risk,
                'negative_consequences': risk_obj.negative_consequences,
                'owner': participant.legal_entity,
                'deal': participant.deal,
                'risk_type': risk_data['type']  # Для идентификации типа риска
            })
            forms.append(form)
        return forms

    def post(self, request, *args, **kwargs):
        deal_id = self.kwargs['deal_id']
        deal = get_object_or_404(Deal, id=deal_id)
        # новая
        is_edit = self.kwargs.get('is_edit', False)

        if is_edit:
            # РЕЖИМ РЕДАКТИРОВАНИЯ: обновляем все существующие риски
            participants = deal.participants.all()
            for participant in participants:
                existing_risks = Risk_DealParticipant.objects.filter(
                    deal=deal,
                    owner=participant.legal_entity
                )

                # Обновляем каждый существующий риск
                for i, risk in enumerate(existing_risks):
                    prefix = f'participant_{participant.id}_risk_{i}'

                    risk.risk = request.POST.get(f'{prefix}_risk', '')
                    risk.negative_consequences = request.POST.get(f'{prefix}_negative_consequences', '')
                    risk.risk_faktor = request.POST.get(f'{prefix}_risk_faktor', '')
                    risk.minimization_measures = request.POST.get(f'{prefix}_minimization_measures', '')
                    risk.level_inherent_risk = request.POST.get(f'{prefix}_level_inherent_risk', '')
                    risk.residual_risk_level = request.POST.get(f'{prefix}_residual_risk_level', '')
                    risk.dop_info = request.POST.get(f'{prefix}_dop_info', '')
                    risk.save()
        else:
            # РЕЖИМ СОЗДАНИЯ: обрабатываем автоматические риски
            # Обрабатываем автоматические риски
            participants = deal.participants.all()
            for participant in participants:
                risk = Risk_analiz(participant)
                test = risk.main()
                # automatic_risks = self.get_risks_for_participant(participant)
                automatic_risks = test

                for i, risk_data in enumerate(automatic_risks):
                    prefix = f'participant_{participant.id}_risk_{i}'

                    # Получаем данные из формы
                    risk_text = request.POST.get(f'{prefix}_risk', '')
                    consequences = request.POST.get(f'{prefix}_negative_consequences', '')
                    risk_faktor = request.POST.get(f'{prefix}_risk_faktor', '')
                    measures = request.POST.get(f'{prefix}_minimization_measures', '')
                    inherent_risk = request.POST.get(f'{prefix}_level_inherent_risk', '')
                    residual_risk = request.POST.get(f'{prefix}_residual_risk_level', '')
                    dop_info = request.POST.get(f'{prefix}_dop_info', '')

                    # Проверяем, существует ли уже такой риск по содержанию
                    existing_risks = Risk_DealParticipant.objects.filter(
                        deal=deal,
                        owner=participant.legal_entity
                    )

                    existing_risk = None
                    for er in existing_risks:
                        if er.risk == risk_text:
                            existing_risk = er
                            break

                    if existing_risk:
                        # Обновляем существующий риск
                        existing_risk.risk = risk_text
                        existing_risk.negative_consequences = consequences
                        existing_risk.risk_faktor = risk_faktor
                        existing_risk.minimization_measures = measures
                        existing_risk.level_inherent_risk = inherent_risk
                        existing_risk.residual_risk_level = residual_risk
                        existing_risk.dop_info = dop_info
                        existing_risk.save()
                    else:
                        # Создаем новый риск
                        Risk_DealParticipant.objects.create(
                            deal=deal,
                            owner=participant.legal_entity,
                            risk=risk_text,
                            negative_consequences=consequences,
                            risk_faktor=risk_faktor,
                            minimization_measures=measures,
                            level_inherent_risk=inherent_risk,
                            residual_risk_level=residual_risk,
                            dop_info=dop_info
                        )

        # Обрабатываем новые риски (нетиповые и из альбома) для обоих режимов
        new_risk_count = int(request.POST.get('new_risk_count', 0))
        for i in range(new_risk_count):
            participant_id = request.POST.get(f'new_risk_{i}_participant_id')
            if participant_id:
                participant = DealParticipant.objects.filter(
                    id=participant_id,
                    deal=deal
                ).first()

                if participant:
                    risk_data = {
                        'risk': request.POST.get(f'new_risk_{i}_risk', ''),
                        'negative_consequences': request.POST.get(f'new_risk_{i}_negative_consequences', ''),
                        'risk_faktor': request.POST.get(f'new_risk_{i}_risk_faktor', ''),
                        'minimization_measures': request.POST.get(f'new_risk_{i}_minimization_measures', ''),
                        'level_inherent_risk': request.POST.get(f'new_risk_{i}_level_inherent_risk', ''),
                        'residual_risk_level': request.POST.get(f'new_risk_{i}_residual_risk_level', ''),
                        'dop_info': request.POST.get(f'new_risk_{i}_dop_info', ''),
                    }

                    Risk_DealParticipant.objects.create(
                        deal=deal,
                        owner=participant.legal_entity,
                        **risk_data
                    )

        return redirect(self.get_success_url())

    def get_success_url(self):
        # Возвращаем на страницу сделки после удаления
        deal_id = self.kwargs['deal_id']
        deal = get_object_or_404(Deal, id=deal_id)
        return reverse_lazy('legal_opin:deal_detail', kwargs={'pk': deal_id})


    def process_existing_risks(self, request, deal):
        """Обработка существующих рисков в режиме редактирования"""
        for risk in Risk_DealParticipant.objects.filter(deal=deal):
            prefix = f'existing_risk_{risk.id}'
            form = Risk_DealParticipantForm(request.POST, prefix=prefix, instance=risk)
            if form.is_valid():
                form.save()


    def process_new_risks(self, request, deal):
        """Обработка новых рисков"""
        new_risk_count = int(request.POST.get('new_risk_count', 0))
        for i in range(new_risk_count):
            participant_id = request.POST.get(f'new_risk_{i}_participant_id')
            if participant_id:
                participant = DealParticipant.objects.filter(id=participant_id, deal=deal).first()
                if participant:
                    risk_data = {
                        'risk': request.POST.get(f'new_risk_{i}_risk', ''),
                        'negative_consequences': request.POST.get(f'new_risk_{i}_negative_consequences', ''),
                        'risk_faktor': request.POST.get(f'new_risk_{i}_risk_faktor', ''),
                        'minimization_measures': request.POST.get(f'new_risk_{i}_minimization_measures', ''),
                        'level_inherent_risk': request.POST.get(f'new_risk_{i}_level_inherent_risk', ''),
                        'residual_risk_level': request.POST.get(f'new_risk_{i}_residual_risk_level', ''),
                        'dop_info': request.POST.get(f'new_risk_{i}_dop_info', ''),
                    }

                    risk_instance = Risk_DealParticipant(
                        deal=deal,
                        owner=participant.legal_entity,
                        **risk_data
                    )
                    risk_instance.save()