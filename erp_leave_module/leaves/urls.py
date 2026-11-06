from django.urls import path

from leaves import views

urlpatterns = [
    path("leaves", views.MyLeaveRequestsView.as_view()),
    path("leaves/<int:leave_id>/approve", views.ApproveLeaveView.as_view()),
    path("leaves/<int:leave_id>/reject", views.RejectLeaveView.as_view()),
    path("leaves/preview", views.LeavePreviewView.as_view()),
    path("login", views.LoginView.as_view()),
    path("logout", views.LogoutView.as_view()),
    path("me", views.CurrentUserView.as_view()),
]
