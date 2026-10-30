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
