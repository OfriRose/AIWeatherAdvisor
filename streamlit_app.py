import streamlit as st
import os
from dotenv import load_dotenv
from src.weather_checker.main import (
    get_weather_data, 
    initialize_session_state, 
    update_weather_display,
    get_user_timezone,
    display_time_info,
    save_default_city
)

# Load API KEY
load_dotenv()
API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

if not API_KEY:
    st.error("API Key not found. Please set OPENWEATHERMAP_API_KEY in your .env file.")
    st.stop()

# Configure page and initialize state
st.set_page_config(page_title="Global Weather Checker", layout="wide")
st.title('Global Weather Checker')
st.write('Enter a city name to get the current weather conditions and local time.')

# Initialize session state
initialize_session_state()

# Set up time display in sidebar
st.sidebar.header("Time Information")

# Get and display user's timezone
user_local_tz_str, timezone_detected = get_user_timezone()
if not timezone_detected:
    st.sidebar.caption("Could not determine your exact local timezone. Defaulting to UTC.")

# Display time information
display_time_info(user_local_tz_str)

# Main App Body (Input and Button)
city_name_input = st.text_input(
    'Enter City Name',
    value=st.session_state.default_city if st.session_state.default_city else '',
    placeholder='e.g., London, New York, Tokyo',
    key='city_input'
)

if st.button('Get Weather', key='get_weather_button'):
    if city_name_input:
        with st.spinner(f'Fetching weather for {city_name_input}...'):
            weather_data = get_weather_data(city_name_input, API_KEY)

        if weather_data:
            st.success(f"Weather data for {city_name_input} fetched successfully!")
            update_weather_display(weather_data)
            st.rerun()  # Update the display

        else:
            st.error(f"'{city_name_input}' not found. Please enter a valid city name.")
            st.session_state.displayed_weather_info = None
            st.session_state.last_queried_city = None
            st.session_state.last_queried_coords = None
            st.rerun()
    else:
        st.warning("Please enter a city name.")

# Display weather information and default city settings
if st.session_state.displayed_weather_info:
    weather = st.session_state.displayed_weather_info
    
    # Default city setting
    st.subheader("Default Settings")
    if st.button(f"Set '{weather['city']}' as Default City"):
        save_default_city(weather['city'])
        st.session_state.default_city = weather['city']
        st.success(f"'{weather['city']}' has been set as your default city!")

    # Weather display
    st.header(f"Current Weather in {weather['city']}, {weather['country']}")

    # Weather metrics
    temp_col, humidity_col, wind_col = st.columns(3)
    with temp_col:
        st.metric(label="Temperature", value=f"{weather['temperature']}°C", 
                 delta=f"{weather['feels_like']}°C Feels like")
    with humidity_col:
        st.metric(label="Humidity", value=f"{weather['humidity']}%")
    with wind_col:
        st.metric(label="Wind Speed", value=f"{weather['wind_speed']} m/s")

    st.info(f"Conditions: {weather['weather_description']}")