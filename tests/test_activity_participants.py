from fastapi.testclient import TestClient

from src import app as app_module


client = TestClient(app_module.app)


def test_unregister_participant_removes_email_from_activity():
    activity_name = "Test Activity"
    app_module.activities[activity_name] = {
        "description": "Temporary test activity",
        "schedule": "Mondays, 3:00 PM",
        "max_participants": 10,
        "participants": [],
    }

    try:
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email=test@example.com"
        )
        assert signup_response.status_code == 200

        delete_response = client.delete(
            f"/activities/{activity_name}/participants/test@example.com"
        )

        assert delete_response.status_code == 200
        assert "test@example.com" not in app_module.activities[activity_name]["participants"]
    finally:
        app_module.activities.pop(activity_name, None)
