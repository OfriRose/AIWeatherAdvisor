
import requests
import os
from datetime import datetime, timedelta, timezone 

# Load environment variables from .env file
#load_dotenv()

# Get API key from environment variable
#API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
#

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

def get_local_time_at_location(timezone_offset_seconds: int) -> datetime:
    """
    Calculates the current local time at a location based on its UTC offset.

    Args:
        timezone_offset_seconds (int): The timezone offset from UTC in seconds.

    Returns:
        datetime: The current local datetime object for that timezone.
    """
    # Get current UTC time
    utc_now = datetime.now(timezone.utc)

    # Create a timedelta object from the offset
    offset_delta = timedelta(seconds=timezone_offset_seconds)

    # Apply the offset to UTC time
    local_time_at_location = utc_now + offset_delta

    return local_time_at_location