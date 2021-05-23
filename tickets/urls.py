from django.urls import path
from tickets.views import TicketsListView, TicketDetailView, TicketCreateView, TicketUpdateView, TicketDeleteView, \
    CommentCreateView, CommentDeleteView, CommentUpdateView, AttachmentUploadView, AttachmentDeleteView

urlpatterns = [
    path('list/', TicketsListView.as_view(), name='list'),
    path('detail/<int:pk>', TicketDetailView.as_view(), name='detail'),
    path('detail/<int:pk>/comment/create', CommentCreateView.as_view(), name='comment-create'),
    path('detail/<int:pk2>/comment/<int:pk>/delete', CommentDeleteView.as_view(), name='comment-delete'),
    path('detail/<int:pk2>/comment/<int:pk>/edit', CommentUpdateView.as_view(), name='comment-edit'),
    path('delete/<int:pk>', TicketDeleteView.as_view(), name='delete'),
    path('edit/<int:pk>', TicketUpdateView.as_view(), name='edit'),
    path('create/', TicketCreateView.as_view(), name='create'),
    path('detail/<int:pk>/attachment/create', AttachmentUploadView.as_view(), name='attachment-create'),
    path('detail/<int:pk2>/attachment/<int:pk>/delete', AttachmentDeleteView.as_view(), name='attachment-delete'),
]
