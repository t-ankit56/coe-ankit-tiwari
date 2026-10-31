import pytest
from fakes import FakeChannel
from notifications.service import NotificationService


@pytest.fixture
def email_channel():
    return FakeChannel()


@pytest.fixture
def sms_channel():
    return FakeChannel()


@pytest.fixture
def service(email_channel, sms_channel):
    return NotificationService({"email": email_channel, "sms": sms_channel})
