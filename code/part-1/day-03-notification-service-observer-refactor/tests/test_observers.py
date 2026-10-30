from fakes import FakeChannel, FakeObserver
from notifications.models import Notification, SendResult
from notifications.service import NotificationService


def test_observer_receives_successful_delivery(service):
    observer = FakeObserver()
    service.subscribe(observer)
    n = Notification(to="a@x.com", body="hi", subject="Hi")
    service.send("email", n)
    assert observer.events == [(n, SendResult(channel="email", ok=True))]


def test_observer_receives_failed_delivery():
    service = NotificationService({"email": FakeChannel(fail_with="down")})
    observer = FakeObserver()
    service.subscribe(observer)
    n = Notification(to="a@x.com", body="hi")
    service.send("email", n)
    assert observer.events == [(n, SendResult(channel="email", ok=False, error="down"))]


def test_all_observers_notified_once_per_channel(service):
    first, second = FakeObserver(), FakeObserver()
    service.subscribe(first)
    service.subscribe(second)
    service.send_many(["email", "sms"], Notification(to="a@x.com", body="hi"))
    assert [r.channel for _, r in first.events] == ["email", "sms"]
    assert first.events == second.events
