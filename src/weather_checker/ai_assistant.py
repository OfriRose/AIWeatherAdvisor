
import os
import json
from time import sleep
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Check for required packages and API key
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    print("Warning: google.generativeai package not installed. Please install it with:")
    print("pip install google-generativeai")
    GENAI_AVAILABLE = False

if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY not found in environment variables or .env file.")
    print("Please make sure you have a .env file with GEMINI_API_KEY='YOUR_KEY'.")
elif not GEMINI_API_KEY.startswith('AI'):
    print("Warning: GEMINI_API_KEY format looks incorrect. Should start with 'AI'.")

# Store last request time and remaining quota
last_request_time = None
remaining_requests = 60  # Free tier typically allows 60 requests per minute

def get_gemini_weather_advice(weather_info: dict, user_question: str) -> str:
    """
    Interacts with the Gemini API to get weather-related advice.

    Args:
        weather_info (dict): A dictionary containing parsed weather information.
                             This should ideally be st.session_state.displayed_weather_info.
        user_question (str): The question asked by the user.

    Returns:
        str: The AI's generated response.
    """
    global last_request_time, remaining_requests

    if not GEMINI_API_KEY:
        return "AI assistant is not configured. Please provide a Gemini API Key."

    # Check rate limiting
    current_time = datetime.now()
    if last_request_time:
        time_since_last = (current_time - last_request_time).total_seconds()
        if time_since_last < 60 and remaining_requests <= 0:
            wait_time = 60 - time_since_last
            return f"Rate limit reached. Please wait {int(wait_time)} seconds before trying again."
        elif time_since_last >= 60:
            remaining_requests = 60  # Reset quota after a minute

    try:
        # Configure with specific options for better region compatibility
        genai.configure(
            api_key=GEMINI_API_KEY,
            transport="rest",  
            client_options={
                "api_endpoint": "generativelanguage.googleapis.com",
                "credentials_file": None  # Don't use local credentials
            }
        )
        
        # List available models first to verify access
        try:
            models = genai.list_models()
            model_found = False
            for m in models:
                if 'gemini-2.0-flash' in m.name.lower():
                    model_found = True
                    break
            
            if not model_found:
                raise Exception("gemini-2.0-flash model not available in your region")
            
            # Initialize the model with basic settings
            model = genai.GenerativeModel(
                model_name='gemini-2.0-flash',
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 256,  # Flash model has lower token limit
                }
            )
        except Exception as e:
            print(f"Model initialization failed: {str(e)}")
            if "region" in str(e).lower():
                raise Exception(f"The Gemini API is not available in your region. Error: {str(e)}")
            else:
                raise  # Re-raise other exceptions

        # Construct a minimal prompt
        prompt = (
            f"Current conditions in {weather_info.get('city')}: "
            f"{weather_info.get('temperature')}°C, "
            f"{weather_info.get('weather_description')}.\n"
            f"Question: {user_question}"
        )

        # Attempt to generate response with simplified retry logic
        for attempt in range(3):
            try:
                print(f"Attempt {attempt + 1} to generate response...")
                response = model.generate_content(prompt)
                
                if hasattr(response, 'text') and response.text:
                    print("Successfully generated response")
                    return response.text.strip()
                
                print("Empty response received, retrying...")
                sleep(1)
                
            except Exception as e:
                print(f"Error on attempt {attempt + 1}: {str(e)}")
                if attempt < 2:  # Only sleep if we're going to retry
                    sleep(2)
                continue
                
        return "I apologize, but I'm having trouble generating a response right now. Please try again in a moment."

    except Exception as e:
        # Log the full error for debugging
        print(f"AI Assistant Error: {str(e)}")
        error_str = str(e).lower()
        
        # Update rate limiting info
        if "429" in str(e) or "quota" in error_str or "rate limit" in error_str:
            remaining_requests = 0
            last_request_time = datetime.now()
            return "Rate limit reached. Please try again in 60 seconds. The free tier of Gemini API has limited requests per minute."
        elif "models/" in str(e) and "not found" in str(e):
            return "Unable to access the AI model. Please check if the Gemini API service is available in your region."
        elif "api_key" in error_str:
            return "Invalid API key. Please check your Gemini API key configuration."
        elif "network" in error_str:
            return "Network error. Please check your internet connection and try again."
        else:
            return f"An unexpected error occurred. Please try again later. Error: {str(e)}"
    else:
        # Update rate limiting info on successful request
        last_request_time = datetime.now()
        remaining_requests -= 1

# Example usage (for testing this module directly)
if __name__ == "__main__":
    # Dummy weather data for testing
    test_weather = {
        "city": "London",
        "country": "GB",
        "temperature": 15.0,
        "feels_like": 14.5,
        "humidity": 70,
        "weather_description": "light rain",
        "wind_speed": 5.2
    }

    print("Asking: What should I pack?")
    advice = get_gemini_weather_advice(test_weather, "What should I pack?")
    print(advice)

    print("\nAsking: What activities can I do?")
    advice = get_gemini_weather_advice(test_weather, "What activities can I do today?")
    print(advice)