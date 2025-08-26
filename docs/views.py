from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.db import transaction
from django.http import JsonResponse, HttpResponseRedirect

from .forms import SearchForm, DocumentForm, DocumentVersionForm, DocumentPDFForm, DocumentInfoForm, DocumentFileForm, DocumentTemplateForm, DocumentPresentationForm, SlideZipUploadForm
from .util import Docx_Reader, make_file_unique
from django.shortcuts import render, get_object_or_404
from .forms import SearchForm
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from io import BytesIO
import os, json
from datetime import datetime
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.core.paginator import Paginator
from django.conf import settings
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from .models import Document, Direction_of_business, Direction, Section, Doc_class, DocumentVersion

BUSINESS_URLS = {
    "Корпоративный бизнес": "kb_home",
    "Инвестиционный и международный бизнес": "mb_home",
    "Розничный бизнес": "rb_home",
    "Административно-хозяйственная деятельность": "ahd_home",
    "Корп. управление и раскрытие информации": "kuri_home",
}

class KBView(ListView):
    template_name = "list.html"
    context_object_name = 'documents'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        buisness = Direction_of_business.objects.get(name='Корпоративный бизнес')
        context['id_app'] = 'docs'  # ВАЖНО! Идентификатор приложения!
        context['categories'] = Section.objects.filter(global_section=buisness.pk)   # список рубрик данного бизнеса
        context['subcategories'] = Doc_class.objects.all()  # список документов данной рубрики
        data = {
            'directional': 'Корпоративный бизнес',
        }
        context['global_section'] = 'Корпоративный бизнес'
        context['search_form'] = SearchForm(initial=data)  # добавляем форму поиска
        return context

    def get_queryset(self):
        buisness = Direction_of_business.objects.get(name='Корпоративный бизнес')
        return Document.objects.filter(global_section=buisness.pk)   # список документов данного бизнеса


class RBView(ListView):
    template_name = "list.html"
    context_object_name = 'documents'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        buisness = Direction_of_business.objects.get(name='Розничный бизнес')
        context['id_app'] = 'docs'  # ВАЖНО! Идентификатор приложения!
        context['categories'] = Section.objects.filter(global_section=buisness.pk)  # список рубрик данного бизнеса
        context['subcategories'] = Doc_class.objects.all()  # список документов данной рубрики
        data = {
            'directional': 'Розничный бизнес',
        }
        context['search_form'] = SearchForm(initial=data)  # добавляем форму поиска
        return context

    def get_queryset(self):
        buisness = Direction_of_business.objects.get(name='Розничный бизнес')
        print(buisness.pk)
        return Document.objects.filter(global_section=buisness.pk)  # список документов данного бизнеса


class AHDView(ListView):
    template_name = "list.html"
    context_object_name = 'documents'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        buisness = Direction_of_business.objects.get(name='Административно-хозяйственная деятельность')
        context['id_app'] = 'docs'  # ВАЖНО! Идентификатор приложения!
        context['categories'] = Section.objects.filter(
            global_section=buisness.pk)  # список рубрик данного бизнеса
        context['subcategories'] = Doc_class.objects.all()  # список документов данной рубрики
        data = {
            'directional': 'Административно-хозяйственная деятельность',
        }
        context['search_form'] = SearchForm(initial=data)  # добавляем форму поиска
        return context

    def get_queryset(self):
        buisness = Direction_of_business.objects.get(name='Административно-хозяйственная деятельность')
        return Document.objects.filter(global_section=buisness.pk)  # список документов данного бизнеса


class MBView(ListView):
    template_name = "list.html"
    context_object_name = 'documents'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        buisness = Direction_of_business.objects.get(name='Инвестиционный и международный бизнес')
        context['id_app'] = 'docs'  # ВАЖНО! Идентификатор приложения!
        context['categories'] = Section.objects.filter(global_section=buisness.pk)  # список рубрик данного бизнеса
        context['subcategories'] = Doc_class.objects.all()  # список документов данной рубрики
        data = {
            'directional': 'Инвестиционный и международный бизнес',
        }
        context['search_form'] = SearchForm(initial=data)  # добавляем форму поиска
        return context

    def get_queryset(self):
        buisness = Direction_of_business.objects.get(name='Инвестиционный и международный бизнес')
        print(buisness.pk)
        return Document.objects.filter(global_section=buisness.pk)  # список документов данного бизнеса


