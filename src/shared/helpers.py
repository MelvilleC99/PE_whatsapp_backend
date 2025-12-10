"""
General helper utilities
"""
from datetime import datetime
import pytz
from loguru import logger


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
