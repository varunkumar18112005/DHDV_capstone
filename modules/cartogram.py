"""
GDP-Weighted Cartogram visualization module.
Constructs geometric cartograms using GeoPandas and Shapely affinity scaling,
distorting geographic landmass area proportional to national GDP to contrast Economic Size vs Trade Openness.
"""

import json
import geopandas as gpd
import pandas as pd
import numpy as np
import shapely.affinity
import plotly.graph_objects as go
from pathlib import Path
from typing import Optional, Dict, Any

from config.settings import RAW_DATA_DIR

def build_gdp_cartogram_geometries(
    gdf_world: gpd.GeoDataFrame,
    df_country_summary: pd.DataFrame,
    min_scale: float = 0.25,
    max_scale: float = 2.80
) -> gpd.GeoDataFrame:
    """
    Apply geometric area distortion based on country GDP relative to global distribution.
    
    Formula:
      Scale Factor S_i = clamp(sqrt(GDP_i / Median_GDP), min_scale, max_scale)
      Transformed Polygon = shapely.affinity.scale(polygon, xfact=S_i, yfact=S_i, origin='centroid')
    
    Args:
        gdf_world: GeoDataFrame of world country boundaries.
        df_country_summary: Country trade & GDP summary DataFrame.
        min_scale: Minimum polygon scaling factor to avoid disappearing nations.
        max_scale: Maximum polygon scaling factor to avoid visual overlap.
        
    Returns:
        GeoDataFrame with distorted geometries and merged trade indicators.
    """
    # Normalize ISO column names in GeoDataFrame
    iso_cols = [c for c in ["ISO_A3", "id", "iso_a3", "ISO3", "adm0_a3"] if c in gdf_world.columns]
    if iso_cols:
        gdf_world["ISO3"] = gdf_world[iso_cols[0]]
    else:
        gdf_world["ISO3"] = gdf_world.index.astype(str)
        
    # Merge with trade summary
    merged = gdf_world.merge(df_country_summary, on="ISO3", how="inner")
    if merged.empty:
        return gdf_world
        
    # Fill missing GDP with median
    valid_gdp = merged["GDP"][merged["GDP"] > 0]
    median_gdp = valid_gdp.median() if not valid_gdp.empty else 1000.0
    
    distorted_geoms = []
    scale_factors = []
    openness_ratios = []
    
    for _, row in merged.iterrows():
        geom = row["geometry"]
        gdp_val = row["GDP"]
        trade_val = row["Total Trade"]
        
        # Calculate Trade Openness Ratio (Trade / GDP * 100)
        openness = (trade_val / gdp_val * 100.0) if gdp_val > 0 else 0.0
        openness_ratios.append(round(openness, 2))
        
        if geom is None or geom.is_empty or gdp_val <= 0:
            distorted_geoms.append(geom)
            scale_factors.append(1.0)
            continue
            
        # Linear scale factor proportional to sqrt of GDP (so area scales linearly with GDP)
        raw_scale = np.sqrt(gdp_val / median_gdp)
        scale_factor = float(np.clip(raw_scale, min_scale, max_scale))
        scale_factors.append(round(scale_factor, 3))
        
        try:
            scaled_geom = shapely.affinity.scale(
                geom,
                xfact=scale_factor,
                yfact=scale_factor,
                origin="centroid"
            )
            distorted_geoms.append(scaled_geom)
        except Exception:
            distorted_geoms.append(geom)
            
    merged["cartogram_geometry"] = distorted_geoms
    merged["scale_factor"] = scale_factors
    merged["trade_openness_pct"] = openness_ratios
    
    return merged

