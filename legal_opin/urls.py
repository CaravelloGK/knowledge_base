from django.urls import path
from . import views
from .views import (CollateralCreateView, CollateralUpdateView, DealCollateralDeleteView,
                    RiskAnalysisView)

app_name = 'legal_opin'

urlpatterns = [
    path('legal-entities/', views.LegalEntityListView.as_view(), name='legal_entity_list'),
    path('legal-entities/<int:pk>/', views.LegalEntityDetailView.as_view(), name='legal_entity_detail'),
    path('', views.LegalEntityListView.as_view(), name='legal_entity_list'),
    path('<int:pk>/', views.LegalEntityDetailView.as_view(), name='legal_entity_detail'),
    path('legal-entities/create/', views.LegalEntityCreateView.as_view(), name='legal_entity_create'),
    path('legal-entities/<int:pk>/edit/', views.LegalEntityUpdateView.as_view(), name='legal_entity_edit'),
    path('legal-entities/<int:pk>/start-update-from-egrul/', views.start_update_from_egrul,
         name='start_update_from_egrul'),
    path('legal-entities/<int:pk>/update-from-egrul/', views.LegalEntityUpdateFromEGRULView.as_view(),
         name='legal_entity_update_from_egrul'),
    path('deals/', views.DealListView.as_view(), name='deal_list'),
    path('deals/create/', views.DealCreateView.as_view(), name='deal_create'),
    path('deals/<int:pk>/', views.DealDetailView.as_view(), name='deal_detail'),
    path('deals/<int:pk>/edit', views.DealUpdateView.as_view(), name='deal_edit'),
    path('deals/<int:deal_pk>/add_participant/', views.add_participant_by_inn, name='add_participant_by_inn'),
    path('deals/<int:deal_pk>/participant/<int:le_pk>/', views.DealParticipantCreateView.as_view(), name='deal_participant_form'),
    path('deals/participant/<int:pk>/edit/', views.DealParticipantUpdateView.as_view(),
         name='deal_participant_form_edit'),
    path('deals/participant/<int:pk>/del/', views.DealParticipantDeleteView.as_view(),
         name='deal_participant_delete'),
    path('deal/<int:deal_id>/collaterals/create/', CollateralCreateView.as_view(), name='collateral_create'),
    path('deal/<int:deal_id>/collaterals/edit/', CollateralUpdateView.as_view(), name='collateral_edit'),
    path('deal/<int:deal_id>/collaterals/del/<int:pk>', DealCollateralDeleteView.as_view(), name='collateral_del'),

    # риски
    path('deal/<int:deal_id>/risk/create/', RiskAnalysisView.as_view(), name='risk_create'),
    # path('add-custom-risk/', add_custom_risk, name='add_custom_risk'),
    path('deal/<int:deal_id>/risk/edit/', RiskAnalysisView.as_view(), kwargs={'is_edit': True}, name='risk_edit'),

    path('check-inn/', views.check_inn_file, name='check_inn'),

]