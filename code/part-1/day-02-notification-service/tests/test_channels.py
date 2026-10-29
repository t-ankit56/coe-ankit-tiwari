import pytest
from notifications.channels import EmailChannel
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
