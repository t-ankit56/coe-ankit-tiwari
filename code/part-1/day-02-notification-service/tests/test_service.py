import pytest
from notifications.models import Notification, SendResult, UnknownChannelError


def test_new_service_has_sent_nothing(service, email_channel, sms_channel):
    assert email_channel.sent == [] and sms_channel.sent == []


def test_send_via_email_reaches_only_email_channel(service, email_channel, sms_channel):
    n = Notification(to="a@x.com", body="hi", subject="Hello")
    service.send("email", n)
    assert email_channel.sent == [n]
    assert sms_channel.sent == []


def test_send_via_sms_reaches_only_sms_channel(service, email_channel, sms_channel):
    n = Notification(to="+919876543210", body="hi")
    service.send("sms", n)
    assert sms_channel.sent == [n]
    assert email_channel.sent == []


def test_send_returns_successful_result(service):
    n = Notification(to="a@x.com", body="hi", subject="Hi")
    assert service.send("email", n) == SendResult(channel="email", ok=True, error=None)


@pytest.mark.parametrize("name", ["fax", "", "EMAIL"])
def test_unknown_channel_raises(service, name):
    with pytest.raises(UnknownChannelError):
        service.send(name, Notification(to="a@x.com", body="hi"))


def test_send_many_delivers_once_per_channel_in_order(service, email_channel, sms_channel):
    n = Notification(to="a@x.com", body="hi", subject="Hi")
    results = service.send_many(["email", "sms"], n)
    assert [r.channel for r in results] == ["email", "sms"]
    assert all(r.ok for r in results)
    assert email_channel.sent == [n]
    assert sms_channel.sent == [n]
