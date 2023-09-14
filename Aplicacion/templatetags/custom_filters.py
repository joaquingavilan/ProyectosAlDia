from django import template
import math
register = template.Library()


@register.filter(name='multiply')
def multiply(value, arg):
    result = float(value) * float(arg)
    return math.ceil(result)


@register.filter(name='intcomma')
def intcomma(value):
    try:
        return "{:,}".format(value).replace(",", ".")
    except (ValueError, TypeError):
        return value


