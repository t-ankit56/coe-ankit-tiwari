import re

from notifications.models import ChannelError


class EmailChannel:
    def __init__(self):
        self.sent = []

    def send(self, notification):
        self._validate(notification)
        self.sent.append(notification)

    def _validate(self, notification):
        if "@" not in notification.to:
            raise ChannelError("email recipient must contain @")
        if not notification.body:
            raise ChannelError("body must not be empty")


class SmsChannel:
    def __init__(self):
        self.sent = []

    def send(self, notification):
        if not re.fullmatch(r"\+?[0-9]{7,15}", notification.to):
            raise ChannelError("sms number must be 7 to 15 digits, optional leading +")
        self.sent.append(notification)
