import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from weather_app.models.login_route import login, auth_bp
from weather_app.models.user_model import Users

from werkzeug.security import generate_password_hash

@pytest.fixture
def app():
    """Fixture to set up the Flask app for testing."""
    app = Flask(__name__)
    app.register_blueprint(auth_bp)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """Fixture to provide a test client for the Flask app."""
    return app.test_client()

def test_login_success(client):
    """Test a successful login."""
    username = "testuser"
    password = "password123"
    password_hash = generate_password_hash(password, method="pbkdf2:sha256")  # Explicit hashing method

    with patch("weather_app.models.login_route.get_db_connection") as mock_get_db_connection:
        # Mock the database connection and User.get_id_by_username
        mock_conn = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn

        with patch("weather_app.models.user_model.Users.get_id_by_username") as mock_get_user:
            mock_user = MagicMock()
            mock_user.password_hash = password_hash
            mock_get_user.return_value = mock_user

            # Make a POST request to the login route
            response = client.post("/login", json={"username": username, "password": password})

            assert response.status_code == 200
            assert response.get_json() == {"message": "Login successful"}

def test_login_invalid_password(client):
    """Test login with an invalid password."""
    username = "testuser"
    password = "wrongpassword"
    password_hash = generate_password_hash("correctpassword", method="pbkdf2:sha256")  # Explicit hashing method

    with patch("weather_app.models.login_route.get_db_connection") as mock_get_db_connection:
        # Mock the database connection and User.get_user_by_username
        mock_conn = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn

        with patch("weather_app.models.user_model.Users.get_id_by_username") as mock_get_user:
            mock_user = MagicMock()
            mock_user.password_hash = password_hash
            mock_get_user.return_value = mock_user

            # Make a POST request to the login route
            response = client.post("/login", json={"username": username, "password": password})

            assert response.status_code == 401
            assert response.get_json() == {"error": "Invalid username or password"}

def test_login_user_not_found(client):
    """Test login when the user does not exist."""
    username = "nonexistentuser"
    password = "password123"

    with patch("weather_app.models.login_route.get_db_connection") as mock_get_db_connection:
        # Mock the database connection and User.get_user_by_username
        mock_conn = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn

        with patch("weather_app.models.user_model.Users.get_id_by_username") as mock_get_user:
            mock_get_user.return_value = None

            # Make a POST request to the login route
            response = client.post("/login", json={"username": username, "password": password})

            assert response.status_code == 401
            assert response.get_json() == {"error": "Invalid username or password"}

def test_login_missing_fields(client):
    """Test login with missing username or password."""
    response = client.post("/login", json={"username": "testuser"})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Username and password are required"}

def test_login_server_error(client):
    """Test login when an exception occurs on the server."""
    username = "testuser"
    password = "password123"

    with patch("weather_app.models.login_route.get_db_connection", side_effect=Exception("Database error")):
        # Make a POST request to the login route
        response = client.post("/login", json={"username": username, "password": password})

        assert response.status_code == 500
        assert "error" in response.get_json()
        assert "An error occurred: Database error" in response.get_json()["error"]
