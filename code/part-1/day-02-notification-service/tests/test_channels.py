from notifications.channels import EmailChannel
from notifications.models import Notification


def test_new_email_channel_has_sent_nothing():
    assert EmailChannel().sent == []


def test_email_channel_records_a_message():
    channel = EmailChannel()
    n = Notification(to="a@x.com", body="hi", subject="Hello")
    channel.send(n)
    assert channel.sent == [n]
