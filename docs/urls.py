from django.urls import path
from .views import KBView, AHDView, RBView, KURIView, MBView, document_detail, docs_search, DocumentCreateView, \
    get_categories_for_global_section, DocumentUpdateView, DocumentDeleteView, DocumentListView, DocumentDetailView, \
    DocumentVersionView, AddDocumentVersionView, upload_presentation_slides, DocumentVersionDeleteView

app_name = 'docs'

urlpatterns = [
    path('KB', KBView.as_view(), name='kb_home'),
    path('RB', RBView.as_view(), name='rb_home'),
    path('AHD', AHDView.as_view(), name='ahd_home'),
    path('MB', MBView.as_view(), name='mb_home'),
    path('KURI', KURIView.as_view(), name='kuri_home'),
    path('search', docs_search, name='search'),  # url для результатов поиска
    path('create/', DocumentCreateView.as_view(), name='document_create'),  # url для создания
    path('document/<int:pk>/update/', DocumentUpdateView.as_view(), name='document_update'),
    path('document/<int:pk>/delete/', DocumentDeleteView.as_view(), name='document_delete'),
    path('document/<int:document_id>/', document_detail, name='document_detail'),
    path('ajax/get-categories/', get_categories_for_global_section, name='get_categories_for_global_section'),
    path('', DocumentListView.as_view(), name='document_list'),
    path('version/<int:version_id>/', DocumentVersionView.as_view(), name='document_version_view'),
    path('document/<int:pk>/add_version/', AddDocumentVersionView.as_view(), name='add_document_version'),
    path('document/<int:document_id>/upload_slides/', upload_presentation_slides, name='upload_presentation_slides'),
    path('document/<int:document_id>/version/<int:version_id>/delete/', DocumentVersionDeleteView.as_view(), name='document_version_delete'),
]