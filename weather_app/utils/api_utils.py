import requests
import os
import logging
from weather_app.utils.logger import configure_logger

# Configure logger for this module
logger = logging.getLogger(__name__)
configure_logger(logger)

# Base URLs for the APIs
BASE_URL_AIR_QUALITY = "http://api.openweathermap.org/data/3.0/air_pollution"
BASE_URL_WEATHER = "http://api.openweathermap.org/data/3.0/onecall"

# API Key from environment variables
API_KEY = os.getenv("API_KEY")

def fetch_air_quality_data(latitude: float, longitude: float) -> dict:
    """
    Fetches current air quality data for a given location.

    Args:
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.

    Returns:
        dict: Air quality data including AQI and pollutants.

    Raises:
        Exception: If the API call fails.
    """
    url = f"{BASE_URL_AIR_QUALITY}?lat={latitude}&lon={longitude}&appid={API_KEY}"
    logger.info("Fetching air quality data from URL: %s", url)

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Extract relevant fields
        aqi = data["list"][0]["main"]["aqi"]
        pollutants = data["list"][0]["components"]
        return {"aqi": aqi, "pollutants": pollutants}
    except requests.RequestException as e:
        logger.error("Error fetching air quality data: %s", str(e))
        raise Exception("Failed to fetch air quality data.") from e

def fetch_historical_data(latitude: float, longitude: float) -> dict:
    """
    Fetches historical weather data for a given location.

    Args:
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.

    Returns:
        dict: Historical weather data including temperature, AQI, etc.

    Raises:
        Exception: If the API call fails.
    """
    # The historical data endpoint might require a timestamp; here, it's assumed to be part of the API.
    url = f"{BASE_URL_WEATHER}/timemachine?lat={latitude}&lon={longitude}&appid={API_KEY}"
    logger.info("Fetching historical weather data from URL: %s", url)

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error("Error fetching historical weather data: %s", str(e))
        raise Exception("Failed to fetch historical weather data.") from e

def fetch_forecast(latitude: float, longitude: float) -> dict:
    """
    Fetches weather forecast for a given location.

    Args:
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.

    Returns:
        dict: Forecast data including temperature, precipitation, etc.

    Raises:
        Exception: If the API call fails.
    """
    url = f"{BASE_URL_WEATHER}?lat={latitude}&lon={longitude}&exclude=current,minutely,hourly,alerts&appid={API_KEY}"
    logger.info("Fetching weather forecast data from URL: %s", url)

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error("Error fetching weather forecast data: %s", str(e))
        raise Exception("Failed to fetch weather forecast data.") from e
