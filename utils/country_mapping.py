"""
Country mapping and standardization utility.
Maps country names to standard ISO 3166-1 alpha-3, alpha-2, and official names.
"""

from typing import Optional, Dict, Any

COUNTRY_MAP: Dict[str, Dict[str, str]] = {
    "United States": {"iso3": "USA", "iso2": "US", "un_code": "842", "region": "North America"},
    "USA": {"iso3": "USA", "iso2": "US", "un_code": "842", "region": "North America"},
    "United States of America": {"iso3": "USA", "iso2": "US", "un_code": "842", "region": "North America"},
    "China": {"iso3": "CHN", "iso2": "CN", "un_code": "156", "region": "Asia"},
    "Germany": {"iso3": "DEU", "iso2": "DE", "un_code": "276", "region": "Europe"},
    "Japan": {"iso3": "JPN", "iso2": "JP", "un_code": "392", "region": "Asia"},
    "India": {"iso3": "IND", "iso2": "IN", "un_code": "356", "region": "Asia"},
    "United Kingdom": {"iso3": "GBR", "iso2": "GB", "un_code": "826", "region": "Europe"},
    "UK": {"iso3": "GBR", "iso2": "GB", "un_code": "826", "region": "Europe"},
    "France": {"iso3": "FRA", "iso2": "FR", "un_code": "250", "region": "Europe"},
    "South Korea": {"iso3": "KOR", "iso2": "KR", "un_code": "410", "region": "Asia"},
    "Korea, Rep.": {"iso3": "KOR", "iso2": "KR", "un_code": "410", "region": "Asia"},
    "Republic of Korea": {"iso3": "KOR", "iso2": "KR", "un_code": "410", "region": "Asia"},
    "Italy": {"iso3": "ITA", "iso2": "IT", "un_code": "380", "region": "Europe"},
    "Canada": {"iso3": "CAN", "iso2": "CA", "un_code": "124", "region": "North America"},
    "Brazil": {"iso3": "BRA", "iso2": "BR", "un_code": "076", "region": "South America"},
    "Australia": {"iso3": "AUS", "iso2": "AU", "un_code": "036", "region": "Oceania"},
    "Netherlands": {"iso3": "NLD", "iso2": "NL", "un_code": "528", "region": "Europe"},
    "Mexico": {"iso3": "MEX", "iso2": "MX", "un_code": "484", "region": "North America"},
    "Saudi Arabia": {"iso3": "SAU", "iso2": "SA", "un_code": "682", "region": "Middle East"},
    "United Arab Emirates": {"iso3": "ARE", "iso2": "AE", "un_code": "784", "region": "Middle East"},
    "UAE": {"iso3": "ARE", "iso2": "AE", "un_code": "784", "region": "Middle East"},
    "Singapore": {"iso3": "SGP", "iso2": "SG", "un_code": "702", "region": "Asia"},
    "Switzerland": {"iso3": "CHE", "iso2": "CH", "un_code": "756", "region": "Europe"},
    "Spain": {"iso3": "ESP", "iso2": "ES", "un_code": "724", "region": "Europe"},
    "Russia": {"iso3": "RUS", "iso2": "RU", "un_code": "643", "region": "Europe/Asia"},
    "Russian Federation": {"iso3": "RUS", "iso2": "RU", "un_code": "643", "region": "Europe/Asia"},
    "Indonesia": {"iso3": "IDN", "iso2": "ID", "un_code": "360", "region": "Asia"},
    "Turkey": {"iso3": "TUR", "iso2": "TR", "un_code": "792", "region": "Middle East/Europe"},
    "Turkiye": {"iso3": "TUR", "iso2": "TR", "un_code": "792", "region": "Middle East/Europe"},
    "South Africa": {"iso3": "ZAF", "iso2": "ZA", "un_code": "710", "region": "Africa"},
    "Vietnam": {"iso3": "VNM", "iso2": "VN", "un_code": "704", "region": "Asia"},
    "Viet Nam": {"iso3": "VNM", "iso2": "VN", "un_code": "704", "region": "Asia"},
    "Malaysia": {"iso3": "MYS", "iso2": "MY", "un_code": "458", "region": "Asia"},
    "Thailand": {"iso3": "THA", "iso2": "TH", "un_code": "764", "region": "Asia"},
    "Belgium": {"iso3": "BEL", "iso2": "BE", "un_code": "056", "region": "Europe"},
    "Poland": {"iso3": "POL", "iso2": "PL", "un_code": "616", "region": "Europe"},
    "Sweden": {"iso3": "SWE", "iso2": "SE", "un_code": "752", "region": "Europe"},
    "Norway": {"iso3": "NOR", "iso2": "NO", "un_code": "578", "region": "Europe"},
    "Argentina": {"iso3": "ARG", "iso2": "AR", "un_code": "032", "region": "South America"},
    "Egypt": {"iso3": "EGY", "iso2": "EG", "un_code": "818", "region": "Africa"},
    "Egypt, Arab Rep.": {"iso3": "EGY", "iso2": "EG", "un_code": "818", "region": "Africa"},
    "Nigeria": {"iso3": "NGA", "iso2": "NG", "un_code": "566", "region": "Africa"},
    "Israel": {"iso3": "ISR", "iso2": "IL", "un_code": "376", "region": "Middle East"},
    "Chile": {"iso3": "CHL", "iso2": "CL", "un_code": "152", "region": "South America"},
    "Colombia": {"iso3": "COL", "iso2": "CO", "un_code": "170", "region": "South America"},
    "Philippines": {"iso3": "PHL", "iso2": "PH", "un_code": "608", "region": "Asia"},
    "Pakistan": {"iso3": "PAK", "iso2": "PK", "un_code": "586", "region": "Asia"},
    "Bangladesh": {"iso3": "BGD", "iso2": "BD", "un_code": "050", "region": "Asia"},
    "Ireland": {"iso3": "IRL", "iso2": "IE", "un_code": "372", "region": "Europe"},
    "Denmark": {"iso3": "DNK", "iso2": "DK", "un_code": "208", "region": "Europe"},
    "Austria": {"iso3": "AUT", "iso2": "AT", "un_code": "040", "region": "Europe"}
}

