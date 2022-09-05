from rest_framework import serializers

from accounts.models import CustomUser
from tickets.models import Ticket, Comment, Attachment


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email']


class TicketSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Ticket
        fields = ['title', 'created', 'description', 'created_by', 'assigned', 'status', 'priority', 'modified']


class CommentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Comment
        fields = ['author', 'ticket', 'created', 'modified', 'description']


class AttachmentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Attachment
        fields = ['ticket', 'author', 'created', 'file']
