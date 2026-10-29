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
