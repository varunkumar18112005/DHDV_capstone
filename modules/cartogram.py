"""
GDP-Weighted Cartogram visualization module.
Constructs geometric cartograms using GeoPandas polygon scaling and Dorling Bubble Cartograms,
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
from utils.country_mapping import get_country_iso3

def build_gdp_cartogram_geometries(
    gdf_world: gpd.GeoDataFrame,
    df_country_summary: pd.DataFrame,
    min_scale: float = 0.30,
    max_scale: float = 2.50
) -> gpd.GeoDataFrame:
    """
    Apply geometric area distortion based on country GDP relative to global distribution.
    Filter out non-trading polar regions (e.g. Antarctica) to prevent projection distortions.
    """
    # Normalize ISO column names in GeoDataFrame
    iso_cols = [c for c in ["ISO3166-1-Alpha-3", "ISO_A3", "id", "iso_a3", "ISO3", "adm0_a3", "ADM0_A3", "iso3"] if c in gdf_world.columns]
    if iso_cols:
        gdf_world["ISO3"] = gdf_world[iso_cols[0]]
    elif "name" in gdf_world.columns:
        gdf_world["ISO3"] = gdf_world["name"].apply(get_country_iso3)
    else:
        gdf_world["ISO3"] = gdf_world.index.astype(str)
        
    # Filter out Antarctica (ATA) to prevent global projection distortion
    gdf_world = gdf_world[gdf_world["ISO3"] != "ATA"].copy()
    
    # Merge with trade summary
    merged = gdf_world.merge(df_country_summary, on="ISO3", how="inner")
    if merged.empty:
        return gdf_world
        
    # Only scale valid trading economies
    merged = merged[merged["GDP"] > 0].copy()
    
    median_gdp = float(merged["GDP"].median()) if not merged.empty else 1000.0
    
    distorted_geoms = []
    scale_factors = []
    openness_ratios = []
    
    for _, row in merged.iterrows():
        geom = row["geometry"]
        gdp_val = row["GDP"]
        trade_val = row["Total Trade"]
        
        openness = (trade_val / gdp_val * 100.0) if gdp_val > 0 else 0.0
        openness_ratios.append(round(openness, 2))
        
        if geom is None or geom.is_empty or gdp_val <= 0:
            distorted_geoms.append(geom)
            scale_factors.append(1.0)
            continue
            
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
    carto_style: str = "Dorling Bubble Cartogram (Recommended)", # "Dorling Bubble Cartogram (Recommended)", "Geometric Polygon Scaling"
    title: Optional[str] = None
) -> go.Figure:
    """
    Generate an interactive GDP-Weighted Cartogram visualization.
    
    Supports:
    1. Dorling Bubble Cartogram: Circle size = GDP, Circle color = Trade Metric.
    2. Non-Contiguous Geometric Polygon Scaling: Landmass scaled by sqrt(GDP).
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
    
    if carto_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No country trade summary available for cartogram.", x=0.5, y=0.5, showarrow=False)
        return fig

    year_str = f" ({year})" if year else ""
    
    # ------------------------------------------------------------------
    # MODE 1: DORLING BUBBLE CARTOGRAM (Clear, intuitive, no overlapping background artifacts)
    # ------------------------------------------------------------------
    if "Dorling" in carto_style:
        # Calculate centroids for scattergeo placement
        lats, lons, names, iso3s, gdps, trades, balances, opennesses, sizes, hover_texts = [], [], [], [], [], [], [], [], [], []
        
        for _, row in carto_df.iterrows():
            geom = row["geometry"]
            if geom is None or geom.is_empty:
                continue
            centroid = geom.centroid
            lon, lat = centroid.x, centroid.y
            
            gdp_val = float(row["GDP"])
            trade_val = float(row["Total Trade"])
            balance_val = float(row["Trade Balance"])
            openness_val = float(row["trade_openness_pct"])
            iso = str(row["ISO3"])
            country = str(row["Country"])
            
            if gdp_val <= 0:
                continue
                
            # Size proportional to sqrt(GDP) for clear visual hierarchy
            marker_size = max(12, min(70, np.sqrt(gdp_val) * 0.38))
            
            tb_sign = "+" if balance_val >= 0 else ""
            ht = (
                f"<b>{country} ({iso})</b>{year_str}<br>"
                f"━━━━━━━━━━━━━━━━━━━━━━<br>"
                f"<b>Economic Size (Nominal GDP):</b> ${gdp_val:,.2f} B<br>"
                f"<b>Trade Openness (Trade/GDP):</b> {openness_val:.1f}%<br>"
                f"<b>Total Trade Volume:</b> ${trade_val:,.2f} B<br>"
                f"<b>Net Trade Balance:</b> {tb_sign}${balance_val:,.2f} B"
            )
            
            lons.append(lon)
            lats.append(lat)
            names.append(country)
            iso3s.append(iso)
            gdps.append(gdp_val)
            trades.append(trade_val)
            balances.append(balance_val)
            opennesses.append(openness_val)
            sizes.append(marker_size)
            hover_texts.append(ht)
            
        # Select color metric
        if metric_color == "Trade Openness (%)":
            z_vals = opennesses
            colorscale = "Viridis"
            colorbar_title = "Trade / GDP (%)"
            zmin, zmax = 0, min(float(np.quantile(opennesses, 0.95)), 200.0) if opennesses else 100.0
        elif metric_color == "Trade Balance":
            z_vals = balances
            colorscale = "RdYlGn"
            max_abs = max(float(np.max(np.abs(balances))), 1.0) if balances else 10.0
            zmin, zmax = -max_abs, max_abs
            colorbar_title = "Balance ($B)"
        else: # Total Trade
            z_vals = trades
            colorscale = "Plasma"
            zmin, zmax = 0, max(float(np.max(trades)), 1.0) if trades else 100.0
            colorbar_title = "Total Trade ($B)"
            
        fig = go.Figure()
        
        # Base geographic outlines trace for clear context
        fig.add_trace(go.Choropleth(
            locations=carto_df["ISO3"],
            z=[0]*len(carto_df),
            showscale=False,
            colorscale=[[0, "#1E293B"], [1, "#1E293B"]],
            marker_line_color="#334155",
            marker_line_width=0.8,
            hoverinfo="none"
        ))
        
        # Dorling GDP Bubble trace
        fig.add_trace(go.Scattergeo(
            lon=lons,
            lat=lats,
            text=hover_texts,
            hoverinfo="text",
            mode="markers+text",
            textposition="top center",
            textfont=dict(size=9, color="#CBD5E1"),
            marker=dict(
                size=sizes,
                color=z_vals,
                colorscale=colorscale,
                cmin=zmin,
                cmax=zmax,
                line=dict(color="#FFFFFF", width=1.2),
                opacity=0.88,
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
            )
        ))
        
        chart_title = title or f"<b>GDP-Weighted Dorling Cartogram{year_str}</b> (Bubble Size = Nominal GDP, Color = {metric_color})"
        
    # ------------------------------------------------------------------
    # MODE 2: GEOMETRIC POLYGON SCALING
    # ------------------------------------------------------------------
    else:
        features = []
        for _, row in carto_df.iterrows():
            geom = row["cartogram_geometry"]
            if geom is not None and not geom.is_empty and row["GDP"] > 0:
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
                
        custom_geojson = {"type": "FeatureCollection", "features": features}
        
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
            
        fig = go.Figure()
        
        # Base background map
        fig.add_trace(go.Choropleth(
            locations=carto_df["ISO3"],
            z=[0]*len(carto_df),
            showscale=False,
            colorscale=[[0, "#1E293B"], [1, "#1E293B"]],
            marker_line_color="#334155",
            marker_line_width=0.5,
            hoverinfo="none"
        ))
        
        # Scaled polygons trace
        fig.add_trace(go.Choropleth(
            geojson=custom_geojson,
            locations=carto_df["ISO3"],
            z=z_values,
            text=hover_text,
            hoverinfo="text",
            colorscale=colorscale,
            zmin=zmin,
            zmax=zmax,
            marker_line_color="#38BDF8",
            marker_line_width=1.0,
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
        
        chart_title = title or f"<b>GDP-Weighted Scaled Polygon Cartogram{year_str}</b> (Area ∝ GDP, Color = {metric_color})"

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
        height=540,
        showlegend=False
    )
    
    return fig
