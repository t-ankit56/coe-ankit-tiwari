from notifications.models import SendResult


class NotificationService:
    def __init__(self, channels):
        self._channels = channels

    def send(self, channel_name, notification):
        self._channels[channel_name].send(notification)
        return SendResult(channel_name, True)
