from datetime import date

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from leaves.models import Holiday, LeaveRequest, Profile
from leaves.rules import count_working_days

DEV_PASSWORD = "password123"

# email, first name, last name, approver email, on probation, probation until
PEOPLE = [
    ("rohan@incubyte.co", "Rohan", "Verma", None, False, None),
    ("priya@incubyte.co", "Priya", "Nair", "rohan@incubyte.co", False, None),
    ("ankit@incubyte.co", "Ankit", "Tiwari", "priya@incubyte.co", False, None),
    ("aarav@incubyte.co", "Aarav", "Singh", "priya@incubyte.co", True, date(2027, 3, 15)),
]

HOLIDAYS = [
    (date(2026, 11, 27), "Thanksgiving"),
    (date(2026, 12, 25), "Christmas"),
    (date(2027, 1, 1), "New Year"),
]


# user email, start, end, half day, status, decision comment
LEAVE_REQUESTS = [
    ("ankit@incubyte.co", date(2026, 7, 8), date(2026, 7, 10), False, "approved", ""),
    ("ankit@incubyte.co", date(2026, 10, 22), date(2026, 10, 23), False, "approved", ""),
    ("ankit@incubyte.co", date(2026, 6, 15), date(2026, 6, 15), False, "rejected",
     "Release day, I need the full team in."),
    ("ankit@incubyte.co", date(2026, 12, 24), date(2026, 12, 28), False, "pending", ""),
    ("aarav@incubyte.co", date(2026, 11, 2), date(2026, 11, 2), False, "approved", ""),
    ("aarav@incubyte.co", date(2026, 11, 3), date(2026, 11, 3), True, "approved", ""),
]


class Command(BaseCommand):
    help = "Create the demo users, profiles and holidays. Safe to run twice."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Wipe seeded data first.")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            LeaveRequest.objects.all().delete()
            Profile.objects.all().delete()
            User.objects.filter(email__in=[person[0] for person in PEOPLE]).delete()
            Holiday.objects.all().delete()

        users = {}
        for email, first_name, last_name, _, _, _ in PEOPLE:
            user, created = User.objects.get_or_create(
                username=email,
                defaults={"email": email, "first_name": first_name, "last_name": last_name},
            )
            if created:
                user.set_password(DEV_PASSWORD)
                user.save()
            users[email] = user

        for email, _, _, approver_email, on_probation, probation_until in PEOPLE:
            Profile.objects.update_or_create(
                user=users[email],
                defaults={
                    "approver": users[approver_email] if approver_email else None,
                    "on_probation": on_probation,
                    "probation_until": probation_until,
                },
            )

        for holiday_date, name in HOLIDAYS:
            Holiday.objects.update_or_create(date=holiday_date, defaults={"name": name})

        holidays = {holiday.date: holiday.name for holiday in Holiday.objects.all()}
        for email, start_date, end_date, half_day, status, comment in LEAVE_REQUESTS:
            user = users[email]
            LeaveRequest.objects.update_or_create(
                user=user,
                start_date=start_date,
                end_date=end_date,
                defaults={
                    "approver": user.profile.approver,
                    "half_day": half_day,
                    "days": count_working_days(start_date, end_date, holidays, half_day),
                    "reason": "Seeded request",
                    "status": status,
                    "decision_comment": comment,
                    "decided_at": None if status == "pending" else timezone.now(),
                },
            )

        self.stdout.write(f"{User.objects.count()} users, {Holiday.objects.count()} holidays, "
            f"{LeaveRequest.objects.count()} leave requests.")
