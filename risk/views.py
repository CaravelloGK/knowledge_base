from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Direction, Kind, Subject, Risk
from .forms import SearchForm, RiskForm, Export_filters
from django.urls import reverse_lazy
import pandas as pd
from django.http import HttpResponse
from io import BytesIO
from django.utils.timezone import now
from django.contrib import messages
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from django.db.models import Q


class RiskHome(ListView):
    """
    ViewClass ListView: Выводит список рисков
    """
    model = Risk  # Модель - риски
    template_name = 'list.html'  # Шаблон html list.html
    context_object_name = 'risks'  # Переменная для массива

    def get_context_data(self, **kwargs):  # Метод создает и возвращает контекст шаблона
        context = super().get_context_data(**kwargs)
        context['id_app'] = 'risk'   # ВАЖНО! Идентификатор приложения!
        context['Direction'] = Direction.objects.all()  # добавляем список направлений
        context['search_form'] = SearchForm()  # добавляем форму поиска
        context['Kind'] = Kind.objects.all()  # добавляем список видов
        context['Subject'] = Subject.objects.all()  # добавляем список предметов
        return context


class RiskDetalView(DetailView):
    """
    ViewClass DetailView: выводит карточку риска
    """
    template_name = 'risk/detail.html'  # Шаблон html modal_risk_detail.html
    context_object_name = 'rsk'  # Переменная для конкретной записи

    def get_object(self, queryset=None):    # Метод для получения объекта
        obj = get_object_or_404(Risk, pk=self.kwargs['pk'])
        return obj


class RiskDeleteView(DeleteView):
    """
    ViewClass DeleteView:Представление для удаления риска
    """
    model = Risk  # модель - Risk
    template_name = 'modal/modal_review_confirm_delete.html'  # Шаблон подтверждения html review_confirm_delete.html
    success_url = reverse_lazy('risk:risk_main')  # в случае успеха - переход к списку обзоров
    success_message = 'Риск успешно удален'

    def get_object(self, queryset=None):
        obj = get_object_or_404(Risk, pk=self.kwargs['pk'])
        return obj


class RiskCreateView(CreateView):
    """
    ViewClass CreateView: Представление для создания новой записи (риска)
    """
    model = Risk  # Модель - риски
    form_class = RiskForm  # Форма - 'RiskForm' (см. Forms.py)
    template_name = 'risk/risk_form.html'  # Шаблон html risk_form.html
    success_message = 'Обзор успешно создан!'

    def get_success_url(self):    # Метод по формированию успешного URL
        return reverse_lazy('risk:risk_detal', kwargs={'pk': self.object.pk})  # в случае успеха - переходим в карточку


class RiskUpdateView(UpdateView):
    """
    ViewClass UpdateView:Представление для редактирования рика
    """
    model = Risk  # модель - Risk
    form_class = RiskForm  # Форма - 'RiskForm' (см. Forms.py)
    template_name = 'risk/risk_form.html'  # Шаблон html review_form.html
    success_message = "All OK!"

    def get_object(self, queryset=None):    # Метод по получению объекта модели
        obj = get_object_or_404(Risk, pk=self.kwargs['pk'])
        return obj

    def get_success_url(self):
        return reverse_lazy('risk:risk_detal', kwargs={'pk': self.object.pk})  # в случае успеха - переходим в карточку


def risk_search(request):
    """
    Функция по поиску
    получаем данные из поля поиска, ищем в полях "Название" и "Краткое описание"
    формируем результаты и отображаем в шаблоне search_res.html
    """
    query = None
    result = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']  # берем данные из поля поиск
            search_vector = SearchVector('risk', 'risk_factor', 'legal_basis', 'negative_consequences',
                                         'minimization_measures', 'associated_risks', 'info_about_risk_realization',
                                         config='russian')  # указываем, что SearchVector будет искать в Названии и Кратком описании
            search_query = SearchQuery('*' + query + '*', config='russian')  # указываем маску поиска + русский язык
            results_AQ = Risk.objects.annotate(
                search=search_vector, rank=SearchRank(search_vector, search_query),
            ).filter(search=search_query)  # формируем результат
            # Далее формируем контекст шаблона
            context = {
                'id_app': 'risk',  # ВАЖНО! Идентификатор приложения!
                'result': results_AQ,
                'query': query,
                'form': SearchForm(),
                'Direction': Direction.objects.all(),
                'Kind': Kind.objects.all(),
                'Subject': Subject.objects.all()
            }
            return render(request, 'list.html', context=context)


