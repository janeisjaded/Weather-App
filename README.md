# Weather-App
# Overview:
The Weather App is a Flask-based application that provides weather data for cities worldwide using the OpenWeather API. It includes functionality to manage a user's collection of favorite locations and supports CRUD operations for favorites.

# Features: 
Weather Data Retrieval: Get real-time weather forecasts and historical data for any location. Air Quality Monitoring: Fetch current air quality data, including AQI and pollutant details. User Authentication: Secure login system to manage personalized features. Favorites Management: Add, view, and remove favorite locations. Database Health Checks: Verify database connectivity and table existence.

API Endpoints This application exposes RESTful API endpoints for interacting with the weather services and managing user data.

Routes and Their Descriptions Health Check Routes

Health Check Route Name: /api/health Request Type: GET Purpose: Verifies that the service is running. Response Format: { "status": "healthy" } Example: curl http://localhost:5000/api/health

Database Check Route Name: /api/db-check Request Type: GET Purpose: Checks database connectivity and ensures required tables exist. Response Format: { "database_status": "healthy" } Example: curl http://localhost:5000/api/db-check Location Management Routes

Add Location Route Name: /api/location Request Type: POST Purpose: Adds a new location to the database. Request Format: { "city": "London", "latitude": 51.5074, "longitude": -0.1278 } Response Format: { "status": "success", "location": { "id": 1, "city": "London", "latitude": 51.5074, "longitude": -0.1278 } } Example: curl -X POST -H "Content-Type: application/json" -d '{"city": "London", "latitude": 51.5074, "longitude": -0.1278}' http://localhost:5000/api/location

Get Location by ID Route Name: /api/location/ Request Type: GET Purpose: Retrieves details for a specific location by ID. Response Format: { "id": 1, "city": "London", "latitude": 51.5074, "longitude": -0.1278 } Example: curl http://localhost:5000/api/location/1 Weather Data Routes

Fetch Air Quality Data Route Name: /api/weather/air-quality/ Request Type: GET Purpose: Retrieves current air quality data for a location by ID. Response Format: { "aqi": 2, "pollutants": { "co": 0.3, "no2": 5.2, "o3": 0.9 } } Example: curl http://localhost:5000/api/weather/air-quality/1

Fetch Historical Weather Data Route Name: /api/weather/historical/ Request Type: GET Purpose: Retrieves historical weather data for a location by ID. Response Format: { "historical_data": { "temperature": 15.2, "humidity": 78 } } Example: curl http://localhost:5000/api/weather/historical/1

Fetch Weather Forecast Route Name: /api/weather/forecast/ Request Type: GET Purpose: Retrieves a 7-day weather forecast for a location by ID. Response Format: { "forecast": { "day1": {"temp": 14, "condition": "Sunny"}, "day2": {"temp": 15, "condition": "Cloudy"} } } Example: curl http://localhost:5000/api/weather/forecast/1 Favorites Management Routes

Get All Favorites Route Name: /api/favorites Request Type: GET Purpose: Retrieves all favorite locations for the logged-in user. Response Format: [ { "id": 1, "city": "London", "latitude": 51.5074, "longitude": -0.1278 } ] Example: curl -H "User-ID: 123" http://localhost:5001/api/favorites

Add to Favorites Route Name: /api/favorites Request Type: POST Purpose: Adds a location to the user's favorites. Request Format: { "city": "London", "latitude": 51.5074, "longitude": -0.1278 } Response Format: { "status": "success", "message": "Location added to favorites" } Example: curl -X POST -H "Content-Type: application/json" -d '{"city": "London", "latitude": 51.5074, "longitude": -0.1278}' http://localhost:5001/api/favorites

Remove from Favorites Route Name: /api/favorites Request Type: DELETE Purpose: Removes a location from the user's favorites by ID. Request Format: { "location_id": 1 } Response Format: { "status": "success", "message": "Location removed from favorites" } Example: curl -X DELETE -H "Content-Type: application/json" -d '{"location_id": 1}' http://localhost:5001/api/favorites

Setup Instructions Environment Variables: Set up an .env file with the following: API_KEY=6ac72ba90c795f7036e775e9b1cc90cf Running the App: Clone the repository: git clone https://github.com/eshaaw/cs411-finalproject.git cd weather-app

Build and run the Docker container: docker build -t weather-app . docker run -p 5000:5000 weather-app Access the app at http://localhost:5001.
