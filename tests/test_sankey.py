"""
Unit tests for Sankey diagram generation.
"""

import pytest
import pandas as pd
from modules.sankey import create_sankey_diagram
import plotly.graph_objects as go

def test_sankey_generation_valid():
    """Verify Sankey figure generates with correct node and link structures."""
    df = pd.DataFrame({
        "year": [2023, 2023, 2023],
        "reporter": ["USA", "Germany", "Japan"],
        "partner": ["China", "China", "USA"],
        "product": ["Machinery", "Automotive", "Electronics"],
        "trade_flow": ["Export", "Export", "Export"],
        "trade_value": [80.0, 50.0, 30.0]
    })
    
    fig = create_sankey_diagram(df, mode="Country → Country", top_n=5, flow_type="Export")
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.data[0].type == "sankey"
    
    # Check node count: unique countries are USA, Germany, Japan, China (4 nodes)
    nodes = fig.data[0].node.label
    assert len(nodes) == 4
    assert "China" in nodes
    assert "USA" in nodes

def test_sankey_empty_dataframe():
    """Verify Sankey gracefully handles empty data with informative annotation."""
    df_empty = pd.DataFrame()
    fig = create_sankey_diagram(df_empty)
    assert isinstance(fig, go.Figure)
    assert len(fig.layout.annotations) > 0
