class LeaveError(Exception):
    """Base class for every domain error. str(exc) is the user-facing message."""


class EndDateIsBeforeStartDate(LeaveError):
    def __init__(self):
        super().__init__("End date cannot be before start date.")


class HalfDayNeedsASingleWorkingDay(LeaveError):
    def __init__(self):
        super().__init__("A half day needs a single working day.")


class LeaveOverlapsExistingLeave(LeaveError):
    def __init__(self, leave):
        self.leave = leave
        super().__init__(f"You already have leave on {leave.start_date}-{leave.end_date}.")


class ProbationLimitExceeded(LeaveError):
    def __init__(self, status):
        self.status = status
        super().__init__("This is over your probation limit.")


class CommentRequiredToReject(LeaveError):
    def __init__(self):
        super().__init__("A comment is required to reject.")


class NoApproverAssigned(LeaveError):
    def __init__(self):
        super().__init__("No approver is assigned to you.")


class NotTheAssignedApprover(LeaveError):
    def __init__(self):
        super().__init__("Only the assigned approver can decide this request.")


class LeaveRequestNotFound(LeaveError):
    def __init__(self):
        super().__init__("Leave request not found.")


class LeaveAlreadyDecided(LeaveError):
    def __init__(self):
        super().__init__("This request has already been decided.")
