import pytest
from app import create_app
from weather_app.utils.db import db
from weather_app.models.location_model import Location

@pytest.fixture
def app():
    """
    Test fixture to set up a Flask app context for testing.
    """
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory database for tests
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def session(app):
    """
    Test fixture to provide a database session for tests.
    """
    return db.session

######################################################
#
#    Add and Delete Tests
#
######################################################

def test_add_location(session):
    """Test adding a location to the database."""
    location = Location.create_location("Boston", 42.3601, -71.0589)

    # Query back the location to check it was added
    result = Location.query.one()
    assert result.city == "Boston"
    assert result.latitude == 42.3601
    assert result.longitude == -71.0589

def test_add_location_invalid_latitude(app):
    """Test error when trying to create a location with invalid latitude."""
    with pytest.raises(ValueError, match="Invalid latitude: -100. Must be between -90 and 90."):
        Location.create_location("Boston", -100, -71.0589)

    with pytest.raises(ValueError, match="Invalid latitude: 100. Must be between -90 and 90."):
        Location.create_location("Boston", 100, -71.0589)

def test_add_location_invalid_longitude(app):
    """Test error when trying to create a location with invalid longitude."""
    with pytest.raises(ValueError, match="Invalid longitude: -200. Must be between -180 and 180."):
        Location.create_location("Boston", 42.3601, -200)

    with pytest.raises(ValueError, match="Invalid longitude: 200. Must be between -180 and 180."):
        Location.create_location("Boston", 42.3601, 200)

def test_delete_location(session):
    """Test deleting a location."""
    location = Location.create_location("Boston", 42.3601, -71.0589)
    Location.delete_location(location.id)

    # Check that the location is removed
    result = Location.query.filter_by(id=location.id).first()
    assert result is None

def test_delete_location_bad_id(session):
    """Test deleting a location that does not exist."""
    with pytest.raises(ValueError, match="Location 999 not found."):
        Location.delete_location(999)

######################################################
#
#    Retrieve Locations Tests
#
######################################################

def test_get_location_by_id(session):
    """Test retrieving a location by ID."""
    location = Location.create_location("Boston", 42.3601, -71.0589)
    result = Location.get_location_by_id(location.id)
    assert result["city"] == "Boston"
    assert result["latitude"] == 42.3601
    assert result["longitude"] == -71.0589

def test_get_location_by_invalid_id(session):
    """Test retrieving a location by invalid ID."""
    with pytest.raises(ValueError, match="Location 999 not found."):
        Location.get_location_by_id(999)

def test_get_all_locations(session):
    """Test retrieving all locations."""
    Location.create_location("Boston", 42.3601, -71.0589)
    Location.create_location("New York", 40.7128, -74.0060)

    results = Location.get_all_locations()
    assert len(results) == 2
    assert results[0]["city"] == "Boston"
    assert results[1]["city"] == "New York"
