
import requests
import os
import pytz 
import json
from datetime import datetime
from typing import Optional, Dict, Tuple, Any
from dotenv import load_dotenv
from timezonefinder import TimezoneFinder
import streamlit as st
import tzlocal

# Initialize TimezoneFinder once
tf = TimezoneFinder()

DEFAULT_SETTINGS_FILE = 'default_settings.json'

def initialize_session_state():
    """Initialize all session state variables needed for the Streamlit app."""
    default_states = {
        'displayed_weather_info': None,
        'last_queried_city': None,
        'last_queried_coords': None,
        'default_city': load_default_city(),
        'ai_question': "",
        'ai_response': None,
        'forecast_data': None,
        'show_forecast': False
    }
    
    for key, default_value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def update_weather_display(weather_data: dict) -> None:
    """Update session state with new weather data and display it."""
    if weather_data:
        # Parse and store display data into session state
        st.session_state.displayed_weather_info = {
            "city": weather_data.get("name"),
            "country": weather_data.get("sys", {}).get("country"),
            "temperature": weather_data.get("main", {}).get("temp"),
            "feels_like": weather_data.get("main", {}).get("feels_like"),
            "humidity": weather_data.get("main", {}).get("humidity"),
            "weather_description": weather_data.get("weather", [])[0].get("description").capitalize() 
                if weather_data.get("weather") else "N/A",
            "weather_icon": weather_data.get("weather", [])[0].get("icon")
                if weather_data.get("weather") else "01d",
            "wind_speed": weather_data.get("wind", {}).get("speed")
        }
        
        # Update location data for time display
        st.session_state.last_queried_city = weather_data.get("name")
        lon = weather_data.get("coord", {}).get("lon")
        lat = weather_data.get("coord", {}).get("lat")
        st.session_state.last_queried_coords = (lat, lon) if lat is not None and lon is not None else None

def get_user_timezone() -> Tuple[str, bool]:
    """Get the user's timezone string"""
    try:
        return tzlocal.get_localzone().key, True
    except Exception:
        return "UTC", False

def display_time_info(user_local_tz_str: str):
    """Display time information in the sidebar."""
    if st.session_state.last_queried_coords:
        lat, lon = st.session_state.last_queried_coords
        formatted_user_time, formatted_location_time, location_tz_str = \
            get_times_for_location(user_local_tz_str, lat, lon)

        st.sidebar.markdown("<div style='font-family: Arial, sans-serif; font-size: 0.9em; color: #2E86C1; margin-bottom: 5px;'>Your Local Time</div>", unsafe_allow_html=True)
        st.sidebar.markdown(f"<div style='font-family: Arial, sans-serif; font-size: 0.85em; color: #333; margin-bottom: 15px;'>{formatted_user_time}</div>", unsafe_allow_html=True)

        if formatted_location_time:
            st.sidebar.markdown(f"<div style='font-family: Arial, sans-serif; font-size: 0.9em; color: #2E86C1; margin-bottom: 5px;'>Time in {st.session_state.last_queried_city}</div>", unsafe_allow_html=True)
            st.sidebar.markdown(f"<div style='font-family: Arial, sans-serif; font-size: 0.85em; color: #333; margin-bottom: 5px;'>{formatted_location_time}</div>", unsafe_allow_html=True)
            if location_tz_str:
                st.sidebar.markdown(f"<div style='font-family: Arial, sans-serif; font-size: 0.75em; color: #666; font-style: italic;'>(Timezone: {location_tz_str})</div>", unsafe_allow_html=True)
        else:
            st.sidebar.markdown("<div style='font-family: Arial, sans-serif; font-size: 0.9em; color: #2E86C1; margin-bottom: 5px;'>Time in City</div>", unsafe_allow_html=True)
            st.sidebar.markdown("<div style='font-family: Arial, sans-serif; font-size: 0.85em; color: #666; font-style: italic;'>Could not determine</div>", unsafe_allow_html=True)
    else:
        current_time_user_local = datetime.now(pytz.timezone(user_local_tz_str))
        st.sidebar.markdown("<div style='font-family: Arial, sans-serif; font-size: 0.9em; color: #2E86C1; margin-bottom: 5px;'>Your Local Time</div>", unsafe_allow_html=True)
        st.sidebar.markdown(f"<div style='font-family: Arial, sans-serif; font-size: 0.85em; color: #333; margin-bottom: 15px;'>{current_time_user_local.strftime('%A, %B %d, %Y, %I:%M %p %Z%z')}</div>", unsafe_allow_html=True)
        st.sidebar.markdown("<div style='font-family: Arial, sans-serif; font-size: 0.9em; color: #2E86C1; margin-bottom: 5px;'>Time in City</div>", unsafe_allow_html=True)
        st.sidebar.markdown("<div style='font-family: Arial, sans-serif; font-size: 0.85em; color: #666; font-style: italic;'>No city queried yet</div>", unsafe_allow_html=True)

