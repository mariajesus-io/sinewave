from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django import template


register = template.Library()


def _entero(value):
    try:
        return int(Decimal(str(value)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
    except (InvalidOperation, TypeError, ValueError):
        return None


@register.filter
def numero_cl(value):
    numero = _entero(value)
    return format(numero, ',').replace(',', '.') if numero is not None else value


@register.filter
def clp(value):
    numero = _entero(value)
    return '$ ' + format(numero, ',').replace(',', '.') if numero is not None else '—'


@register.filter
def valor_reporte(value):
    if value is None:
        return '—'
    return clp(value) if isinstance(value, Decimal) else value
