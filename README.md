# 🌤️ AI Weather Assistant

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://aiweatheradvisor.streamlit.app/)

An intelligent weather application that combines real-time weather data with AI-powered insights to provide personalized weather advice. Built with Python and Streamlit, this project showcases modern data science techniques and AI integration.

[Try the Demo](https://aiweatheradvisor.streamlit.app/)
## ✨ Features

### 🌡️ Real-Time Weather Analytics
- **Current Conditions**: Temperature, humidity, wind speed, and more
- **5-Day Forecast**: Plan ahead with detailed weather predictions
- **Global Coverage**: Access weather data for any city worldwide

### 🤖 AI-Powered Advice
- **Smart Recommendations**: Get personalized suggestions for activities
- **Context-Aware**: AI considers current weather conditions
- **Natural Language**: Ask questions in plain English about the weather

### 🌍 Geographic Intelligence
- **Automatic Time Zones**: Local time detection and conversion
- **Location Awareness**: Precise geographic coordinate handling
- **Global Adaptability**: Works with cities worldwide

### 📊 Interactive Visualization
- **Real-Time Updates**: Dynamic weather metrics display
- **Intuitive Interface**: User-friendly data presentation

## 🛠️ Tech Stack

### Core Technologies
- **Python** (>= 3.13)
- **Streamlit** - For interactive data visualization and web interface
- **Google Generative AI** (Gemini) - For intelligent weather advice
- **OpenWeatherMap API** - For real-time weather data

### Key Dependencies
```toml
dependencies = [
    "streamlit >= 1.47.1"      # Interactive UI and data visualization
    "requests >= 2.32.4"       # HTTP requests for weather API
    "pytz >= 2025.2"          # Timezone calculations
    "timezonefinder >= 7.0.1"  # Geographic timezone detection
    "tzlocal >= 5.3.1"        # Local timezone handling
    "google-generativeai >= 0.8.5"  # AI-powered weather advice
    "python-dotenv"           # Environment variable management
]
```

## 🌟 Features

1. **Real-Time Weather Analysis**
   - Temperature and humidity monitoring
   - Wind speed analysis
   - Weather condition classification

2. **Geographic Time Processing**
   - Automatic timezone detection
   - Local vs. target location time comparison
   - Global timezone handling

3. **AI Weather Assistant**
   - Context-aware weather advice
   - Intelligent clothing recommendations
   - Activity planning suggestions based on conditions

4. **Interactive Data Visualization**
   - Real-time weather metrics display
   - Dynamic user interface
   - Responsive design for various screen sizes

## 📋 Prerequisites

1. Python 3.13 or higher
2. Poetry for dependency management
3. OpenWeatherMap API key
4. Google Gemini API key

## 🚀 Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/OfriRose/WeatherApp.git
   cd weather-checker
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Set up environment variables:
   Create a `.env` file with:
   ```
   OPENWEATHERMAP_API_KEY=your_key_here
   GEMINI_API_KEY=your_key_here
   ```

4. Run the application:
   ```bash
   poetry run streamlit run streamlit_app.py
   ```

## 🔧 Project Structure

```
weather-checker/
├── src/
│   └── weather_checker/
│       ├── __init__.py
│       ├── HelperFuncs.py           # Core processing logic
│       └── ai_assistant.py   # AI integration module
├── streamlit_app.py         # Web interface
├── pyproject.toml          # Project dependencies
└── README.md
```

## 📊 Data Science Components

1. **Data Collection**
   - Real-time weather API integration
   - Geographic coordinate processing
   - Time series data handling

2. **Data Processing**
   - Temperature unit conversion
   - Time zone calculations
   - Weather condition categorization

3. **AI Integration**
   - Natural language processing for user queries
   - Context-aware response generation
   - Weather pattern analysis

4. **Data Visualization**
   - Interactive metrics display
   - Dynamic updates
   - User-friendly data presentation


