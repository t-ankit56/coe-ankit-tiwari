from fakes import FakeObserver
from notifications.models import Notification, SendResult


def test_observer_receives_successful_delivery(service):
    observer = FakeObserver()
    service.subscribe(observer)
    n = Notification(to="a@x.com", body="hi", subject="Hi")
    service.send("email", n)
    assert observer.events == [(n, SendResult(channel="email", ok=True))]
