from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


def calculate_temp_effect(temperature: float) -> float:
    """Return multiplier for energy production based on temperature.
    Baseline 25°C, -0.3% per °C above 25.
    """
    return 1 + (temperature - 25) * -0.3 / 100


def generate_timeframes(timeframe: str) -> Tuple[pd.DatetimeIndex, int]:
    days = 7 if "7" in timeframe else (14 if "14" in timeframe else (30 if "30" in timeframe else 90))
    days = 365 if timeframe == "1 Year" else days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days - 1)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    return date_range, days


def generate_hour_marks() -> pd.DatetimeIndex:
    return pd.date_range(start=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0), periods=24, freq='H')


def generate_profiles(energy: float, days: int) -> Tuple[List[float], List[float]]:
    """Generate hourly pattern and daily energy list with realistic variations."""
    np.random.seed(42)
    hourly_pattern: List[float] = []

    # Typical bell curve across 24 hours
    for h in range(24):
        hour_effect = np.exp(-((h - 12) ** 2) / 18)
        hour_effect *= (0.9 + 0.2 * np.random.random())
        hourly_pattern.append(hour_effect)

    hourly_pattern = [p / sum(hourly_pattern) * energy for p in hourly_pattern]

    daily_energy: List[float] = []
    for _ in range(days):
        day_variation = 0.8 + 0.4 * np.random.random()
        daily_energy.append(energy * day_variation)

    return hourly_pattern, daily_energy


def build_dataframes(date_range: pd.DatetimeIndex, hours: pd.DatetimeIndex, daily_energy: List[float], hourly_pattern: List[float]) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    daily_df = pd.DataFrame({
        'Date': [d.strftime('%Y-%m-%d') for d in date_range],
        'Energy (kWh)': daily_energy,
        'Day': [d.strftime('%a') for d in date_range],
        'DayOfWeek': [d.weekday() for d in date_range],
        'Month': [d.strftime('%b') for d in date_range],
        'Year': [d.year for d in date_range],
    }).drop_duplicates(subset=['Date'], keep='first')

    hourly_df = pd.DataFrame({
        'Hour': [h.hour for h in hours],
        'Energy (kWh)': hourly_pattern,
        'Time': [h.strftime('%H:%M') for h in hours],
    })

    monthly_df = daily_df.groupby(['Year', 'Month'])['Energy (kWh)'].sum().reset_index()
    monthly_df['Date'] = pd.to_datetime(monthly_df['Year'].astype(str) + '-' + monthly_df['Month'] + '-01')

    return daily_df, hourly_df, monthly_df


def compute_core_metrics(total_capacity: float, energy: float, daily_energy: List[float], sunlight_hours: float, electricity_rate: float = 8.0) -> Dict[str, float]:
    monthly_estimate = energy * 30
    annual_estimate = energy * 365

    daily_savings = energy * electricity_rate
    monthly_savings = daily_savings * 30
    annual_savings = daily_savings * 365

    total_energy = float(sum(daily_energy)) if daily_energy else 0.0
    avg_daily = float(np.mean(daily_energy)) if daily_energy else 0.0

    return {
        'monthly_estimate': monthly_estimate,
        'annual_estimate': annual_estimate,
        'daily_savings': daily_savings,
        'monthly_savings': monthly_savings,
        'annual_savings': annual_savings,
        'total_energy': total_energy,
        'avg_daily': avg_daily,
        'system_efficiency': (avg_daily / (total_capacity * 5.5)) * 100 if total_capacity > 0 else 0.0,
    }


def compute_daily_impact(energy: float) -> Dict[str, float]:
    return {
        'tv_hours': (energy * 0.8) / 0.1,
        'fan_hours': (energy * 0.8) / 0.07,
        'bulb_hours': (energy * 0.8) / 0.01,
        'phone_charges': (energy * 0.8) / 0.005,
    }
