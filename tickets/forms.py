from django import forms
from .models import Ticket


class CreateTicket(forms.ModelForm):

    class Meta:
        model = Ticket
        fields = ('title', 'description', 'assigned', 'status', 'priority')