"""
Stacked Bar Chart visualization module.
Displays multi-year commodity composition trends with absolute vs percentage view options.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Optional

def create_stacked_bar(
    df: pd.DataFrame,
    flow_type: str = "Total Trade",  # "Exports", "Imports", "Total Trade"
    is_percentage: bool = False,
    title: Optional[str] = None
) -> go.Figure:
    """
    Generate interactive Stacked Bar Chart for multi-year product composition.
    
    Args:
        df: Filtered trade DataFrame.
        flow_type: 'Exports', 'Imports', or 'Total Trade'.
        is_percentage: If True, normalizes each year's bar to 100%.
        title: Custom chart title.
        
    Returns:
        Plotly Figure.
    """
    if df is None or df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No historical product data available.",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="#94A3B8")
        )
        fig.update_layout(template="plotly_dark", paper_bgcolor="#0F172A", plot_bgcolor="#0F172A")
        return fig
        
    df_bar = df.copy()
    if flow_type == "Exports":
        df_bar = df_bar[df_bar["trade_flow"] == "Export"]
    elif flow_type == "Imports":
        df_bar = df_bar[df_bar["trade_flow"] == "Import"]
        
    # Group by Year and Product
    grouped = df_bar.groupby(["year", "product"])["trade_value"].sum().reset_index()
    
    if is_percentage:
        # Calculate percentage per year
        yearly_total = grouped.groupby("year")["trade_value"].transform("sum")
        grouped["Display Value"] = (grouped["trade_value"] / yearly_total * 100.0).round(2)
        y_col = "Display Value"
        y_title = "Share (% of Annual Total)"
        y_suffix = "%"
    else:
        grouped["Display Value"] = grouped["trade_value"].round(2)
        y_col = "Display Value"
        y_title = "Trade Value ($ Billion USD)"
        y_suffix = " B"
        
    # Modern color palette for product categories
    palette = px.colors.qualitative.Prism + px.colors.qualitative.Safe
    
    fig = px.bar(
        grouped,
        x="year",
        y=y_col,
        color="product",
        color_discrete_sequence=palette,
        barmode="stack"
    )
    
    # Update hover template
    if is_percentage:
        fig.update_traces(
            hovertemplate="<b>%{data.name}</b><br>Year: %{x}<br>Composition: %{y:.2f}%<extra></extra>"
        )
    else:
        fig.update_traces(
            hovertemplate="<b>%{data.name}</b><br>Year: %{x}<br>Value: $%{y:,.2f} B<extra></extra>"
        )
        
    mode_text = "100% Normalized Percentage" if is_percentage else "Absolute Value ($B)"
    chart_title = title or f"<b>Yearly Product Composition ({flow_type})</b> — {mode_text}"
    
    fig.update_layout(
        title=dict(
            text=chart_title,
            font=dict(size=18, color="#F8FAFC", family="Arial, sans-serif"),
            x=0.02, y=0.96
        ),
        xaxis=dict(
            title="Year",
            type="category",
            gridcolor="#334155",
            tickfont=dict(color="#E2E8F0", size=12),
            title_font=dict(color="#E2E8F0", size=13)
        ),
        yaxis=dict(
            title=y_title,
            gridcolor="#334155",
            tickfont=dict(color="#E2E8F0", size=12),
            title_font=dict(color="#E2E8F0", size=13),
            range=[0, 100] if is_percentage else None
        ),
        font=dict(size=12, color="#E2E8F0"),
        paper_bgcolor="#0F172A",
        plot_bgcolor="#0F172A",
        legend=dict(
            title=dict(text="Commodity Category", font=dict(color="#E2E8F0", size=12)),
            font=dict(color="#E2E8F0", size=10),
            bgcolor="rgba(15, 23, 42, 0.7)",
            bordercolor="#334155",
            borderwidth=1,
            orientation="h",
            yanchor="top",
            y=-0.22,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=20, r=20, t=50, b=90),
        height=450
    )
    
    return fig
