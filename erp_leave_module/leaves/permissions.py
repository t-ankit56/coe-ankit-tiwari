from rest_framework.permissions import BasePermission


class IsApprover(BasePermission):
    message = "Only approvers can see approvals."

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.profile.is_approver)
