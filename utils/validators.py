"""
Validation utilities for data integrity, user inputs, and schemas.
"""

from typing import Tuple, List, Dict, Any
import pandas as pd

REQUIRED_TRADE_COLUMNS = [
    "year",
    "reporter",
    "partner",
    "product",
    "trade_flow",
    "trade_value"
]

def validate_trade_dataframe(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validate trade DataFrame schema and basic constraints.
    
    Args:
        df: Pandas DataFrame to validate.
        
    Returns:
        Tuple of (is_valid, list_of_errors).
    """
    errors = []
    if df is None or not isinstance(df, pd.DataFrame):
        return False, ["Input is not a valid pandas DataFrame."]
    
    if df.empty:
        return False, ["DataFrame is empty."]
    
    missing_cols = [col for col in REQUIRED_TRADE_COLUMNS if col not in df.columns]
    if missing_cols:
        errors.append(f"Missing required columns: {', '.join(missing_cols)}")
        
    return len(errors) == 0, errors

def validate_filter_inputs(
    year: int,
    reporter: str,
    flow: str,
    valid_years: List[int],
    valid_reporters: List[str]
) -> Tuple[bool, str]:
    """
    Validate dashboard filter user selections.
    """
    if valid_years and year not in valid_years:
        return False, f"Selected year {year} is not in available dataset range."
    if valid_reporters and reporter != "All Countries" and reporter not in valid_reporters:
        return False, f"Selected country '{reporter}' is not recognized in dataset."
    if flow not in ["Both", "Exports", "Imports", "Export", "Import"]:
        return False, f"Invalid trade flow: {flow}"
    return True, "Valid"
