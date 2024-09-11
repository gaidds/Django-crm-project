from rest_framework import serializers

from accounts.models import Tags
from common.models import Comment
from accounts.serializer import AccountSerializer
from accounts.models import Account
from common.serializer import (
    AttachmentsSerializer,
    ProfileSerializer,
    CommentSerializer,
    UserSerializer,
)
from contacts.serializer import ContactSerializer
from deals.models import Deal


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ("id", "name", "slug")


class DealSerializer(serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(), required=False, allow_null=True)
    account_name = serializers.SerializerMethodField()
    closed_by = ProfileSerializer()
    created_by = UserSerializer()
    tags = TagsSerializer(read_only=True, many=True)
    assigned_to = ProfileSerializer(read_only=True, many=True)
    contacts = ContactSerializer(read_only=True, many=True)
    country = serializers.SerializerMethodField()

    def get_country(self, obj):
        return obj.get_country_display()
    

    def get_account_name(self, obj):
        return obj.account.name if obj.account else None

    class Meta:
        model = Deal
        fields = (
            "id",
            "name",
            "contacts",
            "assigned_to",
            "account",
            "account_name",
            'website',
            "stage",
            "deal_source",
            "industry",
            "currency",
            "country",
            "value",
            "probability",
            "closed_by",
            "close_date",
            "description",
            "tags",
            "created_by",
            "created_at",
            "created_on_arrow",
        )



class DealCreateSerializer(serializers.ModelSerializer):
    probability = serializers.IntegerField(max_value=100)
    closed_on = serializers.DateField

    def __init__(self, *args, **kwargs):
        request_obj = kwargs.pop("request_obj", None)
        super().__init__(*args, **kwargs)
        self.org = request_obj.profile.org

    def validate_name(self, name):
        if self.instance:
            if (
                Deal.objects.filter(name__iexact=name, org=self.org)
                .exclude(id=self.instance.id)
                .exists()
            ):
                raise serializers.ValidationError(
                    "Deal already exists with this name"
                )

        else:
            if Deal.objects.filter(name__iexact=name, org=self.org).exists():
                raise serializers.ValidationError(
                    "Deal already exists with this name"
                )
        return name

    class Meta:
        model = Deal
        fields = (
            "name",
            "account",
            "website",
            "stage",
            "deal_source",
            "industry",
            "currency",
            "country",
            "value",
            "probability",
            "close_date",
            "description",
            "created_by",
            "created_at",
            "created_on_arrow",
            "org"
        )


class DealCreateSwaggerSerializer(serializers.ModelSerializer):
    close_date = serializers.DateField()
    class Meta:
        model = Deal
        fields = (
            "name",
            "account",
            "assigned_to",
            "contacts",
            "website",
            "stage",
            "deal_source",
            "industry",
            "currency",
            "country",
            "value",
            "probability",
            "close_date",
            "description",
            "tags",
        )


class DealDetailEditSwaggerSerializer(serializers.Serializer):
    comment = serializers.CharField()
    deal_attachment = serializers.FileField()


class DealCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            "id",
            "comment",
            "commented_on",
            "commented_by",
            "deal",
        )


class DealCommentEditSwaggerSerializer(serializers.Serializer):
    comment = serializers.CharField()

