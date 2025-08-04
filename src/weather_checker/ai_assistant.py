
from datetime import datetime
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Initialize configuration
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
last_request_time = None
remaining_requests = 60

def initialize_model():
    """Initialize and configure the Gemini model."""
    if not GEMINI_API_KEY:
        raise ValueError("Gemini API Key is not configured")
        
    genai.configure(api_key=GEMINI_API_KEY, transport="rest")
    return genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config={"max_output_tokens": 256}
    )

def get_gemini_weather_advice(weather_info: dict, user_question: str) -> str:
    """Get AI-generated weather advice based on weather conditions."""
    global last_request_time, remaining_requests
    
    try:
        model = initialize_model()
        prompt = (
            f"weather conditions in {weather_info['city']}: "
            f"{weather_info['temperature']}°C, "
            f"{weather_info['weather_description']}.\n"
            f"Question: {user_question} please keep answers short and concise."
        )
        
        time_since_last = (datetime.now() - last_request_time).total_seconds() if last_request_time else 61
        if time_since_last < 60 and remaining_requests <= 0:
            return f"Rate limit reached. Please wait {int(60 - time_since_last)} seconds."
            
        response = model.generate_content(prompt)
        if response.text:
            last_request_time = datetime.now()
            remaining_requests = 60 if time_since_last >= 60 else remaining_requests - 1
            return response.text.strip()
            
        return "Unable to generate a response. Please try again."
                
    except Exception as e:
        if "429" in str(e).lower():
            return "Rate limit reached. Please try again in 60 seconds."
        return f"Error: {str(e)}"
