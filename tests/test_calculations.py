"""
Unit tests for trade calculations and summary aggregations.
"""

import pytest
import pandas as pd
import numpy as np
from modules.calculations import (
    calculate_trade_metrics,
    generate_country_summary,
    generate_product_summary,
    generate_yearly_summary
)

def test_trade_balance_and_total_trade():
    """
    Test 1 & Test 2:
    Exports = 100, Imports = 60
    Expected Trade Balance = 40
    Expected Total Trade = 160
    """
    df = pd.DataFrame({
        "year": [2023, 2023],
        "reporter": ["Country A", "Country A"],
        "partner": ["Country B", "Country B"],
        "product": ["Machinery", "Electronics"],
        "trade_flow": ["Export", "Import"],
        "trade_value": [100.0, 60.0]
    })
    
    metrics = calculate_trade_metrics(df)
    
    assert metrics["total_exports"] == 100.0
    assert metrics["total_imports"] == 60.0
    assert metrics["trade_balance"] == 40.0 # Test 1
    assert metrics["total_trade"] == 160.0  # Test 2

def test_empty_dataset_calculations():
    """Test 8: Verify empty dataset returns graceful zeros without exception."""
    df_empty = pd.DataFrame()
    metrics = calculate_trade_metrics(df_empty)
    
    assert metrics["total_trade"] == 0.0
    assert metrics["total_exports"] == 0.0
    assert metrics["total_imports"] == 0.0
    assert metrics["trade_balance"] == 0.0
    assert metrics["yoy_growth"] == 0.0
    
    country_sum = generate_country_summary(df_empty)
    assert country_sum.empty
    
    prod_sum = generate_product_summary(df_empty)
    assert prod_sum.empty

def test_product_shares_and_growth():
    """Verify product export and import share calculations."""
    df = pd.DataFrame({
        "year": [2022, 2022, 2023, 2023],
        "reporter": ["USA", "USA", "USA", "USA"],
        "partner": ["China", "China", "China", "China"],
        "product": ["Electronics", "Machinery", "Electronics", "Machinery"],
        "trade_flow": ["Export", "Export", "Export", "Export"],
        "trade_value": [40.0, 60.0, 50.0, 75.0]
    })
    
    prod_sum = generate_product_summary(df)
    assert len(prod_sum) == 2
    
    total_val = prod_sum["Total Trade"].sum()
    assert round(total_val, 2) == 225.0
    assert round(prod_sum["Share %"].sum(), 1) == 100.0
    
    # YoY growth for Electronics: (50 - 40) / 40 * 100 = 25.0%
    elec_row = prod_sum[prod_sum["Product"] == "Electronics"].iloc[0]
    assert elec_row["YoY Growth %"] == 25.0
