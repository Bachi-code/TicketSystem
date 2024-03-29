from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.models import Site
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

from .filters import TicketFilter
from .models import Ticket, Comment, Attachment
from .forms import CreateTicket, CreateComment, AddAttachment
from .tables import TicketsTable
from .tasks import task_assigned_email, owner_task_assigned_email, update_task_email, new_comment_email,\
    new_attachment_email


class HomePageView(TemplateView):
    template_name = "tickets/home.html"


class TicketsListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    model = Ticket
    table_class = TicketsTable
    template_name = "tickets/list.html"
    filterset_class = TicketFilter

    def get(self, request, *args, **kwargs):
        filterset_class = self.get_filterset_class()
        self.filterset = self.get_filterset(filterset_class)

        if (
                not self.filterset.is_bound
                or self.filterset.is_valid()
                or not self.get_strict()
        ):
            self.object_list = self.filterset.qs
        else:
            self.object_list = self.filterset.queryset.none()

        context = self.get_context_data(
            filter=self.filterset, object_list=self.object_list
            )
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            table = self.get_table(**self.get_table_kwargs())
            html_table = render_to_string('tickets/tables/list_table.html', {'table': table}, request=request)
            return JsonResponse(html_table, safe=False)
        return self.render_to_response(context)


class UserTicketsListView(TicketsListView):
    def get(self, request, *args, **kwargs):
        filterset_class = self.get_filterset_class()
        self.filterset = self.get_filterset(filterset_class)

        if (
                not self.filterset.is_bound
                or self.filterset.is_valid()
                or not self.get_strict()
        ):
            self.object_list = self.filterset.qs.filter(created_by=request.user)
        else:
            self.object_list = self.filterset.queryset.none()

        context = self.get_context_data(
            filter=self.filterset, object_list=self.object_list
            )
        context['user_tickets'] = True
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            table = self.get_table(**self.get_table_kwargs())
            html_table = render_to_string('tickets/tables/list_table.html', {'table': table}, request=request)
            return JsonResponse(html_table, safe=False)
        return self.render_to_response(context)


class TicketDetailView(LoginRequiredMixin, DetailView):
    model = Ticket
    template_name = "tickets/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comment_list = Comment.objects.filter(ticket_id__exact=self.object.pk)
        paginator_comment = Paginator(comment_list, 10)
        comment_page = self.request.GET.get('comment_page')
        attachment_list = Attachment.objects.filter(ticket_id__exact=self.object.pk)
        paginator_attachment = Paginator(attachment_list, 5)
        attachment_page = self.request.GET.get('attachment_page')
        context['comments'] = paginator_comment.get_page(comment_page)
        context['attachments'] = paginator_attachment.get_page(attachment_page)
        context['form'] = CreateComment(ticket=kwargs.pop('object'))
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

    def get_object(self, queryset=None):
        obj = super(TicketDeleteView, self).get_object()
        if not obj.created_by == self.request.user:
            raise PermissionDenied()
        return obj


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = "comments/delete.html"

    def get_object(self, queryset=None):
        obj = super(CommentDeleteView, self).get_object()
        if not obj.author == self.request.user:
            raise PermissionDenied()
        return obj

    def get_success_url(self):
        ticket = Ticket.objects.get(pk=self.kwargs['pk2'])
        return ticket.get_absolute_url()


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    template_name = "comments/edit.html"
    form_class = CreateComment

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

    def get_object(self, queryset=None):
        obj = super(AttachmentDeleteView, self).get_object()
        if not obj.author == self.request.user:
            raise PermissionDenied()
        return obj

    def get_success_url(self):
        ticket = Ticket.objects.get(pk=self.kwargs['pk2'])
        return ticket.get_absolute_url()
