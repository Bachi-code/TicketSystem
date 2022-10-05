import django_tables2 as tables
from django.utils.html import format_html
from django_tables2 import A

from tickets.dictionary import PRIORITY_BADGES, STATUS_BADGES
from tickets.models import Ticket


def get_priority_class(record):
    priority = record.priority
    return dict(PRIORITY_BADGES)[priority]


def get_status_class(record):
    status = record.status
    return dict(STATUS_BADGES)[status]


class TicketsTable(tables.Table):
    pk = tables.LinkColumn("detail", text=lambda record: f"#{record.pk}", args=[A("pk")])
    priority = tables.Column()
    status = tables.Column()

    class Meta:
        model = Ticket
        template_name = "tickets/tables/list_table.html"
        empty_text = "There are no tickets"
        fields = ['title', 'pk', 'priority', 'status', 'assigned', 'created_by', 'created']
        per_page = 10

    @staticmethod
    def render_priority(value, record):
        priority_class = get_priority_class(record)
        return format_html('<span class="{}">{}</span>', priority_class, value)

    @staticmethod
    def render_status(value, record):
        status_class = get_status_class(record)
        return format_html('<span class="{}">{}</span>', status_class, value)

