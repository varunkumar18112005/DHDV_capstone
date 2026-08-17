"""
Sidebar Filters component.
Renders responsive, dependent controls for multi-dimensional filtering.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List
from config.settings import PRODUCT_CATEGORIES, YEAR_RANGE, DEFAULT_YEAR

def render_sidebar_filters(df_all: pd.DataFrame) -> Dict[str, Any]:
    """
    Render sidebar filter widgets and return selected parameters dictionary.
    
    Args:
        df_all: Full cleaned trade dataset.
        
    Returns:
        Dictionary of user selections.
    """
    st.sidebar.markdown("### ⚙️ Platform Controls")
    
    # 1. Data Source Selection
    data_source = st.sidebar.radio(
        "Data Source Mode",
        options=["Local Offline Dataset", "UN Comtrade & World Bank API"],
        index=0,
        help="Switch between instant local fallback cache and live external APIs."
    )
    use_api = (data_source == "UN Comtrade & World Bank API")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔍 Filter Intelligence")
    
    # Available Years
    if not df_all.empty and "year" in df_all.columns:
        available_years = sorted(df_all["year"].unique())
    else:
        available_years = list(range(YEAR_RANGE[0], YEAR_RANGE[1] + 1))
        
    selected_year = st.sidebar.select_slider(
        "Select Snapshot Year",
        options=available_years,
        value=DEFAULT_YEAR if DEFAULT_YEAR in available_years else available_years[-1],
        help="Visualizations focus on the selected snapshot year, while trend charts analyze full time-series."
    )
    
    # Reporter Country List (Sorted)
    if not df_all.empty and "reporter" in df_all.columns:
        all_reporters = sorted(df_all["reporter"].dropna().unique().tolist())
    else:
        all_reporters = ["United States", "China", "Germany", "Japan", "India"]
        
    reporter_options = ["All Countries"] + all_reporters
    selected_reporter = st.sidebar.selectbox(
        "Reporting Nation (Origin)",
        options=reporter_options,
        index=0,
        help="Select a specific nation to analyze its bilateral trade matrix, or 'All Countries' for global view."
    )
    
    # Dependent Partner Options
    if selected_reporter != "All Countries" and not df_all.empty:
        df_rep = df_all[df_all["reporter"] == selected_reporter]
        available_partners = sorted(df_rep["partner"].dropna().unique().tolist())
    elif not df_all.empty:
        available_partners = sorted(df_all["partner"].dropna().unique().tolist())
    else:
        available_partners = all_reporters
        
    partner_options = ["All Partners"] + available_partners
    selected_partner = st.sidebar.selectbox(
        "Partner Nation (Destination)",
        options=partner_options,
        index=0,
        help="Filter bilateral flows for a specific destination partner."
    )
    
    # Trade Flow Selector
    selected_flow = st.sidebar.radio(
        "Trade Flow Direction",
        options=["Both Flows", "Exports Only", "Imports Only"],
        index=0
    )
    flow_filter = "Both" if selected_flow == "Both Flows" else ("Export" if "Export" in selected_flow else "Import")
    
    # Product Category Filter
    if not df_all.empty and "product" in df_all.columns:
        available_prods = ["All Products"] + sorted(df_all["product"].dropna().unique().tolist())
    else:
        available_prods = PRODUCT_CATEGORIES
        
    selected_product = st.sidebar.selectbox(
        "Commodity / Product Category",
        options=available_prods,
        index=0,
        help="Filter trade data for a specific Harmonized System (HS) category."
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Advanced Parameters")
    
    # Top N Slider
    top_n = st.sidebar.slider(
        "Top N Flow Entities",
        min_value=5,
        max_value=25,
        value=10,
        step=1,
        help="Number of major trading partners/commodities to show in Sankey and charts."
    )
    
    # Moving Average Window
    ma_window = st.sidebar.selectbox(
        "Moving Average Window (Years)",
        options=[3, 5, 7],
        index=0,
        help="Time-series rolling average window for smoothing economic volatility."
    )
    
    # Map Metric
    map_metric = st.sidebar.selectbox(
        "Geospatial Map Metric",
        options=["Trade Balance", "Total Trade", "Exports", "Imports"],
        index=0,
        help="Metric visualized on the global choropleth map."
    )
    
    return {
        "use_api": use_api,
        "year": selected_year,
        "reporter": selected_reporter,
        "partner": selected_partner,
        "flow": flow_filter,
        "product": selected_product,
        "top_n": top_n,
        "ma_window": ma_window,
        "map_metric": map_metric
    }
