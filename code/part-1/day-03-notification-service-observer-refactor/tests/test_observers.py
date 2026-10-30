import pytest
from fakes import FakeChannel, FakeObserver
from notifications.models import Notification, SendResult, UnknownChannelError
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


def test_unknown_channel_notifies_nobody(service):
    observer = FakeObserver()
    service.subscribe(observer)
    with pytest.raises(UnknownChannelError):
        service.send_many(["email", "fax"], Notification(to="a@x.com", body="hi"))
    assert observer.events == []


def test_unsubscribed_observer_is_not_notified(service):
    observer = FakeObserver()
    service.subscribe(observer)
    service.unsubscribe(observer)
    service.send("email", Notification(to="a@x.com", body="hi"))
    assert observer.events == []
