"""
KPI Cards component.
Renders responsive, styled statistical cards with badges, icons, and dynamic deltas.
"""

import streamlit as st
from typing import Dict, Any
from utils.formatters import format_currency, format_percentage

def render_kpi_cards(metrics: Dict[str, float]) -> None:
    """
    Render 5 dynamic top-level KPI metric cards.
    
    Args:
        metrics: Dictionary containing [total_trade, total_exports, total_imports, trade_balance, yoy_growth].
    """
    total_trade = metrics.get("total_trade", 0.0)
    exports = metrics.get("total_exports", 0.0)
    imports = metrics.get("total_imports", 0.0)
    balance = metrics.get("trade_balance", 0.0)
    growth = metrics.get("yoy_growth", 0.0)
    
    # Trade balance badge status
    if balance > 0:
        balance_badge = '<span class="kpi-badge badge-surplus">▲ Surplus</span>'
    elif balance < 0:
        balance_badge = '<span class="kpi-badge badge-deficit">▼ Deficit</span>'
    else:
        balance_badge = '<span class="kpi-badge badge-neutral">● Balanced</span>'
        
    # Growth badge status
    if growth > 0:
        growth_badge = f'<span class="kpi-badge badge-surplus">▲ +{growth:.1f}%</span>'
    elif growth < 0:
        growth_badge = f'<span class="kpi-badge badge-deficit">▼ {growth:.1f}%</span>'
    else:
        growth_badge = f'<span class="kpi-badge badge-neutral">● 0.0%</span>'
        
    # 5-column layout
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🌐 Total Trade</div>
            <div class="kpi-value">{format_currency(total_trade)}</div>
            <div><span class="kpi-badge badge-neutral">Exports + Imports</span></div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">📤 Total Exports</div>
            <div class="kpi-value" style="color: #34D399;">{format_currency(exports)}</div>
            <div><span class="kpi-badge badge-surplus">Outflow Volume</span></div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">📥 Total Imports</div>
            <div class="kpi-value" style="color: #60A5FA;">{format_currency(imports)}</div>
            <div><span class="kpi-badge badge-neutral">Inflow Volume</span></div>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">⚖️ Trade Balance</div>
            <div class="kpi-value">{format_currency(balance)}</div>
            <div>{balance_badge}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">📈 YoY Growth Rate</div>
            <div class="kpi-value">{format_percentage(growth)}</div>
            <div>{growth_badge}</div>
        </div>
        """, unsafe_allow_html=True)
