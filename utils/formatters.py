"""
Value formatting utilities for currency, percentages, and metrics.
"""

from typing import Union

def format_currency(value: Union[float, int], unit: str = "B", currency_symbol: str = "$") -> str:
    """
    Format numerical trade/GDP value into human-readable currency with units.
    
    Args:
        value: Numeric value in billions (or raw if unit specified).
        unit: 'B' for Billion, 'M' for Million, 'T' for Trillion.
        currency_symbol: Prefix symbol (default '$').
        
    Returns:
        Formatted string, e.g. '$142.50 B' or '-$12.30 B'.
    """
    if value is None or (isinstance(value, float) and value != value): # NaN check
        return "N/A"
    
    sign = "-" if value < 0 else ""
    abs_val = abs(value)
    
    if unit == "B":
        return f"{sign}{currency_symbol}{abs_val:,.2f} B"
    elif unit == "M":
        return f"{sign}{currency_symbol}{abs_val:,.2f} M"
    elif unit == "T":
        return f"{sign}{currency_symbol}{abs_val:,.2f} T"
    else:
        return f"{sign}{currency_symbol}{abs_val:,.2f}"

def format_percentage(value: Union[float, int], include_sign: bool = True) -> str:
    """
    Format percentage with positive/negative indicators.
    
    Args:
        value: Percentage value (e.g. 12.34 for 12.34%).
        include_sign: Whether to prefix '+' on positive numbers.
        
    Returns:
        Formatted percentage string, e.g. '+12.34%' or '-5.21%'.
    """
    if value is None or (isinstance(value, float) and value != value):
        return "0.00%"
    
    if include_sign and value > 0:
        return f"+{value:.2f}%"
    return f"{value:.2f}%"

def format_number(value: Union[float, int], decimals: int = 2) -> str:
    """
    Format numbers with comma separators.
    """
    if value is None or (isinstance(value, float) and value != value):
        return "0"
    return f"{value:,.{decimals}f}"
