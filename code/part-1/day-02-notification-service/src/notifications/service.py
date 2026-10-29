from notifications.models import ChannelError, SendResult, UnknownChannelError


class NotificationService:
    def __init__(self, channels):
        self._channels = channels

    def send(self, channel_name, notification):
        channel = self._channel_for(channel_name)
        try:
            channel.send(notification)
        except ChannelError as error:
            return SendResult(channel_name, False, str(error))
        return SendResult(channel_name, True)

    def send_many(self, channel_names, notification):
        return [self.send(name, notification) for name in channel_names]

    def _channel_for(self, channel_name):
        if channel_name not in self._channels:
            raise UnknownChannelError(channel_name)
        return self._channels[channel_name]
