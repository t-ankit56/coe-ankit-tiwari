from notifications.models import SendResult, UnknownChannelError


class NotificationService:
    def __init__(self, channels):
        self._channels = channels

    def send(self, channel_name, notification):
        self._channel_for(channel_name).send(notification)
        return SendResult(channel_name, True)

    def _channel_for(self, channel_name):
        if channel_name not in self._channels:
            raise UnknownChannelError(channel_name)
        return self._channels[channel_name]
