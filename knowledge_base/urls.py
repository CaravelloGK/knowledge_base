"""
    Для авторизации добавить:
    from main.views import home, keycloak_login, keycloak_callback,logout

    # path("auth/login/", keycloak_login, name="login"),
    # path("auth/callback/", keycloak_callback, name="keycloak_callback"),
    # path('logout/', logout, name='logout'),
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from main.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", home, name="index"),
    path('reviews/', include('reviews.urls')),
    path('risks/', include('risk.urls')),
    path('docs/', include('docs.urls')),
    path('legal_opin/', include('legal_opin.urls')),
    path('staff/', include('staff.urls')),
    path('reporting/', include('reporting.urls')),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += [
    path("ckeditor5/", include('django_ckeditor_5.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)