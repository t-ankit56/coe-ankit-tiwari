from django.urls import path

from leaves import views

urlpatterns = [
    path("login", views.LoginView.as_view()),
    path("me", views.CurrentUserView.as_view()),
]
