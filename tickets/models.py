from django.db import models
from django.conf import settings
from django.urls import reverse
from django.contrib.sites.models import Site
import os


def upload_dir(instance, filename):
    return 'tickets/{0}/{1}'.format(instance.ticket.id, filename)


class Ticket(models.Model):
    STATUS = [
        (1, 'Open'),
        (2, 'Reopened'),
        (3, 'Solved'),
        (4, 'Closed'),
        ]

    PRIORITY = [
        (1, 'Critical'),
        (2, 'High'),
        (3, 'Normal'),
        (4, 'Low'),
        (5, 'Very Low'),
        ]

    title = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_by')
    assigned = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name='assigned')
    status = models.PositiveSmallIntegerField(choices=STATUS, default=1,)
    priority = models.PositiveSmallIntegerField(choices=PRIORITY, default=1,help_text='1 = Highest Priority, 5 = Lowest Priority')
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('detail', kwargs={'pk': self.pk})


class Comment(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    description = models.TextField()

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return 'Comment by {} on {}'.format(self.author.get_full_name(), self.ticket)


class Attachment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to=upload_dir)

    def filename(self):
        return os.path.basename(self.file.name)

    def __str__(self):
        return f"{self.ticket.id}-{self.file.name}"
