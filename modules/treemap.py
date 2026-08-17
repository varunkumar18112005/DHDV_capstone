"""
Treemap visualization module.
Displays hierarchical product category export/import composition and growth rates.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Optional

def create_treemap(
    df: pd.DataFrame,
    flow_type: str = "Export",
    color_by: str = "Growth",  # "Growth" or "Share"
    title: Optional[str] = None
) -> go.Figure:
    """
    Generate an interactive Treemap of product trade distribution.
    
    Args:
        df: Filtered trade DataFrame.
        flow_type: 'Export', 'Import', or 'Both'.
        color_by: Metric for color scale ('Growth' or 'Share').
        title: Custom chart title.
        
    Returns:
        Plotly Figure.
    """
    if df is None or df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No product trade data available for selection.",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="#94A3B8")
        )
        fig.update_layout(template="plotly_dark", paper_bgcolor="#0F172A", plot_bgcolor="#0F172A")
        return fig
        
    df_tree = df.copy()
    if flow_type in ["Export", "Import"]:
        df_tree = df_tree[df_tree["trade_flow"] == flow_type]
        
    # Aggregate by product
    grouped = df_tree.groupby("product")["trade_value"].sum().reset_index()
    total_val = grouped["trade_value"].sum()
    grouped["Share %"] = (grouped["trade_value"] / total_val * 100.0) if total_val > 0 else 0.0
    
    # Calculate YoY Growth if multiple years exist
    years = sorted(df["year"].unique())
    if len(years) >= 2:
        curr_yr = years[-1]
        prev_yr = years[-2]
        curr_p = df[df["year"] == curr_yr].groupby("product")["trade_value"].sum()
        prev_p = df[df["year"] == prev_yr].groupby("product")["trade_value"].sum()
        growth_series = ((curr_p - prev_p) / prev_p * 100.0).replace([np.inf, -np.inf], 0.0).fillna(0.0)
        grouped["Growth %"] = grouped["product"].map(growth_series).fillna(0.0)
    else:
        grouped["Growth %"] = 0.0
        
    grouped["Trade Category"] = "International Trade"
    grouped["Trade Value ($B)"] = grouped["trade_value"].round(2)
    grouped["Share %"] = grouped["Share %"].round(2)
    grouped["Growth %"] = grouped["Growth %"].round(2)
    
    color_col = "Growth %" if color_by == "Growth" else "Share %"
    color_scale = "RdYlGn" if color_by == "Growth" else "Viridis"
    color_midpoint = 0.0 if color_by == "Growth" else None
    
    fig = px.treemap(
        grouped,
        path=["Trade Category", "product"],
        values="Trade Value ($B)",
        color=color_col,
        color_continuous_scale=color_scale,
        color_continuous_midpoint=color_midpoint,
        hover_data={
            "Trade Value ($B)": ":,.2f",
            "Share %": ":.2f",
            "Growth %": ":.2f",
            "Trade Category": False
        }
    )
    
    fig.update_traces(
        textinfo="label+value+percent parent",
        textfont=dict(size=13, color="#FFFFFF"),
        marker=dict(cornerradius=4),
        hovertemplate="<b>%{label}</b><br>Trade Value: $%{value:,.2f} B<br>Share: %{customdata[1]:.2f}%<br>YoY Growth: %{customdata[2]:+.2f}%<extra></extra>"
    )
    
    chart_title = title or f"<b>Product Composition ({flow_type}s)</b> — Size: Trade Value ($B), Color: {color_by} %"
    fig.update_layout(
        title=dict(
            text=chart_title,
            font=dict(size=18, color="#F8FAFC", family="Arial, sans-serif"),
            x=0.02, y=0.96
        ),
        font=dict(size=12, color="#E2E8F0"),
        paper_bgcolor="#0F172A",
        plot_bgcolor="#0F172A",
        margin=dict(l=10, r=10, t=50, b=10),
        height=450,
        coloraxis_colorbar=dict(
            title=f"{color_by} %",
            thickness=14,
            len=0.75,
            tickfont=dict(color="#E2E8F0"),
            title_font=dict(color="#E2E8F0")
        )
    )
    
    return fig
