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
        self.sent.append(notification)
