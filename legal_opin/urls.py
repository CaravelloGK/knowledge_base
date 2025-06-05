from django.urls import path
from . import views

app_name = 'legal_opin'

urlpatterns = [
    path('legal-entities/', views.LegalEntityListView.as_view(), name='legal_entity_list'),
    path('legal-entities/<int:pk>/', views.LegalEntityDetailView.as_view(), name='legal_entity_detail'),
    path('api/load-more/', views.load_more_legal_entities, name='load_more_legal_entities'),
]