from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if hasattr(dictionary, '__getitem__'):
        return dictionary.get(key)
    return None