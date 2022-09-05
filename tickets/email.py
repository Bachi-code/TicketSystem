from django.core.mail import EmailMultiAlternatives
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import get_template


def send_mail(subject, template_name, context, to, bcc=False):
    text_template = get_template(f"email/{template_name}.txt")
    text_contents = text_template.render(context)
    try:
        html_template = get_template(f"email/{template_name}.html")
        html_contents = html_template.render(context)
    except TemplateDoesNotExist:
        html_contents = None

    message = EmailMultiAlternatives(
        subject=subject,
        body=text_contents,
        to=to if not bcc else [],
        bcc=to if bcc else [],
        )

    if html_contents:
        message.attach_alternative(html_contents, "text/html")
    return message.send()