class KURIView(ListView):
    template_name = "list.html"
    context_object_name = 'documents'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        buisness = Direction_of_business.objects.get(name='Корп. управление и раскрытие информации')
        context['id_app'] = 'docs'  # ВАЖНО! Идентификатор приложения!
        context['categories'] = Section.objects.filter(global_section=buisness.pk)  # список рубрик данного бизнеса
        context['subcategories'] = Doc_class.objects.all()  # список документов данной рубрики
        data = {
            'directional': 'Корп. управление и раскрытие информации',
        }
        context['search_form'] = SearchForm(initial=data)  # добавляем форму поиска
        return context

    def get_queryset(self):
        buisness = Direction_of_business.objects.get(name='Корп. управление и раскрытие информации')
        print(buisness.pk)
        return Document.objects.filter(global_section=buisness.pk)  # список документов данного бизнеса


class DocumentCreateView(CreateView):
    model = Document
    template_name = 'docs/docs_form.html'
    success_message = 'Информация добавлена!'
    success_url = reverse_lazy('docs:kb_home')

    def get_form_class(self):
        """Возвращает соответствующую форму в зависимости от типа документа"""
        document_type = self.request.GET.get('type', '')
        if document_type == 'document':
            return DocumentPDFForm
        elif document_type == 'info':
            return DocumentInfoForm
        elif document_type == 'file':
            return DocumentFileForm
        elif document_type == 'template':
            return DocumentTemplateForm
        elif document_type == 'presentation':
            return DocumentPresentationForm
        else:
            # По умолчанию возвращаем базовую форму
            return DocumentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['document_type'] = self.request.GET.get('type', '')
        return context

    def form_valid(self, form):
        # Получаем тип документа из GET параметра
        document_type = self.request.GET.get('type', '')
        print(f"DEBUG: Document type = {document_type}")
        
        # Устанавливаем is_template в зависимости от типа
        if document_type == 'template':
            form.instance.is_template = True
        else:
            form.instance.is_template = False
        
        # Устанавливаем статус по умолчанию
        form.instance.status = 'active'
        
        print(f"DEBUG: Form is valid, saving document...")
        # description сохраняется формой (поле 'description')

        # Save document first so we have primary key
        response = super().form_valid(form)  # creates self.object

        if document_type == 'file':
            files = self.request.FILES.getlist('attachments')
            if not files:
                form.add_error(None, 'Необходимо прикрепить хотя бы один файл.')
                return self.form_invalid(form)
            from .models import DocumentAttachment
            for f in files:
                DocumentAttachment.objects.create(
                    document=self.object,
                    file=f,
                    uploaded_by=self.request.user if self.request.user.is_authenticated else None
                )
        return response

    def form_invalid(self, form):
        print(f"DEBUG: Form is invalid")
        print(f"DEBUG: Form errors: {form.errors}")
        return super().form_invalid(form)

    def get_success_url(self):
        business_name = self.object.global_section.name
        url_name = BUSINESS_URLS.get(business_name, "kb_home")
        return reverse_lazy(f"docs:{url_name}")


def docs_search(request):
    """
    Функция по поиску
    получаем данные из поля поиска, ищем в полях "Название" и "Краткое описание"
    формируем результаты и отображаем в шаблоне search_res.html
    """
    query = None
    result = []
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            query = request.POST.get("query")
            buisness = Direction_of_business.objects.get(name=request.POST.get('directional'))
            search_vector = SearchVector('title',
                                         config='russian')  # указываем, что SearchVector будет искать в Названии и Кратком описании
            search_query = SearchQuery('*' + query + '*', config='russian')  # указываем маску поиска + русский язык
            results_AQ = Document.objects.annotate(
                search=search_vector, rank=SearchRank(search_vector, search_query),
            ).filter(search=search_query, global_section=buisness.pk)  # формируем результат
            # Далее формируем контекст шаблона
            context = {
                'id_app': 'docs',
                'result': results_AQ,
                'query': query,
                'rubrics': Section.objects.all(),
                'search_form': SearchForm(),
                'categories': Doc_class.objects.all()
            }
            return render(request, 'list.html', context=context)


