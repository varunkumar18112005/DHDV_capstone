"""
Trend Analysis and Moving Average module.
Computes multi-year trade trajectories, rolling moving averages (3, 5, 7 years),
and rule-based quantitative trend momentum classifications.
"""

import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, Optional

def calculate_trend_analytics(df_yearly: pd.DataFrame, window_size: int = 3) -> Dict[str, Any]:
    r"""
    Calculate quantitative analytics and trend classification from yearly trade series.
    
    Formula for Moving Average:
      MA_t(n) = (1 / n) * \sum_{i=0}^{n-1} Y_{t-i}
      
    Rule-based Trend Classification:
      Compute linear slope beta of normalized trade series.
      If beta > +0.02 (2%/yr) -> "Increasing Trend"
      If beta < -0.02 (-2%/yr) -> "Decreasing Trend"
      Else -> "Stable Trend"
    
    Args:
        df_yearly: Yearly aggregated trade DataFrame with [Year, Total Trade, Exports, Imports].
        window_size: Rolling window (3, 5, 7).
        
    Returns:
        Dictionary of trend metrics and badges.
    """
    if df_yearly is None or df_yearly.empty:
        return {
            "total_growth_pct": 0.0,
            "avg_annual_trade": 0.0,
            "max_year": "N/A",
            "max_value": 0.0,
            "min_year": "N/A",
            "min_value": 0.0,
            "latest_trade": 0.0,
            "latest_ma": 0.0,
            "latest_yoy_growth": 0.0,
            "trend_classification": "Stable Trend",
            "trend_badge_color": "#3B82F6",
            "trend_explanation": "Insufficient historical points."
        }
        
    df_sorted = df_yearly.sort_values(by="Year").reset_index(drop=True)
    trades = df_sorted["Total Trade"].values
    years = df_sorted["Year"].values
    
    # Calculate rolling MA
    ma_series = df_sorted["Total Trade"].rolling(window=window_size, min_periods=1).mean().values
    
    # Key analytics
    first_val = trades[0]
    latest_val = trades[-1]
    total_growth_pct = ((latest_val - first_val) / first_val * 100.0) if first_val > 0 else 0.0
    avg_annual_trade = float(np.mean(trades))
    
    max_idx = int(np.argmax(trades))
    min_idx = int(np.argmin(trades))
    max_year, max_value = int(years[max_idx]), float(trades[max_idx])
    min_year, min_value = int(years[min_idx]), float(trades[min_idx])
    
    latest_ma = float(ma_series[-1])
    
    # Latest YoY Growth
    if len(trades) >= 2 and trades[-2] > 0:
        latest_yoy_growth = ((latest_val - trades[-2]) / trades[-2]) * 100.0
    else:
        latest_yoy_growth = 0.0
        
    # Quantitative Trend Classification via Normalized Ordinary Least Squares (OLS) Slope
    if len(years) >= 3:
        x = np.arange(len(years))
        y_norm = trades / np.mean(trades)
        slope, _ = np.polyfit(x, y_norm, 1) # slope represents annual normalized growth rate
        
        if slope > 0.025:
            classification = "Increasing Trend"
            badge_color = "#10B981" # Green
            explanation = f"Consistent upward trajectory (+{slope*100:.1f}% annual momentum)."
        elif slope < -0.025:
            classification = "Decreasing Trend"
            badge_color = "#EF4444" # Red
            explanation = f"Downward trade trajectory ({slope*100:.1f}% annual contraction)."
        else:
            classification = "Stable Trend"
            badge_color = "#3B82F6" # Blue
            explanation = f"Stable trade volume within ±2.5% annual variance."
    else:
        classification = "Stable Trend"
        badge_color = "#3B82F6"
        explanation = "Baseline stable trend."
        
    return {
        "total_growth_pct": round(total_growth_pct, 2),
        "avg_annual_trade": round(avg_annual_trade, 2),
        "max_year": max_year,
        "max_value": round(max_value, 2),
        "min_year": min_year,
        "min_value": round(min_value, 2),
        "latest_trade": round(latest_val, 2),
        "latest_ma": round(latest_ma, 2),
        "latest_yoy_growth": round(latest_yoy_growth, 2),
        "trend_classification": classification,
        "trend_badge_color": badge_color,
        "trend_explanation": explanation
    }