# Reverse mapping for ISO3 -> Standard Name
ISO3_TO_NAME: Dict[str, str] = {
    "USA": "United States",
    "CHN": "China",
    "DEU": "Germany",
    "JPN": "Japan",
    "IND": "India",
    "GBR": "United Kingdom",
    "FRA": "France",
    "KOR": "South Korea",
    "ITA": "Italy",
    "CAN": "Canada",
    "BRA": "Brazil",
    "AUS": "Australia",
    "NLD": "Netherlands",
    "MEX": "Mexico",
    "SAU": "Saudi Arabia",
    "ARE": "United Arab Emirates",
    "SGP": "Singapore",
    "CHE": "Switzerland",
    "ESP": "Spain",
    "RUS": "Russia",
    "IDN": "Indonesia",
    "TUR": "Turkey",
    "ZAF": "South Africa",
    "VNM": "Vietnam",
    "MYS": "Malaysia",
    "THA": "Thailand",
    "BEL": "Belgium",
    "POL": "Poland",
    "SWE": "Sweden",
    "NOR": "Norway",
    "ARG": "Argentina",
    "EGY": "Egypt",
    "NGA": "Nigeria",
    "ISR": "Israel",
    "CHL": "Chile",
    "COL": "Colombia",
    "PHL": "Philippines",
    "PAK": "Pakistan",
    "BGD": "Bangladesh",
    "IRL": "Ireland",
    "DNK": "Denmark",
    "AUT": "Austria"
}

def get_country_iso3(country_name: str) -> Optional[str]:
    """
    Get ISO3 code from country name.
    
    Args:
        country_name: Name of the country.
        
    Returns:
        3-letter ISO code or None if not found.
    """
    if not country_name:
        return None
    name_clean = country_name.strip()
    if name_clean.upper() in ISO3_TO_NAME:
        return name_clean.upper()
    if name_clean in COUNTRY_MAP:
        return COUNTRY_MAP[name_clean]["iso3"]
    # Case-insensitive search
    for name, info in COUNTRY_MAP.items():
        if name.lower() == name_clean.lower():
            return info["iso3"]
    return None

def standardize_country_name(name_or_code: str) -> str:
    """
    Standardize any country name or ISO code to official standard display name.
    
    Args:
        name_or_code: Country name, ISO2, or ISO3 code.
        
    Returns:
        Standardized display name.
    """
    if not name_or_code:
        return "Unknown"
    clean = str(name_or_code).strip()
    # Check if direct ISO3
    if clean.upper() in ISO3_TO_NAME:
        return ISO3_TO_NAME[clean.upper()]
    # Check in country map
    if clean in COUNTRY_MAP:
        iso3 = COUNTRY_MAP[clean]["iso3"]
        return ISO3_TO_NAME.get(iso3, clean)
    for name, info in COUNTRY_MAP.items():
        if name.lower() == clean.lower():
            return ISO3_TO_NAME.get(info["iso3"], name)
    return clean

def get_un_code(country_name: str) -> Optional[str]:
    """
    Get UN Comtrade numeric country code.
    """
    if country_name in COUNTRY_MAP:
        return COUNTRY_MAP[country_name]["un_code"]
    iso3 = get_country_iso3(country_name)
    if iso3:
        for name, info in COUNTRY_MAP.items():
            if info["iso3"] == iso3:
                return info["un_code"]
    return None
