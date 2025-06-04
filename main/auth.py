from keycloak import KeycloakOpenID
from django.conf import settings
from django.contrib.auth import get_user_model
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
import ssl

# Отключаем SSL-проверки
disable_warnings(InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

User = get_user_model()

# Инициализация Keycloak с отключенной проверкой SSL
keycloak_openid = KeycloakOpenID(
    server_url=settings.KEYCLOAK_CONFIG["KEYCLOAK_URL"],
    realm_name=settings.KEYCLOAK_CONFIG["REALM_NAME"],
    client_id=settings.KEYCLOAK_CONFIG["CLIENT_ID"],
    client_secret_key=settings.KEYCLOAK_CONFIG["CLIENT_SECRET"],
    verify=False  # Отключаем проверку SSL здесь
)


def get_auth_url():
    return (
        f"{settings.KEYCLOAK_CONFIG['KEYCLOAK_URL']}/realms/"
        f"{settings.KEYCLOAK_CONFIG['REALM_NAME']}/protocol/openid-connect/auth?"
        f"client_id={settings.KEYCLOAK_CONFIG['CLIENT_ID']}&"
        f"redirect_uri={settings.KEYCLOAK_CONFIG['REDIRECT_URI']}&"
        "response_type=code&"
        "scope=openid profile email"
    )


class KeycloakBackend:
    def authenticate(self, request, code=None, **kwargs):
        if not code:
            return None

        try:
            token = keycloak_openid.token(
                grant_type="authorization_code",
                code=code,
                redirect_uri=settings.KEYCLOAK_CONFIG["REDIRECT_URI"]
            )
            user_info = keycloak_openid.userinfo(token["access_token"])
            print(user_info)

            groups = user_info.get('groups', [])
            print("Группы пользователя:", groups)

            user, created = User.objects.get_or_create(
                username=user_info.get("preferred_username"),
                defaults={
                    "email": user_info.get("email"),
                    "first_name": user_info.get("given_name", ""),
                    "last_name": user_info.get("family_name", ""),
                }
            )

            # Устанавливаем бэкенд в атрибуте пользователя
            request.session['keycloak_groups'] = groups
            user.backend = 'your_app.auth.KeycloakBackend'
            return user

        except Exception as e:
            print(f"Keycloak auth error: {str(e)}")
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None