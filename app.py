from flask import Flask, jsonify, request, make_response
from dotenv import load_dotenv

from config import ProductionConfig

from werkzeug.exceptions import BadRequest, Unauthorized

from config import ProductionConfig
from weather_app.models.user_model import Users
from weather_app.models.location_model import Location
from weather_app.models.favorites_model import FavoritesModel
from weather_app.utils.api_utils import fetch_air_quality_data, fetch_forecast, fetch_historical_data
from weather_app.utils.sql_utils import check_database_connection, check_table_exists
from weather_app.utils.db import db

# Load environment variables
load_dotenv()

def create_app(config_class=ProductionConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)  # Initialize db with app
    with app.app_context():
        db.create_all()  # Recreate all tables

    ####################################################
    #
    # Health Checks
    #
    ####################################################

    @app.route('/api/health', methods=['GET'])
    def healthcheck():
        """
        Health check route to verify the service is running.
        """
        app.logger.info('Health check')
        return make_response(jsonify({'status': 'healthy'}), 200)

    @app.route('/api/db-check', methods=['GET'])
    def db_check():
        """
        Check if the database is reachable.
        """
        try:
            app.logger.info("Checking database connection...")
            check_database_connection()
            return make_response(jsonify({"database_status": "healthy"}), 200)
        except Exception as e:
            app.logger.error(f"Database check failed: {e}")
            return make_response(jsonify({"error": str(e)}), 500)

    ####################################################
    #
    # User Management
    #
    ####################################################

    @app.route('/api/create-user', methods=['POST'])
    def create_user():
        """
        Create a new user.
        """
        try:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return make_response(jsonify({'error': 'Username and password are required'}), 400)

            Users.create_user(username, password)
            app.logger.info(f"User {username} created successfully.")
            return make_response(jsonify({'status': 'success', 'username': username}), 201)
        except ValueError as e:
            app.logger.error(f"Error creating user: {e}")
            return make_response(jsonify({'error': str(e)}), 400)
        except Exception as e:
            app.logger.error(f"Unexpected error: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/delete-user/<string:username>', methods=['DELETE'])
    def delete_user(username):
        """
        Delete a user by username.
        """
        try:
            Users.delete_user(username)
            app.logger.info(f"User {username} deleted successfully.")
            return make_response(jsonify({'status': 'success', 'username': username}), 200)
        except ValueError as e:
            app.logger.error(f"Error deleting user: {e}")
            return make_response(jsonify({'error': str(e)}), 400)
        except Exception as e:
            app.logger.error(f"Unexpected error: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    ####################################################
    #
    # Location Management
    #
    ####################################################

    @app.route('/api/create-location', methods=['POST'])
    def create_location():
        """
        Create a new location.
        """
        try:
            data = request.get_json()
            city = data.get('city')
            latitude = data.get('latitude')
            longitude = data.get('longitude')

            if not city or latitude is None or longitude is None:
                return make_response(jsonify({'error': 'City, latitude, and longitude are required'}), 400)

            location = Location.create_location(city, latitude, longitude)
            app.logger.info(f"Location created: {location.to_dict()}")
            return make_response(jsonify({'status': 'success', 'location': location.to_dict()}), 201)
        except Exception as e:
            app.logger.error(f"Error creating location: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/get-location/<int:location_id>', methods=['GET'])
    def get_location(location_id):
        """
        Retrieve a location by ID.
        """
        try:
            location = Location.get_location_by_id(location_id)
            return make_response(jsonify({'status': 'success', 'location': location.to_dict()}), 200)
        except Exception as e:
            app.logger.error(f"Error retrieving location: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    ####################################################
    #
    # Weather and Air Quality
    #
    ####################################################

    @app.route('/api/get-weather/<int:location_id>', methods=['GET'])
    def get_weather(location_id):
        """
        Get weather forecast for a location.
        """
        try:
            location = Location.get_location_by_id(location_id)
            forecast = location.get_weather()
            return make_response(jsonify({'status': 'success', 'forecast': forecast}), 200)
        except Exception as e:
            app.logger.error(f"Error fetching forecast: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/get-air-quality/<int:location_id>', methods=['GET'])
    def get_air_quality(location_id):
        """
        Get air quality for a location.
        """
        try:
            location = Location.get_location_by_id(location_id)
            air_quality = location.get_air_quality()
            return make_response(jsonify({'status': 'success', 'air_quality': air_quality}), 200)
        except Exception as e:
            app.logger.error(f"Error fetching air quality: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    ####################################################
    #
    # Favorites Management
    #
    ####################################################

    @app.route('/api/add-favorite', methods=['POST'])
    def add_favorite():
        """
        Add a location to a user's favorites.
        """
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            location_id = data.get('location_id')

            if not user_id or not location_id:
                return make_response(jsonify({'error': 'User ID and Location ID are required'}), 400)

            # Add the favorite
            FavoritesModel.add_favorite(user_id, location_id)
            return make_response(jsonify({'status': 'success', 'message': 'Favorite added successfully'}), 200)
        except ValueError as e:
            app.logger.error(f"Error adding favorite: {e}")
            return make_response(jsonify({'error': str(e)}), 400)
        except Exception as e:
            app.logger.error(f"Unexpected error adding favorite: {e}")
            return make_response(jsonify({'error': 'Internal server error'}), 500)


    @app.route('/api/get-favorites/<int:user_id>', methods=['GET']) 
    def get_favorites(user_id):
        """
        Get all favorite locations for a user.
        """
        try:
            # Fetch the favorite location IDs
            favorite_location_ids = FavoritesModel.get_favorites_by_user_id(user_id)

            # Retrieve location details for each favorite (optional)
            favorite_locations = [
                Location.get_location_by_id(location_id).to_dict()
                for location_id in favorite_location_ids
            ]

            return make_response(jsonify({'status': 'success', 'favorites': favorite_locations}), 200)
        except ValueError as e:
            app.logger.error(f"Error retrieving favorites: {e}")
            return make_response(jsonify({'error': str(e)}), 404)
        except Exception as e:
            app.logger.error(f"Unexpected error retrieving favorites: {e}")
            return make_response(jsonify({'error': 'Internal server error'}), 500)

    @app.route('/api/remove-favorite/<int:user_id>/<int:location_id>', methods=['DELETE'])
    def remove_favorite(user_id, location_id):
        """
        Remove a location from a user's favorites.
        """
        try:
            FavoritesModel.remove_favorite(user_id, location_id)
            return make_response(jsonify({'status': 'success', 'message': 'Favorite removed successfully'}), 200)
        except ValueError as e:
            app.logger.error(f"Error removing favorite: {e}")
            return make_response(jsonify({'error': str(e)}), 404)
        except Exception as e:
            app.logger.error(f"Unexpected error removing favorite: {e}")
            return make_response(jsonify({'error': 'Internal server error'}), 500)
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5001)
