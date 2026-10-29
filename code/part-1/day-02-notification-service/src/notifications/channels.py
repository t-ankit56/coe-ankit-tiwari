import re
from typing import Protocol

from notifications.models import ChannelError, Notification


class Channel(Protocol):
    """Anything with send(notification); raises ChannelError if it cannot deliver."""

    def send(self, notification: Notification) -> None: ...


class _RecordingChannel:
    def __init__(self) -> None:
        self.sent: list[Notification] = []

    def send(self, notification: Notification) -> None:
        """Validate the notification, then record it in sent."""
        self._validate(notification)
        self.sent.append(notification)

    def _validate(self, notification: Notification) -> None:
        if not notification.body:
            raise ChannelError("body must not be empty")


class EmailChannel(_RecordingChannel):
    """Records emails; the recipient must contain @."""

    def _validate(self, notification: Notification) -> None:
        if "@" not in notification.to:
            raise ChannelError("email recipient must contain @")
        super()._validate(notification)


class SmsChannel(_RecordingChannel):
    """Records SMS messages; the number must be 7 to 15 digits with an optional leading +."""

    def _validate(self, notification: Notification) -> None:
        if not re.fullmatch(r"\+?[0-9]{7,15}", notification.to):
            raise ChannelError("sms number must be 7 to 15 digits, optional leading +")
        super()._validate(notification)


class PushChannel(_RecordingChannel):
    """Records push notifications sent to a device token."""
