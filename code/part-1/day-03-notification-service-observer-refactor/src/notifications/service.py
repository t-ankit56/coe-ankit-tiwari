from notifications.channels import Channel
from notifications.models import ChannelError, Notification, SendResult, UnknownChannelError
from notifications.observers import Observer


class NotificationService:
    """Routes a notification to channels by name and reports a SendResult per channel."""

    def __init__(self, channels: dict[str, Channel]) -> None:
        self._channels = channels
        self._observers: list[Observer] = []

    def subscribe(self, observer: Observer) -> None:
        self._observers.append(observer)

    def unsubscribe(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def send(self, channel_name: str, notification: Notification) -> SendResult:
        """Send through one channel; unknown names raise UnknownChannelError."""
        return self._deliver(channel_name, self._channel_for(channel_name), notification)

    def send_many(self, channel_names: list[str], notification: Notification) -> list[SendResult]:
        """Send through several channels in order; all names are checked before anything is sent."""
        channels = [(name, self._channel_for(name)) for name in channel_names]
        return [self._deliver(name, channel, notification) for name, channel in channels]

    def _channel_for(self, channel_name: str) -> Channel:
        if channel_name not in self._channels:
            raise UnknownChannelError(channel_name)
        return self._channels[channel_name]

    def _deliver(self, channel_name: str, channel: Channel, notification: Notification) -> SendResult:
        try:
            channel.send(notification)
        except ChannelError as error:
            result = SendResult(channel_name, False, str(error))
        else:
            result = SendResult(channel_name, True)
        self._notify(notification, result)
        return result

    def _notify(self, notification: Notification, result: SendResult) -> None:
        for observer in self._observers:
            observer.on_delivery(notification, result)
