import requests
import streamlit as st
from streamlit.runtime.caching import cache_data
from app.config import get_api_key


@cache_data(ttl=3600)
def get_sunlight_hours(city: str) -> float:
    """Return approximate average sunlight hours for an Indian city."""
    city_sunlight = {
        'delhi': 6.5,
        'mumbai': 6.0,
        'bengaluru': 6.2,
        'hyderabad': 6.3,
        'chennai': 6.1,
        'kolkata': 5.8,
        'pune': 6.4,
        'ahmedabad': 6.6,
        'jaipur': 6.7,
        'surat': 6.5,
    }
    return city_sunlight.get((city or '').lower().strip(), 5.5)


@cache_data(ttl=3600)
def geocode_city(city: str):
    """Resolve a city name to (lat, lon) using OpenWeather Geocoding API. Returns None on failure."""
    try:
        api_key = get_api_key()
        encoded_city = requests.utils.quote(city)
        geo_url = f"https://api.openweathermap.org/geo/1.0/direct?q={encoded_city}&limit=1&appid={api_key}"
        resp = requests.get(geo_url, timeout=10)
        if resp.status_code == 200:
            arr = resp.json() or []
            if isinstance(arr, list) and len(arr) > 0:
                lat = arr[0].get('lat')
                lon = arr[0].get('lon')
                if lat is not None and lon is not None:
                    return lat, lon
        return None
    except Exception:
        return None


def _shape_weather_payload(data, city: str):
    """Extract and shape OpenWeather response into our dict."""
    # Prefer dynamic day length from API (sunrise/sunset) if available; fallback to city mapping
    try:
        sys_block = data.get('sys') or {}
        sunrise = sys_block.get('sunrise')
        sunset = sys_block.get('sunset')
        if isinstance(sunrise, (int, float)) and isinstance(sunset, (int, float)) and sunset > sunrise:
            sunlight_hours = max(0.0, (float(sunset) - float(sunrise)) / 3600.0)
        else:
            sunlight_hours = get_sunlight_hours(city)
    except Exception:
        sunlight_hours = get_sunlight_hours(city)

    return {
        'temperature': data['main']['temp'],
        'humidity': data['main']['humidity'],
        'wind_speed': data['wind']['speed'],
        'clouds': data['clouds']['all'],
        'description': data['weather'][0]['description'],
        'icon': data['weather'][0]['icon'],
        'sunlight_hours': sunlight_hours,
    }


def get_weather_data(city: str):
    """Fetch current weather for a city from OpenWeatherMap with robust error handling and geocoding fallback."""
    try:
        city = (city or '').strip()
        if not city:
            st.error("❌ Please enter a city name")
            return None

        api_key = get_api_key()
        # First try querying by city name
        encoded_city = requests.utils.quote(city)
        url = f"https://api.openweathermap.org/data/2.5/weather?q={encoded_city}&appid={api_key}&units=metric"

        response = requests.get(url, timeout=10)
        data = response.json()

        # If city not found, try geocoding fallback
        if response.status_code != 200:
            error_msg = (data.get('message') if isinstance(data, dict) else None) or 'Unknown error'
            if 'city not found' in error_msg.lower():
                coords = geocode_city(city)
                if coords:
                    lat, lon = coords
                    url_latlon = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
                    resp2 = requests.get(url_latlon, timeout=10)
                    if resp2.status_code == 200:
                        try:
                            return _shape_weather_payload(resp2.json(), city)
                        except (KeyError, IndexError, TypeError):
                            st.error("❌ Error: Unexpected API response format")
                            return None
                # No coords found
                st.error("❌ City not found. Try entering a larger city or include country code (e.g., 'Paris, FR').")
                return None
            else:
                st.error(f"❌ Error: {error_msg}")
                return None

        # Success on first try
        try:
            return _shape_weather_payload(data, city)
        except (KeyError, IndexError, TypeError):
            st.error("❌ Error: Unexpected API response format")
            return None

    except requests.exceptions.RequestException:
        st.error("❌ Could not connect to weather service. Please check your internet connection.")
        return None
    except Exception:
        st.error("❌ Error processing weather data. Please try again.")
        return None
