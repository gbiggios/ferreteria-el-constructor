from django import template

register = template.Library()


@register.filter
def clp(valor):
    """Formatea un monto en pesos chilenos: 6490 -> $ 6.490"""
    try:
        return '$ ' + f'{int(valor):,}'.replace(',', '.')
    except (TypeError, ValueError):
        return valor
