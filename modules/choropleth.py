"""
Choropleth Map visualization module.
Renders global trade balance, exports, imports, and total trade using Plotly Choropleth.
"""

import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Optional

def create_choropleth_map(
    df_country_summary: pd.DataFrame,
    metric: str = "Trade Balance",  # "Trade Balance", "Total Trade", "Exports", "Imports"
    title: Optional[str] = None
) -> go.Figure:
    """
    Generate an interactive global Choropleth map.
    
    Args:
        df_country_summary: Country summary DataFrame with [Country, ISO3, Exports, Imports, Total Trade, Trade Balance, GDP].
        metric: Metric to visualize ('Trade Balance', 'Total Trade', 'Exports', 'Imports').
        title: Custom title for map.
        
    Returns:
        Plotly Graph Objects Figure.
    """
    if df_country_summary is None or df_country_summary.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No country trade summary available for mapping.",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="#94A3B8")
        )
        fig.update_layout(template="plotly_dark", paper_bgcolor="#0F172A", plot_bgcolor="#0F172A")
        return fig
        
    df_map = df_country_summary.copy()
    if metric not in df_map.columns:
        metric = "Trade Balance"
        
    # Configure color scale and midpoint
    if metric == "Trade Balance":
        colorscale = "RdYlGn"
        # Symmetrical bounds around 0 for clear surplus/deficit indication
        max_abs = max(df_map["Trade Balance"].abs().max(), 1.0)
        zmin, zmax = -max_abs, max_abs
        colorbar_title = "Balance ($B)"
    elif metric == "Exports":
        colorscale = "Greens"
        zmin, zmax = 0, df_map["Exports"].max()
        colorbar_title = "Exports ($B)"
    elif metric == "Imports":
        colorscale = "Blues"
        zmin, zmax = 0, df_map["Imports"].max()
        colorbar_title = "Imports ($B)"
    else:  # Total Trade
        colorscale = "Plasma"
        zmin, zmax = 0, df_map["Total Trade"].max()
        colorbar_title = "Total ($B)"
        
    # Build rich hover text
    hover_text = []
    for _, row in df_map.iterrows():
        tb_sign = "+" if row["Trade Balance"] >= 0 else ""
        text = (
            f"<b>{row['Country']} ({row['ISO3']})</b><br>"
            f"━━━━━━━━━━━━━━━━━━━━━━<br>"
            f"<b>Exports:</b> ${row['Exports']:,.2f} B<br>"
            f"<b>Imports:</b> ${row['Imports']:,.2f} B<br>"
            f"<b>Trade Balance:</b> {tb_sign}${row['Trade Balance']:,.2f} B<br>"
            f"<b>Total Trade:</b> ${row['Total Trade']:,.2f} B<br>"
            f"<b>Nominal GDP:</b> ${row.get('GDP', 0.0):,.2f} B"
        )
        hover_text.append(text)
        
    fig = go.Figure(data=go.Choropleth(
        locations=df_map["ISO3"],
        z=df_map[metric],
        text=hover_text,
        hoverinfo="text",
        colorscale=colorscale,
        zmin=zmin,
        zmax=zmax,
        marker_line_color="#1E293B",
        marker_line_width=0.7,
        colorbar=dict(
            title=dict(text=colorbar_title, font=dict(color="#E2E8F0", size=12)),
            tickfont=dict(color="#E2E8F0", size=11),
            thickness=14,
            len=0.7,
            bgcolor="rgba(15, 23, 42, 0.7)",
            bordercolor="#334155",
            borderwidth=1,
            x=0.98,
            y=0.5
        )
    ))
    
    chart_title = title or f"<b>Global Geospatial Trade Distribution</b> — Metric: {metric} ($ Billion USD)"
    fig.update_layout(
        title=dict(
            text=chart_title,
            font=dict(size=18, color="#F8FAFC", family="Arial, sans-serif"),
            x=0.02, y=0.96
        ),
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor="#475569",
            projection_type="natural earth",
            bgcolor="#0F172A",
            lakecolor="#0F172A",
            landcolor="#1E293B",
            showocean=True,
            oceancolor="#090D16",
            showlakes=False
        ),
        paper_bgcolor="#0F172A",
        plot_bgcolor="#0F172A",
        font=dict(color="#E2E8F0"),
        margin=dict(l=10, r=10, t=50, b=10),
        height=520
    )
    
    return fig
