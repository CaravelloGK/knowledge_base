from re import search
from .forms import SearchForm, ReviewForm, EmailPostForm, RecommendMultipleForm, LoginForm
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.urls import reverse_lazy
from .models import Review, Rubric, Category
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from django.contrib.messages.views import SuccessMessageMixin
from pyexpat.errors import messages
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .filters import ReviewFilter
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from transliterate import translit



class ReviewsHome(ListView):
    """
    ViewClass ListView: Выводит список обзоров
    """
    model = Review  # Модель - обзоры
    template_name = 'list.html'  # Шаблон html list.html
    context_object_name = 'reviews'  # Переменная для массива
    ordering = ['-current_date']  # сортировка в списке по дате создания в обратном порядке
    
    def get_queryset(self):
        """Возвращаем только первые 25 записей для быстрой загрузки"""
        return Review.objects.all().order_by('-current_date')[:25]

    def get_context_data(self, **kwargs):  # Метод создает и возвращает контекст шаблона
        context = super().get_context_data(**kwargs)
        context['id_app'] = 'reviews'   # ВАЖНО! Идентификатор приложения!
        context['local_search_func'] = f'reviews:search'  # ВАЖНО! Функция поиска!
        context['rubrics'] = Rubric.objects.all()  # добавляем список рубрик
        context['search_form'] = SearchForm()  # добавляем форму поиска
        context['categories'] = Category.objects.all()  # добавляем список категорий
        
        # Добавляем данные для прогрессивной загрузки
        total_count = Review.objects.count()
        context['total_count'] = total_count
        context['loaded_count'] = 25
        context['has_more'] = total_count > 25
        
        return context


class ReviewDetalView(DetailView):
    """
    ViewClass DetailView: выводит карточку обзора
    """
    template_name = 'reviews/detail.html'  # Шаблон html modal_review_detail.html
    context_object_name = 'review'  # Переменная для конкретной записи

    def get_object(self, queryset=None):    # Метод для получения объекта
        obj = get_object_or_404(Review, pk=self.kwargs['pk'])
        return obj


class ReviewCreateView(CreateView):
    """
    ViewClass CreateView: Представление для создания новой записи (обзора)
    """
    model = Review  # Модель - обзоры
    form_class = ReviewForm  # Форма - 'ReviewForm' (см. Forms.py)
    template_name = 'reviews/review_form.html'  # Шаблон html review_form.html
    success_message = 'Обзор успешно создан!'

    def get_success_url(self):    # Метод по формированию успешного URL
        return reverse_lazy('reviews:review_detal', kwargs={'pk': self.object.pk})  # в случае успеха - переходим в карточку


class ReviewUpdateView(UpdateView):
    """
    ViewClass UpdateView:Представление для редактирования обзора
    """
    model = Review  # модель - Review
    form_class = ReviewForm  # Форма - 'ReviewForm' (см. Forms.py)
    template_name = 'reviews/review_form.html'  # Шаблон html review_form.html
    success_message = "All OK!"

    def get_object(self, queryset=None):    # Метод по получению объекта модели
        obj = get_object_or_404(Review, pk=self.kwargs['pk'])
        return obj

    def get_success_url(self):
        return reverse_lazy('reviews:review_detal', kwargs={'pk': self.object.pk})  # в случае успеха - переходим в карточку


class ReviewDeleteView(DeleteView):
    """
    ViewClass DeleteView:Представление для удаления записи
    """
    model = Review  # модель - Review
    template_name = 'modal/modal_review_confirm_delete.html'  # Шаблон подтверждения html review_confirm_delete.html
    success_url = reverse_lazy('reviews:reviews_main')  # в случае успеха - переход к списку обзоров
    success_message = 'Обзор успешно удален'

    def get_object(self, queryset=None):
        obj = get_object_or_404(Review, pk=self.kwargs['pk'])
        return obj


def post_search(request):
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
            search_vector = SearchVector('name', 'description',
                                         config='russian')  # указываем, что SearchVector будет искать в Названии и Кратком описании
            search_query = SearchQuery('*' + query + '*', config='russian')  # указываем маску поиска + русский язык
            results_AQ = Review.objects.annotate(
                search=search_vector, rank=SearchRank(search_vector, search_query),
            ).filter(search=search_query)  # формируем результат
            # Далее формируем контекст шаблона
            context = {
                'id_app': 'reviews',
                'result': results_AQ,
                'query': query,
                'rubrics': Rubric.objects.all(),
                'form': SearchForm(),
                'categories': Category.objects.all()
            }
            return render(request, 'list.html', context=context)



