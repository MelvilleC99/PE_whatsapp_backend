"""
PE WhatsApp Backend
WhatsApp automation for property insights delivery
"""

__version__ = "0.1.0"
__author__ = "Property Engine"

from src.config import settings
from src.whatsapp_sender import WhatsAppSender
from src.firebase_manager import FirebaseManager
from src.insight_generator import InsightGenerator

__all__ = [
    "settings",
    "WhatsAppSender",
    "FirebaseManager", 
    "InsightGenerator",
]