def create_gdp_cartogram(
    df_country_summary: pd.DataFrame,
    metric_color: str = "Trade Openness (%)",  # "Trade Openness (%)", "Total Trade", "Trade Balance"
    year: Optional[int] = None,
    title: Optional[str] = None
) -> go.Figure:
    """
    Generate an interactive GDP-Weighted Cartogram visualization.
    
    Args:
        df_country_summary: Country summary with [Country, ISO3, Exports, Imports, Total Trade, Trade Balance, GDP].
        metric_color: Metric to map onto choropleth color scale.
        year: Snapshot year selected by user.
        title: Custom chart title.
        
    Returns:
        Plotly Graph Objects Figure.
    """
    geojson_path = RAW_DATA_DIR / "countries.geojson"
    if not geojson_path.exists():
        fig = go.Figure()
        fig.add_annotation(text="Country boundary GeoJSON not found.", x=0.5, y=0.5, showarrow=False)
        return fig
        
    try:
        gdf_world = gpd.read_file(geojson_path)
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"Failed to parse GeoJSON: {e}", x=0.5, y=0.5, showarrow=False)
        return fig
        
    carto_df = build_gdp_cartogram_geometries(gdf_world, df_country_summary)
    
    if carto_df.empty or "scale_factor" not in carto_df.columns:
        fig = go.Figure()
        fig.add_annotation(text="Insufficient data for cartogram calculation.", x=0.5, y=0.5, showarrow=False)
        return fig
        
    # Prepare GeoJSON dictionary with distorted cartogram geometries
    features = []
    for _, row in carto_df.iterrows():
        geom = row["cartogram_geometry"]
        if geom is not None and not geom.is_empty:
            features.append({
                "type": "Feature",
                "id": row["ISO3"],
                "properties": {
                    "ISO3": row["ISO3"],
                    "Country": row["Country"],
                    "GDP": row["GDP"],
                    "scale_factor": row["scale_factor"],
                    "trade_openness_pct": row["trade_openness_pct"],
                    "Total Trade": row["Total Trade"],
                    "Trade Balance": row["Trade Balance"]
                },
                "geometry": shapely.geometry.mapping(geom)
            })
            
    custom_geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    # Configure metric mapping
    if metric_color == "Trade Openness (%)":
        z_values = carto_df["trade_openness_pct"]
        colorscale = "Viridis"
        colorbar_title = "Trade / GDP (%)"
        zmin, zmax = 0, min(float(z_values.quantile(0.95)), 200.0)
    elif metric_color == "Trade Balance":
        z_values = carto_df["Trade Balance"]
        colorscale = "RdYlGn"
        max_abs = max(float(z_values.abs().max()), 1.0)
        zmin, zmax = -max_abs, max_abs
        colorbar_title = "Balance ($B)"
    else: # Total Trade
        z_values = carto_df["Total Trade"]
        colorscale = "Plasma"
        zmin, zmax = 0, max(float(z_values.max()), 1.0)
        colorbar_title = "Total ($B)"
        
    year_str = f" ({year})" if year else ""
    
    hover_text = []
    for _, row in carto_df.iterrows():
        tb_sign = "+" if row["Trade Balance"] >= 0 else ""
        ht = (
            f"<b>{row['Country']} ({row['ISO3']})</b>{year_str}<br>"
            f"━━━━━━━━━━━━━━━━━━━━━━<br>"
            f"<b>Nominal GDP:</b> ${row['GDP']:,.2f} B<br>"
            f"<b>Area Distortion Factor:</b> {row['scale_factor']:.2f}x<br>"
            f"<b>Trade Openness (Trade/GDP):</b> {row['trade_openness_pct']:.1f}%<br>"
            f"<b>Total Trade:</b> ${row['Total Trade']:,.2f} B<br>"
            f"<b>Trade Balance:</b> {tb_sign}${row['Trade Balance']:,.2f} B"
        )
        hover_text.append(ht)
        
    fig = go.Figure(data=go.Choropleth(
        geojson=custom_geojson,
        locations=carto_df["ISO3"],
        z=z_values,
        text=hover_text,
        hoverinfo="text",
        colorscale=colorscale,
        zmin=zmin,
        zmax=zmax,
        marker_line_color="#38BDF8",
        marker_line_width=1.2,
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
    
    chart_title = title or f"<b>GDP-Weighted Non-Contiguous Cartogram{year_str}</b> (Area ∝ GDP, Color: {metric_color})"
    fig.update_layout(
        title=dict(
            text=chart_title,
            font=dict(size=18, color="#F8FAFC", family="Arial, sans-serif"),
            x=0.02, y=0.96
        ),
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor="#334155",
            projection_type="natural earth",
            bgcolor="#0F172A",
            lakecolor="#0F172A",
            landcolor="#1E293B",
            showocean=True,
            oceancolor="#090D16"
        ),
        paper_bgcolor="#0F172A",
        plot_bgcolor="#0F172A",
        font=dict(color="#E2E8F0"),
        margin=dict(l=10, r=10, t=50, b=10),
        height=520
    )
    
    return fig