def create_trend_chart(
    df_yearly: pd.DataFrame,
    window_size: int = 3,
    title: Optional[str] = None
) -> go.Figure:
    """
    Generate interactive time-series chart showing Actual Trade vs Moving Average.
    
    Args:
        df_yearly: Yearly aggregated trade DataFrame with [Year, Total Trade, Exports, Imports].
        window_size: Moving average window (3, 5, 7).
        title: Custom chart title.
        
    Returns:
        Plotly Graph Objects Figure.
    """
    if df_yearly is None or df_yearly.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No historical trade series available.",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="#94A3B8")
        )
        fig.update_layout(template="plotly_dark", paper_bgcolor="#0F172A", plot_bgcolor="#0F172A")
        return fig
        
    df_sorted = df_yearly.sort_values(by="Year").reset_index(drop=True)
    ma_col = f"MA ({window_size}Y)"
    df_sorted[ma_col] = df_sorted["Total Trade"].rolling(window=window_size, min_periods=1).mean().round(2)
    
    fig = go.Figure()
    
    # 1. Total Trade Bars or Shaded Area
    fig.add_trace(go.Bar(
        x=df_sorted["Year"],
        y=df_sorted["Total Trade"],
        name="Actual Annual Trade",
        marker=dict(
            color="rgba(99, 102, 241, 0.4)",
            line=dict(color="#6366F1", width=1.5)
        ),
        hovertemplate="<b>Year %{x}</b><br>Actual Trade: $%{y:,.2f} B<extra></extra>"
    ))
    
    # 2. Exports Trace
    if "Exports" in df_sorted.columns:
        fig.add_trace(go.Scatter(
            x=df_sorted["Year"],
            y=df_sorted["Exports"],
            name="Exports",
            mode="lines+markers",
            line=dict(color="#10B981", width=2, dash="dot"),
            marker=dict(size=6, symbol="circle"),
            hovertemplate="Exports: $%{y:,.2f} B<extra></extra>"
        ))
        
    # 3. Imports Trace
    if "Imports" in df_sorted.columns:
        fig.add_trace(go.Scatter(
            x=df_sorted["Year"],
            y=df_sorted["Imports"],
            name="Imports",
            mode="lines+markers",
            line=dict(color="#3B82F6", width=2, dash="dot"),
            marker=dict(size=6, symbol="diamond"),
            hovertemplate="Imports: $%{y:,.2f} B<extra></extra>"
        ))
        
    # 4. Moving Average Line
    fig.add_trace(go.Scatter(
        x=df_sorted["Year"],
        y=df_sorted[ma_col],
        name=f"{window_size}-Year Moving Avg",
        mode="lines+markers",
        line=dict(color="#F59E0B", width=3.5),
        marker=dict(size=8, color="#F59E0B", symbol="star"),
        hovertemplate=f"<b>{window_size}-Year MA:</b> $%{{y:,.2f}} B<extra></extra>"
    ))
    
    chart_title = title or f"<b>Annual Trade Trend & {window_size}-Year Moving Average</b>"
    
    fig.update_layout(
        title=dict(
            text=chart_title,
            font=dict(size=18, color="#F8FAFC", family="Arial, sans-serif"),
            x=0.02, y=0.96
        ),
        xaxis=dict(
            title="Year",
            type="category",
            gridcolor="#334155",
            tickfont=dict(color="#E2E8F0", size=12),
            title_font=dict(color="#E2E8F0", size=13)
        ),
        yaxis=dict(
            title="Trade Value ($ Billion USD)",
            gridcolor="#334155",
            tickfont=dict(color="#E2E8F0", size=12),
            title_font=dict(color="#E2E8F0", size=13)
        ),
        font=dict(size=12, color="#E2E8F0"),
        paper_bgcolor="#0F172A",
        plot_bgcolor="#0F172A",
        legend=dict(
            bgcolor="rgba(15, 23, 42, 0.7)",
            bordercolor="#334155",
            borderwidth=1,
            font=dict(color="#E2E8F0", size=11),
            orientation="h",
            yanchor="top",
            y=-0.18,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=20, r=20, t=50, b=70),
        height=450
    )
    
    return fig