def document_detail(request, document_id):
    # функция по рендерингу документа
    document = get_object_or_404(Document, id=document_id)
    display_type = document.get_display_type()
    
    # Обработка версий документа
    version_id = request.GET.get('version')
    show_main = request.GET.get('main') == 'true'
    
    if version_id:
        # Если указана конкретная версия - используем её
        selected_version = get_object_or_404(DocumentVersion, pk=version_id, document=document)
        pdf_url = selected_version.file.url if selected_version.file else None
        is_current_version = False
    elif show_main:
        # Если явно запрошен основной документ - показываем его
        selected_version = None
        pdf_url = document.file.url if document.file else None
        is_current_version = False
    else:
        # По умолчанию показываем актуальную редакцию
        current_version = document.current_version
        if current_version:
            selected_version = current_version
            pdf_url = current_version.file.url if current_version.file else None
            is_current_version = True
        else:
            # Если нет актуальной версии, используем основной файл
            selected_version = None
            pdf_url = document.file.url if document.file else None
            is_current_version = True
    
    context = {
        'object': document,  # для совместимости с шаблоном
        'document': document,
        'display_type': display_type,
        'pdf_url': pdf_url,
        'selected_version': selected_version,
        'is_current_version': is_current_version,
        'word_file_url': (selected_version.word_file.url if selected_version and selected_version.word_file else document.word_file.url if not selected_version and document.word_file else None),
        'show_main': show_main,
    }
    
    # Добавляем специфичные данные в зависимости от типа
    if display_type == 'pdf_document':
        # PDF-документ - используем PDF просмотрщик
        context.update({
            'is_textual_pdf': True,  # PDF.js обрабатывает все PDF
        })
        return render(request, 'docs/addons/document_detail.html', context)
    
    elif display_type == 'word_template':
        # Word-шаблон - конструктор договоров
        return render(request, 'docs/addons/document_detail_template.html', context)
    
    elif display_type == 'presentation':
        # Презентация - слайдер
        slides = document.slides.all()
        context['slides'] = slides
        return render(request, 'docs/addons/document_detail_slide.html', context)
    
    elif display_type == 'mixed_content':
        # Смешанный тип - файл + описание
        return render(request, 'docs/addons/document_detail_mix.html', context)
    
    elif display_type == 'text_only':
        # Только текстовая информация
        return render(request, 'docs/addons/document_detail_inf.html', context)
    
    else:
        # Fallback
        context['error'] = f'Неизвестный тип отображения: {display_type}'
        return render(request, 'docs/addons/document_detail.html', context)


def get_categories_for_global_section(request):
    global_section_id = request.GET.get('global_section_id')
    categories = Section.objects.filter(global_section_id=global_section_id)
    data = [
        {'id': cat.id, 'name': cat.name}
        for cat in categories
    ]
    return JsonResponse({'categories': data})

