import pytest
from unittest.mock import Mock
from weather_app.utils.api_utils import fetch_air_quality_data, fetch_historical_data, fetch_forecast

@pytest.fixture
def mock_requests_get(mocker):
    """Mocks the requests.get response."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "list": [
            {
                "main": {"aqi": 2},
                "components": {"pm10": 10, "pm2_5": 5},
            }
        ]
    }
    mocker.patch("requests.get", return_value=mock_response)
    return mock_response

def test_fetch_air_quality_data(mock_requests_get):
    """Test fetching air quality data."""
    data = fetch_air_quality_data(40.7128, -74.0060)
    assert data["aqi"] == 2
    assert data["pollutants"]["pm10"] == 10

def test_fetch_historical_data(mock_requests_get):
    """Test fetching historical weather data."""
    data = fetch_historical_data(40.7128, -74.0060)
    assert "list" in data

def test_fetch_forecast(mock_requests_get):
    """Test fetching forecast data."""
    data = fetch_forecast(40.7128, -74.0060)
    assert "list" in data
