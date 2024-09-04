import json
import secrets
from multiprocessing import context
from re import template
from smtplib import SMTPException

from django.http import BadHeaderError
import requests
import logging
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.utils import json
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext as _
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
# from common.external_auth import CustomDualAuthentication
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.validators import EmailValidator, ValidationError as DjangoValidationError

from accounts.models import Account, Contact, Tags
from accounts.serializer import AccountSerializer
from cases.models import Case
from cases.serializer import CaseSerializer

# from common.custom_auth import JSONWebTokenAuthentication
from common import serializer, swagger_params1
from common.models import APISettings, Document, Org, Profile, User
from common.serializer import *
# from common.serializer import (
#     CreateUserSerializer,
#     PasswordChangeSerializer,
#     RegisterOrganizationSerializer,
# )
from common.tasks import (
    resend_activation_link_to_user,
    send_email_to_new_user,
    send_email_to_reset_password,
    send_email_user_delete,
    send_forgot_password_email,
)
from common.token_generator import account_activation_token
from django.core.exceptions import ObjectDoesNotExist

# from rest_framework_jwt.serializers import jwt_encode_handler
from common.utils import COUNTRIES, ROLES, jwt_payload_handler
from contacts.serializer import ContactSerializer
from leads.models import Lead
from leads.serializer import LeadSerializer
from opportunity.models import Opportunity
from opportunity.serializer import OpportunitySerializer
from teams.models import Teams
from teams.serializer import TeamsSerializer
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import Group


# Configure logging
logger = logging.getLogger(__name__)


