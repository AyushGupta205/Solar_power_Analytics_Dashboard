# ☀️ Solar Power Analytics Dashboard

An interactive Streamlit dashboard that simulates and visualizes solar energy production using real-time weather data from OpenWeather. It provides estimates of daily, monthly, and annual energy, cost savings, and intuitive charts of system performance.

## Quick Start

1. Install Python 3.10+.
2. Create a virtual environment and activate it.
   - Windows (PowerShell):
     ```powershell
     py -3.10 -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - macOS/Linux (bash):
     ```bash
     python3.10 -m venv .venv
     source .venv/bin/activate
     ```
3. Install dependencies:
   
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with your OpenWeather API key:
   
   ```env
   OPENWEATHER_API_KEY=YOUR_OPENWEATHER_KEY
   ```
   - Get a free API key from: https://openweathermap.org/api

5. Run the app:
   
   ```bash
   streamlit run app/main.py
   ```
   - Streamlit will open in your browser at http://localhost:8501 by default.

## Project Structure

```
app/
  config.py                 # Loads and validates OPENWEATHER_API_KEY from .env
  main.py                   # App entrypoint; orchestrates UI, data, charts, exports
  services/
    weather.py              # Weather + geocode fetch, sunlight hours, caching
  ui/
    layout.py               # Page config, sidebar, footer
    charts.py               # Plotly figure builders (daily, hourly, monthly, perf)
  utils/
    calculations.py         # Core math: profiles, metrics, dataframes
