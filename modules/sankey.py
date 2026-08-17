"""
Sankey diagram visualization module.
Generates multi-mode dynamic Sankey diagrams using Plotly Graph Objects.
"""

import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any

from config.settings import COLOR_PALETTES

def create_sankey_diagram(
    df: pd.DataFrame,
    mode: str = "Country → Country",
    top_n: int = 10,
    flow_type: str = "Export",
    title: Optional[str] = None
) -> go.Figure:
    """
    Generate an interactive Sankey diagram representing international trade flows.
    
    Args:
        df: Filtered trade DataFrame containing [reporter, partner, product, trade_flow, trade_value].
        mode: Visualization flow mode ('Country → Country', 'Country → Product', 'Product → Country').
        top_n: Limit to top N entities for visual clarity.
        flow_type: 'Export', 'Import', or 'Both'.
        title: Custom chart title.
        
    Returns:
        Plotly Graph Objects Figure.
    """
    if df is None or df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No trade data available for the selected filters.",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="#94A3B8")
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0F172A",
            plot_bgcolor="#0F172A"
        )
        return fig
        
    df_sankey = df.copy()
    if flow_type in ["Export", "Import"]:
        df_sankey = df_sankey[df_sankey["trade_flow"] == flow_type]
        
    # Aggregate flows based on mode
    if mode == "Country → Country":
        # Group by Reporter -> Partner
        grouped = df_sankey.groupby(["reporter", "partner"])["trade_value"].sum().reset_index()
        grouped = grouped.sort_values(by="trade_value", ascending=False).head(top_n * 2)
        source_col, target_col = "reporter", "partner"
        source_prefix, target_prefix = "Exporter: ", "Importer: "
        
    elif mode == "Country → Product":
        # Group by Reporter -> Product
        grouped = df_sankey.groupby(["reporter", "product"])["trade_value"].sum().reset_index()
        grouped = grouped.sort_values(by="trade_value", ascending=False).head(top_n * 2)
        source_col, target_col = "reporter", "product"
        source_prefix, target_prefix = "Country: ", "Product: "
        
    elif mode == "Product → Country":
        # Group by Product -> Partner
        grouped = df_sankey.groupby(["product", "partner"])["trade_value"].sum().reset_index()
        grouped = grouped.sort_values(by="trade_value", ascending=False).head(top_n * 2)
        source_col, target_col = "product", "partner"
        source_prefix, target_prefix = "Product: ", "Destination: "
        
    else:
        # Default fallback: Country -> Country
        grouped = df_sankey.groupby(["reporter", "partner"])["trade_value"].sum().reset_index()
        grouped = grouped.sort_values(by="trade_value", ascending=False).head(top_n * 2)
        source_col, target_col = "reporter", "partner"
        source_prefix, target_prefix = "", ""
        
    if grouped.empty:
        fig = go.Figure()
        fig.add_annotation(text="No flows match selected criteria.", x=0.5, y=0.5, showarrow=False)
        return fig

    # Build unique nodes index
    sources = grouped[source_col].unique().tolist()
    targets = grouped[target_col].unique().tolist()
    all_nodes = sources + [t for t in targets if t not in sources]
    node_to_idx = {name: i for i, name in enumerate(all_nodes)}
    
    total_flow_val = grouped["trade_value"].sum()
    
    # Palette of sleek modern colors for nodes
    palette = [
        "#3B82F6", "#10B981", "#F59E0B", "#8B5CF6", "#EC4899",
        "#06B6D4", "#6366F1", "#14B8A6", "#F97316", "#84CC16",
        "#A855F7", "#D946EF", "#0EA5E9", "#E11D48", "#EAB308"
    ]
    node_colors = [palette[i % len(palette)] for i in range(len(all_nodes))]
    
    # Generate Links
    link_sources = [node_to_idx[row[source_col]] for _, row in grouped.iterrows()]
    link_targets = [node_to_idx[row[target_col]] for _, row in grouped.iterrows()]
    link_values = grouped["trade_value"].tolist()
    
    # Link colors with transparency (RGBA)
    link_colors = []
    for s_idx in link_sources:
        hex_color = node_colors[s_idx].lstrip("#")
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        link_colors.append(f"rgba({r}, {g}, {b}, 0.45)")
        
    # Generate rich custom hover template
    hover_labels = []
    for _, row in grouped.iterrows():
        val = row["trade_value"]
        pct = (val / total_flow_val * 100.0) if total_flow_val > 0 else 0.0
        label = (
            f"<b>Flow:</b> {row[source_col]} → {row[target_col]}<br>"
            f"<b>Trade Value:</b> ${val:,.2f} Billion<br>"
            f"<b>Share of Displayed Flows:</b> {pct:.1f}%<br>"
            f"<b>Mode:</b> {mode}"
        )
        hover_labels.append(label)
        
    fig = go.Figure(data=[go.Sankey(
        arrangement="snap",
        node=dict(
            pad=18,
            thickness=22,
            line=dict(color="#1E293B", width=1.5),
            label=all_nodes,
            color=node_colors,
            hovertemplate="<b>%{label}</b><br>Total Node Flow: $%{value:,.2f} B<extra></extra>"
        ),
        link=dict(
            source=link_sources,
            target=link_targets,
            value=link_values,
            color=link_colors,
            customdata=hover_labels,
            hovertemplate="%{customdata}<extra></extra>"
        )
    )])
    
    chart_title = title or f"<b>Bilateral Trade Flows ({mode})</b> — Top {top_n} Flows"
    fig.update_layout(
        title=dict(
            text=chart_title,
            font=dict(size=18, color="#F8FAFC", family="Arial, sans-serif"),
            x=0.02, y=0.96
        ),
        font=dict(size=12, color="#E2E8F0"),
        paper_bgcolor="#0F172A",
        plot_bgcolor="#0F172A",
        margin=dict(l=20, r=20, t=50, b=20),
        height=450
    )
    
    return fig
