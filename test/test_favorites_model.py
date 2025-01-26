import pytest
from app import create_app
from weather_app.models.favorites_model import FavoritesModel
from weather_app.models.location_model import Location
from weather_app.utils.db import db

@pytest.fixture
def app():
    """
    Test fixture to set up a Flask app context for testing.
    """
    app = create_app()  # Replace with your app factory function
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory database for tests
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        db.create_all()  # Create all tables
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def setup_data(app):
    """
    Fixture to set up initial test data in the database.
    """
    with app.app_context():
        db.create_all()  # Ensure all tables are created

        # Add test locations
        location1 = Location(city="Boston", latitude=42.3601, longitude=-71.0589)
        location2 = Location(city="New York", latitude=40.7128, longitude=-74.0060)
        db.session.add(location1)
        db.session.add(location2)

        # Commit test data to the database
        db.session.commit()

        # Return created test data for use in tests
        yield {"location1": location1, "location2": location2}

        # Cleanup
        db.session.remove()
        db.drop_all()

######################################################
#    Add Favorites
######################################################

def test_add_favorite_success(app, setup_data):
    """
    Test successfully adding a favorite.
    """
    with app.app_context():
        location1 = setup_data["location1"]
        FavoritesModel.add_favorite(user_id=1, location_id=location1.id)

        # Verify the favorite was added
        favorites = FavoritesModel.get_favorites_by_user_id(user_id=1)
        assert len(favorites) == 1
        assert favorites[0] == location1.id

def test_add_favorite_duplicate(app, setup_data):
    """
    Test adding a duplicate favorite raises an error.
    """
    with app.app_context():
        location1 = setup_data["location1"]
        FavoritesModel.add_favorite(user_id=1, location_id=location1.id)

        # Adding the same favorite should raise a ValueError
        with pytest.raises(ValueError, match="Favorite already exists"):
            FavoritesModel.add_favorite(user_id=1, location_id=location1.id)

######################################################
#    Retrieve Favorites
######################################################

def test_get_favorites_success(app, setup_data):
    """
    Test retrieving favorites for a user.
    """
    with app.app_context():
        location1 = setup_data["location1"]
        location2 = setup_data["location2"]
        FavoritesModel.add_favorite(user_id=1, location_id=location1.id)
        FavoritesModel.add_favorite(user_id=1, location_id=location2.id)

        # Verify the favorites are retrieved correctly
        favorites = FavoritesModel.get_favorites_by_user_id(user_id=1)
        assert len(favorites) == 2
        assert location1.id in favorites
        assert location2.id in favorites

def test_get_favorites_empty(app):
    """
    Test retrieving favorites for a user with no favorites raises an error.
    """
    with app.app_context():
        with pytest.raises(ValueError, match="Favorites list is empty"):
            FavoritesModel.get_favorites_by_user_id(user_id=1)

######################################################
#    Remove Favorites
######################################################

def test_remove_favorite_success(app, setup_data):
    """
    Test successfully removing a favorite.
    """
    with app.app_context():
        location1 = setup_data["location1"]
        FavoritesModel.add_favorite(user_id=1, location_id=location1.id)

        # Remove the favorite
        FavoritesModel.remove_favorite(user_id=1, location_id=location1.id)

        # Verify the favorite was removed
        with pytest.raises(ValueError, match="Favorites list is empty"):
            FavoritesModel.get_favorites_by_user_id(user_id=1)

def test_remove_favorite_not_found(app, setup_data):
    """
    Test removing a favorite that does not exist raises an error.
    """
    with app.app_context():
        location1 = setup_data["location1"]

        # Attempt to remove a non-existent favorite
        with pytest.raises(ValueError, match="Favorite does not exist"):
            FavoritesModel.remove_favorite(user_id=1, location_id=location1.id)
