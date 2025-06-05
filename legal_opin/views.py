from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from .models import LegalEntity
# from django.db.models import Q


class LegalEntityListView(ListView):
    # класс выводит список юриков
    model = LegalEntity
    template_name = 'list.html'
    context_object_name = 'legal_entities'
    ordering = ['-updated_at']

    def get_queryset(self):
        """Возвращаем только первые 25 записей для быстрой загрузки"""
        return LegalEntity.objects.all().order_by('-updated_at')[:25]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['id_app'] = 'legal_opin'  # ВАЖНО! Идентификатор приложения!
        
        # Добавляем данные для прогрессивной загрузки
        total_count = LegalEntity.objects.count()
        context['total_count'] = total_count
        context['loaded_count'] = 25
        context['has_more'] = total_count > 25
        
        return context


class LegalEntityDetailView(DetailView):
    # класс выводит карточку юрика
    model = LegalEntity
    template_name = 'legal_opin/detail.html'
    context_object_name = 'entity'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity = self.get_object()
        context['deals'] = entity.deals.all()
        return context


def load_more_legal_entities(request):
    """
    API для прогрессивной загрузки юридических лиц.
    Возвращает дополнительные записи в формате JSON.
    """
    # Получаем параметры из GET запроса
    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 50))
    
    # Получаем записи с учетом offset и limit
    entities = LegalEntity.objects.all().order_by('-updated_at')[offset:offset+limit]
    
    # Формируем данные для JSON
    entities_data = []
    for entity in entities:
        entities_data.append({
            'name': entity.name,
            'inn': entity.inn,
            'ogrn': entity.ogrn,
            'update_date': entity.updated_at.strftime('%Y-%m-%d'),
            'formatted_date': entity.updated_at.strftime('%d.%m.%Y'),
            'url': f'/legal_opin/legal-entities/{entity.pk}/'
        })
    
    # Проверяем есть ли еще записи
    total_count = LegalEntity.objects.count()
    has_more = offset + limit < total_count
    
    return JsonResponse({
        'entities': entities_data,
        'has_more': has_more
    })