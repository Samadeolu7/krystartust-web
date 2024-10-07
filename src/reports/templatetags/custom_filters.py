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


@register.filter
def naira(value):
    """
    Formats a numeric value as Naira currency with commas and adds the Naira symbol (₦).
    Usage: {{ value|naira }}
    """
    # Ensure value is a number
    try:
        value = float(value)
        # Format the value with commas and 2 decimal places
        formatted_value = f"{value:,.2f}"
        return f"₦{formatted_value}"
    except (ValueError, TypeError):
        return value


@register.filter
def subtract(value, arg):
    return value - arg

@register.simple_tag
def update_variable(value):
    return value