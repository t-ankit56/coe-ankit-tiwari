from notifications.models import Notification
from notifications.service import NotificationService


class FakeChannel:
    def __init__(self):
        self.sent = []

    def send(self, notification):
        self.sent.append(notification)


def test_new_service_has_sent_nothing():
    email, sms = FakeChannel(), FakeChannel()
    NotificationService({"email": email, "sms": sms})
    assert email.sent == [] and sms.sent == []


def test_send_via_email_reaches_only_email_channel():
    email, sms = FakeChannel(), FakeChannel()
    service = NotificationService({"email": email, "sms": sms})
    n = Notification(to="a@x.com", body="hi", subject="Hello")
    service.send("email", n)
    assert email.sent == [n]
    assert sms.sent == []


def test_send_via_sms_reaches_only_sms_channel():
    email, sms = FakeChannel(), FakeChannel()
    service = NotificationService({"email": email, "sms": sms})
    n = Notification(to="+919876543210", body="hi")
    service.send("sms", n)
    assert sms.sent == [n]
    assert email.sent == []
