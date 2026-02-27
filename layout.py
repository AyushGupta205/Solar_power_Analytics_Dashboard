from __future__ import annotations

from datetime import datetime
from typing import Tuple

import streamlit as st


def render_page_config_and_style():
    st.set_page_config(
        page_title="☀️ Solar Power Dashboard",
        page_icon="☀️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
        <style>
        .main { background-color: #ffffff; }
        .stApp { background: #ffffff; }
        .stButton>button { background: linear-gradient(45deg, #00b4d8, #0077b6); color: white; border: none; border-radius: 8px; padding: 0.5rem 1.5rem; font-weight: 600; transition: all 0.3s; }
        .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0, 180, 216, 0.2); }
        .stSelectbox, .stTextInput, .stSlider, .stNumberInput { margin-bottom: 1.2rem; }
        .stNumberInput input { border-radius: 8px !important; border: 1px solid #dee2e6 !important; }
        .stSlider { padding: 0.5rem 0; }
        .css-1aumxhk { background-color: #ffffff; border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); margin-bottom: 1.5rem; }
        .stTabs [data-baseweb="tab-list"] { gap: 8px; }
        .stTabs [data-baseweb="tab"] { border-radius: 8px !important; padding: 8px 16px; margin: 0 4px; }
        .stTabs [aria-selected="true"] { background-color: #00b4d8 !important; color: white !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("☀️ Solar Power Analytics Dashboard")
    st.markdown(
        """
        <div style='background: linear-gradient(45deg, #00b4d8, #0077b6); padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem; color: white;'>
            <h3 style='margin: 0; font-weight: 600;'>Optimize your solar energy production with real-time insights and advanced analytics</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(default_city: str = "Delhi") -> Tuple[str, int, int, str, str]:
    with st.sidebar:
        st.markdown("## ⚙️ System Configuration")
        city = st.text_input("City", default_city, key="city_name_v2")
        st.markdown("### Panel Configuration")
        col1, col2 = st.columns(2)
        with col1:
            num_panels = st.number_input("Number of Panels", 1, 1000, 10, 1)
        with col2:
            panel_wattage = st.number_input("Panel Wattage (W)", 100, 500, 300, 10)
        st.markdown("### Analysis Settings")
        timeframe = st.selectbox("Timeframe", ["Last 7 Days", "Last 14 Days", "Last 30 Days", "Last 90 Days", "1 Year"]) 
        resolution = st.selectbox("Data Resolution", ["Hourly", "Daily", "Weekly", "Monthly"])  # placeholder for future
    return city, num_panels, panel_wattage, timeframe, resolution


def footer(city: str):
    st.markdown("---")
    st.markdown(
        f"""
        <div style='text-align: center; color: #666; font-size: 0.9em; margin-top: 2rem;'>
            <p>☀️ Solar Power Analytics Dashboard • Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            <p>Data provided by OpenWeatherMap • For demonstration purposes only</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
