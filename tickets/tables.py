import django_tables2 as tables
from django.utils.html import format_html
from django_tables2 import A

from tickets.models import Ticket


def get_priority_class(record):
    priority = record.priority
    if priority == 1:
        return "badge bg-danger"
    elif priority == 2:
        return "badge bg-warning text-dark"
    elif priority == 3:
        return "badge bg-yellow text-dark"
    elif priority == 4:
        return "badge bg-primary"
    else:
        return "badge bg-secondary"


def get_status_class(record):
    status = record.status
    if status == 1:
        return "badge bg-primary"
    elif status == 2:
        return "badge bg-warning text-dark"
    elif status == 3:
        return "badge bg-info text-dark"
    elif status == 4:
        return "badge bg-success"
    else:
        return "badge bg-dark"


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

