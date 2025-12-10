"""
Validation utilities for inputs
"""
from src.utils.formatters import format_phone_number


def validate_whatsapp_number(phone: str) -> bool:
    """
    Validate if phone number is in correct format for WhatsApp
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if valid, False otherwise
    """
    formatted = format_phone_number(phone)
    # Should be 10-15 digits after country code
    return len(formatted) >= 10 and len(formatted) <= 15 and formatted.isdigit()


def validate_email(email: str) -> bool:
    """
    Basic email validation
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid format, False otherwise
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
