from notifications.models import ChannelError


class EmailChannel:
    def __init__(self):
        self.sent = []

    def send(self, notification):
        if "@" not in notification.to:
            raise ChannelError("email recipient must contain @")
        self.sent.append(notification)
