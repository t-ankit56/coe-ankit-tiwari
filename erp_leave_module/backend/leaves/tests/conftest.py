from datetime import date
from types import SimpleNamespace

import pytest
from rest_framework.test import APIClient

from leaves.models import Holiday
from leaves.tests.factories import DEV_PASSWORD, make_user


@pytest.fixture
def holidays(db):
    Holiday.objects.create(date=date(2026, 11, 27), name="Thanksgiving")
    Holiday.objects.create(date=date(2026, 12, 25), name="Christmas")
    Holiday.objects.create(date=date(2027, 1, 1), name="New Year")


@pytest.fixture
def people(db):
    rohan = make_user("rohan@incubyte.co", "Rohan", "Verma")
    priya = make_user("priya@incubyte.co", "Priya", "Nair", approver=rohan)
    ankit = make_user("ankit@incubyte.co", "Ankit", "Tiwari", approver=priya)
    aarav = make_user("aarav@incubyte.co", "Aarav", "Singh", approver=priya, on_probation=True)
    return SimpleNamespace(rohan=rohan, priya=priya, ankit=ankit, aarav=aarav)


@pytest.fixture
def api_client():
    return APIClient()


def login_as(client, user):
    assert client.login(username=user.username, password=DEV_PASSWORD)
    return client
