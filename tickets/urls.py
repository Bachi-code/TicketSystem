from django.urls import path
from tickets.views import TicketsListView, TicketDetailView, TicketCreateView, TicketUpdateView, TicketDeleteView

urlpatterns = [
    path('list/', TicketsListView.as_view(), name='list'),
    path('detail/<int:pk>', TicketDetailView.as_view(), name='detail'),
    path('delete/<int:pk>', TicketDeleteView.as_view(), name='delete'),
    path('edit/<int:pk>', TicketUpdateView.as_view(), name='edit'),
    path('create/', TicketCreateView.as_view(), name='create'),
]
