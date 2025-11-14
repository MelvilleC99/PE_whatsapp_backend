"""
Formatting utilities for phone numbers, currency, dates, etc.
"""
import re
from datetime import datetime
from loguru import logger


def format_phone_number(phone: str) -> str:
    """
    Format phone number to E.164 format (required by WhatsApp)
    
    Examples:
        '0821234567' -> '27821234567'
        '+27821234567' -> '27821234567'
        '27821234567' -> '27821234567'
    
    Args:
        phone: Phone number in various formats
        
    Returns:
        E.164 formatted phone number (without + prefix)
    """
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # If starts with 0, replace with country code (assuming South Africa)
    if digits.startswith('0'):
        digits = '27' + digits[1:]
    
    # Remove leading + if present
    if phone.startswith('+'):
        return digits
    
    return digits


def format_currency(value: float, currency_symbol: str = "R") -> str:
    """
    Format a number as currency
    
    Args:
        value: Numeric value to format
        currency_symbol: Currency symbol (default: R for ZAR)
        
    Returns:
        Formatted currency string (e.g., "R1,234.56")
    """
    try:
        return f"{currency_symbol}{value:,.2f}"
    except (ValueError, TypeError):
        logger.warning(f"Could not format value as currency: {value}")
        return str(value)


def format_date(date: datetime, format_string: str = "%d %B %Y") -> str:
    """
    Format a datetime object to a string
    
    Args:
        date: Datetime object to format
        format_string: strftime format string
        
    Returns:
        Formatted date string
    """
    return date.strftime(format_string)


def format_percentage(value: float, decimal_places: int = 1) -> str:
    """
    Format a number as a percentage
    
    Args:
        value: Numeric value to format (e.g., 0.15 for 15%)
        decimal_places: Number of decimal places
        
    Returns:
        Formatted percentage string (e.g., "15.0%")
    """
    try:
        return f"{value * 100:.{decimal_places}f}%"
    except (ValueError, TypeError):
        logger.warning(f"Could not format value as percentage: {value}")
        return str(value)