def fetch_weather_api(endpoint: str, city_name: str, api_key: str) -> Optional[Dict[str, Any]]:
    """Generic function to fetch weather data from OpenWeatherMap API."""
    base_url = f"http://api.openweathermap.org/data/2.5/{endpoint}?"
    complete_url = f"{base_url}q={city_name}&appid={api_key}&units=metric"

    try:
        response = requests.get(complete_url)
        response.raise_for_status()
        data = response.json()

        if str(data.get("cod")) not in ["200", "201"]:
            print(f"API Error: {data.get('message', 'Unknown error')}")
            return None

        return data
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return None
    except ValueError as e:
        print(f"Data parsing error: {e}")
        return None

def get_weather_data(city_name: str, api_key: str) -> Optional[Dict[str, Any]]:
    """Fetch current weather data."""
    return fetch_weather_api("weather", city_name, api_key)

def get_weather_forecast(city_name: str, api_key: str) -> Optional[Dict[str, Any]]:
    """Fetch 5-day weather forecast data."""
    return fetch_weather_api("forecast", city_name, api_key)

def display_forecast(forecast_data: dict) -> None:
    """Display 5-day weather forecast."""
    if not forecast_data or 'list' not in forecast_data:
        return

    st.subheader("5-Day Weather Forecast")
    
    # Group forecast data by day
    daily_forecasts = {}
    for item in forecast_data['list']:
        date = datetime.fromtimestamp(item['dt']).date()
        if date not in daily_forecasts:
            daily_forecasts[date] = {
                'temp': [],
                'humidity': [],
                'description': [],
                'icon': []
            }
        daily_forecasts[date]['temp'].append(item['main']['temp'])
        daily_forecasts[date]['humidity'].append(item['main']['humidity'])
        daily_forecasts[date]['description'].append(item['weather'][0]['description'])
        daily_forecasts[date]['icon'].append(item['weather'][0]['icon'])

    # Display forecast cards in columns
    cols = st.columns(min(5, len(daily_forecasts)))  # Limit to 5 days
    for col, (date, data) in zip(cols, list(daily_forecasts.items())[:5]):  # Take only first 5 days
        with col:
            st.write(f"**{date.strftime('%A')}**")
            st.write(f"{date.strftime('%b %d')}")
            avg_temp = sum(data['temp']) / len(data['temp'])
            avg_humidity = sum(data['humidity']) / len(data['humidity'])
            most_common_desc = max(set(data['description']), key=data['description'].count)
            icon = max(set(data['icon']), key=data['icon'].count)
            
            # Display weather icon
            icon_url = f"http://openweathermap.org/img/wn/{icon}@2x.png"
            st.image(icon_url, width=50)
            
            st.metric("Temp", f"{avg_temp:.1f}°C")
            st.metric("Humidity", f"{avg_humidity:.0f}%")
            st.caption(most_common_desc.capitalize())

TIME_FORMAT = "%A, %B %d, %Y, %I:%M %p %Z%z"

def format_time_for_zone(tz: Optional[pytz.timezone], reference_time: Optional[datetime] = None) -> str:
    """Format time for a specific timezone."""
    try:
        if not tz:
            raise pytz.UnknownTimeZoneError("No timezone provided")
            
        time = reference_time.astimezone(tz) if reference_time else datetime.now(tz)
        return time.strftime(TIME_FORMAT)
    except pytz.UnknownTimeZoneError:
        return "Could not determine time (invalid timezone)"

def get_times_for_location(user_local_tz_str: str, location_lat: float, location_lon: float) -> Tuple[str, Optional[str], Optional[str]]:
    """Calculate times for user's local timezone and specified location."""
    # Get user's timezone
    try:
        user_tz = pytz.timezone(user_local_tz_str)
        user_time = datetime.now(user_tz)
        formatted_user_time = format_time_for_zone(user_tz)
    except pytz.UnknownTimeZoneError:
        return ("Could not determine local time", None, None)

    # Get location's timezone
    if None in (location_lat, location_lon):
        return (formatted_user_time, "Location coordinates not available", None)

    location_tz_str = tf.timezone_at(lng=location_lon, lat=location_lat)
    if not location_tz_str:
        return (formatted_user_time, "Could not determine location timezone", None)

    try:
        location_tz = pytz.timezone(location_tz_str)
        formatted_location_time = format_time_for_zone(location_tz, user_time)
        return (formatted_user_time, formatted_location_time, location_tz_str)
    except pytz.UnknownTimeZoneError:
        return (formatted_user_time, f"Invalid timezone: {location_tz_str}", None)

def load_default_city() -> Optional[str]:
    """
    Loads the default city name from the DEFAULT_SETTINGS_FILE.
    Returns the city name if found, otherwise None.
    """
    if os.path.exists(DEFAULT_SETTINGS_FILE):
        try:
            with open(DEFAULT_SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                return settings.get('default_city')
        except (json.JSONDecodeError, KeyError):
            print(f"Warning: Could not read default city from {DEFAULT_SETTINGS_FILE}.")
            return None
    return None

def save_default_city(city_name: str):
    """
    Saves the provided city name as the default city in the DEFAULT_SETTINGS_FILE.
    """
    settings = {'default_city': city_name}
    try:
        with open(DEFAULT_SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
        print(f"Default city '{city_name}' saved to {DEFAULT_SETTINGS_FILE}")
    except IOError as e:
        print(f"Error saving default city to {DEFAULT_SETTINGS_FILE}: {e}")