from weather_app.utils.db import db
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

class FavoritesModel(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)

    def __init__(self, user_id: int, location_id: int):
        self.user_id = user_id
        self.location_id = location_id

    @classmethod
    def get_favorites_by_user_id(cls, user_id: int) -> list:
        """
        Retrieves a list of favorite location IDs for a user by user_id.

        Args:
            user_id (int): The ID of the user whose favorites are being retrieved.

        Raises:
            ValueError: If no favorites are found for the user.

        Returns:
            list: A list of favorite location IDs for the user.
        """
        try:
            logger.info("Fetching favorites for user ID %d", user_id)
            favorites = cls.query.filter_by(user_id=user_id).all()

            if not favorites:
                logger.warning("No favorites found for user ID %d", user_id)
                raise ValueError("Favorites list is empty")

            favorite_ids = [favorite.location_id for favorite in favorites]
            logger.info("Favorites retrieved: %s", favorite_ids)
            return favorite_ids
        except SQLAlchemyError as e:
            logger.error("Database error while retrieving favorites: %s", str(e))
            raise

    @classmethod
    def add_favorite(cls, user_id: int, location_id: int) -> None:
        """
        Adds a location to the user's list of favorites.

        Args:
            user_id (int): The ID of the user.
            location_id (int): The ID of the location to be added.

        Raises:
            ValueError: If the favorite already exists.
        """
        try:
            logger.info("Adding location ID %d to favorites for user ID %d", location_id, user_id)

            # Check if the favorite already exists
            existing_favorite = cls.query.filter_by(user_id=user_id, location_id=location_id).first()
            if existing_favorite:
                logger.warning("Favorite already exists for user ID %d and location ID %d", user_id, location_id)
                raise ValueError("Favorite already exists")

            new_favorite = cls(user_id=user_id, location_id=location_id)
            db.session.add(new_favorite)
            db.session.commit()
            logger.info("Favorite added successfully")
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error("Database error while adding favorite: %s", str(e))
            raise

    @classmethod
    def remove_favorite(cls, user_id: int, location_id: int) -> None:
        """
        Removes a location from the user's list of favorites.

        Args:
            user_id (int): The ID of the user.
            location_id (int): The ID of the location to be removed.

        Raises:
            ValueError: If the favorite does not exist.
        """
        try:
            logger.info("Removing location ID %d from favorites for user ID %d", location_id, user_id)

            favorite = cls.query.filter_by(user_id=user_id, location_id=location_id).first()
            if not favorite:
                logger.warning("Favorite does not exist for user ID %d and location ID %d", user_id, location_id)
                raise ValueError("Favorite does not exist")

            db.session.delete(favorite)
            db.session.commit()
            logger.info("Favorite removed successfully")
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error("Database error while removing favorite: %s", str(e))
            raise
