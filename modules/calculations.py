"""
Trade metrics calculations and summary aggregations module.
Computes Total Trade, Trade Balance, Export/Import shares, YoY growth rates,
rolling moving averages, and exports structured summary tables.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, Tuple
from pathlib import Path

from config.settings import PROCESSED_DATA_DIR, RAW_DATA_DIR
from utils.country_mapping import ISO3_TO_NAME

def calculate_trade_metrics(df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate top-level KPI metrics for given trade DataFrame.
    
    Args:
        df: Cleaned trade records DataFrame.
        
    Returns:
        Dict with total_trade, total_exports, total_imports, trade_balance, yoy_growth.
    """
    if df is None or df.empty:
        return {
            "total_trade": 0.0,
            "total_exports": 0.0,
            "total_imports": 0.0,
            "trade_balance": 0.0,
            "yoy_growth": 0.0
        }
        
    exports = df[df["trade_flow"] == "Export"]["trade_value"].sum()
    imports = df[df["trade_flow"] == "Import"]["trade_value"].sum()
    total_trade = exports + imports
    trade_balance = exports - imports
    
    # Calculate YoY growth if multiple years present
    years = sorted(df["year"].unique())
    yoy_growth = 0.0
    if len(years) >= 2:
        curr_yr = years[-1]
        prev_yr = years[-2]
        curr_val = df[df["year"] == curr_yr]["trade_value"].sum()
        prev_val = df[df["year"] == prev_yr]["trade_value"].sum()
        if prev_val > 0:
            yoy_growth = ((curr_val - prev_val) / prev_val) * 100.0
            
    return {
        "total_trade": round(total_trade, 2),
        "total_exports": round(exports, 2),
        "total_imports": round(imports, 2),
        "trade_balance": round(trade_balance, 2),
        "yoy_growth": round(yoy_growth, 2)
    }

def generate_country_summary(
    df_trade: pd.DataFrame,
    df_gdp: Optional[pd.DataFrame] = None,
    include_all_countries: bool = True
) -> pd.DataFrame:
    """
    Generate Country Summary table with Exports, Imports, Total Trade, Trade Balance, and GDP.
    Ensures all recognized global countries are represented for complete geospatial mapping.
    """
    if not include_all_countries and (df_trade is None or df_trade.empty):
        return pd.DataFrame(columns=["Country", "ISO3", "Exports", "Imports", "Total Trade", "Trade Balance", "GDP"])
        
    all_countries_df = pd.DataFrame([
        {"Country": name, "ISO3": iso3} for iso3, name in ISO3_TO_NAME.items()
    ])
    
    if df_trade is None or df_trade.empty:
        grouped = all_countries_df.copy()
        grouped["Exports"] = 0.0
        grouped["Imports"] = 0.0
        grouped["Total Trade"] = 0.0
        grouped["Trade Balance"] = 0.0
    else:
        # Group by reporter
        trade_grouped = df_trade.groupby(["reporter_iso", "trade_flow"])["trade_value"].sum().unstack(fill_value=0.0).reset_index()
        
        if "Export" not in trade_grouped.columns:
            trade_grouped["Export"] = 0.0
        if "Import" not in trade_grouped.columns:
            trade_grouped["Import"] = 0.0
            
        trade_grouped["Total Trade"] = trade_grouped["Export"] + trade_grouped["Import"]
        trade_grouped["Trade Balance"] = trade_grouped["Export"] - trade_grouped["Import"]
        
        trade_grouped = trade_grouped.rename(columns={
            "reporter_iso": "ISO3",
            "Export": "Exports",
            "Import": "Imports"
        })
        
        if include_all_countries:
            grouped = all_countries_df.merge(trade_grouped, on="ISO3", how="left").fillna(0.0)
        else:
            grouped = trade_grouped
            
    # Merge GDP if provided
    if df_gdp is not None and not df_gdp.empty:
        latest_year = df_trade["year"].max() if (df_trade is not None and not df_trade.empty and "year" in df_trade.columns) else 2023
        gdp_subset = df_gdp[df_gdp["year"] == latest_year][["iso_code", "gdp"]].drop_duplicates(subset=["iso_code"])
        grouped = grouped.merge(gdp_subset, left_on="ISO3", right_on="iso_code", how="left")
        grouped["GDP"] = grouped["gdp"].fillna(0.0)
        grouped = grouped.drop(columns=["iso_code", "gdp"], errors="ignore")
    else:
        grouped["GDP"] = 0.0
        
    # Round numerical fields
    for col in ["Exports", "Imports", "Total Trade", "Trade Balance", "GDP"]:
        grouped[col] = grouped[col].round(2)
        
    return grouped.sort_values(by="Total Trade", ascending=False).reset_index(drop=True)

