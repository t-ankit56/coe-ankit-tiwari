from notifications.models import SendResult, UnknownChannelError


class NotificationService:
    def __init__(self, channels):
        self._channels = channels

    def send(self, channel_name, notification):
        if channel_name not in self._channels:
            raise UnknownChannelError(channel_name)
        self._channels[channel_name].send(notification)
        return SendResult(channel_name, True)
