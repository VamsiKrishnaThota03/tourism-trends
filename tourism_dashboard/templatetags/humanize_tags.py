from django import template

register = template.Library()


@register.filter
def compact_number(value):
    """1234567 -> '1.2M', 45300 -> '45.3K'."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return value
    for threshold, suffix in ((1e9, 'B'), (1e6, 'M'), (1e3, 'K')):
        if abs(number) >= threshold:
            return f'{number / threshold:.1f}'.rstrip('0').rstrip('.') + suffix
    return f'{number:.0f}'
