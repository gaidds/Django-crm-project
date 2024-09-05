from django.urls import path

from deals import views

app_name = "api_deals"

urlpatterns = [
    path("", views.DealListView.as_view()),
]
