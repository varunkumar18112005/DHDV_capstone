"""
Unit tests for Trend Analysis and Moving Average calculations.
"""

import pytest
import pandas as pd
import numpy as np
from modules.trend_analysis import calculate_trend_analytics, create_trend_chart
from modules.calculations import generate_yearly_summary

def test_moving_average_calculation():
    """
    Test 3: Verify n-year rolling moving average calculation.
    Values: [100, 120, 140, 160]
    3-year MA at index 2 (yr 3): (100 + 120 + 140) / 3 = 120.0
    3-year MA at index 3 (yr 4): (120 + 140 + 160) / 3 = 140.0
    """
    df_yearly = pd.DataFrame({
        "Year": [2020, 2021, 2022, 2023],
        "Total Trade": [100.0, 120.0, 140.0, 160.0],
        "Exports": [60.0, 70.0, 80.0, 90.0],
        "Imports": [40.0, 50.0, 60.0, 70.0]
    })
    
    analytics = calculate_trend_analytics(df_yearly, window_size=3)
    
    assert analytics["latest_trade"] == 160.0
    assert analytics["latest_ma"] == 140.0 # (120 + 140 + 160) / 3
    assert analytics["trend_classification"] == "Increasing Trend"
    assert analytics["max_year"] == 2023
    assert analytics["min_year"] == 2020

def test_decreasing_trend_classification():
    """Verify decreasing trend classification when trade volume contracts."""
    df_decreasing = pd.DataFrame({
        "Year": [2020, 2021, 2022, 2023],
        "Total Trade": [200.0, 170.0, 140.0, 110.0],
        "Exports": [120.0, 100.0, 80.0, 60.0],
        "Imports": [80.0, 70.0, 60.0, 50.0]
    })
    
    analytics = calculate_trend_analytics(df_decreasing, window_size=3)
    assert analytics["trend_classification"] == "Decreasing Trend"
    assert analytics["max_year"] == 2020
    assert analytics["min_year"] == 2023

def test_trend_chart_generation():
    """Verify Plotly figure generation for trends."""
    df_yearly = pd.DataFrame({
        "Year": [2021, 2022, 2023],
        "Total Trade": [100.0, 110.0, 120.0],
        "Exports": [60.0, 65.0, 70.0],
        "Imports": [40.0, 45.0, 50.0]
    })
    
    fig = create_trend_chart(df_yearly, window_size=3)
    assert len(fig.data) >= 3 # Actual Trade, Exports, Imports, MA
