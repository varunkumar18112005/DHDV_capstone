"""
Download or generate standard country geometries for GeoPandas and Cartogram visualizations.
"""
import urllib.request
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import RAW_DATA_DIR

def get_country_geojson():
    out_file = RAW_DATA_DIR / "countries.geojson"
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    urls = [
        "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson",
        "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json"
    ]
    
    downloaded = False
    for url in urls:
        try:
            print(f"Attempting download from {url}...")
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                with open(out_file, "w", encoding="utf-8") as f:
                    json.dump(data, f)
                print(f"Successfully saved GeoJSON ({len(data.get('features', []))} features) to {out_file}")
                downloaded = True
                break
        except Exception as e:
            print(f"Failed to download from {url}: {e}")
            
    if not downloaded:
        print("Creating fallback synthetic country GeoJSON boundaries...")
        # Create standard bounding box/centroid polygons for countries if offline
        from utils.country_mapping import COUNTRY_MAP, ISO3_TO_NAME
        import shapely.geometry
        
        # Centroid coordinates for major nations
        coords = {
            "USA": (-98.5, 39.8), "CHN": (104.1, 35.8), "DEU": (10.4, 51.1), "JPN": (138.2, 36.2),
            "IND": (78.9, 20.5), "GBR": (-3.4, 55.3), "FRA": (2.2, 46.2), "KOR": (127.7, 35.9),
            "ITA": (12.5, 41.8), "CAN": (-106.3, 56.1), "BRA": (-51.9, -14.2), "AUS": (133.7, -25.2),
            "NLD": (5.2, 52.1), "MEX": (-102.5, 23.6), "SAU": (45.0, 23.8), "ARE": (53.8, 23.4),
            "SGP": (103.8, 1.3), "CHE": (8.2, 46.8), "ESP": (-3.7, 40.4), "RUS": (105.3, 61.5),
            "IDN": (113.9, -0.7), "TUR": (35.2, 38.9), "ZAF": (22.9, -30.5), "VNM": (108.2, 14.0),
            "MYS": (101.9, 4.2), "THA": (100.9, 15.8), "BEL": (4.4, 50.5), "POL": (19.1, 51.9),
            "SWE": (18.6, 60.1), "NOR": (8.4, 60.4), "ARG": (-63.6, -38.4), "EGY": (30.8, 26.8),
            "NGA": (8.6, 9.0), "ISR": (34.8, 31.0), "CHL": (-71.5, -35.6), "COL": (-74.2, 4.5),
            "PHL": (121.7, 12.8), "PAK": (69.3, 30.3), "BGD": (90.3, 23.6), "IRL": (-8.2, 53.4),
            "DNK": (9.5, 56.2), "AUT": (14.5, 47.5)
        }
        
        features = []
        for iso3, name in ISO3_TO_NAME.items():
            cx, cy = coords.get(iso3, (0, 0))
            # Create a 4x4 degree representative polygon box
            dx, dy = 3.0, 2.5
            box = shapely.geometry.box(cx - dx, cy - dy, cx + dx, cy + dy)
            features.append({
                "type": "Feature",
                "id": iso3,
                "properties": {
                    "ISO_A3": iso3,
                    "ADMIN": name,
                    "name": name
                },
                "geometry": shapely.geometry.mapping(box)
            })
            
        fc = {"type": "FeatureCollection", "features": features}
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(fc, f)
        print(f"Created fallback GeoJSON with {len(features)} countries.")

if __name__ == "__main__":
    get_country_geojson()
