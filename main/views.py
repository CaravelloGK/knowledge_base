from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import login
from .auth import get_auth_url, KeycloakBackend
from django.conf import settings
from django.contrib.auth import logout as django_logout
from django.http import HttpResponseRedirect
from urllib.parse import urlencode


def home(request):
    return render(request, 'main.html', {'user': request.user})


def keycloak_login(request):
    """Перенаправляет на страницу входа Keycloak."""
    return redirect(get_auth_url())


def keycloak_callback(request):
    code = request.GET.get("code")
    if code:
        # Явно указываем бэкенд при аутентификации
        user = KeycloakBackend().authenticate(request, code=code)
        if user:
            # Явно указываем бэкенд при логине
            login(request, user, backend='main.auth.KeycloakBackend')
            return redirect("/")
    return redirect("/auth/login")


def logout(request):
    # Сохраняем id_token из сессии перед выходом
    id_token = request.session.get('oidc_id_token', None)

    # Выход из Django
    django_logout(request)
    request.session.flush()  # Полная очистка сессии

    # Параметры для выхода из Keycloak
    params = {
        'post_logout_redirect_uri': settings.KEYCLOAK_CONFIG['LOGOUT_REDIRECT_URI'],
        'client_id': settings.KEYCLOAK_CONFIG['CLIENT_ID'],
    }

    # Добавляем id_token_hint если есть
    if id_token:
        params['id_token_hint'] = id_token

    # Формируем URL выхода
    logout_url = f"{settings.KEYCLOAK_CONFIG['OIDC_LOGOUT_URL']}?{urlencode(params)}"

    # Создаем ответ с очисткой cookies
    response = HttpResponseRedirect(logout_url)
    response.delete_cookie('sessionid')
    return response