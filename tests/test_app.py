"""Tests for the FastAPI application"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivitiesEndpoint:
    """Test the /activities endpoint"""

    def test_get_activities(self):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
        # Check that activities have expected structure
        for activity_name, activity_details in activities.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)


class TestSignupEndpoint:
    """Test the signup endpoint"""

    def test_signup_new_participant(self):
        """Test signing up a new participant"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=test@example.com"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@example.com" in data["message"]
        assert "Chess Club" in data["message"]

    def test_signup_duplicate_participant(self):
        """Test that duplicate signups are rejected"""
        email = "duplicate@example.com"
        activity = "Programming Class"

        # First signup should succeed
        response1 = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response1.status_code == 200

        # Second signup with same email should fail
        response2 = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_nonexistent_activity(self):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/NonExistent/signup?email=test@example.com"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestUnregisterEndpoint:
    """Test the unregister endpoint"""

    def test_unregister_participant(self):
        """Test unregistering a participant"""
        email = "unreg@example.com"
        activity = "Basketball Team"

        # First, sign up
        response1 = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response1.status_code == 200

        # Then unregister
        response2 = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert response2.status_code == 200
        data = response2.json()
        assert "message" in data
        assert email in data["message"]

    def test_unregister_nonexistent_activity(self):
        """Test unregistering from non-existent activity"""
        response = client.delete(
            "/activities/NonExistent/unregister?email=test@example.com"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_unregister_not_registered(self):
        """Test unregistering someone not registered"""
        response = client.delete(
            "/activities/Tennis Club/unregister?email=notregistered@example.com"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_updates_participant_list(self):
        """Test that unregistering actually removes participant"""
        email = "update@example.com"
        activity = "Art Studio"

        # Sign up
        client.post(f"/activities/{activity}/signup?email={email}")

        # Verify participant is in the list
        response1 = client.get("/activities")
        assert email in response1.json()[activity]["participants"]

        # Unregister
        client.delete(f"/activities/{activity}/unregister?email={email}")

        # Verify participant is removed
        response2 = client.get("/activities")
        assert email not in response2.json()[activity]["participants"]


class TestRootEndpoint:
    """Test the root endpoint"""

    def test_root_redirect(self):
        """Test that root redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
