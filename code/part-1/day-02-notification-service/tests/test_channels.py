import pytest
from notifications.channels import EmailChannel, SmsChannel
from notifications.models import ChannelError, Notification


def test_new_email_channel_has_sent_nothing():
    assert EmailChannel().sent == []


def test_email_channel_records_a_message():
    channel = EmailChannel()
    n = Notification(to="a@x.com", body="hi", subject="Hello")
    channel.send(n)
    assert channel.sent == [n]


@pytest.mark.parametrize("to", ["", "no-at-sign"])
def test_email_channel_rejects_bad_recipient(to):
    channel = EmailChannel()
    with pytest.raises(ChannelError):
        channel.send(Notification(to=to, body="hi", subject="Hello"))
    assert channel.sent == []


def test_email_channel_rejects_empty_body():
    channel = EmailChannel()
    with pytest.raises(ChannelError):
        channel.send(Notification(to="a@x.com", body="", subject="Hello"))
    assert channel.sent == []


def test_new_sms_channel_has_sent_nothing():
    assert SmsChannel().sent == []


def test_sms_channel_records_a_message():
    channel = SmsChannel()
    n = Notification(to="+919876543210", body="hi")
    channel.send(n)
    assert channel.sent == [n]


@pytest.mark.parametrize("to", ["", "12345", "abcdefghij", "+1234567890123456"])
def test_sms_channel_rejects_bad_number(to):
    channel = SmsChannel()
    with pytest.raises(ChannelError):
        channel.send(Notification(to=to, body="hi"))
    assert channel.sent == []
