from django.views.generic import ListView, DetailView
from .models import LegalEntity
# from django.db.models import Q


class LegalEntityListView(ListView):
    # класс выводит список юриков
    model = LegalEntity
    template_name = 'list.html'
    context_object_name = 'legal_entities'

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
        context['deals'] = entity.deals.all()
        return context