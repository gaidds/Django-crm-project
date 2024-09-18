from celery import Celery
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from common.models import Profile
from deals.models import Deal

app = Celery("redis://")


@app.task
def send_email_to_assigned_user(recipients, deal_id):
    """Send Mail To Users When they are assigned to a deal"""
    deal = Deal.objects.get(id=deal_id)
    created_by = deal.created_by
    for user in recipients:
        recipients_list = []
        profile = Profile.objects.filter(id=user, is_active=True).first()
        if profile:
            recipients_list.append(profile.user.email)
            context = {}
            context["url"] = settings.DOMAIN_NAME
            context["user"] = profile.user
            context["deal"] = deal
            context["created_by"] = created_by
            subject = "Assigned a deal for you."
            html_content = render_to_string(
                "assigned_to/deal_assigned.html", context=context
            )

            msg = EmailMessage(subject, html_content, to=recipients_list)
            msg.content_subtype = "html"
            msg.send()
