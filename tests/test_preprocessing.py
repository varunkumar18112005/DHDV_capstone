"""
Unit tests for data preprocessing and cleaning module.
"""

import pytest
import pandas as pd
import numpy as np
from modules.preprocessing import TradeDataPreprocessor
from utils.country_mapping import get_country_iso3, standardize_country_name

def test_missing_values_handling():
    """Test 4: Verify null records in critical fields are removed and counted."""
    raw_data = pd.DataFrame({
        "year": [2023, None, 2023, 2023],
        "reporter": ["United States", "China", None, "Germany"],
        "partner": ["China", "Germany", "Japan", None],
        "product": ["Electronics", "Machinery", "Automotive", "Chemicals"],
        "trade_flow": ["Export", "Import", "Export", "Import"],
        "trade_value": [50.0, 30.0, 20.0, 40.0]
    })
    
    preprocessor = TradeDataPreprocessor()
    cleaned_df, stats = preprocessor.clean_trade_data(raw_data)
    
    assert len(cleaned_df) == 1
    assert stats["missing_records"] == 3
    assert cleaned_df.iloc[0]["reporter"] == "United States"

def test_invalid_trade_values():
    """Test 5: Verify negative, zero, and infinite trade values are removed."""
    raw_data = pd.DataFrame({
        "year": [2023, 2023, 2023, 2023, 2023],
        "reporter": ["USA", "USA", "USA", "USA", "USA"],
        "partner": ["China", "Germany", "Japan", "UK", "France"],
        "product": ["Electronics", "Machinery", "Automotive", "Chemicals", "Metals"],
        "trade_flow": ["Export", "Export", "Export", "Export", "Export"],
        "trade_value": [100.0, -10.0, 0.0, np.nan, np.inf]
    })
    
    preprocessor = TradeDataPreprocessor()
    cleaned_df, stats = preprocessor.clean_trade_data(raw_data)
    
    assert len(cleaned_df) == 1
    assert cleaned_df.iloc[0]["trade_value"] == 100.0
    assert stats["invalid_records"] == 3

def test_duplicate_removal():
    """Verify duplicate records are pruned."""
    raw_data = pd.DataFrame({
        "year": [2023, 2023, 2023],
        "reporter": ["India", "India", "India"],
        "partner": ["USA", "USA", "Germany"],
        "product": ["Pharmaceuticals", "Pharmaceuticals", "Textiles"],
        "trade_flow": ["Export", "Export", "Export"],
        "trade_value": [15.0, 15.0, 25.0]
    })
    
    preprocessor = TradeDataPreprocessor()
    cleaned_df, stats = preprocessor.clean_trade_data(raw_data)
    
    assert len(cleaned_df) == 2
    assert stats["removed_duplicates"] == 1

def test_country_mapping_and_iso():
    """Test 6: Verify country name standardization and ISO-3 resolution."""
    assert get_country_iso3("United States") == "USA"
    assert get_country_iso3("USA") == "USA"
    assert get_country_iso3("India") == "IND"
    assert get_country_iso3("Germany") == "DEU"
    assert get_country_iso3("China") == "CHN"
    
    assert standardize_country_name("USA") == "United States"
    assert standardize_country_name("DEU") == "Germany"
    assert standardize_country_name("UK") == "United Kingdom"
