"""
Data collection module.
Fetches international trade statistics from UN Comtrade API / World Bank API,
with graceful local fallback caching and offline execution support.
"""

import os
import requests
import pandas as pd
from typing import Optional, Dict, Any, List
from pathlib import Path
import logging

from config.settings import (
    COMTRADE_API_KEY,
    COMTRADE_BASE_URL,
    WORLD_BANK_GDP_URL,
    RAW_DATA_DIR,
    CACHE_DIR
)
from utils.country_mapping import get_un_code, get_country_iso3, standardize_country_name

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_trade_data(
    reporter: Optional[str] = None,
    partner: Optional[str] = None,
    start_year: int = 2018,
    end_year: int = 2024,
    product_code: Optional[str] = None,
    flow: Optional[str] = None,
    use_api: bool = False
) -> pd.DataFrame:
    """
    Retrieve trade data from UN Comtrade API or local fallback storage.
    
    Args:
        reporter: Reporter country name or ISO3 code.
        partner: Partner country name or ISO3 code.
        start_year: Initial year (e.g. 2018).
        end_year: Final year (e.g. 2024).
        product_code: Harmonized System (HS) product code or category name.
        flow: 'Export', 'Import', or None for both.
        use_api: If True, attempts to call UN Comtrade API first.
        
    Returns:
        Pandas DataFrame containing bilateral trade records.
    """
    local_file = RAW_DATA_DIR / "trade_data.csv"
    
    if use_api and COMTRADE_API_KEY:
        try:
            logger.info("Attempting UN Comtrade API fetch...")
            # Prepare API request parameters
            headers = {
                "Ocp-Apim-Subscription-Key": COMTRADE_API_KEY,
                "User-Agent": "GlobalTradeAnalytics/1.0"
            }
            
            reporter_code = get_un_code(reporter) if reporter else "all"
            partner_code = get_un_code(partner) if partner else "all"
            
            params = {
                "reporterCode": reporter_code,
                "partnerCode": partner_code,
                "period": f"{start_year}",
                "cmdCode": product_code if product_code else "TOTAL",
                "flowCode": "M,X" # Imports, Exports
            }
            
            response = requests.get(COMTRADE_BASE_URL, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "data" in data and len(data["data"]) > 0:
                    records = []
                    for item in data["data"]:
                        flow_desc = "Export" if str(item.get("flowCode")) in ["X", "2", "Exports"] else "Import"
                        records.append({
                            "year": item.get("period", start_year),
                            "reporter": item.get("reporterDesc", reporter),
                            "reporter_iso": get_country_iso3(item.get("reporterDesc", reporter)),
                            "partner": item.get("partnerDesc", partner),
                            "partner_iso": get_country_iso3(item.get("partnerDesc", partner)),
                            "product": item.get("cmdDesc", "Total Trade"),
                            "trade_flow": flow_desc,
                            "trade_value": float(item.get("primaryValue", 0)) / 1e9, # normalize to Billions
                            "currency": "USD"
                        })
                    df_api = pd.DataFrame(records)
                    logger.info(f"Retrieved {len(df_api)} records from UN Comtrade API.")
                    return df_api
                else:
                    logger.warning("UN Comtrade API returned empty data. Using local dataset.")
            else:
                logger.warning(f"UN Comtrade API returned HTTP {response.status_code}. Falling back to local data.")
        except Exception as e:
            logger.warning(f"UN Comtrade API request failed: {e}. Falling back to local dataset.")
            
    # Local fallback
    if not local_file.exists():
        raise FileNotFoundError(f"Local trade data file not found at: {local_file}")
        
    df = pd.read_csv(local_file)
    
    # Filter by years
    df = df[(df["year"] >= start_year) & (df["year"] <= end_year)]
    
    # Filter by reporter
    if reporter and reporter != "All Countries":
        std_rep = standardize_country_name(reporter)
        df = df[df["reporter"] == std_rep]
        
    # Filter by partner
    if partner and partner != "All Partners":
        std_part = standardize_country_name(partner)
        df = df[df["partner"] == std_part]
        
    # Filter by product
    if product_code and product_code != "All Products":
        df = df[df["product"] == product_code]
        
    # Filter by trade flow
    if flow and flow in ["Export", "Import", "Exports", "Imports"]:
        flow_clean = "Export" if "Export" in flow else "Import"
        df = df[df["trade_flow"] == flow_clean]
        
    return df

def fetch_gdp_data(start_year: int = 2018, end_year: int = 2024, use_api: bool = False) -> pd.DataFrame:
    """
    Retrieve World Bank GDP data (in Billions USD) with local fallback.
    """
    local_file = RAW_DATA_DIR / "gdp_data.csv"
    
    if use_api:
        try:
            logger.info("Attempting World Bank GDP API fetch...")
            # Query World Bank GDP indicator: NY.GDP.MKTP.CD
            url = f"{WORLD_BANK_GDP_URL}?date={start_year}:{end_year}&format=json&per_page=1000"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if len(data) >= 2 and isinstance(data[1], list):
                    records = []
                    for item in data[1]:
                        val = item.get("value")
                        if val is not None:
                            country_name = item.get("country", {}).get("value", "")
                            iso3 = item.get("countryiso3code", "") or get_country_iso3(country_name)
                            records.append({
                                "country": standardize_country_name(country_name),
                                "iso_code": iso3,
                                "year": int(item.get("date", 0)),
                                "gdp": round(float(val) / 1e9, 2) # Billions USD
                            })
                    if records:
                        df_gdp = pd.DataFrame(records)
                        logger.info(f"Retrieved {len(df_gdp)} GDP records from World Bank API.")
                        return df_gdp
        except Exception as e:
            logger.warning(f"World Bank GDP API request failed: {e}. Falling back to local data.")
            
    if not local_file.exists():
        raise FileNotFoundError(f"Local GDP dataset not found at: {local_file}")
        
    df_gdp = pd.read_csv(local_file)
    df_gdp = df_gdp[(df_gdp["year"] >= start_year) & (df_gdp["year"] <= end_year)]
    return df_gdp
