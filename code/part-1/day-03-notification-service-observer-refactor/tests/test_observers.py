import pytest
from fakes import FakeChannel, FakeObserver
from notifications.models import Notification, SendResult, UnknownChannelError
from notifications.service import NotificationService


class ExplodingObserver:
    def on_delivery(self, notification, result):
        raise RuntimeError("boom")


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


def test_unsubscribing_unknown_observer_raises(service):
    with pytest.raises(ValueError):
        service.unsubscribe(FakeObserver())


def test_failing_observer_does_not_break_delivery(service, email_channel):
    good = FakeObserver()
    service.subscribe(ExplodingObserver())
    service.subscribe(good)
    n = Notification(to="a@x.com", body="hi")
    assert service.send("email", n).ok
    assert email_channel.sent == [n]
    assert len(good.events) == 1
