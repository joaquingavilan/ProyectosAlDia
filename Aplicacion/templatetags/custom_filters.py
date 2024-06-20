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


@register.filter(name='split')
def split(value, key):
    """
    Returns the value turned into a list.
    """
    return value.split(key)

@register.filter
def anydevolucion(devoluciones, pedido_id):
    return devoluciones.filter(pedido__id=pedido_id).exists()


@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


@register.filter
def zip_lists(a, b):
    return zip(a, b)