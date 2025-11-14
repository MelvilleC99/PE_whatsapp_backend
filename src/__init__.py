"""
PE WhatsApp Backend
WhatsApp automation for property insights delivery
"""

__version__ = "0.1.0"
__author__ = "Property Engine"

# Import from new structure
from src.config import settings
from src.integrations.whatsapp_client import WhatsAppClient
from src.integrations.firebase_client import FirebaseClient
from src.services.insights_service import InsightsService
from src.services.user_service import UserService

__all__ = [
    "settings",
    "WhatsAppClient",
    "FirebaseClient", 
    "InsightsService",
    "UserService",
]
