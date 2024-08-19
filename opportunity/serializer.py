from rest_framework import serializers

from accounts.models import Tags
from accounts.serializer import AccountSerializer
from common.serializer import AttachmentsSerializer, ProfileSerializer,UserSerializer
from contacts.serializer import ContactSerializer
from opportunity.models import Opportunity
from teams.serializer import TeamsSerializer


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ("id", "name", "slug")


class OpportunitySerializer(serializers.ModelSerializer):
    account = AccountSerializer()
    closed_by = ProfileSerializer()
    created_by = UserSerializer()
    tags = TagsSerializer(read_only=True, many=True)
    assigned_to = ProfileSerializer(read_only=True, many=True)
    contacts = ContactSerializer(read_only=True, many=True)
    teams = TeamsSerializer(read_only=True, many=True)
    opportunity_attachment = AttachmentsSerializer(read_only=True, many=True)

    class Meta:
        model = Opportunity
        # fields = ‘__all__’
        fields = (
            "id",
            "name",
            "stage",
            "currency",
            "amount",
            "lead_source",
            "probability",
            "contacts",
            "closed_by",
            "closed_on",
            "description",
            "assigned_to",
            "created_by",
            "created_at",
            "is_active",
            "tags",
            "opportunity_attachment",
            "teams",
            "created_on_arrow",
            "account",
            # "get_team_users",
            # "get_team_and_assigned_users",
            # "get_assigned_users_not_in_teams",
        )


class OpportunityCreateSerializer(serializers.ModelSerializer):
    probability = serializers.IntegerField(max_value=100)
    closed_on = serializers.DateField

    def __init__(self, *args, **kwargs):
        request_obj = kwargs.pop("request_obj", None)
        super().__init__(*args, **kwargs)
        self.org = request_obj.profile.org

    def validate_name(self, name):
        if self.instance:
            if (
                Opportunity.objects.filter(name__iexact=name, org=self.org)
                .exclude(id=self.instance.id)
                .exists()
            ):
                raise serializers.ValidationError(
                    "Opportunity already exists with this name"
                )

        else:
            if Opportunity.objects.filter(name__iexact=name, org=self.org).exists():
                raise serializers.ValidationError(
                    "Opportunity already exists with this name"
                )
        return name
    
    def validate_assigned_to(self, assigned_to):
        """Ensure that users with the 'USER' role cannot be assigned."""
        if assigned_to:
            for user_profile in assigned_to:
                if user_profile.role == "USER":
                    raise serializers.ValidationError(
                        f"{user_profile.user.email} cannot be assigned as they have the USER role."
                    )
        return assigned_to

    class Meta:
        model = Opportunity
        fields = (
            "name",
            "account",
            "stage",
            "currency",
            "amount",
            "lead_source",
            "probability",
            "closed_on",
            "description",
            "created_by",
            "created_at",
            "is_active",
            "created_on_arrow",
            "org"
            # "get_team_users",
            # "get_team_and_assigned_users",
            # "get_assigned_users_not_in_teams",
        )

class OpportunityCreateSwaggerSerializer(serializers.ModelSerializer):
    due_date = serializers.DateField()
    opportunity_attachment = serializers.FileField()
    class Meta:
        model = Opportunity
        fields = (
            "name",
            "account",
            "amount",
            "currency",
            "stage",
            "teams",
            "lead_source",
            "probability",
            "description",
            "assigned_to",
            "contacts",
            "due_date",
            "tags",
            "opportunity_attachment"
        )

    def validate_assigned_to(self, assigned_to):
        """Ensure that users with the 'USER' role cannot be assigned."""
        if assigned_to:
            for user_profile in assigned_to:
                if user_profile.role == "USER":
                    raise serializers.ValidationError(
                        f"{user_profile.user.email} cannot be assigned as they have the USER role."
                    )
        return assigned_to

class OpportunityDetailEditSwaggerSerializer(serializers.Serializer):
    comment = serializers.CharField()
    opportunity_attachment = serializers.FileField()

class OpportunityCommentEditSwaggerSerializer(serializers.Serializer):
    comment = serializers.CharField()

