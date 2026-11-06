from django.contrib.auth.models import User
from django.db import models
from django.db.models import F, Q


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    approver = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="direct_reports",
    )
    on_probation = models.BooleanField(default=False)
    probation_until = models.DateField(null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~Q(approver=F("user")),
                name="profile_approver_is_not_self",
            )
        ]

    @property
    def is_approver(self) -> bool:
        return self.user.direct_reports.exists()

    def __str__(self) -> str:
        return f"Profile of {self.user.username}"


class Holiday(models.Model):
    date = models.DateField(unique=True)
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"{self.name} ({self.date})"


class LeaveRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending"
        APPROVED = "approved"
        REJECTED = "rejected"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="leave_requests")
    approver = models.ForeignKey(User, on_delete=models.PROTECT, related_name="leave_requests_to_decide")
    start_date = models.DateField()
    end_date = models.DateField()
    half_day = models.BooleanField(default=False)
    days = models.DecimalField(max_digits=4, decimal_places=1)
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    decision_comment = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.user.username} {self.start_date}..{self.end_date} ({self.status})"
