from celery.utils.log import get_task_logger
from TicketSystem.celery import app
from .models import Ticket, Comment
from .email import send_mail

logger = get_task_logger(__name__)


@app.task(name="task_assigned_email")
def task_assigned_email(ticket_id, site):
    ticket = Ticket.objects.get(pk=ticket_id)
    logger.info("Sent assigned email")
    return send_mail(f"Task {ticket.title} assigned", "assigned",
                     {"ticket": ticket, "site": site, },
                     [ticket.assigned.email])


@app.task(name="owner_task_assigned_email")
def owner_task_assigned_email(ticket_id, site):
    ticket = Ticket.objects.get(pk=ticket_id)
    logger.info("Sent assigned email")
    return send_mail(f"Your task {ticket.title} was assigned", "assigned_create",
                     {"ticket": ticket, "site": site, },
                     [ticket.created_by.email])


@app.task(name="update_task_email")
def update_task_email(ticket_id, site):
    ticket = Ticket.objects.get(pk=ticket_id)
    ticket_emails = ticket.get_emails()
    comments_emails = list(Comment.objects.filter(ticket_id__exact=ticket_id).values_list
                           ('author__email', flat=True).distinct().order_by())
    all_emails = list(set(ticket_emails + comments_emails))
    logger.info("Sent update email")
    return send_mail(f"Your task {ticket.title} has been updated", "updated",
                     {"ticket": ticket, "site": site, },
                     all_emails)


@app.task(name="new_comment_email")
def new_comment_email(comment_id, ticket_id, site):
    ticket = Ticket.objects.get(pk=ticket_id)
    ticket_emails = ticket.get_emails()
    comments_emails = list(Comment.objects.filter(ticket_id__exact=ticket_id).values_list
                           ('author__email', flat=True).distinct().order_by())
    all_emails = list(set(ticket_emails + comments_emails))
    comment = Comment.objects.get(pk=comment_id)
    logger.info("Sent new comment email")
    return send_mail(f"Task {ticket.title} has new comment", "comment",
                     {"ticket": ticket, "site": site, "comment": comment, },
                     all_emails)


@app.task(name="new_attachment_email")
def new_attachment_email(attachment_name, ticket_id, site):
    ticket = Ticket.objects.get(pk=ticket_id)
    ticket_emails = ticket.get_emails()
    comments_emails = list(Comment.objects.filter(ticket_id__exact=ticket_id).values_list
                           ('author__email', flat=True).distinct().order_by())
    all_emails = list(set(ticket_emails + comments_emails))
    logger.info("Sent new attachment email")
    return send_mail(f"Task {ticket.title} has new attachment", "attachment",
                     {"ticket": ticket, "site": site, "attachment_name": attachment_name, },
                     all_emails)

