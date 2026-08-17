# Development of a Global Trade and Import-Export Flow Visualization Platform Using Sankey and Geospatial Charts

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-5.18+-purple.svg)](https://plotly.com/)
[![GeoPandas](https://img.shields.io/badge/GeoPandas-0.14+-green.svg)](https://geopandas.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📌 1. Project Overview & Problem Statement

International trade represents over **$32 Trillion** in annual cross-border economic activity. However, analyzing trade data presents major challenges:
- Trade databases (e.g., UN Comtrade, WTO) contain **millions of complex multi-dimensional records** (origin, destination, HS product classification, bilateral trade flow, value).
- Policymakers, supply chain leaders, and economists struggle to intuitively decipher **supply chain vulnerabilities, bilateral trade imbalances, commodity dependencies, and macroeconomic shifts** using tabular records.
- Standard maps distort reality because physical landmass area does not correlate with actual economic weight or trade intensity.

### 🎯 Primary Objectives
1. **End-to-End Trade Intelligence**: Ingest, cleanse, and standardize multi-year bilateral trade data and macroeconomic indicators (World Bank GDP).
2. **Multi-Dimensional Flow Analysis**: Visualize origin-destination supply chains dynamically through multi-tier **Sankey Diagrams** and **Treemaps**.
3. **Geospatial & Cartographic Analytics**: Compare physical geographic borders (**Choropleth**) with economic mass (**GDP-Weighted Cartograms**).
4. **Time-Series Econometrics**: Detect quantitative trade momentum using **Rolling Moving Averages** and **Rule-Based Trend Classifiers**.

---

## 💡 2. Real-World Use Cases & Applications

| Domain | Practical Use Case | Key Platform Feature Used |
| :--- | :--- | :--- |
| **Government & Trade Ministries** | Evaluating bilateral trade deficits/surpluses and identifying export diversification targets. | **Choropleth Balance Map** & **KPI Surplus Cards** |
| **Supply Chain & Multinational Corporations** | Mapping critical commodity dependencies and finding alternate sourcing partners. | **Sankey Flow Diagrams** & **Treemap Composition** |
| **Economic Research & Think Tanks** | Analyzing trade openness ($\frac{\text{Trade}}{\text{GDP}}$) and economic scale vs land area. | **GDP-Weighted Cartograms** & **Moving Averages** |
| **Financial Analysts & Investment Banks** | Tracking historical commodity cycles and predicting export momentum. | **Stacked Bar Composition** & **Trend Classifiers** |

---

## 🏛️ 3. System Architecture & Pipeline

```
┌────────────────────────────────────────────────────────┐
│                   Data Ingestion Layer                 │
│  - UN Comtrade API (with API Key / Public v1)          │
│  - World Bank GDP API & Local Datasets                 │
│  - Natural Earth GeoJSON Country Boundaries            │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│              Preprocessing & Validation                │
│  - ISO-3 / Country Name Standardizer                   │
│  - Duplicate, Null, Negative Value Cleansing           │
│  - Cleaning Stats Tracker & Currency Normalization     │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│               Calculations & Aggregations              │
│  - Total Trade = Exports + Imports                     │
│  - Trade Balance = Exports - Imports                   │
│  - Export / Import Shares & YoY Growth Rates           │
│  - Rolling Moving Averages (3, 5, 7 yrs) & Trend Logic │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│                  Visualization Engines                 │
│  - Plotly Sankey: Country-Country / Country-Product    │
│  - Plotly Treemap: Product Hierarchy & Growth Color    │
│  - Plotly Stacked Bar: Time-Series Composition         │
│  - Plotly Choropleth: Global Trade Balance & GDP Hover │
│  - GeoPandas Cartogram: GDP Area-Distorted Geometry    │
│  - Plotly Trends: Actual vs Moving Avg + Regressions   │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│              Streamlit Presentation Layer              │
│  - Dynamic Sidebar Filters (Dependent selections)      │
│  - KPI Cards & Statistical Metric Tiles                │
│  - Interactive Visualizations & Geospatial Maps        │
│  - Filtered Data Table & Multi-Format CSV Exporter     │
└────────────────────────────────────────────────────────┘
```

---

## 🔬 4. Mathematical Formulations & Algorithms

### 1. Sankey Diagram Flow Generation
Given a filtered set of bilateral trade transactions:
1. Extract unique entity set $\mathcal{N} = \{s_1, \dots, s_u\} \cup \{t_1, \dots, t_v\}$.
2. Construct node index mapping $f: \mathcal{N} \to \{0, 1, \dots, |\mathcal{N}|-1\}$.
3. Aggregate flow weight $W_{ij} = \sum \text{trade\_value}(s_i \to t_j)$ for top $N$ links.
4. Compute link share: $\text{Share}_{ij} = \frac{W_{ij}}{\sum_{u,v} W_{uv}} \times 100\%$.

### 2. Treemap Product Proportions & Growth
- **Node Size**: Mapped to total trade volume $V_p = \sum_{t \in \text{prod } p} \text{value}_t$.
- **YoY Growth Rate**:
  $$\text{Growth}_p = \frac{V_p(t) - V_p(t-1)}{V_p(t-1)} \times 100\%$$
- **Color Scale**: Centered at $0\%$ using a diverging `RdYlGn` palette.

### 3. GDP-Weighted Non-Contiguous Cartogram
A true geometric cartogram scales land area proportional to nominal GDP:
1. Let $\text{GDP}_i$ be the GDP of country $i$ and $\overline{\text{GDP}}$ be the median global GDP.
2. Because area $A$ scales quadratically with linear dimension ($A' = S_i^2 A$), the linear scaling factor $S_i$ is computed as:
   $$S_i = \text{clamp}\left(\sqrt{\frac{\text{GDP}_i}{\overline{\text{GDP}}}}, S_{\min}, S_{\max}\right)$$
3. The distorted polygon $P'_i$ is computed using Shapely affine transformation anchored at the country's centroid $C_i$:
   $$P'_i = \mathcal{A}_{\text{scale}}(P_i, x_{\text{fact}}=S_i, y_{\text{fact}}=S_i, \text{origin}=C_i)$$
4. **Trade Openness Metric**: Polygons are colored by trade openness:
   $$\text{Trade Openness}_i = \frac{\text{Total Trade}_i}{\text{GDP}_i} \times 100\%$$

### 4. Rolling Moving Average & Trend Momentum Classifier
- **$n$-Year Moving Average**:
  $$\text{MA}_t(n) = \frac{1}{n} \sum_{i=0}^{n-1} Y_{t-i}$$
- **Rule-Based Trend Momentum**:
  Fit a linear regression $y_{\text{norm}} = \beta \cdot x + \alpha$ on the normalized trade trajectory $\frac{Y_t}{\overline{Y}}$:
  $$\text{Classification} = \begin{cases} \text{Increasing Trend} & \text{if } \beta > +0.025 \ (+2.5\%/\text{year}) \\ \text{Decreasing Trend} & \text{if } \beta < -0.025 \ (-2.5\%/\text{year}) \\ \text{Stable Trend} & \text{otherwise} \end{cases}$$

---

## 🗂️ 5. Project Directory Structure

```text
global-trade-analytics/
│
├── app.py                      # Main Streamlit Dashboard
├── requirements.txt            # Package dependencies
├── README.md                   # Comprehensive Capstone Documentation
├── .gitignore                  # Git ignore configuration
├── .env.example                # API credentials template
│
├── config/
│   ├── __init__.py
│   └── settings.py             # Global constants, paths, color palettes
│
├── data/
│   ├── raw/                    # Raw bilateral trade, GDP, GeoJSON boundaries
│   │   ├── trade_data.csv
│   │   ├── gdp_data.csv
│   │   └── countries.geojson
│   │
│   ├── processed/              # Cleaned datasets and summary aggregations
│   │   ├── cleaned_trade.csv
│   │   ├── country_summary.csv
│   │   ├── product_summary.csv
│   │   └── yearly_summary.csv
│   │
│   └── cache/
│
├── modules/
│   ├── __init__.py
│   ├── data_collection.py      # UN Comtrade & World Bank API client + fallback
│   ├── preprocessing.py        # Cleansing pipeline & audit metrics tracker
│   ├── calculations.py         # Total trade, Balance, YoY growth, summaries
│   ├── sankey.py               # Plotly Sankey flow engine
│   ├── treemap.py              # Plotly Treemap hierarchy engine
│   ├── stacked_bar.py          # Year-wise composition stacked bar engine
│   ├── choropleth.py           # Global trade balance choropleth map
│   ├── cartogram.py            # GeoPandas/Shapely GDP-scaled cartogram
│   └── trend_analysis.py       # Time-series trend analytics & MA engine
│
├── utils/
│   ├── __init__.py
│   ├── country_mapping.py      # ISO-2/3 & country name standardizer
│   ├── formatters.py           # Currency ($B), percentage, number formatters
│   └── validators.py           # Input, schema, and range validation
│
├── components/
│   ├── __init__.py
│   ├── filters.py              # Dynamic dependent sidebar filters
│   ├── kpi_cards.py            # Styled KPI summary cards
│   └── data_table.py           # Filtered records table & CSV exporters
│
├── scripts/
│   ├── generate_seed_data.py   # Seed dataset generator (53k+ records)
│   └── download_geojson.py     # GeoJSON boundary downloader
│
├── tests/
│   ├── test_preprocessing.py   # Tests for cleaning & null handling
│   ├── test_calculations.py    # Tests for trade balance & metrics
│   ├── test_sankey.py          # Tests for Sankey node/link generation
│   └── test_trends.py          # Tests for moving averages & classification
│
└── assets/
    └── styles.css              # Custom Glassmorphism CSS styles
```

---

## 🚀 6. Installation & Execution Guide

### Prerequisites
- Python 3.11 or higher
- pip package manager

### Step 1: Clone or Navigate to Directory
```powershell
cd "c:\Users\srika\OneDrive\Documents\DHDV\capstone project"
```

### Step 2: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Run Unit Tests
```powershell
python -m pytest tests/ -v
```

### Step 4: Launch the Streamlit Dashboard
```powershell
python -m streamlit run app.py
```
Open your browser at **`http://localhost:8501`**.

---

## ⚙️ 7. Configuration & Dual Data Modes

The platform supports two operational modes configurable via `.env` or sidebar:
1. **Local Mode (Default)**: Instant offline analytics using the bundled 53,200+ record multi-year dataset (2018–2024) across 20+ major global economies and standard HS product classifications.
2. **API Mode**: Queries live data from the UN Comtrade API v1 and World Bank Indicator APIs when internet access and API keys are available.

---

## 🧪 8. Test Suite Verification

Run the full automated test suite:
```powershell
python -m pytest tests/ -v
```

**Results**:
- ✅ `test_trade_balance_and_total_trade`: Verified $\text{Exports}=100$, $\text{Imports}=60 \implies \text{Balance}=40$, $\text{Total}=160$.
- ✅ `test_empty_dataset_calculations`: Verified graceful zero-handling on empty datasets.
- ✅ `test_product_shares_and_growth`: Verified product share $\%$ and YoY growth.
- ✅ `test_missing_values_handling`: Verified NaN pruning and audit counters.
- ✅ `test_invalid_trade_values`: Verified negative/zero/inf value elimination.
- ✅ `test_country_mapping_and_iso`: Verified ISO-3 standardization.
- ✅ `test_sankey_generation_valid`: Verified node and link graph construction.
- ✅ `test_moving_average_calculation`: Verified 3-year rolling average.
- ✅ `test_decreasing_trend_classification`: Verified quantitative trend classification.

---

## 🎓 9. Capstone Project Attribution
- **Title**: Development of a Global Trade and Import-Export Flow Visualization Platform Using Sankey and Geospatial Charts
- **Domain**: Full-Stack Data Engineering, Geospatial Analytics & Data Visualization
- **Target Audience**: B.Tech / Final Year Engineering Evaluation, Economists, Supply Chain Analysts.
