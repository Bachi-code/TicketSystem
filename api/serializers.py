from rest_framework import serializers

from accounts.models import CustomUser
from api.fields import CustomDateTimeField
from tickets.models import Ticket, Comment, Attachment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username']


class TicketSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')
    assigned = serializers.ReadOnlyField(source='assigned.username')
    created = CustomDateTimeField(required=False)
    modified = CustomDateTimeField(required=False)

    class Meta:
        model = Ticket
        fields = ['title', 'created', 'description', 'created_by', 'assigned', 'status', 'priority', 'modified']


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    created = CustomDateTimeField(required=False)
    modified = CustomDateTimeField(required=False)
    ticket = serializers.ReadOnlyField(source='ticket.title')

    class Meta:
        model = Comment
        fields = ['author', 'ticket', 'created', 'modified', 'description']
        read_only_fields = ['author']


class AttachmentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    created = CustomDateTimeField(required=False)
    file = serializers.FileField(use_url=False)
    ticket = serializers.ReadOnlyField(source='ticket.title')

    class Meta:
        model = Attachment
        fields = ['ticket', 'author', 'created', 'file']
        read_only_fields = ['author']
