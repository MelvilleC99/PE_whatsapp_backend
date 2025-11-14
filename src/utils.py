"""
Utility functions for the WhatsApp backend
"""
import re
from typing import Optional
from datetime import datetime
import pytz
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


def get_current_time_in_timezone(timezone: str = "Africa/Johannesburg") -> datetime:
    """
    Get current time in specified timezone
    
    Args:
        timezone: Timezone string (default: Africa/Johannesburg)
        
    Returns:
        Current datetime in specified timezone
    """
    tz = pytz.timezone(timezone)
    return datetime.now(tz)


def format_insight_message(insights: dict, user_name: str) -> str:
    """
    Format insights into a WhatsApp message
    
    Args:
        insights: Dictionary of insight data
        user_name: Name of the user
        
    Returns:
        Formatted message string
    """
    # Customize your header here
    message = f"🏡 *Your Weekly Property Report*\n"
    message += f"Hello {user_name}! 👋\n\n"
    message += f"Here's your performance summary:\n\n"
    
    # Add insights dynamically based on your metrics
    if "leads" in insights:
        message += f"📈 *New Leads:* {insights['leads']}\n"
    
    if "most_active_portal" in insights:
        message += f"🌐 *Top Portal:* {insights['most_active_portal']}\n"
    
    if "new_offers" in insights:
        message += f"💼 *New Offers:* {insights['new_offers']}\n"
    
    if "sales" in insights:
        message += f"🏠 *Sales Closed:* {insights['sales']}\n"
    
    if "revenue" in insights:
        try:
            # Try to format as currency if it's a number
            revenue_val = float(insights['revenue'])
            message += f"💰 *Revenue:* R{revenue_val:,.2f}\n"
        except (ValueError, TypeError):
            # If not a number, just display as-is
            message += f"💰 *Revenue:* {insights['revenue']}\n"
    
    if "commission" in insights:
        try:
            # Try to format as currency if it's a number
            commission_val = float(insights['commission'])
            message += f"🎯 *Commission:* R{commission_val:,.2f}\n"
        except (ValueError, TypeError):
            # If not a number, just display as-is
            message += f"🎯 *Commission:* {insights['commission']}\n"
    
    # Legacy fields (for backward compatibility)
    if "sales_change" in insights:
        emoji = "📈" if "+" in str(insights["sales_change"]) else "📉"
        message += f"{emoji} *Sales Change:* {insights['sales_change']}\n"
    
    if "active_listings" in insights:
        message += f"🏘️ *Active Listings:* {insights['active_listings']}\n"
    
    if "avg_price" in insights:
        try:
            # Try to format as currency if it's a number
            price_val = float(insights['avg_price'])
            message += f"💵 *Average Price:* R{price_val:,.2f}\n"
        except (ValueError, TypeError):
            # If not a number, just display as-is
            message += f"💵 *Average Price:* {insights['avg_price']}\n"
    
    if "sales_velocity" in insights:
        message += f"⚡ *Sales Velocity:* {insights['sales_velocity']}\n"
    
    # Add footer
    message += f"\n━━━━━━━━━━━━━━━━━\n"
    message += f"📅 {datetime.now().strftime('%d %B %Y')}\n"
    message += f"\n💡 _Reply 'insights' anytime for your latest report_"
    
    return message


def setup_logging(log_level: str = "INFO"):
    """
    Setup loguru logger configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    logger.remove()  # Remove default handler
    logger.add(
        "logs/whatsapp_backend.log",
        rotation="10 MB",
        retention="30 days",
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    )
    logger.add(
        lambda msg: print(msg, end=""),
        level=log_level,
        colorize=True,
        format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}"
    )
