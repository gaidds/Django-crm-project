from django.urls import path

from deals import views

app_name = "api_deals"

urlpatterns = [
    path("", views.DealListView.as_view()),
    path("<str:pk>/", views.DealDetailView.as_view()),
    path("comment/<str:pk>/", views.DealCommentView.as_view()),
    path("attachment/<str:pk>/", views.DealAttachmentView.as_view()),
]
