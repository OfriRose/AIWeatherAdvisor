
"""
AI Assistant module for weather-related advice using the Gemini API.
Handles API interactions, rate limiting, and error management.
"""

import os
from time import sleep
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai

# Constants
MODEL_NAME = "gemini-2.0-flash"
REQUESTS_PER_MINUTE = 60
RETRY_ATTEMPTS = 3
RETRY_DELAY = 2

# Initialize configuration
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Rate limiting state
last_request_time = None
remaining_requests = REQUESTS_PER_MINUTE

def check_rate_limit() -> tuple[bool, str]:
    """Check if we're within rate limits."""
    global last_request_time, remaining_requests
    
    if not last_request_time:
        return True, ""
        
    time_since_last = (datetime.now() - last_request_time).total_seconds()
    if time_since_last < 60 and remaining_requests <= 0:
        return False, f"Rate limit reached. Please wait {int(60 - time_since_last)} seconds."
    if time_since_last >= 60:
        remaining_requests = REQUESTS_PER_MINUTE
    return True, ""

def initialize_model():
    """Initialize and configure the Gemini model."""
    if not GEMINI_API_KEY:
        raise ValueError("Gemini API Key is not configured")
        
    genai.configure(api_key=GEMINI_API_KEY, transport="rest")
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        generation_config={
            "temperature": 0.7,
            "max_output_tokens": 256,
        }
    )
    return model

def get_gemini_weather_advice(weather_info: dict, user_question: str) -> str:
    """
    Get AI-generated weather advice based on current conditions.
    
    Args:
        weather_info: Dictionary containing weather data
        user_question: User's weather-related question
    
    Returns:
        AI-generated response or error message
    
    Raises:
        ValueError: If the Gemini API key is not configured
    """
    model = initialize_model()
    
    # Check rate limiting
    can_proceed, error_msg = check_rate_limit()
    if not can_proceed:
        return error_msg
    
    try:
        model = initialize_model()

        # Generate response with retry logic
        prompt = f"Current conditions in {weather_info.get('city')}: {weather_info.get('temperature')}°C, {weather_info.get('weather_description')}.\nQuestion: {user_question}"
        
        for attempt in range(3):
            try:
                response = model.generate_content(prompt)
                if hasattr(response, 'text') and response.text:
                    # Update rate limit tracking on success
                    global last_request_time, remaining_requests
                    last_request_time = datetime.now()
                    remaining_requests -= 1
                    return response.text.strip()
                
                if attempt < 2:
                    sleep(1)
            except Exception as e:
                error_str = str(e).lower()
                if any(msg in error_str for msg in ["429", "quota", "rate limit"]):
                    remaining_requests = 0
                    last_request_time = datetime.now()
                    return "Rate limit reached. Please try again in 60 seconds."
                if attempt < 2:
                    sleep(2)
                continue
        
        return "Unable to generate a response. Please try again."
                
    except Exception as e:
        error_str = str(e).lower()
        if "api_key" in error_str:
            return "Invalid API key configuration."
        if "network" in error_str:
            return "Network error. Please check your connection."
        return f"Error: {str(e)}"
