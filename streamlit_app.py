import streamlit as st
import os
from dotenv import load_dotenv
from datetime import datetime
import pytz 

# Import the functions from your main application script
from src.weather_checker.main import get_weather_data, get_local_time_at_location

# Load API KEY from .env file
load_dotenv()
API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

if not API_KEY:
    st.error("API Key not found.")
    st.stop() 

st.title('Global Weather Checker')
st.write('Enter a city name to get the current weather conditions.')

# Display user's current local time
st.sidebar.header("Your Local Time")
user_local_time_placeholder = st.sidebar.empty()

# Input field for city name
city_name = st.text_input('Enter City Name', placeholder='e.g., London, New York, Tokyo')

# Button to fetch weather data
if st.button('Get Weather'):
    if city_name:
        # Use a spinner to indicate loading
        with st.spinner(f'Fetching weather for {city_name}...'):
            weather_data = get_weather_data(city_name, API_KEY)

        if weather_data:
            st.success(f"Weather data for {city_name} fetched successfully!")

            # Extract relevant data
            city = weather_data.get("name")
            country = weather_data.get("sys", {}).get("country")
            temperature = weather_data.get("main", {}).get("temp")
            feels_like = weather_data.get("main", {}).get("feels_like")
            humidity = weather_data.get("main", {}).get("humidity")
            weather_description = weather_data.get("weather", [])[0].get("description").capitalize() if weather_data.get("weather") else "N/A"
            wind_speed = weather_data.get("wind", {}).get("speed")
            timezone_offset = weather_data.get("timezone", 0)
            # Display data
            st.header(f"Current Weather in {city}, {country}")

            # Using st.metric for key numerical values
            temp_col, humidity_col, wind_col = st.columns(3)
            with temp_col:
                st.metric(label="Temperature", value=f"{temperature}°C", delta=f"{feels_like}°C Feels like")
            with humidity_col:
                st.metric(label="Humidity", value=f"{humidity}%")
            with wind_col:
                st.metric(label="Wind Speed", value=f"{wind_speed} m/s")

            st.info(f"Conditions: {weather_description}")

        else:
            st.error(f"'{city_name}'not found. please enter a valid city name.")
    else:
        st.warning("Please enter a city name.")

    # Update time displays
    st.sidebar.header("Time Information")
    
    # Get location's local time
    if timezone_offset:
        local_time = get_local_time_at_location(timezone_offset)
        time_format = "%d-%m-%Y  %H:%M:%S"
        
        # Display both times in sidebar
        user_local_time_placeholder.write(f"Your Local Time:\n{local_time.strftime(time_format)}")
        st.sidebar.write(f"Local Time in {city_name}:\n{local_time.strftime(time_format)}")
    else:
        user_local_time_placeholder.write("Could not determine local time.")
        st.sidebar.write("Could not determine local time for the specified city.")