# ────────────────────────────────────────────────────────────────────
# 1) Форма выбора нескольких обзоров + AJAX‑фильтрация
#    /reviews/recommend-multiple/
# ────────────────────────────────────────────────────────────────────
def recommend_multiple_reviews(request):
    """Отображает страницу выбора обзоров
       + принимает POST и редиректит на preview."""
    # ➊ фильтруем обзоры по GET‑параметрам
    review_filter = ReviewFilter(request.GET, queryset=Review.objects.all())
    filtered = review_filter.qs

    # ----------- POST: пользователь нажал «Сформировать текст» ----------
    if request.method == 'POST':
        selected_ids = request.POST.getlist('reviews')
        if not selected_ids:
            messages.warning(request, 'Сначала выберите хотя бы один обзор.')
        else:
            ids_str = ','.join(selected_ids)
            preview_url = (
                f"{reverse_lazy('reviews:recommend_multiple_preview')}?ids={ids_str}"
            )
            return redirect(preview_url)

    # ----------- GET: показать форму выбора с учётом фильтров ----------
    form = RecommendMultipleForm()
    form.fields['reviews'].queryset = filtered   # чек‑боксы только по фильтру

    return render(
        request,
        'reviews/recommend_multiple_form.html',
        {
            'form': form,
            'reviews_list': filtered,
            'filter': review_filter,
            'rubrics': Rubric.objects.all(),
            'categories': Category.objects.all(),
            'selected_filters': request.GET,
        },
    )

# ────────────────────────────────────────────────────────────────────
# 2) Страница‑шаблон для копирования текста
#    /reviews/recommend-multiple/preview/?ids=1,5,9
# ────────────────────────────────────────────────────────────────────
def recommend_multiple_preview(request):
    """Генерирует HTML‑шаблон письма с выбранными обзорами."""
    id_list = request.GET.get('ids', '')
    pks = [int(pk) for pk in id_list.split(',') if pk.isdigit()]
    reviews = Review.objects.filter(pk__in=pks)

    return render(
        request,
        'reviews/reviews_list_mass.html',
        {'reviews': reviews},
    )


# ────────────────────────────────────────────────────────────────────
# 3) AJAX‑эндпоинт: вернуть HTML‑фрагмент чек‑боксов под текущие фильтры
#    /reviews/recommend-multiple/filter/
# ────────────────────────────────────────────────────────────────────
def recommend_multiple_filter_ajax(request):
    """Возвращает фрагмент со списком обзоров для живой фильтрации."""
    review_filter = ReviewFilter(request.GET, queryset=Review.objects.all())
    form = RecommendMultipleForm()
    form.fields['reviews'].queryset = review_filter.qs

    html = render_to_string(
        'reviews/addons/review_checkbox_fragment.html',
        {'form': form},
        request=request,
    )
    return JsonResponse({'html': html})

def review_preview(request, pk):
        """
        AJAX-функция, возвращающая JSON с HTML-фрагментом предпросмотра обзора.
        """
        review = get_object_or_404(Review, pk=pk)
        # Рендерим мини-шаблон (фрагмент), лежащий теперь в main/
        html_snippet = render_to_string('reviews/addons/review_preview_fragment.html', {
            'review': review,
        })
        return JsonResponse({'html': html_snippet})

def load_more_reviews(request):
    """
    API для прогрессивной загрузки обзоров.
    Возвращает дополнительные обзоры в формате JSON для JavaScript.
    """
    # Получаем параметры из GET запроса
    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 50))
    
    # Получаем обзоры с учетом offset и limit
    reviews = Review.objects.all().order_by('-current_date')[offset:offset+limit]
    
    # Формируем данные для JSON
    reviews_data = []
    for review in reviews:
        reviews_data.append({
            'title': review.name,  # Используем name вместо title
            'description': review.description,
            'category': review.category.name,
            'rubrics': [r.name for r in review.rubric.all()],
            'publish_date': review.current_date.strftime('%Y-%m-%d'),
            'formatted_date': review.current_date.strftime('%d.%m.%Y'),
            'powers': review.powers if review.powers else '',
            'power_date': review.power_date.strftime('%d.%m.%Y') if review.power_date else '',
            'url': f'/reviews/{review.pk}/'
        })
    
    # Проверяем есть ли еще записи
    total_count = Review.objects.count()
    has_more = offset + limit < total_count
    
    return JsonResponse({
        'reviews': reviews_data,
        'has_more': has_more
    })