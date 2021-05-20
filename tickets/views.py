from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import render
from .models import Ticket
from .forms import CreateTicket


class HomePageView(TemplateView):
    template_name = "tickets/home.html"


class TicketsListView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = "tickets/list.html"


class TicketDetailView(LoginRequiredMixin, DetailView):
    model = Ticket
    template_name = "tickets/detail.html"


class TicketCreateView(LoginRequiredMixin, CreateView):
    model = Ticket
    template_name = "tickets/add.html"
    form_class = CreateTicket

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class TicketUpdateView(LoginRequiredMixin, UpdateView):
    model = Ticket
    template_name = "tickets/add.html"
    form_class = CreateTicket


class TicketDeleteView(LoginRequiredMixin, DeleteView):
    model = Ticket
    template_name = "tickets/delete.html"
    success_url = reverse_lazy('list')
