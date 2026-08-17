"""
Data preprocessing and cleaning module.
Cleans raw trade datasets, standardizes entities, handles nulls/anomalies,
and records comprehensive data cleaning audit metrics.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, Optional
from pathlib import Path

from config.settings import PROCESSED_DATA_DIR, RAW_DATA_DIR
from utils.country_mapping import (
    standardize_country_name,
    get_country_iso3
)

class TradeDataPreprocessor:
    """
    Pipeline for cleaning and standardizing international trade data.
    """
    
    def __init__(self):
        self.stats: Dict[str, int] = {
            "original_records": 0,
            "removed_duplicates": 0,
            "missing_records": 0,
            "invalid_records": 0,
            "final_records": 0
        }
        
    def clean_trade_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
        """
        Clean and standardize raw trade dataframe.
        
        Args:
            df: Raw trade DataFrame.
            
        Returns:
            Tuple of (cleaned_df, cleaning_stats_dict).
        """
        if df is None or df.empty:
            return pd.DataFrame(), self.stats
            
        df_clean = df.copy()
        self.stats["original_records"] = len(df_clean)
        
        # 1. Remove Exact & Subset Duplicates
        subset_cols = ["year", "reporter", "partner", "product", "trade_flow"]
        available_subset = [c for c in subset_cols if c in df_clean.columns]
        before_dup = len(df_clean)
        df_clean = df_clean.drop_duplicates(subset=available_subset)
        self.stats["removed_duplicates"] = before_dup - len(df_clean)
        
        # 2. Handle Missing Values
        before_na = len(df_clean)
        critical_cols = ["year", "reporter", "partner", "trade_flow", "trade_value"]
        existing_crit = [c for c in critical_cols if c in df_clean.columns]
        df_clean = df_clean.dropna(subset=existing_crit)
        self.stats["missing_records"] = before_na - len(df_clean)
        
        # 3. Numeric Conversion & Validation
        df_clean["year"] = pd.to_numeric(df_clean["year"], errors="coerce")
        df_clean["trade_value"] = pd.to_numeric(df_clean["trade_value"], errors="coerce")
        
        # Filter valid year and trade values (trade_value must be > 0 and finite)
        before_invalid = len(df_clean)
        valid_mask = (
            df_clean["year"].notna() &
            (df_clean["year"] >= 1990) &
            (df_clean["year"] <= 2030) &
            df_clean["trade_value"].notna() &
            (df_clean["trade_value"] > 0) &
            np.isfinite(df_clean["trade_value"])
        )
        df_clean = df_clean[valid_mask]
        self.stats["invalid_records"] = before_invalid - len(df_clean)
        
        df_clean["year"] = df_clean["year"].astype(int)
        
        # 4. Standardize Country Names and ISO Codes
        df_clean["reporter"] = df_clean["reporter"].apply(standardize_country_name)
        df_clean["partner"] = df_clean["partner"].apply(standardize_country_name)
        
        if "reporter_iso" not in df_clean.columns or df_clean["reporter_iso"].isna().any():
            df_clean["reporter_iso"] = df_clean["reporter"].apply(get_country_iso3)
        if "partner_iso" not in df_clean.columns or df_clean["partner_iso"].isna().any():
            df_clean["partner_iso"] = df_clean["partner"].apply(get_country_iso3)
            
        # 5. Standardize Trade Flow
        flow_map = {
            "export": "Export", "exports": "Export", "x": "Export", "2": "Export",
            "import": "Import", "imports": "Import", "m": "Import", "1": "Import"
        }
        df_clean["trade_flow"] = df_clean["trade_flow"].astype(str).str.strip().str.lower().map(
            lambda x: flow_map.get(x, "Export" if "exp" in x else "Import")
        )
        
        # 6. Standardize Currency
        df_clean["currency"] = "USD"
        
        # Sort values
        df_clean = df_clean.sort_values(by=["year", "reporter", "partner", "product"])
        self.stats["final_records"] = len(df_clean)
        
        return df_clean, self.stats

def preprocess_and_save_all() -> Tuple[pd.DataFrame, Dict[str, int]]:
    """
    Run full preprocessing pipeline on raw trade data and save cleaned output.
    """
    raw_path = RAW_DATA_DIR / "trade_data.csv"
    if not raw_path.exists():
        from scripts.generate_seed_data import generate_seed_trade_data
        generate_seed_trade_data()
        
    df_raw = pd.read_csv(raw_path)
    preprocessor = TradeDataPreprocessor()
    df_cleaned, stats = preprocessor.clean_trade_data(df_raw)
    
    # Save cleaned trade data
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    cleaned_out = PROCESSED_DATA_DIR / "cleaned_trade.csv"
    df_cleaned.to_csv(cleaned_out, index=False)
    
    return df_cleaned, stats
