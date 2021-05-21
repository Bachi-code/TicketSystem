from django import forms
from .models import Ticket, Comment


class CreateTicket(forms.ModelForm):

    class Meta:
        model = Ticket
        fields = ('title', 'description', 'assigned', 'status', 'priority')


class CreateComment(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('description',)
