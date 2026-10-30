from typing import Protocol

from notifications.models import Notification, SendResult


class Observer(Protocol):
    """Anything with on_delivery(notification, result); told about every delivery attempt."""

    def on_delivery(self, notification: Notification, result: SendResult) -> None: ...
