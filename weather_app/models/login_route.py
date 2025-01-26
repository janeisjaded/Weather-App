from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from weather_app.models.user_model import Users
from weather_app.utils.sql_utils import get_db_connection

# Define a Blueprint for authentication-related routes
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticates a user by checking the provided password against the stored hash.

    Request JSON:
    {
        "username": "user1",
        "password": "password123"
    }

    Response JSON (on success):
    {
        "message": "Login successful"
    }

    Response JSON (on failure):
    {
        "error": "Invalid username or password"
    }
    """
    data = request.get_json()

    # Validate input data
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Username and password are required"}), 400

    username = data['username']
    password = data['password']

    try:
        # Fetch the user from the database
        with get_db_connection() as conn:
            user = Users.get_id_by_username(username, conn)
            if not user:
                return jsonify({"error": "Invalid username or password"}), 401

            # Check the provided password against the stored hash
            if check_password_hash(user.password_hash, password):
                return jsonify({"message": "Login successful"}), 200
            else:
                return jsonify({"error": "Invalid username or password"}), 401

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
