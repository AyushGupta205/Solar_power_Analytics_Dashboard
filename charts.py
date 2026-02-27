from __future__ import annotations

from datetime import datetime
from typing import List

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def daily_production_chart(date_range: pd.DatetimeIndex, daily_energy: List[float], days: int) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=date_range,
        y=daily_energy,
        name='Daily Production',
        marker_color='#00b4d8',
        hovertemplate='%{y:.1f} kWh<extra></extra>',
        opacity=0.8,
    ))

    rolling_avg = pd.Series(daily_energy).rolling(window=7).mean()
    fig.add_trace(go.Scatter(
        x=date_range,
        y=rolling_avg,
        name='7-Day Average',
        line=dict(color='#ff6b6b', width=3),
        hovertemplate='7-Day Avg: %{y:.2f} kWh<extra></extra>',
        mode='lines+markers',
        marker=dict(size=5),
    ))

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            showgrid=False,
            title='Date',
            rangeslider_visible=True if days > 30 else False,
            rangeselector=dict(
                buttons=[
                    dict(count=7, label="1w", step="day", stepmode="backward"),
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(step="all", label="All"),
                ] if days > 30 else []
            ),
        ),
        yaxis=dict(
            title='Energy (kWh)',
            showgrid=True,
            gridcolor='rgba(200,200,200,0.2)',
            zeroline=False,
        ),
        hovermode='x unified',
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=40, b=20),
        height=400,
    )

    if days > 7:
        max_idx = int(np.argmax(daily_energy))
        min_idx = int(np.argmin(daily_energy))
        fig.add_annotation(x=date_range[max_idx], y=daily_energy[max_idx], text=f"Peak: {daily_energy[max_idx]:.1f} kWh", showarrow=True, arrowhead=1, ax=0, ay=-40)
        fig.add_annotation(x=date_range[min_idx], y=daily_energy[min_idx], text=f"Lowest: {daily_energy[min_idx]:.1f} kWh", showarrow=True, arrowhead=1, ax=0, ay=40)

    return fig


def hourly_energy_chart(hours_labels: List[str], hourly_energy: List[float], total_capacity: float) -> go.Figure:
    from datetime import datetime
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hours_labels,
        y=hourly_energy,
        fill='tozeroy',
        mode='lines+markers',
        name='Power Output',
        line=dict(color='#00b4d8', width=3),
        fillcolor='rgba(0, 180, 216, 0.2)',
        hovertemplate='%{y:.2f} kW<extra></extra>',
    ))

    sunrise = 6
    sunset = 18
    current_hour = datetime.now().hour
    fig.add_vline(x=sunrise, line_dash="dash", line_color="orange", annotation_text="Sunrise", annotation_position="top")
    fig.add_vline(x=sunset, line_dash="dash", line_color="purple", annotation_text="Sunset", annotation_position="top")
    if 0 <= current_hour <= 23:
        fig.add_vline(x=current_hour, line_color="red", annotation_text="Now", annotation_position="bottom")

    max_possible = total_capacity * 0.9
    peak_value = float(np.max(hourly_energy)) if hourly_energy else 0.0
    efficiency = (peak_value / max_possible) * 100 if max_possible > 0 else 0.0

    fig.add_annotation(x=hours_labels[int(np.argmax(hourly_energy))] if hourly_energy else 0,
                       y=peak_value,
                       text=f"Peak: {peak_value:.2f} kW",
                       showarrow=True, arrowhead=1, ax=0, ay=-40)
    fig.add_annotation(x=0.5, y=1.1, xref='paper', yref='paper', text=f"System Efficiency: {efficiency:.1f}% of maximum capacity", showarrow=False, font=dict(size=12, color='gray'))

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title='Time of Day', showgrid=False, tickmode='array', tickangle=45),
        yaxis=dict(title='Power Output (kW)', showgrid=True, gridcolor='rgba(200,200,200,0.2)', zeroline=False),
        hovermode='x unified', showlegend=False, margin=dict(l=20, r=20, t=40, b=60), height=400,
    )
    return fig


def performance_chart(date_range: pd.DatetimeIndex, daily_energy: List[float], total_capacity: float) -> go.Figure:
    performance_ratio = [min(100, (e / (total_capacity * 5.5)) * 100) if total_capacity > 0 else 0 for e in daily_energy]
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Bar(
        x=date_range,
        y=daily_energy,
        name='Daily Production',
        marker_color='#00b4d8',
        opacity=0.8,
        hovertemplate='%{x|%b %d}: %{y:.1f} kWh<extra></extra>'
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=date_range,
        y=performance_ratio,
        name='Efficiency %',
        line=dict(color='#00b4d8', width=3),
        mode='lines+markers',
        hovertemplate='%{y:.1f}%<extra></extra>',
        yaxis='y2',
    ), secondary_y=True)

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=50, r=50, t=40, b=40), height=350,
        showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(title=None, showgrid=False, tickformat='%b %d'),
        yaxis=dict(title='Energy (kWh)', showgrid=True, gridcolor='rgba(200,200,200,0.2)', zeroline=False),
        yaxis2=dict(title='Efficiency %', overlaying='y', side='right', range=[0, 110], showgrid=False),
        hovermode='x unified', hoverlabel=dict(bgcolor='white', font_size=12, font_family="Arial"),
    )

    max_day = date_range[int(np.argmax(daily_energy))] if len(daily_energy) else None
    if max_day is not None:
        fig.add_annotation(x=max_day, y=max(daily_energy), text=f"Peak: {max(daily_energy):.1f} kWh", showarrow=True, arrowhead=1, ax=0, ay=-40, font=dict(color="#ff9f43"))

    return fig


def monthly_chart(df_monthly: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_monthly['Month'],
        y=df_monthly['Energy (kWh)'],
        name='Actual',
        marker_color='#00b4d8',
        text=df_monthly['Energy (kWh)'].round(0).astype(int).astype(str) + ' kWh',
        textposition='auto',
    ))

    fig.add_trace(go.Scatter(
        x=df_monthly['Month'],
        y=df_monthly['Target'],
        name='Target',
        mode='lines+markers',
        line=dict(color='#ff6b6b', width=2, dash='dash'),
        marker=dict(symbol='diamond', size=8),
    ))

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title='Month', showgrid=False, type='category'),
        yaxis=dict(title='Energy (kWh)', showgrid=True, gridcolor='rgba(200,200,200,0.2)', zeroline=False),
        hovermode='x unified', showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=40, b=20), height=450,
    )

    if len(df_monthly):
        best_month = df_monthly.loc[df_monthly['Energy (kWh)'].idxmax()]
        worst_month = df_monthly.loc[df_monthly['Energy (kWh)'].idxmin()]
        fig.add_annotation(x=best_month['Month'], y=best_month['Energy (kWh)'], text=f"Best Month: {best_month['Energy (kWh)']/1000:.1f} MWh", showarrow=True, arrowhead=1, ax=0, ay=-40, font=dict(color="#06d6a0"))
        fig.add_annotation(x=worst_month['Month'], y=worst_month['Energy (kWh)'], text=f"Lowest: {worst_month['Energy (kWh)']/1000:.1f} MWh", showarrow=True, arrowhead=1, ax=0, ay=40, font=dict(color="#ff6b6b"))

    return fig
