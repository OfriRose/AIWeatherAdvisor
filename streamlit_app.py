import streamlit as st
import os
from dotenv import load_dotenv
from datetime import datetime
import pytz
import tzlocal

from src.weather_checker.main import get_weather_data, get_times_for_location, load_default_city, save_default_city

# Load API KEY
load_dotenv()
API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

if not API_KEY:
    st.error("API Key not found. Please set OPENWEATHERMAP_API_KEY in your .env file.")
    st.stop() # Stop the app if API key is missing

st.set_page_config(page_title="Global Weather Checker", layout="wide")
st.title('Global Weather Checker')
st.write('Enter a city name to get the current weather conditions and local time.')

# --- Streamlit Session State for persistent data ---
# This will store all the data needed for the weather display
if 'displayed_weather_info' not in st.session_state:
    st.session_state.displayed_weather_info = None

# These are for the sidebar time display
if 'last_queried_city' not in st.session_state:
    st.session_state.last_queried_city = None
if 'last_queried_coords' not in st.session_state:
    st.session_state.last_queried_coords = None

if 'default_city' not in st.session_state:
    st.session_state.default_city = load_default_city()

# --- Time Display in Sidebar ---
st.sidebar.header("Time Information")

user_local_tz_str = "UTC"
try:
    user_local_tz_str = tzlocal.get_localzone().key
except Exception:
    st.sidebar.caption("Could not determine your exact local timezone. Defaulting to UTC.")

user_local_time_placeholder = st.sidebar.empty()
location_time_placeholder = st.sidebar.empty()
location_timezone_info_placeholder = st.sidebar.empty()


# Calculate and display times based on current state (this block runs on every rerun)
if st.session_state.last_queried_coords:
    lat, lon = st.session_state.last_queried_coords
    formatted_user_time, formatted_location_time, location_tz_str = \
        get_times_for_location(user_local_tz_str, lat, lon)

    user_local_time_placeholder.markdown(f"**Your Local Time:**\n{formatted_user_time}")

    if formatted_location_time:
        location_time_placeholder.markdown(f"**Time in {st.session_state.last_queried_city}:**\n{formatted_location_time}")
        if location_tz_str:
            location_timezone_info_placeholder.caption(f"(Timezone: {location_tz_str})")
    else:
        location_time_placeholder.markdown("**Time in City:**\n_Could not determine_")
        location_timezone_info_placeholder.empty()
else:
    current_time_user_local = datetime.now(pytz.timezone(user_local_tz_str))
    user_local_time_placeholder.markdown(f"**Your Local Time:**\n{current_time_user_local.strftime('%A, %B %d, %Y, %I:%M %p %Z%z')}")
    location_time_placeholder.markdown("**Time in City:**\n_No city queried yet_")
    location_timezone_info_placeholder.empty()


# --- Main App Body (Input and Button) ---
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

            # Parse and store ALL display data into session state
            st.session_state.displayed_weather_info = {
                "city": weather_data.get("name"),
                "country": weather_data.get("sys", {}).get("country"),
                "temperature": weather_data.get("main", {}).get("temp"),
                "feels_like": weather_data.get("main", {}).get("feels_like"),
                "humidity": weather_data.get("main", {}).get("humidity"),
                "weather_description": weather_data.get("weather", [])[0].get("description").capitalize() if weather_data.get("weather") else "N/A",
                "wind_speed": weather_data.get("wind", {}).get("speed")
            }
            
            # Update data for sidebar time
            st.session_state.last_queried_city = weather_data.get("name")
            lon = weather_data.get("coord", {}).get("lon")
            lat = weather_data.get("coord", {}).get("lat")
            if lat is not None and lon is not None:
                st.session_state.last_queried_coords = (lat, lon)
            else:
                st.session_state.last_queried_coords = None
                st.warning(f"Could not get coordinates for {city_name_input} to determine exact timezone.")

            st.rerun() # Forces a rerun to update both sidebar and main display based on new session state

        else:
            st.error(f"'{city_name_input}' not found. Please enter a valid city name.")
            # Clear stored data if fetch failed
            st.session_state.displayed_weather_info = None
            st.session_state.last_queried_city = None
            st.session_state.last_queried_coords = None
            st.rerun() # Rerun to clear any previous weather/time info
    else:
        st.warning("Please enter a city name.")

if st.session_state.displayed_weather_info:
    # Use a sub-header for clarity or place in sidebar
    st.subheader("Default Settings")
    if st.button(f"Set '{st.session_state.displayed_weather_info['city']}' as Default City"):
        save_default_city(st.session_state.displayed_weather_info['city'])
        st.session_state.default_city = st.session_state.displayed_weather_info['city'] # Update session state immediately
        st.success(f"'{st.session_state.displayed_weather_info['city']}' has been set as your default city!")

if st.session_state.displayed_weather_info:
    weather_to_display = st.session_state.displayed_weather_info
    
    st.header(f"Current Weather in {weather_to_display['city']}, {weather_to_display['country']}")

    temp_col, humidity_col, wind_col = st.columns(3)
    with temp_col:
        st.metric(label="Temperature", value=f"{weather_to_display['temperature']}°C", delta=f"{weather_to_display['feels_like']}°C Feels like")
    with humidity_col:
        st.metric(label="Humidity", value=f"{weather_to_display['humidity']}%")
    with wind_col:
        st.metric(label="Wind Speed", value=f"{weather_to_display['wind_speed']} m/s")

    st.info(f"Conditions: {weather_to_display['weather_description']}")