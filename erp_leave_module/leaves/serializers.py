from rest_framework import serializers


class LoginInputSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()


class CurrentUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.SerializerMethodField()
    email = serializers.EmailField()
    is_approver = serializers.SerializerMethodField()
    on_probation = serializers.SerializerMethodField()
    approver = serializers.SerializerMethodField()

    def get_name(self, user) -> str:
        return user.get_full_name()

    def get_is_approver(self, user) -> bool:
        return user.profile.is_approver

    def get_on_probation(self, user) -> bool:
        return user.profile.on_probation

    def get_approver(self, user) -> dict | None:
        approver = user.profile.approver
        return {"name": approver.get_full_name()} if approver else None


class LeaveRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    half_day = serializers.BooleanField()
    days = serializers.DecimalField(max_digits=4, decimal_places=1, coerce_to_string=False)
    reason = serializers.CharField()
    status = serializers.CharField()
    approver_name = serializers.SerializerMethodField()
    decision_comment = serializers.CharField()
    submitted_at = serializers.DateTimeField(source="created_at")

    def get_approver_name(self, leave_request) -> str:
        return leave_request.approver.get_full_name()


class MyLeavesSummarySerializer(serializers.Serializer):
    days_taken = serializers.DecimalField(max_digits=5, decimal_places=1, coerce_to_string=False)
    pending_count = serializers.IntegerField()


class MyLeavesResponseSerializer(serializers.Serializer):
    summary = MyLeavesSummarySerializer(source="*")
    leaves = LeaveRequestSerializer(many=True)


class LeaveSubmissionInputSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    half_day = serializers.BooleanField(default=False)
    reason = serializers.CharField()


class LeavePreviewQueryInputSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    half = serializers.BooleanField(default=False)


class DayInRangeSerializer(serializers.Serializer):
    date = serializers.DateField()
    counts = serializers.DecimalField(max_digits=3, decimal_places=1, coerce_to_string=False)
    label = serializers.CharField(allow_null=True)


class OverlapSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()


class LeavePreviewSerializer(serializers.Serializer):
    days = serializers.DecimalField(max_digits=4, decimal_places=1, coerce_to_string=False)
    breakdown = DayInRangeSerializer(many=True)
    overlap = OverlapSerializer(allow_null=True)
    probation = serializers.SerializerMethodField()

    def get_probation(self, preview):
        return None  # filled in by Task 3


class RejectionInputSerializer(serializers.Serializer):
    # Blank text is allowed here on purpose: "a comment is required" is a leave rule,
    # so the service decides and raises CommentRequiredToReject.
    comment = serializers.CharField(allow_blank=True, trim_whitespace=False, default="")
