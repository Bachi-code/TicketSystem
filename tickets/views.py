from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.models import Site
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import render, get_object_or_404
from .models import Ticket, Comment, Attachment
from .forms import CreateTicket, CreateComment, AddAttachment
from .tasks import task_assigned_email, owner_task_assigned_email, update_task_email, new_comment_email,\
    new_attachment_email


class HomePageView(TemplateView):
    template_name = "tickets/home.html"


class TicketsListView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = "tickets/list.html"


class TicketDetailView(LoginRequiredMixin, DetailView):
    model = Ticket
    template_name = "tickets/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(ticket_id__exact=self.object.pk)
        context['attachments'] = Attachment.objects.filter(ticket_id__exact=self.object.pk)
        context['form'] = CreateComment()
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CreateComment

    def form_valid(self, form):
        form.instance.author = self.request.user
        ticket = get_object_or_404(Ticket, pk=self.kwargs['pk'])
        form.instance.ticket = ticket
        self.object = form.save(commit=False)
        site = Site.objects.get_current().domain
        comment = form.save()
        new_comment_email.delay(comment.id, ticket.id, site)
        return super().form_valid(form)

    def get_success_url(self):
        ticket = Ticket.objects.get(pk=self.kwargs['pk'])
        return ticket.get_absolute_url()


class TicketCreateView(LoginRequiredMixin, CreateView):
    model = Ticket
    template_name = "tickets/add.html"
    form_class = CreateTicket

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        self.object = form.save(commit=False)
        ticket = self.object
        self.object = form.save()
        site = Site.objects.get_current().domain
        if ticket.assigned is not None:
            task_assigned_email.delay(ticket.id, site)
            owner_task_assigned_email.delay(ticket.id, site)
        return super().form_valid(form)


class TicketUpdateView(LoginRequiredMixin, UpdateView):
    model = Ticket
    template_name = "tickets/edit.html"
    form_class = CreateTicket

    def get_queryset(self):
        qs = super(TicketUpdateView, self).get_queryset()
        return qs.filter(Q(created_by=self.request.user) | Q(assigned=self.request.user))

    def form_valid(self, form):
        old_ticket = Ticket.objects.get(pk=self.object.pk)
        new_ticket = form.save(commit=False)
        site = Site.objects.get_current().domain
        if new_ticket.assigned != old_ticket.assigned:
            task_assigned_email.delay(new_ticket.id, site)
            update_task_email.delay(new_ticket.id, site)
        else:
            update_task_email.delay(new_ticket.id, site)
        return super().form_valid(form)


class TicketDeleteView(LoginRequiredMixin, DeleteView):
    model = Ticket
    template_name = "tickets/delete.html"
    success_url = reverse_lazy('list')

    def get_queryset(self):
        qs = super(TicketDeleteView, self).get_queryset()
        return qs.filter(created_by=self.request.user)


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = "comments/delete.html"

    def get_success_url(self):
        ticket = Ticket.objects.get(pk=self.kwargs['pk2'])
        return ticket.get_absolute_url()


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    template_name = "comments/edit.html"
    fields = ['description']

    def get_queryset(self):
        qs = super(CommentUpdateView, self).get_queryset()
        return qs.filter(author=self.request.user)

    def get_success_url(self):
        ticket = Ticket.objects.get(pk=self.kwargs['pk2'])
        return ticket.get_absolute_url()


class AttachmentUploadView(LoginRequiredMixin, CreateView):
    model = Attachment
    template_name = "attachments/add.html"
    form_class = AddAttachment

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ticket'] = get_object_or_404(Ticket, pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        ticket = get_object_or_404(Ticket, pk=self.kwargs['pk'])
        form.instance.ticket = ticket
        site = Site.objects.get_current().domain
        new_attachment_email.delay(form.instance.file.name, ticket.id, site)
        return super().form_valid(form)

    def get_success_url(self):
        ticket = Ticket.objects.get(pk=self.kwargs['pk'])
        return ticket.get_absolute_url()


class AttachmentDeleteView(LoginRequiredMixin, DeleteView):
    model = Attachment
    template_name = "attachments/delete.html"

    def get_success_url(self):
        ticket = Ticket.objects.get(pk=self.kwargs['pk2'])
        return ticket.get_absolute_url()