def generate_product_summary(df_trade: pd.DataFrame) -> pd.DataFrame:
    """
    Generate Product Summary with Exports, Imports, Total Trade, Share %, and YoY Growth %.
    """
    if df_trade is None or df_trade.empty:
        return pd.DataFrame(columns=["Product", "Exports", "Imports", "Total Trade", "Share %", "YoY Growth %"])
        
    # Aggregate by product and flow
    prod_flow = df_trade.groupby(["product", "trade_flow"])["trade_value"].sum().unstack(fill_value=0.0).reset_index()
    if "Export" not in prod_flow.columns:
        prod_flow["Export"] = 0.0
    if "Import" not in prod_flow.columns:
        prod_flow["Import"] = 0.0
        
    prod_flow["Total Trade"] = prod_flow["Export"] + prod_flow["Import"]
    prod_flow["Trade Balance"] = prod_flow["Export"] - prod_flow["Import"]
    
    grand_total = prod_flow["Total Trade"].sum()
    prod_flow["Share %"] = (prod_flow["Total Trade"] / grand_total * 100.0) if grand_total > 0 else 0.0
    
    # Calculate Product YoY Growth if multiple years exist
    years = sorted(df_trade["year"].unique())
    if len(years) >= 2:
        curr_yr = years[-1]
        prev_yr = years[-2]
        curr_p = df_trade[df_trade["year"] == curr_yr].groupby("product")["trade_value"].sum()
        prev_p = df_trade[df_trade["year"] == prev_yr].groupby("product")["trade_value"].sum()
        growth_series = ((curr_p - prev_p) / prev_p * 100.0).replace([np.inf, -np.inf], 0.0).fillna(0.0)
        prod_flow["YoY Growth %"] = prod_flow["product"].map(growth_series).fillna(0.0)
    else:
        prod_flow["YoY Growth %"] = 0.0
        
    prod_flow = prod_flow.rename(columns={
        "product": "Product",
        "Export": "Exports",
        "Import": "Imports"
    })
    
    for col in ["Exports", "Imports", "Total Trade", "Trade Balance", "Share %", "YoY Growth %"]:
        prod_flow[col] = prod_flow[col].round(2)
        
    return prod_flow.sort_values(by="Total Trade", ascending=False).reset_index(drop=True)

def generate_yearly_summary(df_trade: pd.DataFrame, window_size: int = 3) -> pd.DataFrame:
    """
    Generate Yearly Summary with Exports, Imports, Total Trade, Trade Balance, Moving Average, and YoY Growth.
    """
    if df_trade is None or df_trade.empty:
        return pd.DataFrame(columns=["Year", "Exports", "Imports", "Total Trade", "Trade Balance", f"MA ({window_size}Y)", "YoY Growth %"])
        
    yearly = df_trade.groupby(["year", "trade_flow"])["trade_value"].sum().unstack(fill_value=0.0).reset_index()
    if "Export" not in yearly.columns:
        yearly["Export"] = 0.0
    if "Import" not in yearly.columns:
        yearly["Import"] = 0.0
        
    yearly["Total Trade"] = yearly["Export"] + yearly["Import"]
    yearly["Trade Balance"] = yearly["Export"] - yearly["Import"]
    
    yearly = yearly.sort_values(by="year").reset_index(drop=True)
    
    # Calculate Moving Average: MA(n) = sum(prev n observations) / n
    ma_col = f"MA ({window_size}Y)"
    yearly[ma_col] = yearly["Total Trade"].rolling(window=window_size, min_periods=1).mean().round(2)
    
    # Calculate YoY Growth %
    yearly["YoY Growth %"] = (yearly["Total Trade"].pct_change() * 100.0).fillna(0.0).round(2)
    
    yearly = yearly.rename(columns={
        "year": "Year",
        "Export": "Exports",
        "Import": "Imports"
    })
    
    for col in ["Exports", "Imports", "Total Trade", "Trade Balance"]:
        yearly[col] = yearly[col].round(2)
        
    return yearly

def save_all_summaries(df_trade: pd.DataFrame, df_gdp: Optional[pd.DataFrame] = None) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Generate and persist all summary CSV files to data/processed/.
    """
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    country_sum = generate_country_summary(df_trade, df_gdp)
    product_sum = generate_product_summary(df_trade)
    yearly_sum = generate_yearly_summary(df_trade)
    
    country_sum.to_csv(PROCESSED_DATA_DIR / "country_summary.csv", index=False)
    product_sum.to_csv(PROCESSED_DATA_DIR / "product_summary.csv", index=False)
    yearly_sum.to_csv(PROCESSED_DATA_DIR / "yearly_summary.csv", index=False)
    
    return country_sum, product_sum, yearly_sum
