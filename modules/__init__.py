"""Modules package initialization."""
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
from modules.cartogram import create_gdp_cartogram, build_gdp_cartogram_geometries
from modules.trend_analysis import create_trend_chart, calculate_trend_analytics
