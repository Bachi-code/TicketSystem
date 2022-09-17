from django.db.models import Q
from rest_framework import viewsets, mixins
from rest_framework import permissions
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from accounts.models import CustomUser
from tickets.models import Ticket, Comment, Attachment

from api.serializers import UserSerializer, TicketSerializer, CommentSerializer, AttachmentSerializer
from tickets.tasks import task_assigned_email, owner_task_assigned_email, update_task_email, new_comment_email,\
    new_attachment_email


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = CustomUser.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class TicketViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows tickets to be viewed or edited.
    """
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.data.get('assigned'):
            assigned = get_user_model().objects.get(username=self.request.data['assigned'])
            ticket = serializer.save(created_by=self.request.user, assigned=assigned)
        else:
            ticket = serializer.save(created_by=self.request.user)
        site = Site.objects.get_current().domain
        if ticket.assigned is not None:
            task_assigned_email.delay(ticket.id, site)
            owner_task_assigned_email.delay(ticket.id, site)

    def perform_update(self, serializer):
        old_ticket = serializer.instance
        if self.request.data.get('assigned'):
            assigned = get_user_model().objects.get(username=self.request.data['assigned'])
            new_ticket = serializer.save(assigned=assigned)
        else:
            new_ticket = serializer.save()
        site = Site.objects.get_current().domain
        if new_ticket.assigned != old_ticket.assigned:
            task_assigned_email.delay(new_ticket.id, site)
            update_task_email.delay(new_ticket.id, site)
        else:
            update_task_email.delay(new_ticket.id, site)

    def get_queryset(self):
        return self.queryset.filter(Q(created_by=self.request.user) | Q(assigned=self.request.user))


class CommentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows comments to be viewed or edited.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        ticket = Ticket.objects.get(pk=self.request.data['ticket'])
        comment = serializer.save(author=self.request.user, ticket=ticket)
        site = Site.objects.get_current().domain
        new_comment_email.delay(comment.id, comment.ticket.id, site)

    def get_queryset(self):
        return self.queryset.filter(author=self.request.user)


class AttachmentViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin,
                        mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    API endpoint that allows attachments to be viewed or edited.
    """
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def pre_save(self, obj):
        obj.file = self.request.FILES.get('file')

    def perform_create(self, serializer):
        ticket = Ticket.objects.get(pk=self.request.data['ticket'])
        attachment = serializer.save(author=self.request.user, ticket=ticket)
        site = Site.objects.get_current().domain
        new_attachment_email.delay(attachment.file.name, attachment.ticket.id, site)

    def get_queryset(self):
        return self.queryset.filter(author=self.request.user)
