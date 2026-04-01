import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app, follow_redirects=False)


def test_get_root_redirect():
    """Test that GET / redirects to static index.html"""
    # Arrange - no setup needed

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    """Test that GET /activities returns all activities data"""
    # Arrange - no setup needed

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0  # Should have activities

    # Check structure of first activity
    first_activity = next(iter(data.values()))
    assert "description" in first_activity
    assert "schedule" in first_activity
    assert "max_participants" in first_activity
    assert "participants" in first_activity
    assert isinstance(first_activity["participants"], list)


def test_signup_success():
    """Test successful signup for an activity"""
    # Arrange
    activity_name = "Programming Class"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert f"Signed up {email} for {activity_name}" == result["message"]


def test_signup_duplicate():
    """Test signup fails when student is already signed up"""
    # Arrange
    activity_name = "Gym Class"
    email = "duplicate@mergington.edu"

    # Act - first signup
    client.post(f"/activities/{activity_name}/signup?email={email}")
    # Second signup
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    result = response.json()
    assert "detail" in result
    assert "already signed up" in result["detail"]


def test_signup_activity_not_found():
    """Test signup fails for non-existent activity"""
    # Arrange
    invalid_activity = "NonExistent Activity"
    email = "test@mergington.edu"

    # Act
    response = client.post(f"/activities/{invalid_activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "detail" in result
    assert "Activity not found" in result["detail"]


def test_signup_full_activity():
    """Test signup fails when activity reaches max participants"""
    # Arrange
    activity_name = "Chess Club"
    email_base = "fulltest"

    # Get current data
    response = client.get("/activities")
    data = response.json()
    max_participants = data[activity_name]["max_participants"]
    current_count = len(data[activity_name]["participants"])

    # Fill the activity to max
    for i in range(max_participants - current_count):
        client.post(f"/activities/{activity_name}/signup?email={email_base}{i}@test.com")

    # Act - try to signup one more
    response = client.post(f"/activities/{activity_name}/signup?email={email_base}full@test.com")

    # Assert
    assert response.status_code == 400
    result = response.json()
    assert "detail" in result
    assert "Activity is full" in result["detail"]


def test_delete_success():
    """Test successful removal from an activity"""
    # Arrange
    activity_name = "Art Studio"
    email = "removeme@mergington.edu"

    # First signup
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert f"Removed {email} from {activity_name}" == result["message"]


def test_delete_not_signed_up():
    """Test delete fails when student is not signed up"""
    # Arrange
    activity_name = "Tennis Club"
    email = "notsigned@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "detail" in result
    assert "Student not signed up" in result["detail"]


def test_delete_activity_not_found():
    """Test delete fails for non-existent activity"""
    # Arrange
    invalid_activity = "Fake Activity"
    email = "test@mergington.edu"

    # Act
    response = client.delete(f"/activities/{invalid_activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "detail" in result
    assert "Activity not found" in result["detail"]