import unittest
from unittest.mock import patch

from backend.weather_module import get_weather


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception("HTTP error")

    def json(self):
        return self._payload


class WeatherModuleTests(unittest.TestCase):
    def test_get_weather_falls_back_without_api_key(self):
        payload = {
            "current_condition": [
                {
                    "temp_C": "32",
                    "FeelsLikeC": "35",
                    "humidity": "74",
                    "windspeedKmph": "18",
                    "weatherDesc": [{"value": "Sunny"}],
                }
            ],
            "nearest_area": [
                {
                    "areaName": [{"value": "Mumbai"}],
                    "region": [{"value": "Maharashtra"}],
                    "country": [{"value": "India"}],
                }
            ],
        }

        with patch.dict("os.environ", {}, clear=True):
            with patch("backend.weather_module.requests.get", return_value=FakeResponse(payload)) as mock_get:
                result = get_weather("Mumbai")

        self.assertEqual(result["type"], "text")
        self.assertIn("Weather in Mumbai", result["data"])
        self.assertIn("32°C", result["data"])
        self.assertIn("Sunny", result["data"])
        mock_get.assert_called_once()


if __name__ == "__main__":
    unittest.main()
