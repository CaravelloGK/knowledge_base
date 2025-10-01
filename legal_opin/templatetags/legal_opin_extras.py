from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Получает значение из словаря по ключу"""
    return dictionary.get(key)


@register.filter
def field_title(field_name):
    """Преобразует имя поля в читаемый заголовок"""
    field_titles = {
        'name': 'Название',
        'inn': 'ИНН',
        'ogrn': 'ОГРН',
        'legal_form': 'Организационно-правовая форма',
        'status': 'Статус',
        'authorized_capital': 'Уставной капитал',
        'company_group': 'Группа компаний',
        'registrar': 'Реестродержатель',
        'registrar_inn': 'ИНН реестродержателя',
        'share': 'Доля'
    }
    return field_titles.get(field_name, field_name.replace('_', ' ').title())


@register.filter
def has_differences(differences_dict):
    """Проверяет, есть ли различия в данных"""
    if not differences_dict:
        return False

    # Проверяем основные поля
    for field, diff in differences_dict.items():
        if field not in ['executive_bodies', 'participants']:
            return True

    # Проверяем связанные данные
    for data_type in ['executive_bodies', 'participants']:
        if data_type in differences_dict:
            type_diff = differences_dict[data_type]
            if type_diff and any(type_diff.values()):
                return True

    return False

@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter(name='find_changes')
def find_changes(changes_list, inn):
    """Находит изменения для ЕИО по ИНН"""
    if not changes_list or not inn:
        return {'changes': {}}
    for item in changes_list:
        if item.get('inn') == inn:
            return item
    return {'changes': {}}


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)