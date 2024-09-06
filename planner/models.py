from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy

from common.models import User
from common.base import BaseModel
from common.utils import EVENT_PARENT_TYPE, EVENT_STATUS
from contacts.models import Contact
from deals.models import Deal


class Reminder(BaseModel):
    reminder_type = models.CharField(max_length=5, blank=True, null=True)
    reminder_time = models.IntegerField(
        pgettext_lazy("time of the reminder to event in Seconds", "Reminder"),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Reminder"
        verbose_name_plural = "Reminders"
        db_table = "reminder"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.reminder_type}"


class PlannerEvent(BaseModel):
    limit = (
        models.Q(app_label="account", model="Account", id=10)
        | models.Q(app_label="deals", model="Deal", id=13)
        | models.Q(app_label="cases", model="Case", id=11)
    )
    name = models.CharField(pgettext_lazy("Name of the Event", "Event"), max_length=64)
    event_type = models.CharField(
        _("Type of the event"), max_length=7
    )  # call meeting task
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        limit_choices_to=limit,
        choices=EVENT_PARENT_TYPE,
    )
    object_id = models.PositiveIntegerField(blank=True, null=True)
    parent = GenericForeignKey("content_type", "object_id")
    status = models.CharField(
        pgettext_lazy("status of the Event", "Status"),
        choices=EVENT_STATUS,
        max_length=64,
        blank=True,
    )
    direction = models.CharField(max_length=20, blank=True)  # only for calls
    # start_date = models.DateTimeField(default=None)
    # close_date = models.DateTimeField(default=None, null=True)
    start_date = models.DateField(default=None)
    close_date = models.DateField(default=None, null=True)

    duration = models.IntegerField(
        pgettext_lazy("Duration of the Event in Seconds", "Durations"),
        default=None,
        null=True,
    )  # not for tasks
    reminders = models.ManyToManyField(Reminder, blank=True)
    priority = models.CharField(max_length=10, blank=True)  # only for task
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_user",
    )
    attendees_user = models.ManyToManyField(
        User, blank=True, related_name="attendees_user"
    )
    attendees_contacts = models.ManyToManyField(
        Contact, blank=True, related_name="attendees_contact"
    )
    attendees_deals = models.ManyToManyField(
        Deal, blank=True, related_name="attendees_deal"
    )
    created_on = models.DateTimeField(_("Created on"), auto_now_add=True)
    created_by = models.ForeignKey(
        User, related_name="event_created_by", on_delete=models.SET_NULL, null=True
    )
    assigned_to = models.ManyToManyField(
        User, blank=True, related_name="event_assigned_users",
    )
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = "PlannerEvent"
        verbose_name_plural = "PlannerEvents"
        db_table = "planner_event"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.name}"
