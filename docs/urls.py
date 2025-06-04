from django.urls import path
from .views import KBView, AHDView, RBView, KURIView, MBView, document_detail, docs_search, DocumentCreateView, get_categories_for_global_section

app_name = 'docs'

urlpatterns = [
    path('KB', KBView.as_view(), name='kb_home'),
    path('RB', RBView.as_view(), name='rb_home'),
    path('AHD', AHDView.as_view(), name='ahd_home'),
    path('MB', MBView.as_view(), name='mb_home'),
    path('KURI', KURIView.as_view(), name='kuri_home'),
    path('search', docs_search, name='search'),  # url для результатов поиска
    path('create/', DocumentCreateView.as_view(), name='document_create'),  # url для создания
    path('document/<int:document_id>/', document_detail, name='document_detail'),
    path('ajax/get-categories/', get_categories_for_global_section, name='get_categories_for_global_section'),
]