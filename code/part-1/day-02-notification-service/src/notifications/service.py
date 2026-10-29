from notifications.models import ChannelError, SendResult, UnknownChannelError


class NotificationService:
    def __init__(self, channels):
        self._channels = channels

    def send(self, channel_name, notification):
        return self._deliver(channel_name, self._channel_for(channel_name), notification)

    def send_many(self, channel_names, notification):
        channels = [(name, self._channel_for(name)) for name in channel_names]
        return [self._deliver(name, channel, notification) for name, channel in channels]

    def _channel_for(self, channel_name):
        if channel_name not in self._channels:
            raise UnknownChannelError(channel_name)
        return self._channels[channel_name]

    def _deliver(self, channel_name, channel, notification):
        try:
            channel.send(notification)
        except ChannelError as error:
            return SendResult(channel_name, False, str(error))
        return SendResult(channel_name, True)
