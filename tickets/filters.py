import django_filters

from tickets.models import Ticket


class TicketFilter(django_filters.FilterSet):
    priority = django_filters.MultipleChoiceFilter(choices=Ticket.PRIORITY)
    status = django_filters.MultipleChoiceFilter(choices=Ticket.STATUS)
    created = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = Ticket
        fields = ['title', 'priority', 'status', 'created']
