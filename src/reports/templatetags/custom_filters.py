from django import template
from django.utils.safestring import SafeString
from decimal import Decimal, InvalidOperation

register = template.Library()

@register.filter
def lookup(form, key):
    return form.fields.get(key) and form[key] or ''

@register.filter
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})

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
    try:
        # Convert SafeString to float
        if isinstance(value, SafeString):
            value = float(value)
        if isinstance(arg, SafeString):
            arg = float(arg)
        
        # Convert to Decimal for precise arithmetic
        value = Decimal(value)
        arg = Decimal(arg)
        
        return value - arg
    except (ValueError, TypeError, InvalidOperation):
        return ''

@register.simple_tag
def update_variable(value):
    return value


@register.filter
def sum_values(values):
    return sum(values)


@register.filter
def list_dict_values(diction):
    return list(diction)

@register.filter
def first_word(value):
    return value.split()[0] if value else ''