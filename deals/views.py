from django.shortcuts import render

from django.db.models import Q
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Account, Tags
from accounts.serializer import AccountSerializer, TagsSerailizer
from common.models import APISettings, Attachments, Comment, Profile, User

from common.serializer import (
    AttachmentsSerializer,
    CommentSerializer,
    ProfileSerializer,
)
from common.utils import (
    INDCHOICES,
    CURRENCY_CODES,
    SOURCES,
    STAGES,
)
from contacts.models import Contact
from contacts.serializer import ContactSerializer
from deals import swagger_params1
from deals.models import Deal
from deals.serializer import *
# from deals.tasks import (
#     create_deal_from_file,
#     send_email_to_assigned_user,
#     send_dea,_assigned_emails,
# )


class DealListView(APIView, LimitOffsetPagination):

    permission_classes = (IsAuthenticated,)
    model = Deal

    def get_context_data(self, **kwargs):
        params = self.request.query_params
        queryset = self.model.objects.filter(
            org=self.request.profile.org).order_by("-id")
        accounts = Account.objects.filter(org=self.request.profile.org)
        contact = Contact.objects.filter(org=self.request.profile.org)
        if not (self.request.profile.role == "ADMIN" or self.request.profile.role == "SALES MANAGER"):
            queryset = queryset.filter(
                Q(created_by=self.request.profile.user) | Q(
                    assigned_to=self.request.profile)
            ).distinct()

        if params:
            if params.get("name"):
                queryset = queryset.filter(name__icontains=params.get("name"))
            if params.get("account"):
                queryset = queryset.filter(account=params.get("account"))
            if params.get("stage"):
                queryset = queryset.filter(stage__contains=params.get("stage"))
            if params.get("lead_source"):
                queryset = queryset.filter(
                    lead_source__contains=params.get("lead_source")
                )
            if params.get("tags"):
                queryset = queryset.filter(
                    tags__in=params.get("tags")
                ).distinct()

        context = {}
        results_deals = self.paginate_queryset(
            queryset.distinct(), self.request, view=self
        )
        deals = DealSerializer(
            results_deals, many=True).data
        if results_deals:
            offset = queryset.filter(
                id__gte=results_deals[-1].id).count()
            if offset == queryset.count():
                offset = None
        else:
            offset = 0
        context["per_page"] = 10
        page_number = (int(self.offset / 10) + 1,)
        context["page_number"] = page_number
        context.update(
            {
                "deals_count": self.count,
                "offset": offset,
            }
        )
        context["deals"] = deals
        context["accounts_list"] = AccountSerializer(accounts, many=True).data
        context["contacts_list"] = ContactSerializer(contact, many=True).data
        context["tags"] = TagsSerailizer(Tags.objects.filter(), many=True).data
        context["stage"] = STAGES
        context["deal_source"] = SOURCES
        context["currency"] = CURRENCY_CODES
        context["industries"] = INDCHOICES

        users = Profile.objects.filter(is_active=True, org=self.request.profile.org).values(
            "id", "user__email"
        )
        context["users"] = users.exclude(role='USER')

        return context

    @extend_schema(
        tags=["Deals"],
        parameters=swagger_params1.deal_list_get_params,
    )
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return Response(context)

    @extend_schema(
        tags=["Deals"],
        parameters=swagger_params1.organization_params, request=DealCreateSwaggerSerializer
    )
    def post(self, request, *args, **kwargs):
        params = request.data
        serializer = DealCreateSerializer(
            data=params, request_obj=request)
        if not (self.request.profile.role == "ADMIN" or self.request.profile.role == "SALES MANAGER"):
            return Response(
                {
                    "error": True,
                    "errors": "You do not have permission to perform this action",
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        if serializer.is_valid():
            deal_obj = serializer.save(
                created_by=request.profile.user,
                close_date=params.get("close_date"),
                website=params.get("website"),
                org=request.profile.org,
            )

            if params.get("contacts"):
                contacts_list = params.get("contacts")
                contacts = Contact.objects.filter(
                    id__in=contacts_list, org=request.profile.org)
                deal_obj.contacts.add(*contacts)

            if params.get("tags"):
                tags = params.get("tags")
                for tag in tags:
                    obj_tag = Tags.objects.filter(slug=tag.lower())
                    if obj_tag.exists():
                        obj_tag = obj_tag[0]
                    else:
                        obj_tag = Tags.objects.create(name=tag)
                    deal_obj.tags.add(obj_tag)

            if params.get("stage"):
                stage = params.get("stage")
                if stage in ["CLOSED WON", "CLOSED LOST"]:
                    deal_obj.closed_by = self.request.user

            if params.get("assigned_to"):
                assinged_to_list = params.get("assigned_to")
                profiles = Profile.objects.filter(
                    id__in=assinged_to_list, org=request.profile.org, is_active=True
                ).exclude(role='USER')
                deal_obj.assigned_to.add(*profiles)

            if self.request.FILES.get("deal_attachment"):
                attachment = Attachments()
                attachment.created_by = self.request.profile.user
                attachment.file_name = self.request.FILES.get(
                    "deal_attachment"
                ).name
                attachment.opportunity = deal_obj
                attachment.attachment = self.request.FILES.get(
                    "deal_attachment")
                attachment.save()

            recipients = list(
                deal_obj.assigned_to.all().values_list("id", flat=True)
            )

            # send_email_to_assigned_user.delay(
            #     recipients,
            #     deal_obj.id,
            # )
            return Response(
                {"error": False, "message": "Deal Created Successfully"},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"error": True, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

