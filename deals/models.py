import arrow
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy
from phonenumber_field.modelfields import PhoneNumberField

from accounts.models import Tags, Account
from common.models import Org, Profile
from common.base import BaseModel
from contacts.models import Contact
from teams.models import Teams
from common.utils import (
    INDCHOICES,
    CURRENCY_CODES,
    SOURCES,
    STAGES,
)


class Deal(BaseModel):
    name = models.CharField(pgettext_lazy("Name of Deal", "Name"), max_length=64)
    contacts = models.ManyToManyField(Contact)
    assigned_to = models.ManyToManyField(
        Profile, related_name="deal_assigned_to"
    )
    account = models.ForeignKey(
        Account,
        related_name="deals",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    website = models.CharField(_("Website"), max_length=255, blank=True, null=True)
    stage = models.CharField(pgettext_lazy("Stage of Deal", "Stage"), max_length=64, choices=STAGES)
    deal_source = models.CharField(_("Source of Deal"), max_length=255, choices=SOURCES, blank=True, null=True)
    industry = models.CharField(_("Industry Type"), max_length=255, choices=INDCHOICES, blank=True, null=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CODES, blank=True, null=True)
    value = models.DecimalField(_("Deal Value"), decimal_places=2, max_digits=12, blank=True, null=True)
    probability = models.IntegerField(default=0, blank=True, null=True)
    closed_by = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deal_closed_by",
    )
    close_date = models.DateField(default=None, null=True)
    description = models.TextField(blank=True, null=True)
    tags = models.ManyToManyField(Tags, blank=True)

    class Meta:
        verbose_name = "Deal"
        verbose_name_plural = "Deals"
        db_table = "deal"
        ordering = ("-created_at",)    
    
    
    def __str__(self):
        return f"{self.name}"
    
    @property
    def created_on_arrow(self):
        return arrow.get(self.created_at).humanize()
    
    @property
    def get_team_users(self):
        team_user_ids = list(self.teams.values_list("users__id", flat=True))
        return Profile.objects.filter(id__in=team_user_ids)

    @property
    def get_team_and_assigned_users(self):
        team_user_ids = list(self.teams.values_list("users__id", flat=True))
        assigned_user_ids = list(self.assigned_to.values_list("id", flat=True))
        user_ids = team_user_ids + assigned_user_ids
        return Profile.objects.filter(id__in=user_ids)

    @property
    def get_assigned_users_not_in_teams(self):
        team_user_ids = list(self.teams.values_list("users__id", flat=True))
        assigned_user_ids = list(self.assigned_to.values_list("id", flat=True))
        user_ids = set(assigned_user_ids) - set(team_user_ids)
        return Profile.objects.filter(id__in=list(user_ids))


