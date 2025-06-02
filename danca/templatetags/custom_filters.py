from django import template
from django.views.decorators.cache import cache_page, cache_control
from ..models import Evento

register = template.Library()

@register.filter
def format_currency(value):
    if value is None:
        return 'R$ 0,00'
    return f'R$ {value:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

@register.filter
@cache_page(60 * 15)  # Cache por 15 minutos
@cache_control(private=True)
def get_evento(value):
    try:
        return Evento.objects.get(id=value)
    except Evento.DoesNotExist:
        return None

@register.filter
def sum_attribute(queryset, attribute):
    """
    Soma os valores de um atributo em um queryset ou lista de objetos.
    Ignora valores None.
    """
    return sum(getattr(obj, attribute, 0) or 0 for obj in queryset)