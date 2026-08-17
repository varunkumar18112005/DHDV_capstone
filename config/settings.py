"""
Configuration and settings module for the Global Trade Analytics platform.
"""
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
CACHE_DIR = DATA_DIR / "cache"
ASSETS_DIR = BASE_DIR / "assets"

# Ensure directories exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# API Configurations
COMTRADE_API_KEY = os.getenv("COMTRADE_API_KEY", "")
COMTRADE_BASE_URL = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"
WORLD_BANK_GDP_URL = "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD"

# Application Settings
APP_TITLE = "Global Trade Analytics & Visualization Platform"
APP_SUBTITLE = "Import-Export Flow & Geospatial Intelligence Platform"
DEFAULT_DATA_SOURCE = os.getenv("DATA_SOURCE", "local")  # "api" or "local"

# Default Visual Settings
DEFAULT_YEAR = 2023
YEAR_RANGE = (2018, 2024)
DEFAULT_TOP_N = 10
DEFAULT_MA_WINDOW = 3

# Product Categories (Standard Harmonized System (HS) Aggregated Categories)
PRODUCT_CATEGORIES = [
    "All Products",
    "Machinery & Electrical Equipment",
    "Electronics & Optical Products",
    "Automotive & Transport Vehicles",
    "Mineral Fuels & Petroleum",
    "Chemicals & Pharmaceuticals",
    "Agricultural & Food Products",
    "Metals & Metal Products",
    "Textiles & Apparel",
    "Plastics & Rubber",
    "Precision Instruments & Medical Devices"
]

# Color Schemes
COLOR_PALETTES = {
    "exports": "#10B981",       # Emerald Green
    "imports": "#3B82F6",       # Cobalt Blue
    "trade_balance_pos": "#059669", # Dark Green
    "trade_balance_neg": "#EF4444", # Crimson Red
    "total_trade": "#8B5CF6",   # Purple
    "growth_pos": "#10B981",
    "growth_neg": "#F43F5E",
    "background_dark": "#0E1117",
    "card_dark": "#1E293B",
    "text_light": "#F8FAFC",
    "accent": "#6366F1"
}
