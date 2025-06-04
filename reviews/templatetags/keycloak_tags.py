from django import template
from django.conf import settings

register = template.Library()

@register.filter(name='in_group')
def in_group(user, group_name):
    """Проверяет, состоит ли пользователь в указанной группе Keycloak"""
    if hasattr(user, 'session'):
        return group_name in user.session.get('keycloak_groups', [])
    return False