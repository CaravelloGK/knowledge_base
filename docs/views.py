from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse

from .forms import SearchForm, DocumentForm
# from lib2to3.fixes.fix_input import context  # Removed: unnecessary and causes ModuleNotFoundError
from .util import Docx_Reader
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
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Document, Direction_of_business, Direction, Section, Doc_class

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


class DocumentCreateView(CreateView,
                       # ModeratorRequiredMixin
                       ):

    model = Document  # Модель - обзоры
    form_class = DocumentForm  # Форма - 'DocumentForm' (см. Forms.py)
    template_name = 'docs/docs_form.html'  # Шаблон html docs_form.html
    success_message = 'Информация добавлена!'
    success_url = reverse_lazy('docs:kb_home')

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
    info = document.description
    if info:
        doc_info = {
            'title':document.title,
            'status': document.status,
            'created_at': document.created_at,
            'global_section': document.global_section,
            'section': document.section,
            'category': document.category,
            'subcategory': document.subcategory,
            'text': info
        }
        return render(request, 'docs/addons/document_detail_inf.html', doc_info)
    else:
        string = str(document.file)
        parts = string.split("/", 1)
        substring = parts[1]  # Получаем первую часть строки (до первого "#")
        extension = substring[substring.find(".") + 1 : ]
        if extension == 'docx':
            doc_parser = Docx_Reader(document.file.path, document.is_template)
            itog = doc_parser.itog()
            return render(request, 'docs/addons/document_detail.html', itog)
        elif extension == 'pptx':
            pass
        elif extension == 'pdf':
            pass

    return render(request, 'docs/addons/document_detail.html', context)


def get_categories_for_global_section(request):
    global_section_id = request.GET.get('global_section_id')
    categories = Section.objects.filter(global_section_id=global_section_id)
    data = [
        {'id': cat.id, 'name': cat.name}
        for cat in categories
    ]
    return JsonResponse({'categories': data})