import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables as early as possible
load_dotenv()

@st.cache_resource
def get_api_key() -> str:
    """Fetch OpenWeather API key from environment and validate it."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        st.error("❌ OPENWEATHER_API_KEY not found in .env file")
        st.stop()
    return api_key
