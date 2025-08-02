
import requests
import os
import pytz 
import json
from datetime import datetime
from dotenv import load_dotenv
from timezonefinder import TimezoneFinder
import streamlit as st
import tzlocal

# Initialize TimezoneFinder once for efficiency
tf = TimezoneFinder()

DEFAULT_SETTINGS_FILE = 'default_settings.json'

def initialize_session_state():
    """Initialize all session state variables needed for the Streamlit app."""
    if 'displayed_weather_info' not in st.session_state:
        st.session_state.displayed_weather_info = None
    if 'last_queried_city' not in st.session_state:
        st.session_state.last_queried_city = None
    if 'last_queried_coords' not in st.session_state:
        st.session_state.last_queried_coords = None
    if 'default_city' not in st.session_state:
        st.session_state.default_city = load_default_city()
    # Initialize AI-related session state variables
    if 'ai_question' not in st.session_state:
        st.session_state.ai_question = ""
    if 'ai_response' not in st.session_state:
        st.session_state.ai_response = None
    # Initialize forecast-related session state
    if 'forecast_data' not in st.session_state:
        st.session_state.forecast_data = None
    if 'show_forecast' not in st.session_state:
        st.session_state.show_forecast = False

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
            "wind_speed": weather_data.get("wind", {}).get("speed")
        }
        
        # Update location data for time display
        st.session_state.last_queried_city = weather_data.get("name")
        lon = weather_data.get("coord", {}).get("lon")
        lat = weather_data.get("coord", {}).get("lat")
        st.session_state.last_queried_coords = (lat, lon) if lat is not None and lon is not None else None

def get_user_timezone() -> tuple[str, bool]:
    """Get the user's timezone string and whether it was successfully determined."""
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

        st.sidebar.markdown(f"**Your Local Time:**\n{formatted_user_time}")

        if formatted_location_time:
            st.sidebar.markdown(f"**Time in {st.session_state.last_queried_city}:**\n{formatted_location_time}")
            if location_tz_str:
                st.sidebar.caption(f"(Timezone: {location_tz_str})")
        else:
            st.sidebar.markdown("**Time in City:**\n_Could not determine_")
    else:
        current_time_user_local = datetime.now(pytz.timezone(user_local_tz_str))
        st.sidebar.markdown(f"**Your Local Time:**\n{current_time_user_local.strftime('%A, %B %d, %Y, %I:%M %p %Z%z')}")
        st.sidebar.markdown("**Time in City:**\n_No city queried yet_")

def get_weather_data(city_name: str, api_key: str) -> dict | None:

    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}q={city_name}&appid={api_key}&units=metric"

    try:
        response = requests.get(complete_url)
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        # Check if the city was not found
        if data.get("cod") == "404":
            print(f"Error: City '{city_name}' not found.")
            return None
        elif data.get("cod") != 200:
             print(f"Error: API returned code {data.get('cod', 'N/A')}. Message: {data.get('message', 'No message.')}")
             return None


        return data
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while making the API request: {e}")
        return None
    except ValueError as e: # For JSON decoding errors
        print(f"Error decoding JSON response: {e}")
        return None

def get_weather_forecast(city_name: str, api_key: str) -> dict | None:
    """Fetch 5-day weather forecast data."""
    base_url = "http://api.openweathermap.org/data/2.5/forecast?"
    complete_url = f"{base_url}q={city_name}&appid={api_key}&units=metric"

    try:
        response = requests.get(complete_url)
        response.raise_for_status()
        data = response.json()

        if data.get("cod") != "200":
            print(f"Error: {data.get('message', 'Unknown error')}")
            return None

        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching forecast: {e}")
        return None

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

def display_weather(weather_data: dict):
    """
    Displays relevant weather information from the fetched data.

    Args:
        weather_data (dict): A dictionary containing weather data.
    """
    if weather_data:
        city = weather_data.get("name")
        country = weather_data.get("sys", {}).get("country")
        temperature = weather_data.get("main", {}).get("temp")
        feels_like = weather_data.get("main", {}).get("feels_like")
        humidity = weather_data.get("main", {}).get("humidity")
        weather_description = weather_data.get("weather", [])[0].get("description") if weather_data.get("weather") else "N/A"
        wind_speed = weather_data.get("wind", {}).get("speed")

        print(f"\n--- Weather in {city}, {country} ---")
        print(f"Temperature: {temperature}°C")
        print(f"Feels like: {feels_like}°C")
        print(f"Conditions: {weather_description.capitalize()}")
        print(f"Humidity: {humidity}%")
        print(f"Wind Speed: {wind_speed} m/s")
    else:
        print("Could not display weather data.")

def get_times_for_location(user_local_tz_str: str, location_lat: float, location_lon: float) -> tuple[str, str | None, str | None]:
    """
    Calculates and formats current times for the user's local timezone and the specified location's timezone.

    Args:
        user_local_tz_str (str): The IANA timezone string for the user's local system (e.g., 'America/New_York').
        location_lat (float): Latitude of the location.
        location_lon (float): Longitude of the location.

    Returns:
        tuple[str, str | None, str | None]:
            - Formatted string of user's current local time.
            - Formatted string of location's current time (or None if timezone not found).
            - The IANA timezone string of the location (or None if not found).
    """
    time_format = "%A, %B %d, %Y, %I:%M %p %Z%z" # Added %Z%z to show timezone abbreviation and offset

    #User's current local time
    try:
        user_tz = pytz.timezone(user_local_tz_str)
        user_time = datetime.now(user_tz)
        formatted_user_time = user_time.strftime(time_format)
    except pytz.UnknownTimeZoneError:
        formatted_user_time = "Could not determine your local time (invalid timezone)."
        user_tz = None # Indicate that user_tz could not be set

    #Location's current time
    formatted_location_time = None
    location_tz_str = None

    if location_lat is not None and location_lon is not None:
        location_tz_str = tf.timezone_at(lng=location_lon, lat=location_lat)
        if location_tz_str:
            try:
                location_tz = pytz.timezone(location_tz_str)
                # If we have a valid user_tz, convert from that to location_tz
                if user_tz:
                    location_time = user_time.astimezone(location_tz)
                else: # Fallback if user_tz detection failed, use UTC as reference
                    location_time = datetime.now(pytz.utc).astimezone(location_tz)
                formatted_location_time = location_time.strftime(time_format)
            except pytz.UnknownTimeZoneError:
                formatted_location_time = f"Could not determine time for location (unknown timezone: {location_tz_str})."
        else:
            formatted_location_time = "Could not determine timezone for location coordinates."
    else:
        formatted_location_time = "Location coordinates not available for timezone lookup."

    return formatted_user_time, formatted_location_time, location_tz_str

def load_default_city() -> str | None:
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
            print(f"Warning: Could not read default city from {DEFAULT_SETTINGS_FILE}. File might be corrupted or malformed.")
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