import os
from kivy.config import Config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

width, height = 1920, 1080

Config.set('graphics', 'width', width)
Config.set('graphics', 'height', height)
# Config.set('graphics', 'fullscreen', 'True') # Commented out for easier debugging/usage
Config.set('graphics', 'resizable', '1')

# API Keys and Config
EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("PASSWORD")

IP_ADDR_API_URL = os.environ.get("IP_ADDR_API_URL")
NEWS_FETCH_API_URL = os.environ.get("NEWS_FETCH_API_URL")
NEWS_FETCH_API_KEY = os.environ.get("NEWS_FETCH_API_KEY")
NEWS_SEARCH_URL = os.environ.get("NEWS_SEARCH_URL") # New variable
WEATHER_FORECAST_API_URL = os.environ.get("WEATHER_FORECAST_API_URL")
WEATHER_FORECAST_API_KEY = os.environ.get("WEATHER_FORECAST_API_KEY")
WEATHER_CURRENT_URL = os.environ.get("WEATHER_CURRENT_URL") # New variable
WEATHER_FORECAST_URL = os.environ.get("WEATHER_FORECAST_URL") # New variable
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

SMTP_URL = os.environ.get("SMTP_URL")
SMTP_PORT = os.environ.get("SMTP_PORT")

SCREEN_WIDTH = Config.getint('graphics', 'width')
SCREEN_HEIGHT = Config.getint('graphics', 'height')

# App Paths (Dynamic or customizable)
NOTEPAD_PATH = "notepad.exe" # uses system path
DISCORD_PATH = os.environ.get("DISCORD_PATH", "Discord.exe") # Allow override, default to simple name
GTA_PATH = os.environ.get("GTA_PATH", "")

def get_app_path(app_name):
    """Helper to get path or just return name for system run"""
    if app_name == "notepad":
        return NOTEPAD_PATH
    elif app_name == "discord":
        return DISCORD_PATH
    return None
