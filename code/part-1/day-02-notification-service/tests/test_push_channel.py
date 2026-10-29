import pytest
from notifications import ChannelError, Notification, NotificationService, PushChannel


def test_new_push_channel_has_sent_nothing():
    assert PushChannel().sent == []


def test_push_channel_delivers_through_the_service():
    push = PushChannel()
    service = NotificationService({"push": push})
    n = Notification(to="device-token-123", body="hi")
    assert service.send("push", n).ok
    assert push.sent == [n]


def test_push_channel_rejects_empty_device_token():
    push = PushChannel()
    with pytest.raises(ChannelError):
        push.send(Notification(to="", body="hi"))
    assert push.sent == []
