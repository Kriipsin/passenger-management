from django import template

register = template.Library()

@register.filter
def dict_get(dictionary, key):
    if dictionary is None:  # Jeśli dictionary jest None, zwróć None
        return None
    return dictionary.get(key, None)  # Jeśli key nie istnieje, zwróć None

