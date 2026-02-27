from __future__ import annotations

from datetime import datetime
from typing import List

import os
import sys

# Ensure project root is on sys.path so 'import app.*' works when running this file directly
PACKAGE_ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(PACKAGE_ROOT)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import numpy as np
import pandas as pd
import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards
import plotly.graph_objects as go

from app.services.weather import get_weather_data
from app.ui.charts import (
    daily_production_chart,
    hourly_energy_chart,
    monthly_chart,
    performance_chart,
)
from app.ui.layout import footer, render_page_config_and_style, render_sidebar
from app.utils.calculations import (
    build_dataframes,
    calculate_temp_effect,
    compute_core_metrics,
    compute_daily_impact,
    generate_hour_marks,
    generate_profiles,
    generate_timeframes,
)


def run():
    # Page setup & header
    render_page_config_and_style()

    # Sidebar
    city, num_panels, panel_wattage, timeframe, _resolution = render_sidebar()

    # Weather
    weather = get_weather_data(city)

    if not weather:
        st.error("❌ Could not fetch weather data. Please check the city name and try again.")
        st.info("💡 Try entering a major city name or check your internet connection.")
        return

    # System parameters
    total_capacity = num_panels * panel_wattage / 1000.0  # kW
    cloud_factor = weather.get('clouds', 0) / 100.0
    sunlight_hours = float(weather.get('sunlight_hours', 5.5))

    # Production calculations (mirroring the original logic)
    base_energy = total_capacity * 18 / 100 * sunlight_hours * (1 - 10 / 100) * (1 - cloud_factor)
    temp_effect = calculate_temp_effect(weather['temperature'])
    energy = base_energy * temp_effect * (1 - 5 / 100)

    # Time ranges and profiles
    date_range, days = generate_timeframes(timeframe)
    hours = generate_hour_marks()
    hourly_pattern, daily_energy = generate_profiles(energy, days)

    # Dataframes
    daily_df, hourly_df, monthly_df = build_dataframes(date_range, hours, daily_energy, hourly_pattern)

    # Metrics
    metrics = compute_core_metrics(total_capacity, energy, daily_energy, sunlight_hours)
    daily_impact = compute_daily_impact(energy)

    # Weather summary
    st.markdown("### 🌤️ Current Weather")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("🌡️ Temperature", f"{weather['temperature']:.1f}°C")
    with c2:
        st.metric("☁️ Cloud Cover", f"{weather['clouds']}%")
    with c3:
        st.metric("💨 Wind Speed", f"{weather['wind_speed']} m/s")
    with c4:
        st.metric("☀️ Sunlight Hours", f"{sunlight_hours:.1f} hours")

    st.markdown("---")

    # System Overview metrics
    st.markdown("## 📊 System Performance Overview")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("☀️ Total System Size", f"{total_capacity:.1f} kW", f"{num_panels} × {panel_wattage}W panels")
    with m2:
        st.metric("⚡ Daily Production", f"{energy:.1f} kWh", f"{energy/24:.1f} kWh/h peak")
    with m3:
        st.metric("📅 Monthly Estimate", f"{metrics['monthly_estimate']:,.0f} kWh", f"{metrics['monthly_estimate']/30:.1f} kWh/day avg")
    with m4:
        st.metric("📈 Annual Potential", f"{metrics['annual_estimate']:,.0f} kWh", f"{metrics['annual_estimate']/12:,.0f} kWh/month avg")

    style_metric_cards(background_color="#ffffff", border_left_color="#00b4d8", box_shadow="0 2px 4px rgba(0,0,0,0.05)")

    # Tabs
    tab1, tab2, tab3 = st.tabs(["Dashboard", "Monthly", "System"])

    with tab1:
        st.markdown("### ⚡ Solar Power Overview")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("🔋 Total Capacity", f"{total_capacity:.1f} kW")
        with c2:
            st.metric("📊 Daily Energy", f"{energy:.1f} kWh")
        with c3:
            st.metric("📅 Monthly Estimate", f"{metrics['monthly_estimate']:.1f} kWh")
        with c4:
            st.metric("📈 Annual Estimate", f"{metrics['annual_estimate']:.1f} kWh")

        # Daily chart
        st.markdown("### 📈 Energy Production")
        st.plotly_chart(daily_production_chart(date_range, daily_energy, days), use_container_width=True, config={'displayModeBar': True})

        # Stats
        a1, a2, a3 = st.columns(3)
        with a1:
            st.metric("📊 Average Daily", f"{metrics['avg_daily']:.1f} kWh")
        with a2:
            st.metric("📈 Total Production", f"{metrics['total_energy']:.1f} kWh")
        with a3:
            st.metric("📅 Days Recorded", f"{len(daily_energy)}")

        # Savings and Impact
        st.markdown("---")
        st.markdown("### 💰 Monthly Savings & Impact")
        s1, s2 = st.columns([1, 1.5])
        with s1:
            st.markdown("#### Financials")
            st.metric("Daily Savings", f"₹{metrics['daily_savings']:.1f}")
            st.metric("Monthly Savings", f"₹{metrics['monthly_savings']:,.0f}", f"₹{metrics['daily_savings']:.1f} per day")
            st.metric("Annual Savings", f"₹{metrics['annual_savings']:,.0f}", f"{total_capacity:.1f} kW system")
            st.markdown(
                """
                <div style='background: #f8f9fa; padding: 12px; border-radius: 8px; margin-top: 15px; border-left: 4px solid #4CAF50;'>
                    <p style='margin: 0; color: #2E7D32; font-size: 13px; line-height: 1.4;'>
                        💡 Based on ₹8/kWh electricity rate. Actual savings may vary by location and usage.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with s2:
            st.markdown("#### Daily Power Usage")
            st.markdown(
                f"""
                <div style='background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
                    <div style='display: flex; justify-content: space-between; margin: 10px 0;'>
                        <span>📺 TV Time:</span>
                        <strong>{daily_impact['tv_hours']:.0f} hours</strong>
                    </div>
                    <div style='display: flex; justify-content: space-between; margin: 10px 0;'>
                        <span>💨 Fan Time:</span>
                        <strong>{daily_impact['fan_hours']:.0f} hours</strong>
                    </div>
                    <div style='display: flex; justify-content: space-between; margin: 10px 0;'>
                        <span>💡 LED Bulbs:</span>
                        <strong>{daily_impact['bulb_hours']/10:.0f} bulbs for 10h</strong>
                    </div>
                    <div style='display: flex; justify-content: space-between; margin: 10px 0;'>
                        <span>📱 Phone Charges:</span>
                        <strong>{daily_impact['phone_charges']:.0f} full charges</strong>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            fig = go.Figure(go.Bar(
                y=['Phone', 'LED Bulbs', 'Fan', 'TV'],
                x=[
                    daily_impact['phone_charges'],
                    daily_impact['bulb_hours']/10,
                    daily_impact['fan_hours'],
                    daily_impact['tv_hours'],
                ],
                orientation='h',
                marker_color=['#4cc9f0', '#4895ef', '#4361ee', '#3a0ca3'],
                text=[
                    f"{daily_impact['phone_charges']:.0f} charges",
                    f"{daily_impact['bulb_hours']/10:.0f} bulbs",
                    f"{daily_impact['fan_hours']:.0f} hours",
                    f"{daily_impact['tv_hours']:.0f} hours",
                ],
                textposition='auto',
            ))
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=10, b=10), height=200, showlegend=False,
                xaxis=dict(showgrid=False, showticklabels=False, title=None), yaxis=dict(showgrid=False, title=None),
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # Hourly energy
        st.markdown("### 🌞 Hourly Energy Production")
        hourly_energy = [p * (0.9 + 0.2 * np.random.random()) for p in hourly_pattern]
        hours_labels: List[str] = [h.strftime('%H:%M') for h in hours]

        # Metrics first (top of section)
        peak_power = max(hourly_energy) if hourly_energy else 0.0
        daily_total = float(np.sum(hourly_energy)) if hourly_energy else 0.0
        avg_power = float(np.mean(hourly_energy)) if hourly_energy else 0.0
        mhh1, mhh2, mhh3 = st.columns(3)
        with mhh1:
            st.metric("🔺 Peak Power", f"{peak_power:.2f} kW")
        with mhh2:
            st.metric("🧮 Est. Daily Total", f"{daily_total:.1f} kWh")
        with mhh3:
            st.metric("📊 Avg Power Output", f"{avg_power:.2f} kW")

        # Chart after metrics and info
        st.plotly_chart(
            hourly_energy_chart(hours_labels, hourly_energy, total_capacity),
            use_container_width=True,
            config={'displayModeBar': True},
        )

        # System performance indicators
        st.markdown("#### 📊 System Performance")
        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric("☀️ Sun Hours", f"{sunlight_hours:.1f} hours")
        with k2:
            st.metric("⚡ Daily Output", f"{energy:.1f} kWh")
        with k3:
            st.metric("📈 System Efficiency", f"{metrics['system_efficiency']:.1f}%")

    with tab2:
        # Specifications
        st.markdown("### ⚙️ System Overview")
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Total Capacity", f"{total_capacity:.1f} kW")
            st.metric("Panel Wattage", f"{panel_wattage}W")
        with c2:
            st.metric("Number of Panels", num_panels)
            st.metric("Location", city.title())

        st.markdown("---")
        st.markdown("#### 📊 Performance Summary")
        system_efficiency = metrics['system_efficiency']
        performance_ratio_value = min(100, system_efficiency * 1.3)

        s1, s2, s3 = st.columns(3)
        with s1:
            st.metric("Daily Average", f"{metrics['avg_daily']:.1f} kWh")
            st.metric("System Efficiency", f"{system_efficiency:.1f}%")
        with s2:
            st.metric("Performance Ratio", f"{performance_ratio_value:.0f}%")
            st.metric("Sunlight Hours", f"{sunlight_hours:.1f} hrs/day")
        with s3:
            temp_impact = (temp_effect - 1) * 100
            st.metric("Temp. Impact", f"{temp_impact:+.1f}%")
            st.metric("Cloud Impact", f"-{weather['clouds']:.0f}%")

        st.markdown("---")
        st.markdown("#### 📅 Recent Production")
        last_7 = min(7, len(daily_energy))
        recent_dates = date_range[-last_7:]
        recent_vals = daily_energy[-last_7:]
        fig_recent = go.Figure(go.Bar(x=recent_dates, y=recent_vals, marker_color='#00b4d8', hovertemplate='%{x|%b %d}: %{y:.1f} kWh<extra></extra>'))
        fig_recent.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=30, b=20), height=250,
                                 xaxis=dict(title=None, showgrid=False), yaxis=dict(title='kWh', showgrid=True, gridcolor='rgba(0,0,0,0.05)'))
        st.plotly_chart(fig_recent, use_container_width=True, config={'displayModeBar': False})

        st.markdown("### 📅 Monthly Energy Production")
        # Seasonal monthly energy similar to original
        months = pd.date_range(start=datetime.now().replace(day=1), periods=12, freq='MS')
        monthly_energy_rows = []
        for i, month in enumerate(months):
            seasonal_factor = 0.9 + 0.2 * np.sin(2 * np.pi * (i - 6) / 12)
            random_factor = 0.9 + 0.2 * np.random.random()
            next_month = months[i + 1] if i < 11 else month + pd.DateOffset(months=1)
            days_in_month = (next_month - month).days
            monthly_energy_rows.append({
                'Month': month.strftime('%b'),
                'Energy (kWh)': energy * days_in_month * seasonal_factor * random_factor,
                'Target': energy * days_in_month,
                'Season': 'Winter' if i in [11, 0, 1] else ('Summer' if i in [5, 6, 7] else 'Spring/Fall'),
            })
        df_monthly = pd.DataFrame(monthly_energy_rows)
        st.plotly_chart(monthly_chart(df_monthly), use_container_width=True)

    with tab3:
        st.markdown("### ⚙️ System Overview")
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Total Capacity", f"{total_capacity:.1f} kW")
            st.metric("Panel Wattage", f"{panel_wattage} W")
        with c2:
            st.metric("Number of Panels", num_panels)
            st.metric("Current Output", f"{energy:.2f} kWh")

        st.markdown("---")
        st.markdown("### 📊 Performance Metrics")
        st.plotly_chart(performance_chart(date_range, daily_energy, total_capacity), use_container_width=True)

        st.markdown("#### Key Performance Indicators")
        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric("Today's Production", f"{daily_energy[-1]:.1f} kWh")
            st.metric("7-Day Average", f"{np.mean(daily_energy[-7:]):.1f} kWh")
        with k2:
            st.metric("Peak Output", f"{max(daily_energy):.1f} kWh")
            st.metric("Efficiency", f"{metrics['system_efficiency']:.1f}%")
        with k3:
            st.metric("Monthly Estimate", f"{metrics['monthly_estimate']:,.1f} kWh")
            st.metric("Annual Estimate", f"{metrics['annual_estimate']:,.0f} kWh")

        st.markdown("---")
        st.markdown("### 🌞 Daily Production Pattern")
        hours_labels = [f"{h:02d}:00" for h in range(24)]
        fig_hour_bar = go.Figure(go.Bar(x=hours_labels, y=hourly_pattern, marker_color='#4cc9f0', name='Hourly Output', hovertemplate='%{x}: %{y:.2f} kWh<extra></extra>'))
        sunrise, sunset, current_hour = 6, 18, datetime.now().hour
        fig_hour_bar.add_vline(x=sunrise, line_dash="dash", line_color="orange", annotation_text="Sunrise", annotation_position="top")
        fig_hour_bar.add_vline(x=sunset, line_dash="dash", line_color="purple", annotation_text="Sunset", annotation_position="top")
        if 0 <= current_hour <= 23:
            fig_hour_bar.add_vline(x=current_hour, line_color="red", annotation_text="Now", annotation_position="bottom")
        fig_hour_bar.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=30, b=20), height=400, showlegend=False,
                                   xaxis=dict(tickangle=45, title=None, showgrid=False), yaxis=dict(title='Energy (kWh)', showgrid=True, gridcolor='rgba(200,200,200,0.2)', zeroline=False), hovermode='x unified')
        st.plotly_chart(fig_hour_bar, use_container_width=True)

        st.markdown("---")
        st.markdown("### 📊 System Status")
        s1, s2 = st.columns(2)
        with s1:
            st.metric("Panel Efficiency", f"{metrics['system_efficiency']:.1f}%")
            st.metric("Temperature Impact", f"{(temp_effect-1)*100:+.1f}%")
        with s2:
            st.metric("Weather Conditions", f"{weather['description'].title()}")
            st.metric("Cloud Cover Impact", f"-{weather['clouds']:.0f}%")

        st.caption(f"{city} • {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        st.markdown(
            """
            <style>
            .stMetricValue { font-size: 24px !important; font-weight: 600 !important; }
            .stMetricLabel { font-size: 14px !important; color: #666 !important; }
            </style>
            """,
            unsafe_allow_html=True,
        )

    # Export data section (CSV/Excel)
    st.markdown("---")
    st.markdown("## 📤 Export Data")
    e1, e2 = st.columns(2)
    with e1:
        csv = daily_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"solar_export_{city}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
            help="Download data in CSV format with dates included",
        )
    with e2:
        excel_file = "solar_export.xlsx"
        daily_df.to_excel(excel_file, index=False)
        with open(excel_file, "rb") as f:
            st.download_button(
                label="📥 Download Excel",
                data=f,
                file_name=f"solar_export_{city}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                help="Download data in Excel format with dates included",
            )

    footer(city)


if __name__ == "__main__":
    run()

