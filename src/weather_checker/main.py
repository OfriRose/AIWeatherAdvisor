
import requests
import os
import pytz 
import json
from datetime import datetime
from dotenv import load_dotenv
from timezonefinder import TimezoneFinder

# Initialize TimezoneFinder once for efficiency
tf = TimezoneFinder()
# Load environment variables from .env file
#load_dotenv()

# Get API key from environment variable
#API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
#

DEFAULT_SETTINGS_FILE = 'default_settings.json'

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