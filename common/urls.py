from django.urls import path
from rest_framework_simplejwt import views as jwt_views

from common import views

app_name = "api_common"


urlpatterns = [
    path("dashboard/", views.ApiHomeView.as_view()),
    path("dashboard/deals-per-month", views.DealsPerMonthView.as_view()),
    path(
        "auth/refresh-token/",
        jwt_views.TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    # GoogleLoginView
    path('auth/register/', views.RegisterUserView.as_view(), name='register'),
    path("auth/login/", views.LoginView.as_view()),
    path("auth/google/", views.GoogleLoginView.as_view()),
    path('auth-config/', views.AuthConfigView.as_view()),
    path("org/", views.OrgProfileCreateView.as_view()),
    path("profile/", views.ProfileView.as_view()),
    path("users/get-teams-and-users/", views.GetTeamsAndUsersView.as_view()),
    path("users/", views.UsersListView.as_view()),
    path("user/<str:pk>/", views.UserDetailView.as_view()),
    path("documents/", views.DocumentListView.as_view()),
    path("documents/<str:pk>/", views.DocumentDetailView.as_view()),
    path("api-settings/", views.DomainList.as_view()),
    path("api-settings/<str:pk>/", views.DomainDetailView.as_view()),
    path("user/<str:pk>/status/", views.UserStatusView.as_view()),
    path("auth/reset-password/<str:uidb64>/<str:token>/",
         views.PasswordResetConfirmAPIView.as_view(), name='password_reset_confirm'),
    path('auth/change-password/', views.ChangePasswordView.as_view()),
    path("auth/send-forgot-password-email/",
         views.SendForgotPasswordEmail.as_view()),
    path("auth/reset-forgot-password/<str:uidb64>/<str:token>/",
         views.ForgotPasswordResetView.as_view(), name='forgot-password_reset'),
]
