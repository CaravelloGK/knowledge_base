from django.contrib import admin
from django.urls import path
from .views import RiskHome, RiskDetalView, risk_search, RiskDeleteView, RiskUpdateView, RiskCreateView, import_excel, load_excel, export_filters

app_name = 'risk'

"""
Ниже url маршруты
"""
urlpatterns = [

    path('', RiskHome.as_view(), name='risk_main'),  # Основной адрес
    path('create/', RiskCreateView.as_view(), name='risk_create'),  # url для создания
    path('update/<int:pk>/', RiskUpdateView.as_view(), name='risk_update'),  # url для редактирования
    path('delete/<int:pk>/', RiskDeleteView.as_view(), name='risk_delete'),  # url для удаления
    path('detail/<int:pk>/', RiskDetalView.as_view(), name='risk_detal'),  # url карточка риска
    path('search', risk_search, name='risk_search'),  # url для результатов поиска
    path('upload_excel/', import_excel, name='upload_excel'),    # url для загрузки Excel
    path('load_excel/', load_excel, name='load_excel'),  # url для загрузки Excel
    path('load_excel_filter/', export_filters, name='load_excel_filter')  # url для загрузки Excel c фильтрами


]
