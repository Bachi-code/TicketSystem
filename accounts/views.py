from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import UserRegisterForm


class RegisterView(CreateView):
    form_class = UserRegisterForm
    success_url = reverse_lazy('home')
    template_name = 'accounts/register.html'


