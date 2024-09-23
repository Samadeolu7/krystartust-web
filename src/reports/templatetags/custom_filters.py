# reports/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter
def dict_item(dictionary, key):
    """
    Retrieves a nested dictionary's value.
    Usage: {{ outer_dict|get_item:outer_key|dict_item:inner_key }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

import locale

# Set locale to use comma as thousand separator
locale.setlocale(locale.LC_ALL, '')

@register.filter
def naira(value):
    """
    Formats a numeric value as Naira currency with commas and adds the Naira symbol (₦).
    Usage: {{ value|naira }}
    """
    # Ensure value is a number
    try:
        # Format the value with commas and 2 decimal places
        value = locale.format_string("%.2f", float(value), grouping=True)
        return f"₦{value}"
    except (ValueError, TypeError):
        return value