requirements.txt
solarew.py                  # Legacy monolithic prototype (commented for reference)
```

## Features

- Real-time weather-driven simulation (temperature, clouds, wind, description).
- Configurable system inputs (city, panel count, panel wattage, timeframe).
- Daily/Monthly/Annual energy estimates and cost savings (₹ at ₹8/kWh default).
- Interactive charts (Plotly): daily production, hourly output, performance ratio, monthly projections.
- CSV and Excel export for daily production data.
- Robust error handling and API fallback via geocoding when city lookup fails.

## Key Technologies

- Streamlit UI (`streamlit`, `streamlit-extras`)
- Data and math (`pandas`, `numpy`)
- Charts (`plotly`)
- Weather API (`requests`, OpenWeather)
- Config and exports (`python-dotenv`, `openpyxl`)

## How It Works

- The main flow is in `app/main.py`:
  - Reads user inputs from `ui/layout.py: render_sidebar()`.
  - Calls `services/weather.py: get_weather_data(city)` which:
    - Queries OpenWeather by name; on failure, geocodes name to coordinates and retries by lat/lon.
    - Shapes the API payload, estimating `sunlight_hours` from sunrise/sunset when available, or falls back to a city-specific baseline.
  - Computes total capacity, base energy, temperature effect, and final daily energy.
  - Generates realistic hourly and daily profiles and builds dataframes via `utils/calculations.py`.
  - Renders tabs with charts from `ui/charts.py` and provides CSV/Excel exports.

### Core Calculations (in `app/utils/calculations.py`)

- `calculate_temp_effect(temperature: float) -> float`
  - Multiplier for energy production with a baseline of 25°C and -0.3% per °C above 25°C.

- `generate_timeframes(timeframe: str) -> (pd.DatetimeIndex, int)`
  - Returns a date range and number of days for: 7/14/30/90 days or 1 Year.

- `generate_hour_marks() -> pd.DatetimeIndex`
  - Returns 24 hourly timestamps for the current day.

- `generate_profiles(energy: float, days: int) -> (List[float], List[float])`
  - Builds a Gaussian-like bell curve for hourly production and a list of daily energies with realistic random variation.

- `build_dataframes(date_range, hours, daily_energy, hourly_pattern)`
  - Returns three DataFrames:
    - `daily_df`: columns `Date`, `Energy (kWh)`, `Day`, `DayOfWeek`, `Month`, `Year`.
    - `hourly_df`: columns `Hour`, `Energy (kWh)`, `Time`.
    - `monthly_df`: aggregated monthly sums with a `Date` column at month start.

- `compute_core_metrics(total_capacity, energy, daily_energy, sunlight_hours, electricity_rate=8.0)`
  - Computes `monthly_estimate`, `annual_estimate`, `daily_savings`, `monthly_savings`, `annual_savings`, `total_energy`, `avg_daily`, and `system_efficiency`.

- `compute_daily_impact(energy)`
  - Converts daily kWh into relatable usage such as TV hours, fan hours, LED bulbs, and phone charges.

### Weather and Sunlight Hours (in `app/services/weather.py`)

- `get_weather_data(city)`
  - Cached for 1 hour. Uses API key from `app/config.py:get_api_key()`.
  - On "city not found", geocodes the name to `(lat, lon)` and retries.
  - Shapes to include: temperature, humidity, wind, clouds, description, icon, and `sunlight_hours`.

- `get_sunlight_hours(city)`
  - City-specific baseline sunlight hours for common Indian cities; default 5.5 hours.

## Configuration

- Create a `.env` file with `OPENWEATHER_API_KEY`.
- `app/config.py:get_api_key()` loads the key and stops the app with a helpful message if missing.
- Electricity rate defaults to ₹8/kWh; you can change it by passing a custom `electricity_rate` to `compute_core_metrics()` or adjusting the call site in `app/main.py`.
- Caching: API results are cached for 1 hour using Streamlit's caching (`@cache_data`).

## Running & Usage

- Start the app and use the sidebar to set:
  - City (e.g., "Delhi", "Mumbai").
  - Number of Panels and Panel Wattage.
  - Timeframe (7/14/30/90 days, or 1 Year).
- Explore the tabs:
  - Dashboard: Key metrics, daily chart with 7-day average, hourly generation, savings and impact.
  - Monthly: System overview + monthly projections with target line.
  - System: Performance ratio and KPIs.

### Tips

- Use full city names or include a country code for ambiguous locations (e.g., `Paris, FR`).
- If a city name fails, the app will attempt geocoding via OpenWeather and retry by coordinates.

## Exports

- Download `CSV` and `Excel` of daily production from within the app. The Excel is produced on-the-fly as `solar_export.xlsx` and streamed to the user.

## Troubleshooting

- Missing API Key:
  - Ensure `.env` exists and contains `OPENWEATHER_API_KEY`. The app will show a Streamlit error and stop if missing.
- City not found:
  - Try a larger nearby city or include country code (e.g., `Paris, FR`). Geocoding fallback is automatic when possible.
- Network/API issues:
  - Errors are displayed in the UI. Data requests are cached for 1 hour to reduce API load.
- Empty charts:
  - Ensure valid inputs and that weather data was fetched successfully.

- Windows PowerShell execution policy:
  - If `.venv\Scripts\Activate.ps1` is blocked, run PowerShell as Administrator and temporarily allow scripts:
    ```powershell
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    ```
    Then activate the venv again.

- Corporate proxy/firewall:
  - If API calls fail, ensure `api.openweathermap.org` is reachable or configure your proxy settings for `requests`.

## Notes

- `solarew.py` is a legacy monolithic version retained only for reference. The modular app entrypoint is `app/main.py`.
- The simulation uses reasonable assumptions and randomness for illustrative purposes and is not intended for engineering-grade forecasting.

## Development

- Project layout is modular under `app/` with clear separation of config, services, UI, and utils.
- When editing code, prefer updating the functions in:
  - `app/services/weather.py` for API and sunlight hours.
  - `app/utils/calculations.py` for computation logic and dataframes.
  - `app/ui/charts.py` for visualization.
  - `app/ui/layout.py` for page style and sidebar.

### Dependency versions

See `requirements.txt` for pinned/compatible versions used by the app.

## Screenshots (Optional)

Add screenshots to illustrate the Dashboard, Monthly, and System tabs if desired:

```
assets/
  dashboard.png
  monthly.png
  system.png
```

Then reference them here with Markdown image links.
