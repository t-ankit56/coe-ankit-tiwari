from notifications.models import ChannelError


class FakeChannel:
    def __init__(self, fail_with=None):
        self.sent = []
        self._fail_with = fail_with

    def send(self, notification):
        if self._fail_with:
            raise ChannelError(self._fail_with)
        self.sent.append(notification)
