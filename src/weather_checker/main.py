
import requests
import os
from dotenv import load_dotenv # Import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")


def get_weather_data(city_name: str, api_key: str) -> dict | None:
    """
    Fetches current weather data for a given city using the OpenWeatherMap API.

    Args:
        city_name (str): The name of the city.
        api_key (str): Your OpenWeatherMap API key.

    Returns:
        dict | None: A dictionary containing weather data if successful, None otherwise.
    """
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

def main():

    print("Welcome to the Weather Checker Application!")

    while True:
        city_input = input("\nEnter a city name (or 'q' to quit): ").strip()
        if city_input.lower() == 'q':
            print("Exiting application. Goodbye!")
            break

        weather = get_weather_data(city_input, API_KEY)
        display_weather(weather)

if __name__ == "__main__":
    main()