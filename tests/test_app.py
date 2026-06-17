from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture(autouse=True)
def reset_activities():
    original = deepcopy(app_module.activities)
    yield
    app_module.activities = deepcopy(original)


@pytest.fixture
def client():
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_catalog(client):
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_signup_successfully_adds_participant(client):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up newstudent@mergington.edu for Chess Club"
    }
    assert "newstudent@mergington.edu" in app_module.activities["Chess Club"]["participants"]


def test_signup_unknown_activity_returns_404(client):
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_duplicate_email_returns_400(client):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up"}


def test_remove_participant_success(client):
    response = client.delete(
        "/activities/Chess Club/participants/michael@mergington.edu"
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Removed michael@mergington.edu from Chess Club"
    }
    assert "michael@mergington.edu" not in app_module.activities["Chess Club"]["participants"]


def test_remove_participant_unknown_activity_returns_404(client):
    response = client.delete(
        "/activities/Unknown Club/participants/michael@mergington.edu"
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_remove_participant_unknown_email_returns_404(client):
    response = client.delete(
        "/activities/Chess Club/participants/ghost@mergington.edu"
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not found"}
