import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from unittest.mock import patch, MagicMock
from weather_app.utils.db import db
from weather_app.models.user_model import Users
from sqlalchemy.exc import IntegrityError

@pytest.fixture
def app():
    """Fixture to create a Flask application for testing."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory database
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        db.init_app(app)
        db.create_all()  # Initialize tables
        yield app


@pytest.fixture
def mock_db_session(app):
    """Fixture to mock the database session."""
    with patch("weather_app.utils.db.db.session", autospec=True) as mock_session:
        yield mock_session


def test_create_user_success(app, mock_db_session):
    """Test successful user creation."""
    username = "newuser"
    password = "securepassword"
    
    with patch("weather_app.models.user_model.Users._generate_hashed_password", return_value=("salt123", "hashedpassword123")):
        with app.app_context():
            Users.create_user(username, password)
            mock_db_session.add.assert_called_once()
            mock_db_session.commit.assert_called_once()


def test_create_user_duplicate_username(app, mock_db_session):
    """Test user creation with a duplicate username."""
    mock_db_session.commit.side_effect = IntegrityError("Duplicate entry", {}, None)

    with app.app_context():
        with pytest.raises(ValueError, match="User with username 'existinguser' already exists"):
            Users.create_user("existinguser", "password123")
        mock_db_session.rollback.assert_called_once()


def test_check_password_success(app):
    """Test password validation for an existing user."""
    user = MagicMock()
    user.salt = "random_salt"
    user.password = "hashed_password_123"

    with patch("weather_app.models.user_model.Users.query") as mock_query, \
         patch("hashlib.sha256") as mock_sha256:
        
        mock_query.filter_by.return_value.first.return_value = user  # Correctly chain return values
        mock_sha256.return_value.hexdigest.return_value = "hashed_password_123"

        with app.app_context():
            result = Users.check_password("testuser", "correct_password")
            assert result is True

    mock_query.filter_by.assert_called_once_with(username="testuser")
    mock_sha256.assert_called_once_with("correct_passwordrandom_salt".encode())




def test_check_password_failure(app, mock_db_session):
    """Test password validation with incorrect password."""
    user = MagicMock()
    user.salt = "salt123"
    user.password = "hashedpassword123"

    with patch("weather_app.models.user_model.Users.query.filter_by") as mock_query, \
         patch("hashlib.sha256") as mock_hash:
        mock_query.return_value.first.return_value = user
        mock_hash().hexdigest.return_value = "wronghashedpassword"

        with app.app_context():
            result = Users.check_password("testuser", "wrongpassword")
            assert result is False


def test_delete_user_success(app, mock_db_session):
    """Test successful deletion of a user."""
    user = MagicMock()

    with patch("weather_app.models.user_model.Users.query") as mock_query:
        mock_query.filter_by.return_value.first.return_value = user  # Correctly return the user object

        with app.app_context():
            Users.delete_user("testuser")
            mock_db_session.delete.assert_called_once_with(user)
            mock_db_session.commit.assert_called_once()

    mock_query.filter_by.assert_called_once_with(username="testuser")



def test_delete_user_not_found(app):
    """Test user deletion when user does not exist."""
    with patch("weather_app.models.user_model.Users.query.filter_by") as mock_query:
        mock_query.return_value.first.return_value = None

        with app.app_context():
            with pytest.raises(ValueError, match="User testuser not found"):
                Users.delete_user("testuser")


def test_update_password_success(app, mock_db_session):
    """Test successful password update."""
    user = MagicMock()
    user.salt = "oldsalt"
    user.password = "oldhashedpassword"

    with patch("weather_app.models.user_model.Users.query") as mock_query, \
         patch("weather_app.models.user_model.Users._generate_hashed_password", return_value=("newsalt", "newhashedpassword")):
        
        mock_query.filter_by.return_value.first.return_value = user  # Mock user retrieval

        with app.app_context():
            Users.update_password("testuser", "newpassword")
            
            # Validate the mock's attributes were updated
            assert user.salt == "newsalt"
            assert user.password == "newhashedpassword"
            mock_db_session.commit.assert_called_once()

    mock_query.filter_by.assert_called_once_with(username="testuser")



def test_update_password_user_not_found(app):
    """Test password update when user does not exist."""
    with patch("weather_app.models.user_model.Users.query.filter_by") as mock_query:
        mock_query.return_value.first.return_value = None

        with app.app_context():
            with pytest.raises(ValueError, match="User testuser not found"):
                Users.update_password("testuser", "newpassword")
