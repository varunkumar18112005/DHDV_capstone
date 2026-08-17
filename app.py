"""
Global Trade Analytics and Visualization Platform
Main Streamlit Application Dashboard.
Structured multi-page navigation architecture with analytical explanations.
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import os
import sys

# Configure page layout and metadata
st.set_page_config(
    page_title="Global Trade Analytics & Flow Intelligence",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from config.settings import (
    APP_TITLE,
    APP_SUBTITLE,
    ASSETS_DIR,
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR
)
from modules.data_collection import fetch_trade_data, fetch_gdp_data
from modules.preprocessing import TradeDataPreprocessor, preprocess_and_save_all
from modules.calculations import (
    calculate_trade_metrics,
    generate_country_summary,
    generate_product_summary,
    generate_yearly_summary,
    save_all_summaries
)
from modules.sankey import create_sankey_diagram
from modules.treemap import create_treemap
from modules.stacked_bar import create_stacked_bar
from modules.choropleth import create_choropleth_map
from modules.cartogram import create_gdp_cartogram
from modules.trend_analysis import create_trend_chart, calculate_trend_analytics
from components.kpi_cards import render_kpi_cards
from components.filters import render_sidebar_filters
from components.data_table import render_data_table
from utils.country_mapping import standardize_country_name

# Inject custom CSS
def load_css():
    css_file = ASSETS_DIR / "styles.css"
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Cached data loaders
@st.cache_data(show_spinner=False)
def load_base_datasets(use_api: bool = False):
    """
    Load raw trade data and GDP data, run preprocessing, and return cleaned datasets.
    """
    try:
        df_raw = fetch_trade_data(use_api=use_api)
        df_gdp = fetch_gdp_data(use_api=use_api)
        
        preprocessor = TradeDataPreprocessor()
        df_cleaned, stats = preprocessor.clean_trade_data(df_raw)
        
        # Save summaries
        country_sum, prod_sum, year_sum = save_all_summaries(df_cleaned, df_gdp)
        
        return df_cleaned, df_gdp, stats, country_sum, prod_sum, year_sum
    except Exception as e:
        st.error(f"Error initializing datasets: {e}")
        return pd.DataFrame(), pd.DataFrame(), {}, pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Main Application Entry Point
def main():
    # Load base dataset
    df_cleaned, df_gdp, stats, df_country_sum_all, df_prod_sum_all, df_year_sum_all = load_base_datasets(use_api=False)
    
    if df_cleaned.empty:
        st.error("⚠️ Dataset could not be loaded. Please verify raw files in data/raw/ directory.")
        st.stop()
        
    # Render Sidebar Filters
    filters = render_sidebar_filters(df_cleaned)
    
    # Check if user requested API mode
    if filters["use_api"]:
        st.sidebar.info("📡 Connecting to UN Comtrade & World Bank APIs...")
        
    # ----------------------------------------------------
    # Filter Data according to user selections
    # ----------------------------------------------------
    df_filtered = df_cleaned.copy()
    
    # 1. Reporter Filter
    if filters["reporter"] != "All Countries":
        std_rep = standardize_country_name(filters["reporter"])
        df_filtered = df_filtered[df_filtered["reporter"] == std_rep]
        
    # 2. Partner Filter
    if filters["partner"] != "All Partners":
        std_part = standardize_country_name(filters["partner"])
        df_filtered = df_filtered[df_filtered["partner"] == std_part]
        
    # 3. Product Filter
    if filters["product"] != "All Products":
        df_filtered = df_filtered[df_filtered["product"] == filters["product"]]
        
    # 4. Flow Filter
    if filters["flow"] in ["Export", "Import"]:
        df_filtered = df_filtered[df_filtered["trade_flow"] == filters["flow"]]
        
    # Snapshot year filtered data (for snapshot charts: Sankey, Treemap, Maps)
    df_year_filtered = df_filtered[df_filtered["year"] == filters["year"]]
    
    # Calculate top-level KPIs for snapshot year
    kpis = calculate_trade_metrics(df_year_filtered)
    
    # Country summary for snapshot year (for maps)
    df_country_summary_snap = generate_country_summary(
        df_cleaned[df_cleaned["year"] == filters["year"]],
        df_gdp
    )
    
    # Yearly summary for trend analysis
    df_yearly_trend = generate_yearly_summary(df_filtered, window_size=filters["ma_window"])
    trend_stats = calculate_trend_analytics(df_yearly_trend, window_size=filters["ma_window"])
    
    # Product summary for snapshot year
    df_prod_summary_snap = generate_product_summary(df_year_filtered)

    # ----------------------------------------------------
    # DASHBOARD HEADER
    # ----------------------------------------------------
    reporter_display = filters["reporter"] if filters["reporter"] != "All Countries" else "Global Economy"
    product_display = filters["product"] if filters["product"] != "All Products" else "All Commodities"
    
    st.markdown(f"""
    <div class="header-container">
        <div class="header-title">🌐 {APP_TITLE}</div>
        <div class="header-subtitle">
            {APP_SUBTITLE} &nbsp;•&nbsp; 
            <strong>Focus:</strong> {reporter_display} &nbsp;|&nbsp; 
            <strong>Snapshot Year:</strong> {filters['year']} &nbsp;|&nbsp; 
            <strong>Category:</strong> {product_display}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Data Quality & Audit Expander
    with st.expander("🛡️ Data Ingestion Pipeline & Quality Audit Report", expanded=False):
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.markdown(f"<div class='audit-badge'>📥 Raw Records: <strong>{stats.get('original_records', 0):,}</strong></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='audit-badge'>🧹 Duplicates Purged: <strong>{stats.get('removed_duplicates', 0):,}</strong></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='audit-badge'>⚠️ Nulls Removed: <strong>{stats.get('missing_records', 0):,}</strong></div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='audit-badge'>🚫 Invalid Dropped: <strong>{stats.get('invalid_records', 0):,}</strong></div>", unsafe_allow_html=True)
        c5.markdown(f"<div class='audit-badge'>✅ Cleaned Pipeline: <strong>{stats.get('final_records', 0):,}</strong></div>", unsafe_allow_html=True)

    # Render Top KPI Cards
    render_kpi_cards(kpis)

    # ----------------------------------------------------
    # MULTI-PAGE TAB NAVIGATION
    # ----------------------------------------------------
    page_tab1, page_tab2, page_tab3, page_tab4, page_tab5 = st.tabs([
        "📊 Executive Flow Dashboard",
        "🌍 Geospatial Intelligence Map",
        "📐 GDP-Weighted Cartogram",
        "📈 Commodity & Trend Econometrics",
        "📑 Data Explorer & Export Center"
    ])

    # ====================================================
    # PAGE 1: EXECUTIVE FLOW DASHBOARD
    # ====================================================
    with page_tab1:
        st.markdown('<div class="section-heading">🌊 Bilateral Trade Flows & Product Composition</div>', unsafe_allow_html=True)
        st.caption("Analyze how trade volumes flow between nations and examine the commodity distribution for the selected snapshot year.")
        
        col_sankey, col_treemap = st.columns([1.1, 0.9])
        
        with col_sankey:
            sankey_mode = st.selectbox(
                "Sankey Flow Hierarchy",
                options=["Country → Country", "Country → Product", "Product → Country"],
                index=0,
                key="sb_sankey_mode"
            )
            flow_mode_sankey = "Export" if filters["flow"] == "Both" else filters["flow"]
            fig_sankey = create_sankey_diagram(
                df=df_year_filtered,
                mode=sankey_mode,
                top_n=filters["top_n"],
                flow_type=flow_mode_sankey
            )
            st.plotly_chart(fig_sankey, use_container_width=True)
            st.info("💡 **How to Read Sankey**: The thickness of each connecting band represents bilateral trade value ($B). Hover over nodes or links to view exact values and percentage contributions.")
            
        with col_treemap:
            tree_color = st.radio(
                "Treemap Color Scale",
                options=["YoY Growth %", "Share %"],
                index=0,
                horizontal=True,
                key="rb_tree_color"
            )
            color_param = "Growth" if "Growth" in tree_color else "Share"
            fig_treemap = create_treemap(
                df=df_year_filtered,
                flow_type="Export" if filters["flow"] == "Both" else filters["flow"],
                color_by=color_param
            )
            st.plotly_chart(fig_treemap, use_container_width=True)
            st.info("💡 **How to Read Treemap**: Rectangle area represents product trade volume. Green indicates positive YoY growth, while red highlights contracting sectors.")

    # ====================================================
    # PAGE 2: GEOSPATIAL TRADE INTELLIGENCE
    # ====================================================
    with page_tab2:
        st.markdown('<div class="section-heading">🌍 Global Geospatial Trade Balance & Macroeconomic Map</div>', unsafe_allow_html=True)
        st.caption("Visualize international trade balances, export volumes, and import dependencies on a natural earth geographic projection.")
        
        fig_choro = create_choropleth_map(
            df_country_summary=df_country_summary_snap,
            metric=filters["map_metric"]
        )
        st.plotly_chart(fig_choro, use_container_width=True)
        
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.6); padding: 14px 18px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.08); margin-top: 10px;">
            <strong>📌 Geographical Map Insights:</strong><br>
            • <strong>Trade Balance (Surplus/Deficit)</strong>: Green represents net exporting surplus nations, while red highlights net importing deficit economies.<br>
            • <strong>Interactive Tooltips</strong>: Hovering over any sovereign nation reveals its nominal GDP, total exports, total imports, and net trade balance.
        </div>
        """, unsafe_allow_html=True)

    # ====================================================
    # PAGE 3: GDP-WEIGHTED CARTOGRAM
    # ====================================================
    with page_tab3:
        st.markdown('<div class="section-heading">🗺️ Advanced GDP-Weighted Geometric Cartogram</div>', unsafe_allow_html=True)
        st.caption(r"Country polygon boundaries are distorted and scaled proportionally to national nominal GDP (Area $\propto$ GDP), contrasting economic scale against geographic landmass.")
        
        carto_color_metric = st.selectbox(
            "Cartogram Color Scale Metric",
            options=["Trade Openness (%)", "Total Trade", "Trade Balance"],
            index=0,
            key="sb_carto_metric"
        )
        
        fig_carto = create_gdp_cartogram(
            df_country_summary=df_country_summary_snap,
            metric_color=carto_color_metric
        )
        st.plotly_chart(fig_carto, use_container_width=True)
        
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.6); padding: 14px 18px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.08); margin-top: 10px;">
            <strong>📐 Mathematical Cartogram Formulation:</strong><br>
            • <strong>Polygon Scaling</strong>: Each country polygon is transformed via <code>shapely.affinity.scale</code> using scale factor $S_i = \text{clamp}(\sqrt{\text{GDP}_i / \text{Median\_GDP}}, 0.25, 2.80)$.<br>
            • <strong>Trade Openness Ratio</strong>: Computed as $\text{Trade Openness} = \frac{\text{Total Trade}}{\text{GDP}} \times 100\%$, highlighting nations that punch above their economic weight in international trade.
        </div>
        """, unsafe_allow_html=True)

    # ====================================================
    # PAGE 4: COMMODITY & TREND ECONOMETRICS
    # ====================================================
    with page_tab4:
        st.markdown('<div class="section-heading">📈 Time-Series Commodity Composition & Rolling Momentum</div>', unsafe_allow_html=True)
        st.caption("Examine multi-year historical trade trajectories, rolling moving averages, and quantitative trend momentum indicators.")
        
        col_stacked, col_trend = st.columns([1.0, 1.0])
        
        with col_stacked:
            bar_view = st.radio(
                "Stacked Bar View Mode",
                options=["Absolute Value ($B)", "100% Normalized Composition"],
                index=0,
                horizontal=True,
                key="rb_bar_view"
            )
            is_normalized = ("Normalized" in bar_view)
            flow_stacked = "Total Trade" if filters["flow"] == "Both" else (filters["flow"] + "s")
            fig_stacked = create_stacked_bar(
                df=df_filtered,
                flow_type=flow_stacked,
                is_percentage=is_normalized
            )
            st.plotly_chart(fig_stacked, use_container_width=True)
            
        with col_trend:
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; background: rgba(30,41,59,0.5); padding: 8px 12px; border-radius: 8px;">
                <span style="font-size: 0.95rem; font-weight: 600; color: #E2E8F0;">
                    Trajectory: <strong style="color: {trend_stats['trend_badge_color']};">{trend_stats['trend_classification']}</strong>
                </span>
                <span style="font-size: 0.85rem; color: #94A3B8;">
                    Peak Year: <strong style="color: #38BDF8;">{trend_stats['max_year']} (${trend_stats['max_value']}B)</strong>
                </span>
            </div>
            """, unsafe_allow_html=True)
            
            fig_trend = create_trend_chart(
                df_yearly=df_yearly_trend,
                window_size=filters["ma_window"]
            )
            st.plotly_chart(fig_trend, use_container_width=True)
            
        st.info("💡 **Moving Average Formula**: $\\text{MA}_t(n) = \\frac{1}{n} \\sum_{i=0}^{n-1} Y_{t-i}$. The orange line smooths short-term fluctuations to reveal underlying structural growth.")

    # ====================================================
    # PAGE 5: DATA EXPLORER & EXPORT CENTER
    # ====================================================
    with page_tab5:
        render_data_table(
            df_filtered=df_year_filtered,
            df_country_summary=df_country_summary_snap,
            df_product_summary=df_prod_summary_snap,
            df_yearly_summary=df_yearly_trend
        )

if __name__ == "__main__":
    main()
