from decimal import Decimal

from django.contrib.auth.models import User

from leaves.models import Holiday, LeaveRequest, Profile

DEV_PASSWORD = "password123"


def make_user(email, first_name, last_name, approver=None, on_probation=False):
    user = User.objects.create_user(
        username=email, email=email, password=DEV_PASSWORD,
        first_name=first_name, last_name=last_name,
    )
    Profile.objects.create(user=user, approver=approver, on_probation=on_probation)
    return user


def make_leave(user, start_date, end_date, status="pending", half_day=False,
               days=None, reason="Test", approver=None):
    if days is None:
        from leaves.rules import count_working_days  # rules arrive in step 1.1

        holidays = {holiday.date: holiday.name for holiday in Holiday.objects.all()}
        days = count_working_days(start_date, end_date, holidays, half_day)
    return LeaveRequest.objects.create(
        user=user,
        approver=approver or user.profile.approver,
        start_date=start_date,
        end_date=end_date,
        half_day=half_day,
        days=Decimal(days),
        reason=reason,
        status=status,
    )
