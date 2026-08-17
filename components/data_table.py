"""
Data Table and Export Downloads component.
Renders searchable, formatted data tables and handles CSV downloads for processed summaries.
"""

import streamlit as st
import pandas as pd
from typing import Optional

def render_data_table(
    df_filtered: pd.DataFrame,
    df_country_summary: Optional[pd.DataFrame] = None,
    df_product_summary: Optional[pd.DataFrame] = None,
    df_yearly_summary: Optional[pd.DataFrame] = None
) -> None:
    """
    Render data explorer table and download buttons for filtered data & summary tables.
    """
    st.markdown('<div class="section-heading">📑 Filtered Trade Dataset & Export Center</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 Filtered Trade Records",
        "🌍 Country Aggregates",
        "📦 Product Summaries",
        "📅 Yearly Trends"
    ])
    
    with tab1:
        if df_filtered is not None and not df_filtered.empty:
            st.caption(f"Displaying {len(df_filtered):,} matching trade records.")
            
            # Format display copy
            df_disp = df_filtered.copy()
            if "trade_value" in df_disp.columns:
                df_disp["Trade Value ($B)"] = df_disp["trade_value"].round(3)
                df_disp = df_disp.drop(columns=["trade_value"], errors="ignore")
                
            col_rename = {
                "year": "Year",
                "reporter": "Reporter Nation",
                "reporter_iso": "Origin ISO3",
                "partner": "Partner Nation",
                "partner_iso": "Dest ISO3",
                "product": "Product Category",
                "trade_flow": "Flow",
                "currency": "Currency"
            }
            df_disp = df_disp.rename(columns=col_rename)
            
            st.dataframe(
                df_disp,
                use_container_width=True,
                height=350
            )
            
            csv_data = df_filtered.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Filtered Trade Records (CSV)",
                data=csv_data,
                file_name="filtered_trade_data.csv",
                mime="text/csv",
                key="dl_filtered"
            )
        else:
            st.info("No records match the current filter selection.")
            
    with tab2:
        if df_country_summary is not None and not df_country_summary.empty:
            st.caption(f"Displaying country-level bilateral and macroeconomic summaries ({len(df_country_summary)} countries).")
            st.dataframe(df_country_summary, use_container_width=True, height=350)
            csv_country = df_country_summary.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Country Summary (CSV)",
                data=csv_country,
                file_name="country_summary.csv",
                mime="text/csv",
                key="dl_country"
            )
        else:
            st.info("Country summary not available.")
            
    with tab3:
        if df_product_summary is not None and not df_product_summary.empty:
            st.caption(f"Displaying commodity category distributions and YoY performance.")
            st.dataframe(df_product_summary, use_container_width=True, height=350)
            csv_prod = df_product_summary.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Product Summary (CSV)",
                data=csv_prod,
                file_name="product_summary.csv",
                mime="text/csv",
                key="dl_product"
            )
        else:
            st.info("Product summary not available.")
            
    with tab4:
        if df_yearly_summary is not None and not df_yearly_summary.empty:
            st.caption("Displaying annual trade totals, trade balances, moving averages, and growth trajectory.")
            st.dataframe(df_yearly_summary, use_container_width=True, height=350)
            csv_year = df_yearly_summary.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Yearly Summary (CSV)",
                data=csv_year,
                file_name="yearly_summary.csv",
                mime="text/csv",
                key="dl_yearly"
            )
        else:
            st.info("Yearly summary not available.")
