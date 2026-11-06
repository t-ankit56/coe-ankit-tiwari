from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from leaves.serializers import (
    CurrentUserSerializer,
    LeavePreviewQueryInputSerializer,
    LeavePreviewSerializer,
    LeaveRequestSerializer,
    LeaveSubmissionInputSerializer,
    LoginInputSerializer,
    MyLeavesResponseSerializer,
)
from leaves.services.approval_service import approve_leave
from leaves.services.leave_service import list_my_leaves, preview_leave, submit_leave


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        credentials = LoginInputSerializer(data=request.data)
        credentials.is_valid(raise_exception=True)
        user = authenticate(
            username=credentials.validated_data["email"],
            password=credentials.validated_data["password"],
        )
        if user is None:
            raise ValidationError("Wrong email or password.")
        login(request._request, user)
        get_token(request._request)
        return Response(CurrentUserSerializer(user).data)


class LogoutView(APIView):
    def post(self, request):
        logout(request._request)
        return Response(status=204)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CurrentUserView(APIView):
    def get(self, request):
        return Response(CurrentUserSerializer(request.user).data)


class MyLeaveRequestsView(APIView):
    def get(self, request):
        return Response(MyLeavesResponseSerializer(list_my_leaves(request.user)).data)

    def post(self, request):
        submission = LeaveSubmissionInputSerializer(data=request.data)
        submission.is_valid(raise_exception=True)
        leave = submit_leave(request.user, **submission.validated_data)
        return Response({"leave": LeaveRequestSerializer(leave).data}, status=201)


class LeavePreviewView(APIView):
    def get(self, request):
        query = LeavePreviewQueryInputSerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        preview = preview_leave(
            request.user,
            query.validated_data["start_date"],
            query.validated_data["end_date"],
            query.validated_data["half"],
        )
        return Response(LeavePreviewSerializer(preview).data)


class ApproveLeaveView(APIView):
    def post(self, request, leave_id):
        leave = approve_leave(request.user, leave_id)
        return Response({"leave": LeaveRequestSerializer(leave).data})