class RegisterUserView(APIView):
    authentication_classes = []

    @extend_schema(
        request=RegisterUserSerializer,
        tags=["auth"],
        responses={
            200: "User registered successfully",
            400: "Bad Request",
            500: "Internal Server Error",
        },
    )
    def post(self, request, *args, **kwargs):
        if User.objects.exists():
            return Response({'error': True, 'errors': 'No new users can be created. Please contact the admin to send you an invitation to create a new account.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = RegisterUserSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({
                'error': False, 
                'message': 'User registered successfully.',
                'username': user.email,
                'access_token': access_token,
                'refresh_token': str(refresh),
                'user_id': user.id
            }, status=status.HTTP_201_CREATED)
        
        return Response({'error': True, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        

class SendForgotPasswordEmail(APIView):
    authentication_classes = []

    @extend_schema(
        request=SendForgotPasswordEmail,
        tags=["auth"],
        responses={
            200: "Forgot password email has been sent successfully",
            400: "Bad Request",
            500: "Internal Server Error",
        },
    )
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": True, "errors": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Validate the email format
            EmailValidator()(email)

            # Check if a user with this email exists
            user = User.objects.get(email=email)
            send_forgot_password_email(email)
            return Response({"error": False, "message": "Forgot password email has been sent successfully"}, status=status.HTTP_200_OK)

        except DjangoValidationError:
            return Response({"error": True, "errors": "Invalid email format"}, status=status.HTTP_400_BAD_REQUEST)

        except ObjectDoesNotExist:
            return Response({"error": True, "errors": "No user is associated with this email address"}, status=status.HTTP_400_BAD_REQUEST)
        
        except BadHeaderError:
            return Response({"error": True, "errors": "Invalid header found"}, status=status.HTTP_400_BAD_REQUEST)
        
        except SMTPException:
            return Response({"error": True, "errors": "Error occurred while sending the email. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:
            return Response({"error": True, "errors": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class ForgotPasswordResetView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        request=ForgotPasswordResetSerializer,
        tags=["auth"],
        responses={
            200: "Password has been reset successfully",
            400: "Bad Request",
        },
    )
    def post(self, request, uidb64, token):
        serializer = ForgotPasswordResetSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": True, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        password = serializer.validated_data['password']

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)

            if not default_token_generator.check_token(user, token):
                return Response({"error": True, "errors": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

            validate_password(password, user=user)

            user.set_password(password)
            user.save()

            return Response({"error": False, "message": "Password has been reset successfully"}, status=status.HTTP_200_OK)

        except DjangoValidationError as e:
            return Response({"error": True, "errors": list(e.messages)}, status=status.HTTP_400_BAD_REQUEST)

        except ValueError:
            return Response({"error": True, "errors": "Invalid user ID"}, status=status.HTTP_400_BAD_REQUEST)

        except ObjectDoesNotExist:
            return Response({"error": True, "errors": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": True, "errors": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PasswordResetConfirmAPIView(APIView):
    permission_classes = [AllowAny]  # Allow any user to access this view
    authentication_classes = []  # Ensure no authentication is required

    @extend_schema(
        request=PasswordResetSerializer,
        tags=["auth"],
        responses={
            200: "Password and profile information have been set successfully", 400: "Bad Request"},
    )
    def post(self, request, uidb64, token, format=None):
        password = request.data.get('password')
        phone = request.data.get('phone')
        # Assuming address is passed as a dictionary
        address_data = request.data.get('address')

        # Log request data for debugging
        logger.debug(
            f"Received password reset request: uidb64={uidb64}, token={token}")

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            logger.error(f"Exception occurred during user lookup: {str(e)}")
            return Response({'error': 'Invalid user or token'}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            try:
                # Validate password using Django's password validators
                validate_password(password, user=user)

                # Validate and save the phone number
                if phone:
                    if Profile.objects.filter(phone=phone).exists():
                        return Response({'error': 'Phone number already in use'}, status=status.HTTP_400_BAD_REQUEST)

                # Retrieve or create the user profile
                profile, created = Profile.objects.get_or_create(user=user)

                # Update phone number if provided
                if phone:
                    profile.phone = phone

                # Validate and update the address if provided
                if address_data:
                    # Assuming the Profile has a ForeignKey to BillingAddress
                    if profile.address:  # If the user already has an address
                        # Update the existing address
                        address_serializer = BillingAddressSerializer(
                            profile.address, data=address_data, partial=True)
                        if address_serializer.is_valid():
                            address_serializer.save()
                        else:
                            return Response({'errors': address_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                    else:  # If no existing address, create a new one
                        address_serializer = BillingAddressSerializer(
                            data=address_data)
                        if address_serializer.is_valid():
                            profile.address = address_serializer.save()
                        else:
                            return Response({'errors': address_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

                # Save the password
                form = SetPasswordForm(
                    user, {'new_password1': password, 'new_password2': password})
                if form.is_valid():
                    form.save()

                    # Save the profile updates
                    profile.save()

                    return Response({'message': 'Password and profile information have been set successfully'}, status=status.HTTP_200_OK)
                else:
                    logger.error(f"Password reset form errors: {form.errors}")
                    errors = {field: messages for field,
                              messages in form.errors.items()}
                    return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

            except ValidationError as e:
                # Capture and format the validation errors
                errors = list(e.messages)
                logger.error(f"Password validation errors: {errors}")
                return Response({'errors': {'password': errors}}, status=status.HTTP_400_BAD_REQUEST)

        else:
            logger.warning("Invalid token provided")
            return Response({'error': 'You have already set the password.'}, status=status.HTTP_400_BAD_REQUEST)


class GetTeamsAndUsersView(APIView):

    permission_classes = (IsAuthenticated,)

    @extend_schema(tags=["users"], parameters=swagger_params1.organization_params)
    def get(self, request, *args, **kwargs):
        data = {}
        teams = Teams.objects.filter(org=request.profile.org).order_by("-id")
        teams_data = TeamsSerializer(teams, many=True).data
        profiles = Profile.objects.filter(is_active=True, org=request.profile.org).order_by(
            "user__email"
        )
        profiles_data = ProfileSerializer(profiles, many=True).data
        data["teams"] = teams_data
        data["profiles"] = profiles_data
        return Response(data)


class UsersListView(APIView, LimitOffsetPagination):

    permission_classes = (IsAuthenticated,)

    @extend_schema(parameters=swagger_params1.organization_params, request=UserCreateSwaggerSerializer)
    def post(self, request, format=None):
        print(request.profile.role, request.user.is_superuser)
        if self.request.profile.role != "ADMIN" and not self.request.user.is_superuser:
            return Response(
                {"error": True, "errors": "Permission Denied"},
                status=status.HTTP_403_FORBIDDEN,
            )
        else:
            params = request.data
            if params:
                user_serializer = CreateUserSerializer(
                    data=params, org=request.profile.org)
                address_serializer = BillingAddressSerializer(data=params)
                profile_serializer = CreateProfileSerializer(data=params)
                data = {}
                if not user_serializer.is_valid():
                    data["user_errors"] = dict(user_serializer.errors)
                if not profile_serializer.is_valid():
                    data["profile_errors"] = profile_serializer.errors
                if not address_serializer.is_valid():
                    data["address_errors"] = (address_serializer.errors,)
                if data:
                    return Response(
                        {"error": True, "errors": data},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                if address_serializer.is_valid():
                    address_obj = address_serializer.save()
                    user = user_serializer.save(
                        is_active=True,
                    )
                    user.email = user.email
                    user.save()
                    # if params.get("password"):
                    #     user.set_password(params.get("password"))
                    #     user.save()
                    profile = Profile.objects.create(
                        user=user,
                        date_of_joining=timezone.now(),
                        role=params.get("role"),
                        address=address_obj,
                        org=request.profile.org,
                    )

                    # send_email_to_new_user.delay(
                    #     profile.id,
                    #     request.profile.org.id,
                    # )
                    send_email_to_reset_password.delay(user.email)
                    return Response(
                        {"error": False, "message": "User Created Successfully"},
                        status=status.HTTP_201_CREATED,
                    )

    @extend_schema(parameters=swagger_params1.user_list_params)
    def get(self, request, format=None):
        # if self.request.profile.role != "ADMIN" and not self.request.user.is_superuser:
        #     return Response(
        #         {"error": True, "errors": "Permission Denied"},
        #         status=status.HTTP_403_FORBIDDEN,
        #     )
        queryset = Profile.objects.filter(
            org=request.profile.org).order_by("-id")
        params = request.query_params
        if params:
            if params.get("email"):
                queryset = queryset.filter(
                    user__email__icontains=params.get("email"))
            if params.get("role"):
                queryset = queryset.filter(role=params.get("role"))
            if params.get("status"):
                queryset = queryset.filter(is_active=params.get("status"))

        context = {}
        queryset_active_users = queryset.filter(is_active=True)
        results_active_users = self.paginate_queryset(
            queryset_active_users.distinct(), self.request, view=self
        )
        active_users = ProfileSerializer(results_active_users, many=True).data
        if results_active_users:
            offset = queryset_active_users.filter(
                id__gte=results_active_users[-1].id
            ).count()
            if offset == queryset_active_users.count():
                offset = None
        else:
            offset = 0
        context["active_users"] = {
            "active_users_count": self.count,
            "active_users": active_users,
            "offset": offset,
        }

        queryset_inactive_users = queryset.filter(is_active=False)
        results_inactive_users = self.paginate_queryset(
            queryset_inactive_users.distinct(), self.request, view=self
        )
        inactive_users = ProfileSerializer(
            results_inactive_users, many=True).data
        if results_inactive_users:
            offset = queryset_inactive_users.filter(
                id__gte=results_inactive_users[-1].id
            ).count()
            if offset == queryset_inactive_users.count():
                offset = None
        else:
            offset = 0
        context["inactive_users"] = {
            "inactive_users_count": self.count,
            "inactive_users": inactive_users,
            "offset": offset,
        }

        context["admin_email"] = settings.ADMIN_EMAIL
        context["roles"] = ROLES
        context["status"] = [("True", "Active"), ("False", "In Active")]
        return Response(context)


class UserDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        profile = get_object_or_404(Profile, pk=pk)
        return profile

    @extend_schema(tags=["users"], parameters=swagger_params1.organization_params)
    def get(self, request, pk, format=None):
        profile_obj = self.get_object(pk)
        # if (
        #     self.request.profile.role != "ADMIN"
        #     and not self.request.profile.is_admin
        #     and self.request.profile.id != profile_obj.id
        # ):
        #     return Response(
        #         {"error": True, "errors": "Permission Denied"},
        #         status=status.HTTP_403_FORBIDDEN,
        #     )
        if profile_obj.org != request.profile.org:
            return Response(
                {"error": True, "errors": "User company doesnot match with header...."},
                status=status.HTTP_403_FORBIDDEN,
            )
        assigned_data = Profile.objects.filter(org=request.profile.org, is_active=True).values(
            "id", "user__email"
        )
        context = {}
        context["profile_obj"] = ProfileSerializer(profile_obj).data
        opportunity_list = Opportunity.objects.filter(assigned_to=profile_obj)
        context["opportunity_list"] = OpportunitySerializer(
            opportunity_list, many=True
        ).data
        contacts = Contact.objects.filter(assigned_to=profile_obj)
        context["contacts"] = ContactSerializer(contacts, many=True).data
        cases = Case.objects.filter(assigned_to=profile_obj)
        context["cases"] = CaseSerializer(cases, many=True).data
        context["assigned_data"] = assigned_data
        comments = profile_obj.user_comments.all()
        context["comments"] = CommentSerializer(comments, many=True).data
        context["countries"] = COUNTRIES
        return Response(
            {"error": False, "data": context},
            status=status.HTTP_200_OK,
        )

    @extend_schema(tags=["users"], parameters=swagger_params1.organization_params, request=UserCreateSwaggerSerializer)
    def put(self, request, pk, format=None):
        params = request.data
        profile = self.get_object(pk)
        address_obj = profile.address
        if (
            self.request.profile.role != "ADMIN"
            and not self.request.user.is_superuser
            and self.request.profile.id != profile.id
        ):
            return Response(
                {"error": True, "errors": "Permission Denied"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if profile.org != request.profile.org:
            return Response(
                {"error": True, "errors": "User company doesnot match with header...."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if 'role' in params and params['role'] != profile.role and self.request.profile.role != "ADMIN" and not self.request.user.is_superuser:
            return Response(
                {"error": True, "errors": "You do not have permission to change the role."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = CreateUserSerializer(
            data=params, instance=profile.user, org=request.profile.org
        )
        address_serializer = BillingAddressSerializer(
            data=params, instance=address_obj)
        profile_serializer = CreateProfileSerializer(
            data=params, instance=profile)
        data = {}
        if not serializer.is_valid():
            data["contact_errors"] = serializer.errors
        if not address_serializer.is_valid():
            data["address_errors"] = (address_serializer.errors,)
        if not profile_serializer.is_valid():
            data["profile_errors"] = (profile_serializer.errors,)
        if data:
            data["error"] = True
            return Response(
                data,
                status=status.HTTP_400_BAD_REQUEST,
            )
        if address_serializer.is_valid():
            address_obj = address_serializer.save()
            user = serializer.save()
            user.email = user.email
            user.save()
        if profile_serializer.is_valid():
            profile = profile_serializer.save()
            return Response(
                {"error": False, "message": "User Updated Successfully"},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"error": True, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(
        tags=["users"], parameters=swagger_params1.organization_params
    )
    def delete(self, request, pk, format=None):
        if self.request.profile.role != "ADMIN" and not self.request.profile.is_admin:
            return Response(
                {"error": True, "errors": "Permission Denied"},
                status=status.HTTP_403_FORBIDDEN,
            )
        self.object = self.get_object(pk)
        if self.object.id == request.profile.id:
            return Response(
                {"error": True, "errors": "Permission Denied"},
                status=status.HTTP_403_FORBIDDEN,
            )
        deleted_by = self.request.profile.user.email
        send_email_user_delete.delay(
            self.object.user.email,
            deleted_by=deleted_by,
        )
        self.object.delete()
        return Response({"status": "success"}, status=status.HTTP_200_OK)


# check_header not working
class ApiHomeView(APIView):

    permission_classes = (IsAuthenticated,)

    @extend_schema(parameters=swagger_params1.organization_params)
    def get(self, request, format=None):
        accounts = Account.objects.filter(
            status="open", org=request.profile.org)
        contacts = Contact.objects.filter(org=request.profile.org)
        leads = Lead.objects.filter(org=request.profile.org).exclude(
            Q(status="converted") | Q(status="closed")
        )
        opportunities = Opportunity.objects.filter(org=request.profile.org)

        if self.request.profile.role != "ADMIN" and not self.request.user.is_superuser:
            accounts = accounts.filter(
                Q(assigned_to=self.request.profile) | Q(
                    created_by=self.request.profile.user)
            )
            contacts = contacts.filter(
                Q(assigned_to__id__in=self.request.profile)
                | Q(created_by=self.request.profile.user)
            )
            leads = leads.filter(
                Q(assigned_to__id__in=self.request.profile)
                | Q(created_by=self.request.profile.user)
            ).exclude(status="closed")
            opportunities = opportunities.filter(
                Q(assigned_to__id__in=self.request.profile)
                | Q(created_by=self.request.profile.user)
            )
        context = {}
        context["accounts_count"] = accounts.count()
        context["contacts_count"] = contacts.count()
        context["leads_count"] = leads.count()
        context["opportunities_count"] = opportunities.count()
        context["accounts"] = AccountSerializer(accounts, many=True).data
        context["contacts"] = ContactSerializer(contacts, many=True).data
        context["leads"] = LeadSerializer(leads, many=True).data
        context["opportunities"] = OpportunitySerializer(
            opportunities, many=True).data
        return Response(context, status=status.HTTP_200_OK)


class OrgProfileCreateView(APIView):
    # authentication_classes = (CustomDualAuthentication,)
    permission_classes = (IsAuthenticated,)

    model1 = Org
    model2 = Profile
    serializer_class = OrgProfileCreateSerializer
    profile_serializer = CreateProfileSerializer

    @extend_schema(
        description="Organization and profile Creation api",
        request=OrgProfileCreateSerializer
    )
    def post(self, request, format=None):
        data = request.data
        data['api_key'] = secrets.token_hex(16)
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            org_obj = serializer.save()

            # now creating the profile
            profile_obj = self.model2.objects.create(
                user=request.user, org=org_obj)
            # now the current user is the admin of the newly created organisation
            profile_obj.is_organization_admin = True
            profile_obj.role = 'ADMIN'
            profile_obj.save()

            return Response(
                {
                    "error": False,
                    "message": "New Org is Created.",
                    "org": self.serializer_class(org_obj).data,
                    "status": status.HTTP_201_CREATED,
                }
            )
        else:
            return Response(
                {
                    "error": True,
                    "errors": serializer.errors,
                    "status": status.HTTP_400_BAD_REQUEST,
                }
            )

    @extend_schema(
        description="Just Pass the token, will return ORG list, associated with user"
    )
    def get(self, request, format=None):
        """
        here we are passing profile list of the user, where org details also included
        """
        profile_list = Profile.objects.filter(user=request.user)
        serializer = ShowOrganizationListSerializer(profile_list, many=True)
        return Response(
            {
                "error": False,
                "status": status.HTTP_200_OK,
                "profile_org_list": serializer.data,
            }
        )


class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(parameters=swagger_params1.organization_params)
    def get(self, request, format=None):
        # profile=Profile.objects.get(user=request.user)
        context = {}
        context["user_obj"] = ProfileSerializer(self.request.profile).data
        return Response(context, status=status.HTTP_200_OK)


class DocumentListView(APIView, LimitOffsetPagination):
    # authentication_classes = (CustomDualAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = Document

    def get_context_data(self, **kwargs):
        params = self.request.query_params
        queryset = self.model.objects.filter(
            org=self.request.profile.org).order_by("-id")
        if self.request.user.is_superuser or self.request.profile.role == "ADMIN":
            queryset = queryset
        else:
            if self.request.profile.documents():
                doc_ids = self.request.profile.documents().values_list("id", flat=True)
                shared_ids = queryset.filter(
                    Q(status="active") & Q(
                        shared_to__id__in=[self.request.profile.id])
                ).values_list("id", flat=True)
                queryset = queryset.filter(
                    Q(id__in=doc_ids) | Q(id__in=shared_ids))
            else:
                queryset = queryset.filter(
                    Q(status="active") & Q(
                        shared_to__id__in=[self.request.profile.id])
                )

        request_post = params
        if request_post:
            if request_post.get("title"):
                queryset = queryset.filter(
                    title__icontains=request_post.get("title"))
            if request_post.get("status"):
                queryset = queryset.filter(status=request_post.get("status"))

            if request_post.get("shared_to"):
                queryset = queryset.filter(
                    shared_to__id__in=json.loads(request_post.get("shared_to"))
                )

        context = {}
        profile_list = Profile.objects.filter(
            is_active=True, org=self.request.profile.org)
        if self.request.profile.role == "ADMIN" or self.request.profile.is_admin:
            profiles = profile_list.order_by("user__email")
        else:
            profiles = profile_list.filter(
                role="ADMIN").order_by("user__email")
        search = False
        if (
            params.get("document_file")
            or params.get("status")
            or params.get("shared_to")
        ):
            search = True
        context["search"] = search

        queryset_documents_active = queryset.filter(status="active")
        results_documents_active = self.paginate_queryset(
            queryset_documents_active.distinct(), self.request, view=self
        )
        documents_active = DocumentSerializer(
            results_documents_active, many=True).data
        if results_documents_active:
            offset = queryset_documents_active.filter(
                id__gte=results_documents_active[-1].id
            ).count()
            if offset == queryset_documents_active.count():
                offset = None
        else:
            offset = 0
        context["documents_active"] = {
            "documents_active_count": self.count,
            "documents_active": documents_active,
            "offset": offset,
        }

        queryset_documents_inactive = queryset.filter(status="inactive")
        results_documents_inactive = self.paginate_queryset(
            queryset_documents_inactive.distinct(), self.request, view=self
        )
        documents_inactive = DocumentSerializer(
            results_documents_inactive, many=True
        ).data
        if results_documents_inactive:
            offset = queryset_documents_inactive.filter(
                id__gte=results_documents_active[-1].id
            ).count()
            if offset == queryset_documents_inactive.count():
                offset = None
        else:
            offset = 0
        context["documents_inactive"] = {
            "documents_inactive_count": self.count,
            "documents_inactive": documents_inactive,
            "offset": offset,
        }

        context["users"] = ProfileSerializer(profiles, many=True).data
        context["status_choices"] = Document.DOCUMENT_STATUS_CHOICE
        return context

    @extend_schema(
        tags=["documents"], parameters=swagger_params1.document_get_params
    )
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return Response(context)

    @extend_schema(
        tags=["documents"], parameters=swagger_params1.organization_params, request=DocumentCreateSwaggerSerializer
    )
    def post(self, request, *args, **kwargs):
        params = request.data
        serializer = DocumentCreateSerializer(data=params, request_obj=request)
        if serializer.is_valid():
            doc = serializer.save(
                created_by=request.profile.user,
                org=request.profile.org,
                document_file=request.FILES.get("document_file"),
            )
            if params.get("shared_to"):
                assinged_to_list = params.get("shared_to")
                profiles = Profile.objects.filter(
                    id__in=assinged_to_list, org=request.profile.org, is_active=True
                )
                if profiles:
                    doc.shared_to.add(*profiles)
            if params.get("teams"):
                teams_list = params.get("teams")
                teams = Teams.objects.filter(
                    id__in=teams_list, org=request.profile.org)
                if teams:
                    doc.teams.add(*teams)

            return Response(
                {"error": False, "message": "Document Created Successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"error": True, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class DocumentDetailView(APIView):
    # authentication_classes = (CustomDualAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        return Document.objects.filter(id=pk).first()

    @extend_schema(
        tags=["documents"], parameters=swagger_params1.organization_params
    )
    def get(self, request, pk, format=None):
        self.object = self.get_object(pk)
        if not self.object:
            return Response(
                {"error": True, "errors": "Document does not exist"},
                status=status.HTTP_403_FORBIDDEN,
            )
        if self.object.org != self.request.profile.org:
            return Response(
                {"error": True, "errors": "User company doesnot match with header...."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if self.request.profile.role != "ADMIN" and not self.request.user.is_superuser:
            if not (
                (self.request.profile == self.object.created_by)
                or (self.request.profile in self.object.shared_to.all())
            ):
                return Response(
                    {
                        "error": True,
                        "errors": "You do not have Permission to perform this action",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
        profile_list = Profile.objects.filter(org=self.request.profile.org)
        if request.profile.role == "ADMIN" or request.user.is_superuser:
            profiles = profile_list.order_by("user__email")
        else:
            profiles = profile_list.filter(
                role="ADMIN").order_by("user__email")
        context = {}
        context.update(
            {
                "doc_obj": DocumentSerializer(self.object).data,
                "file_type_code": self.object.file_type()[1],
                "users": ProfileSerializer(profiles, many=True).data,
            }
        )
        return Response(context, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["documents"], parameters=swagger_params1.organization_params
    )
    def delete(self, request, pk, format=None):
        document = self.get_object(pk)
        if not document:
            return Response(
                {"error": True, "errors": "Documdnt does not exist"},
                status=status.HTTP_403_FORBIDDEN,
            )
        if document.org != self.request.profile.org:
            return Response(
                {"error": True, "errors": "User company doesnot match with header...."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if self.request.profile.role != "ADMIN" and not self.request.user.is_superuser:
            if (
                self.request.profile != document.created_by
            ):  # or (self.request.profile not in document.shared_to.all()):
                return Response(
                    {
                        "error": True,
                        "errors": "You do not have Permission to perform this action",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
        document.delete()
        return Response(
            {"error": False, "message": "Document deleted Successfully"},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["documents"], parameters=swagger_params1.organization_params, request=DocumentEditSwaggerSerializer
    )
    def put(self, request, pk, format=None):
        self.object = self.get_object(pk)
        params = request.data
        if not self.object:
            return Response(
                {"error": True, "errors": "Document does not exist"},
                status=status.HTTP_403_FORBIDDEN,
            )
        if self.object.org != self.request.profile.org:
            return Response(
                {"error": True, "errors": "User company doesnot match with header...."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if self.request.profile.role != "ADMIN" and not self.request.user.is_superuser:
            if not (
                (self.request.profile == self.object.created_by)
                or (self.request.profile in self.object.shared_to.all())
            ):
                return Response(
                    {
                        "error": True,
                        "errors": "You do not have Permission to perform this action",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
        serializer = DocumentCreateSerializer(
            data=params, instance=self.object, request_obj=request
        )
        if serializer.is_valid():
            doc = serializer.save(
                document_file=request.FILES.get("document_file"),
                status=params.get("status"),
                org=request.profile.org,
            )
            doc.shared_to.clear()
            if params.get("shared_to"):
                assinged_to_list = params.get("shared_to")
                profiles = Profile.objects.filter(
                    id__in=assinged_to_list, org=request.profile.org, is_active=True
                )
                if profiles:
                    doc.shared_to.add(*profiles)

            doc.teams.clear()
            if params.get("teams"):
                teams_list = params.get("teams")
                teams = Teams.objects.filter(
                    id__in=teams_list, org=request.profile.org)
                if teams:
                    doc.teams.add(*teams)
            return Response(
                {"error": False, "message": "Document Updated Successfully"},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"error": True, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserStatusView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        description="User Status View", parameters=swagger_params1.organization_params, request=UserUpdateStatusSwaggerSerializer
    )
    def post(self, request, pk, format=None):
        if self.request.profile.role != "ADMIN" and not self.request.user.is_superuser:
            return Response(
                {
                    "error": True,
                    "errors": "You do not have permission to perform this action",
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        params = request.data
        profiles = Profile.objects.filter(org=request.profile.org)
        profile = profiles.get(id=pk)

        if params.get("status"):
            user_status = params.get("status")
            if user_status == "Active":
                profile.is_active = True
            elif user_status == "Inactive":
                profile.is_active = False
            else:
                return Response(
                    {"error": True, "errors": "Please enter Valid Status for user"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            profile.save()

        context = {}
        active_profiles = profiles.filter(is_active=True)
        inactive_profiles = profiles.filter(is_active=False)
        context["active_profiles"] = ProfileSerializer(
            active_profiles, many=True).data
        context["inactive_profiles"] = ProfileSerializer(
            inactive_profiles, many=True
        ).data
        return Response(context)


class DomainList(APIView):
    model = APISettings
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=["Settings"], parameters=swagger_params1.organization_params
    )
    def get(self, request, *args, **kwargs):
        api_settings = APISettings.objects.filter(org=request.profile.org)
        users = Profile.objects.filter(is_active=True, org=request.profile.org).order_by(
            "user__email"
        )
        return Response(
            {
                "error": False,
                "api_settings": APISettingsListSerializer(api_settings, many=True).data,
                "users": ProfileSerializer(users, many=True).data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Settings"], parameters=swagger_params1.organization_params, request=APISettingsSwaggerSerializer
    )
    def post(self, request, *args, **kwargs):
        params = request.data
        assign_to_list = []
        if params.get("lead_assigned_to"):
            assign_to_list = params.get("lead_assigned_to")
        serializer = APISettingsSerializer(data=params)
        if serializer.is_valid():
            settings_obj = serializer.save(
                created_by=request.profile.user, org=request.profile.org)
            if params.get("tags"):
                tags = params.get("tags")
                for tag in tags:
                    tag_obj = Tags.objects.filter(name=tag).first()
                    if not tag_obj:
                        tag_obj = Tags.objects.create(name=tag)
                    settings_obj.tags.add(tag_obj)
            if assign_to_list:
                settings_obj.lead_assigned_to.add(*assign_to_list)
            return Response(
                {"error": False, "message": "API key added sucessfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"error": True, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class DomainDetailView(APIView):
    model = APISettings
    # authentication_classes = (CustomDualAuthentication,)
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=["Settings"], parameters=swagger_params1.organization_params
    )
    def get(self, request, pk, format=None):
        api_setting = self.get_object(pk)
        return Response(
            {"error": False, "domain": APISettingsListSerializer(
                api_setting).data},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Settings"], parameters=swagger_params1.organization_params, request=APISettingsSwaggerSerializer
    )
    def put(self, request, pk, **kwargs):
        api_setting = self.get_object(pk)
        params = request.data
        assign_to_list = []
        if params.get("lead_assigned_to"):
            assign_to_list = params.get("lead_assigned_to")
        serializer = APISettingsSerializer(data=params, instance=api_setting)
        if serializer.is_valid():
            api_setting = serializer.save()
            api_setting.tags.clear()
            api_setting.lead_assigned_to.clear()
            if params.get("tags"):
                tags = params.get("tags")
                for tag in tags:
                    tag_obj = Tags.objects.filter(name=tag).first()
                    if not tag_obj:
                        tag_obj = Tags.objects.create(name=tag)
                    api_setting.tags.add(tag_obj)
            if assign_to_list:
                api_setting.lead_assigned_to.add(*assign_to_list)
            return Response(
                {"error": False, "message": "API setting Updated sucessfully"},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"error": True, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(
        tags=["Settings"], parameters=swagger_params1.organization_params
    )
    def delete(self, request, pk, **kwargs):
        api_setting = self.get_object(pk)
        if api_setting:
            api_setting.delete()
        return Response(
            {"error": False, "message": "API setting deleted sucessfully"},
            status=status.HTTP_200_OK,
        )


class GoogleLoginView(APIView):

    """
    Check for existing users and log in with Google OAuth.
    post:
        If there is at least one existing user in the database:
            - Verifies the email associated with the Google account.
            - Logs in the user if they exist in the database.
            - Prevents creating a new account if the user does not exist.
        If there are no users in the database:
            - Allows the creation of a new user using Google account information.
        Returns:
            - Token of the successfully logged-in user.
            - Error message if creating a new user is not allowed.
    """
     
    permission_classes = (AllowAny,)

    @extend_schema(
        description="Login or sign in through Google",  request=SocialLoginSerializer,
    )

    def post(self, request):
        auth_config = AuthConfig.objects.filter().first()
        if not auth_config or not auth_config.is_google_login:
            return Response(
                {'error': True, 'message': 'Google login is disabled for this organization.'},
                status=status.HTTP_403_FORBIDDEN
            )

        payload = {'access_token': request.data.get("token")}
        r = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', params=payload)
        data = json.loads(r.text)
        
        if 'error' in data:
            return Response({'message': 'Invalid or expired Google token.'}, status=status.HTTP_400_BAD_REQUEST)
        
        email = data.get('email')

        if User.objects.exists():
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({'message': 'No new users can be created. Please contact the admin to send you an invitation to create a new account.'}, 
                                status=status.HTTP_403_FORBIDDEN)
        else:
            user = User()
            user.email = email
            user.profile_pic = data.get('picture')
            user.set_password(User.objects.make_random_password())
            user.save()
        
        token = RefreshToken.for_user(user)
        response = {
            'username': user.email,
            'access_token': str(token.access_token),
            'refresh_token': str(token),
            'user_id': user.id
        }
        return Response(response, status=status.HTTP_200_OK)


logger = logging.getLogger(__name__)


class LoginView(APIView):
    """
    Check for authentication with email and password
    post:
        Returns token of logged in user
    """
    @extend_schema(
        description="Login with email and password to get a JWT token",
        request=LoginSerializer,
        responses={200: 'JWT token'},
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')

            # Get the user with the given email
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = None

            if user is not None and user.check_password(password):
                token = RefreshToken.for_user(user)
                return Response({
                    'access': str(token.access_token),
                    'refresh': str(token)
                }, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            logger.debug(f"Serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthConfigView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(tags=["auth"])
    def get(self, request, format=None):
        auth_config = AuthConfig.objects.filter().first()

        if auth_config is None:
            return Response({"error": True, "message": "AuthConfig not found for this organization."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AuthConfigSerializer(auth_config)
        is_first_user = not User.objects.exists()
        
        return Response({"error": False, "data": {"is_google_login": serializer.data["is_google_login"],  "is_first_user": is_first_user}}, 
                         status=status.HTTP_200_OK)

    @extend_schema(
        tags=["auth"],
        request=AuthConfigSerializer,
    )
    def put(self, request, format=None):
        self.permission_classes = [IsAdminUser]  # Set permission for this method
        self.check_permissions(request)  # Check permissions for the request

        auth_config = AuthConfig.objects.filter().first()

        if auth_config is None:
            return Response({"error": True, "message": "AuthConfig not found for this organization."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AuthConfigSerializer(auth_config, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"error": False, "message": "AuthConfig updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"error": True, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Change password",
        request=ChangePasswordSerializer,
    )
    def put(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={'request': request})

        if serializer.is_valid():
            old_password = serializer.validated_data.get('old_password')
            new_password = serializer.validated_data.get('new_password')

            user = request.user
            if not user.check_password(old_password):
                return Response({"error": True, "message": "The old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()

            return Response({"error": False, "message": "Password changed successfully!"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
