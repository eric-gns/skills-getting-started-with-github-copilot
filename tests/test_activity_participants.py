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


def test_unregister_participant_removes_email_from_activity(client):
    # Arrange
    activity_name = "Test Activity"
    app_module.activities[activity_name] = {
        "description": "Temporary test activity",
        "schedule": "Mondays, 3:00 PM",
        "max_participants": 10,
        "participants": [],
    }

    # Act
    signup_response = client.post(
        f"/activities/{activity_name}/signup?email=test@example.com"
    )
    delete_response = client.delete(
        f"/activities/{activity_name}/participants/test@example.com"
    )

    # Assert
    assert signup_response.status_code == 200
    assert delete_response.status_code == 200
    assert "test@example.com" not in app_module.activities[activity_name]["participants"]
