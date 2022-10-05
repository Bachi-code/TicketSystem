from django import template
from django.utils.safestring import mark_safe

from tickets.dictionary import PRIORITY_BADGES, STATUS_BADGES

register = template.Library()


@register.filter(is_safe=True, name='badge_priority')
def badge_priority(value):
    return mark_safe(f'<span class="{dict(PRIORITY_BADGES)[value.priority]} m-0">{value.get_priority_display()}</span>')


@register.filter(is_safe=True, name='badge_status')
def badge_priority(value):
    return mark_safe(f'<span class="{dict(STATUS_BADGES)[value.status]} m-0">{value.get_status_display()}</span>')
