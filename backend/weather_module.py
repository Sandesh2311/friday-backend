import os
import requests


def _format_weather_text(data, source):
    if source == "weatherapi":
        location = data["location"]["name"]
        region = data["location"]["region"]
        country = data["location"]["country"]

        temp = data["current"]["temp_c"]
        feels_like = data["current"]["feelslike_c"]
        humidity = data["current"]["humidity"]
        wind = data["current"]["wind_kph"]
        condition = data["current"]["condition"]["text"]

        return (
            f"🌤 Weather in {location}, {region}, {country}\n\n"
            f"🌡 Temperature : {temp}°C\n"
            f"🤗 Feels Like : {feels_like}°C\n"
            f"☁ Condition : {condition}\n"
            f"💧 Humidity : {humidity}%\n"
            f"🌬 Wind : {wind} km/h"
        )

    location = data["nearest_area"][0]["areaName"][0]["value"]
    region = data["nearest_area"][0]["region"][0]["value"]
    country = data["nearest_area"][0]["country"][0]["value"]

    current = data["current_condition"][0]
    temp = current.get("temp_C", current.get("temp_F", "N/A"))
    feels_like = current.get("FeelsLikeC", current.get("FeelsLikeF", "N/A"))
    humidity = current.get("humidity", "N/A")
    wind = current.get("windspeedKmph", "N/A")
    condition = current.get("weatherDesc", [{}])[0].get("value", "Unknown")

    return (
        f"🌤 Weather in {location}, {region}, {country}\n\n"
        f"🌡 Temperature : {temp}°C\n"
        f"🤗 Feels Like : {feels_like}°C\n"
        f"☁ Condition : {condition}\n"
        f"💧 Humidity : {humidity}%\n"
        f"🌬 Wind : {wind} km/h"
    )


def get_weather(city="Mumbai"):
    """
    Get current weather using WeatherAPI.com when a key is available, otherwise fall back to wttr.in.
    """

    api_key = os.getenv("WEATHER_API_KEY")
    city = city.strip() or "Mumbai"

    try:
        if api_key:
            url = "https://api.weatherapi.com/v1/current.json"
            params = {"key": api_key, "q": city, "aqi": "no"}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return {
                "type": "text",
                "data": _format_weather_text(data, "weatherapi")
            }

        fallback_url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(fallback_url, timeout=10)
        response.raise_for_status()
        data = response.json()

        return {
            "type": "text",
            "data": _format_weather_text(data, "wttr")
        }

    except requests.exceptions.HTTPError:
        try:
            error = response.json().get("error", {}).get("message", "Unknown error")
        except Exception:
            error = "Unable to fetch weather."

        return {
            "type": "text",
            "data": f"❌ Weather API Error: {error}"
        }

    except requests.exceptions.RequestException:
        return {
            "type": "text",
            "data": "⚠ Unable to connect to the Weather service."
        }

    except Exception as e:
        return {
            "type": "text",
            "data": f"⚠ Unexpected Error: {str(e)}"
        }