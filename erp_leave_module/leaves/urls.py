from django.urls import path

from leaves import views

urlpatterns = [
    path("me", views.CurrentUserView.as_view()),
]