class DocumentUpdateView(UpdateView):
    model = Document
    template_name = 'docs/document_update_form.html'
    success_message = 'Документ обновлён'

    def dispatch(self, request, *args, **kwargs):
        self.version_id = request.GET.get('version')
        self.editing_version = None
        if self.version_id:
            from .models import DocumentVersion
            self.editing_version = get_object_or_404(DocumentVersion, pk=self.version_id, document_id=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        """Возвращает соответствующую форму в зависимости от типа документа"""
        document_type = self.object.get_display_type()
        if document_type == 'pdf_document':
            if self.editing_version:
                from .forms import DocumentVersionForm
                return DocumentVersionForm
            else:
                return DocumentPDFForm
        elif document_type == 'text_only':
            return DocumentInfoForm
        elif document_type == 'mixed_content':
            from .forms import DocumentFileUpdateForm
            return DocumentFileUpdateForm
        elif document_type == 'word_template':
            return DocumentTemplateForm
        elif document_type == 'presentation':
            return DocumentPresentationForm
        else:
            # По умолчанию возвращаем базовую форму
            return DocumentForm

    def get_initial(self):
        initial = super().get_initial()
        if self.editing_version:
            doc = self.object
            initial.update({
                'title': doc.title,
                'global_section': doc.global_section_id,
                'section': doc.section_id,
                'category': doc.category_id,
                'subcategory': doc.subcategory_id,
                'file': self.editing_version.file,
                'word_file': self.editing_version.word_file,
                'version_date': self.editing_version.version_date,
                'comment': self.editing_version.comment,
            })
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['document_type'] = 'pdf_version' if self.editing_version else self.object.get_display_type()
        context['editing_version'] = self.editing_version
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        doc_type = self.object.get_display_type()
        if self.editing_version:
            # Для редактирования версии все поля необязательные
            for field_name in ['file', 'word_file', 'version_date', 'comment', 'file_type']:
                if field_name in form.fields:
                    form.fields[field_name].required = False
        elif doc_type == 'presentation':
            form.fields['file'].required = False
            form.fields['slides_zip'].required = False
        elif doc_type == 'pdf_document':
            form.fields['file'].required = False
            if 'word_file' in form.fields:
                form.fields['word_file'].required = False
        return form

    def form_valid(self, form):
        # Устанавливаем is_template в зависимости от типа документа
        document_type = self.object.get_display_type()
        if document_type == 'word_template':
            form.instance.is_template = True
        else:
            form.instance.is_template = False
        response = super().form_valid(form)

        # если mixed_content – обрабатываем новые attachments
        if document_type == 'mixed_content':
            files = self.request.FILES.getlist('attachments')
            if files:
                from .models import DocumentAttachment
                for f in files:
                    DocumentAttachment.objects.create(
                        document=self.object,
                        file=f,
                        uploaded_by=self.request.user if self.request.user.is_authenticated else None
                    )

            # handle deletions
            delete_ids = self.request.POST.getlist('delete_attachments')
            if delete_ids:
                from .models import DocumentAttachment
                DocumentAttachment.objects.filter(document=self.object, id__in=delete_ids).delete()
        return response

    # куда перенаправлять после сохранения
    def get_success_url(self):
        if self.editing_version:
            return reverse_lazy('docs:document_detail', kwargs={'document_id': self.object.pk}) + f'?version={self.editing_version.id}'
        else:
            return reverse_lazy('docs:document_detail', kwargs={'document_id': self.object.pk})


class DocumentVersionDeleteView(DeleteView):
    model = DocumentVersion
    template_name = 'docs/document_confirm_delete.html'
    pk_url_kwarg = 'version_id'
    
    def get_object(self, queryset=None):
        document_id = self.kwargs['document_id']
        version_id = self.kwargs['version_id']
        return get_object_or_404(DocumentVersion, pk=version_id, document_id=document_id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['delete_type'] = 'version'
        context['document'] = self.object.document
        context['version'] = self.object
        return context
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        document = self.object.document
        
        # Сохраняем ссылку на документ перед удалением версии
        success_url = self.get_success_url()
        
        # Удаляем версию
        self.object.delete()
        
        # Перенумеровываем оставшиеся версии
        self._renumber_remaining_versions(document)
        
        return redirect(success_url)
    
    def _renumber_remaining_versions(self, document):
        """Перенумеровывает оставшиеся версии после удаления"""
        versions_with_date = list(document.versions.filter(version_date__isnull=False).order_by('version_date'))
        versions_without_date = list(document.versions.filter(version_date__isnull=True).order_by('uploaded_at'))
        
        from django.db import transaction
        offset = 1000
        with transaction.atomic():
            # Сначала сдвигаем все номера
            for v in versions_with_date + versions_without_date:
                v.version_number += offset
                v.save(update_fields=['version_number'])
            
            # Затем перенумеровываем корректно
            current_num = 1
            for v in versions_with_date:
                v.version_number = current_num
                v.save(update_fields=['version_number'])
                current_num += 1
            
            for v in versions_without_date:
                v.version_number = current_num
                v.save(update_fields=['version_number'])
                current_num += 1
    
    def get_success_url(self):
        return reverse('docs:document_detail', kwargs={'document_id': self.object.document.pk})


class DocumentDeleteView(DeleteView):
    model = Document
    template_name = 'docs/document_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['delete_type'] = 'document'
        return context

    # здесь нужен динамический success_url (зависит от global_section)
    def get_success_url(self):
        business_name = self.object.global_section.name
        url_name = BUSINESS_URLS.get(business_name, 'kb_home')
        # reverse_lazy нельзя (нужен арг из словаря), используем reverse
        return reverse(f'docs:{url_name}')

class DocumentListView(ListView):
    model = Document
    template_name = 'docs/document_list.html'

class DocumentDetailView(DetailView):
    model = Document
    template_name = 'docs/document_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        version_id = self.request.GET.get('version')
        if version_id:
            selected_version = get_object_or_404(DocumentVersion, pk=version_id, document=self.object)
        else:
            selected_version = self.object.latest_version
        context['selected_version'] = selected_version
        return context

class DocumentVersionView(DetailView):
    model = DocumentVersion
    pk_url_kwarg = 'version_id'
    template_name = 'docs/document_version_detail.html'

class AddDocumentVersionView(CreateView):
    model = DocumentVersion
    form_class = DocumentVersionForm
    template_name = 'docs/add_document_version.html'

    def dispatch(self, request, *args, **kwargs):
        self.document = get_object_or_404(Document, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        print("DEBUG: form_valid called")
        form.instance.document = self.document
        
        # Проверяем уникальность файлов перед сохранением
        if form.cleaned_data.get('file'):
            make_file_unique(form.cleaned_data['file'], self.document)
        if form.cleaned_data.get('word_file'):
            make_file_unique(form.cleaned_data['word_file'], self.document)
        
        # Временно ставим любой номер, потом перенумеруем все версии
        form.instance.version_number = 999
        form.instance.uploaded_by = self.request.user if self.request.user.is_authenticated else None
        
        # Сохраняем версию
        result = super().form_valid(form)
        
        # После сохранения перенумеровываем все версии
        self._renumber_all_versions()
        
        return result

    def _renumber_all_versions(self):
        """Перенумеровывает все версии документа по порядку дат редакции"""
        versions_with_date = list(self.document.versions.filter(version_date__isnull=False).order_by('version_date'))
        versions_without_date = list(self.document.versions.filter(version_date__isnull=True).order_by('uploaded_at'))

        # Чтобы обойти ограничение unique_together, сначала сдвигаем все номера на offset
        offset = 1000
        with transaction.atomic():
            for v in versions_with_date + versions_without_date:
                v.version_number += offset
                v.save(update_fields=['version_number'])

            # Теперь пронумеровываем корректно
            current_num = 1
            for v in versions_with_date:
                v.version_number = current_num
                v.save(update_fields=['version_number'])
                current_num += 1

            for v in versions_without_date:
                v.version_number = current_num
                v.save(update_fields=['version_number'])
                current_num += 1

    def form_invalid(self, form):
        print("DEBUG: form_invalid called")
        print(f"DEBUG: Form errors: {form.errors}")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('docs:document_detail', kwargs={'document_id': self.document.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['document'] = self.document
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Для создания версии поля документа не обязательны
        for field_name in ['title', 'global_section', 'section', 'category', 'subcategory', 'file_type']:
            if field_name in form.fields:
                form.fields[field_name].required = False
        return form

def upload_presentation_slides(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    if request.method == 'POST':
        form = SlideZipUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document.slides.all().delete()
            form.save(document)
            return redirect('docs:document_detail', document_id=document.id)
    else:
        form = SlideZipUploadForm()
    return render(request, 'docs/addons/upload_slides.html', {'form': form, 'document': document})