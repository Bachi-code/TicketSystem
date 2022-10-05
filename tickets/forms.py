from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Button, Layout, ButtonHolder, HTML, Field
from django import forms
from django.urls import reverse

from .models import Ticket, Comment, Attachment


class CreateTicket(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['priority'].help_text = None
        self.helper = FormHelper()
        self.helper.form_class = 'col-12 col-lg-4'
        self.helper.form_method = 'post'

        if self.instance:
            self.helper.add_input(Submit('submit', 'Edit'))
        else:
            self.helper.add_input(Submit('submit', 'Create'))

    class Meta:
        model = Ticket
        fields = ('title', 'description', 'assigned', 'status', 'priority')


class CreateComment(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.ticket_id = kwargs.pop('ticket', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        if self.instance.pk:
            self.helper.form_class = 'col-12 col-lg-4'
        else:
            self.helper.form_class = 'pt-4 px-4 col-auto'
        self.helper.form_method = 'post'
        if self.ticket_id:
            self.helper.form_action = reverse('comment-create', kwargs={'pk': self.ticket_id.pk})

        if self.instance.pk:
            layout = Layout(
                Field('description'),
                ButtonHolder(
                    Submit('submit', 'Edit'),
                    HTML('<a class="btn btn-secondary" href={% url "detail" object.pk %}>Cancel</a>'),
                    ),
                )
            self.helper.add_layout(layout)
        else:
            self.helper.add_input(Submit('submit', 'Comment'))

    class Meta:
        model = Comment
        fields = ('description',)
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            }


class AddAttachment(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'pt-4 px-4 col-lg-6 col-12'

        self.helper.add_input(Submit('submit', 'Upload'))

    class Meta:
        model = Attachment
        fields = ('file',)
