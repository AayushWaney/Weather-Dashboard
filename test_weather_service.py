from service.weather_service import get_weather_data
import os
from dotenv import load_dotenv


load_dotenv()


def test_get_weather_data_success():
    """Test that a valid city returns successful weather data."""
    api_key = os.getenv("API_KEY")
    result = get_weather_data(api_key, city_name="London")

    assert result["success"] is True
    assert "temp" in result
    assert "aqi" in result


def test_get_weather_data_invalid_city():
    """Test that error handling successfully catches typos."""
    api_key = os.getenv("API_KEY")
    result = get_weather_data(api_key, city_name="FakeCity12345")

    assert result["success"] is False
    assert "City not found" in result["error"]