def import_excel(request):
    """
    Функция по загрузке excel в БД рисков
    на вход принимает файл excel
    """
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']

        try:
            # Читаем Excel файл
            df = pd.read_excel(excel_file, engine='openpyxl')

            # Проверяем наличие необходимых колонок
            required_columns = {
                'direction', 'kind', 'subject', 'risk', 'risk_factor',
                'legal_basis', 'negative_consequences', 'minimization_measures',
                'associated_risks', 'info_about_risk_realization'
            }

            if not required_columns.issubset(df.columns):
                missing_cols = required_columns - set(df.columns)
                messages.error(request, f'В файле отсутствуют обязательные колонки: {", ".join(missing_cols)}')
                return redirect('risk:risk_main')

            created_count = 0
            updated_count = 0

            for _, row in df.iterrows():
                try:
                    # Получаем связанные объекты
                    direction = Direction.objects.get(name=row['direction'])
                    kind = Kind.objects.get(name=row['kind'])
                    subject = Subject.objects.get(name=row['subject'])

                    # Проверяем существование записи
                    risk, created = Risk.objects.get_or_create(
                        direction=direction,
                        kind=kind,
                        subject=subject,
                        risk=row['risk'],
                        defaults={
                            'risk_factor': row.get('risk_factor', ''),
                            'legal_basis': row.get('legal_basis', ''),
                            'negative_consequences': row.get('negative_consequences', ''),
                            'minimization_measures': row.get('minimization_measures', ''),
                            'associated_risks': row.get('associated_risks', ''),
                            'info_about_risk_realization': row.get('info_about_risk_realization', ''),
                        }
                    )

                    if not created:
                        # Обновляем существующую запись, если данные изменились
                        update_fields = []
                        for field in ['risk_factor', 'legal_basis', 'negative_consequences',
                                      'minimization_measures', 'associated_risks',
                                      'info_about_risk_realization']:
                            new_value = row.get(field, '')
                            if getattr(risk, field) != new_value:
                                setattr(risk, field, new_value)
                                update_fields.append(field)

                        if update_fields:
                            risk.save(update_fields=update_fields)
                            updated_count += 1

                    if created:
                        created_count += 1

                except Direction.DoesNotExist:
                    messages.warning(request, f'Направление "{row["direction"]}" не найдено в базе. Пропускаем запись.')
                    continue
                except Kind.DoesNotExist:
                    messages.warning(request, f'Вид "{row["kind"]}" не найден в базе. Пропускаем запись.')
                    continue
                except Subject.DoesNotExist:
                    messages.warning(request, f'Предмет "{row["subject"]}" не найден в базе. Пропускаем запись.')
                    continue
                except Exception as e:
                    messages.warning(request, f'Ошибка при обработке строки: {e}')
                    continue

            messages.success(request, f'Обработка завершена. Создано: {created_count}, обновлено: {updated_count}')

        except Exception as e:
            messages.error(request, f'Ошибка при обработке файла: {str(e)}')

        return redirect('risk:risk_main')

    return render(request, 'risk/upload_risks.html')


def load_excel(request):
    """
    Функция по выгрузке всех рисков
    """
    risks = Risk.objects.select_related('direction', 'kind', 'subject').all()

    # Создаем список словарей с данными
    data = []
    for risk in risks:
        data.append({
            'direction': risk.direction.name if risk.direction else '',
            'kind': risk.kind.name if risk.kind else '',
            'subject': risk.subject.name if risk.subject else '',
            'risk': risk.risk,
            'risk_factor': risk.risk_factor,
            'legal_basis': risk.legal_basis,
            'negative_consequences': risk.negative_consequences,
            'minimization_measures': risk.minimization_measures,
            'associated_risks': risk.associated_risks,
            'info_about_risk_realization': risk.info_about_risk_realization,
        })

    # Создаем DataFrame
    df = pd.DataFrame(data)

    # Создаем Excel файл в памяти
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, sheet_name='Risks', index=False)
    writer.close()
    output.seek(0)

    # Создаем HttpResponse с Excel файлом
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f'risks_export_{now().strftime("%Y-%m-%d_%H-%M")}.xlsx'
    response['Content-Disposition'] = f'attachment; filename={filename}'

    return response


def export_filters(request):
    """
    Функция по выгрузке отфильтрованных рисков
    """
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = Export_filters(request.POST)
        # check whether it's valid:
        if form.is_valid():
            direction_f = form.cleaned_data['direction']
            kind_f = form.cleaned_data['kind']
            subject_f = form.cleaned_data['subject']
            print(direction_f, kind_f, subject_f, sep='\n')
            filter_kwargs = {
                key: value
                for key, value in [('direction', direction_f), ('kind', kind_f), ('subject', subject_f)] if value is not None
            }
            print(filter_kwargs)
            risks = Risk.objects.filter(**filter_kwargs)

            # Создаем список словарей с данными
            data = []
            for risk in risks:
                data.append({
                    'direction': risk.direction.name if risk.direction else '',
                    'kind': risk.kind.name if risk.kind else '',
                    'subject': risk.subject.name if risk.subject else '',
                    'risk': risk.risk,
                    'risk_factor': risk.risk_factor,
                    'legal_basis': risk.legal_basis,
                    'negative_consequences': risk.negative_consequences,
                    'minimization_measures': risk.minimization_measures,
                    'associated_risks': risk.associated_risks,
                    'info_about_risk_realization': risk.info_about_risk_realization,
                })

            # Создаем DataFrame
            df = pd.DataFrame(data)

            # Создаем Excel файл в памяти
            output = BytesIO()
            writer = pd.ExcelWriter(output, engine='openpyxl')
            df.to_excel(writer, sheet_name='Risks', index=False)
            writer.close()
            output.seek(0)

            # Создаем HttpResponse с Excel файлом
            response = HttpResponse(
                output.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            filename = f'risks_export_{now().strftime("%Y-%m-%d_%H-%M")}.xlsx'
            response['Content-Disposition'] = f'attachment; filename={filename}'

            return response

    else:
        form = Export_filters()

    return render(request, 'risk/upload_form.html', {"form": form})


def view_name(request):
    pass