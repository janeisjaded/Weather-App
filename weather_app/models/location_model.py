from dataclasses import dataclass, asdict
import logging
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import validates
from weather_app.utils.db import db
from weather_app.utils.api_utils import fetch_air_quality_data, fetch_forecast, fetch_historical_data
from weather_app.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class Location(db.Model):
    __tablename__ = 'locations'

    id: int = db.Column(db.Integer, primary_key=True)
    city: str = db.Column(db.String(80), nullable=False)
    latitude: float = db.Column(db.Float, nullable=False)
    longitude: float = db.Column(db.Float, nullable=False)

    @validates('latitude', 'longitude')
    def validate_coordinates(self, key, value):
        """
        Validates latitude and longitude values.
        """
        if key == 'latitude' and not (-90 <= value <= 90):
            raise ValueError(f"Invalid latitude: {value}. Must be between -90 and 90.")
        if key == 'longitude' and not (-180 <= value <= 180):
            raise ValueError(f"Invalid longitude: {value}. Must be between -180 and 180.")
        return value

    @classmethod
    def create_location(cls, city: str, latitude: float, longitude: float) -> 'Location':
        """
        Adds a new location to the database.
        """
        try:
            location = cls(city=city, latitude=latitude, longitude=longitude)
            db.session.add(location)
            db.session.commit()
            logger.info("Location created successfully: %s", asdict(location))
            return location
        except IntegrityError as e:
            db.session.rollback()
            logger.error("Database integrity error: %s", str(e))
            raise ValueError("Location already exists or integrity error occurred.")
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating location: %s", str(e))
            raise

    @classmethod
    def delete_location(cls, location_id: int) -> None:
        """
        Deletes a location by marking it as removed.
        """
        location = cls.query.filter_by(id=location_id).first()
        if not location:
            logger.info("Location with ID %s not found", location_id)
            raise ValueError(f"Location {location_id} not found.")

        db.session.delete(location)
        db.session.commit()
        logger.info("Location with ID %s deleted successfully.", location_id)

    @classmethod
    def get_location_by_id(cls, location_id: int) -> dict:
        """
        Retrieves a location by its ID.
        """
        logger.info("Retrieving location by ID: %d", location_id)
        location = cls.query.filter_by(id=location_id).first()
        if not location:
            logger.error("Location with ID %s not found", location_id)
            raise ValueError(f"Location {location_id} not found.")
        return location

    @classmethod
    def get_all_locations(cls) -> list[dict]:
        """
        Retrieves all locations from the database.
        """
        logger.info("Retrieving all locations.")
        locations = cls.query.all()
        return [asdict(location) for location in locations]
    
    @classmethod
    def get_weather(self) -> dict:
        """
        Fetches weather forecast for this location using its latitude and longitude.

        Returns:
            dict: Weather forecast data.
        """
        try:
            forecast_data = fetch_forecast(self.latitude, self.longitude)
            return forecast_data
        except Exception as e:
            logger.error("Error fetching forecast for location %s: %s", self.city, str(e))
            raise

    def to_dict(self) -> dict:
        """
        Converts the Location instance into a dictionary.
        """
        return {
            "id": self.id,
            "city": self.city,
            "latitude": self.latitude,
            "longitude": self.longitude
        }
