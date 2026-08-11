from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client():
    return TestClient(app_module.app)


@pytest.fixture(autouse=True)
def restore_activities():
    original_activities = deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(original_activities)


def test_get_activities_returns_catalog(client):
    # Arrange
    expected_activity_names = sorted(app_module.activities)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert sorted(payload) == expected_activity_names


def test_signup_for_activity_adds_participant(client):
    # Arrange
    activity_name = "Test Activity"
    app_module.activities[activity_name] = {
        "description": "Temporary test activity",
        "schedule": "Mondays, 3:00 PM",
        "max_participants": 10,
        "participants": [],
    }

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email=test@example.com")

    # Assert
    assert response.status_code == 200
    assert app_module.activities[activity_name]["participants"] == ["test@example.com"]
    assert response.json()["message"] == f"Signed up test@example.com for {activity_name}"


def test_signup_for_activity_rejects_duplicate_email(client):
    # Arrange
    activity_name = "Test Activity"
    app_module.activities[activity_name] = {
        "description": "Temporary test activity",
        "schedule": "Mondays, 3:00 PM",
        "max_participants": 10,
        "participants": ["test@example.com"],
    }

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email=test@example.com")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_for_unknown_activity_returns_not_found(client):
    # Arrange
    activity_name = "Missing Activity"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email=test@example.com")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_delete_participant_removes_existing_participant(client):
    # Arrange
    activity_name = "Test Activity"
    app_module.activities[activity_name] = {
        "description": "Temporary test activity",
        "schedule": "Mondays, 3:00 PM",
        "max_participants": 10,
        "participants": ["test@example.com"],
    }

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/test@example.com")

    # Assert
    assert response.status_code == 200
    assert app_module.activities[activity_name]["participants"] == []
    assert response.json()["message"] == f"Removed test@example.com from {activity_name}"


def test_delete_participant_returns_not_found_when_missing(client):
    # Arrange
    activity_name = "Test Activity"
    app_module.activities[activity_name] = {
        "description": "Temporary test activity",
        "schedule": "Mondays, 3:00 PM",
        "max_participants": 10,
        "participants": [],
    }

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/test@example.com")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
