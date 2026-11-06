import pytest

from leaves.tests.conftest import login_as


@pytest.mark.django_db
def test_my_leaves_response_has_a_summary_and_a_list(api_client, people):
    login_as(api_client, people.ankit)

    response = api_client.get("/api/leaves")

    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"summary", "leaves"}
    assert set(body["summary"].keys()) == {"days_taken", "pending_count"}
    assert body["leaves"] == []
