from rest_framework.authentication import SessionAuthentication


class SessionAuthenticationWith401(SessionAuthentication):
    def authenticate_header(self, request):
        return "Session"  # makes DRF answer 401 instead of 403 for anonymous users
