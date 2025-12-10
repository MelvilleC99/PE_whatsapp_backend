"""
Message Sender Tool - Send messages via WhatsApp
"""
from typing import Dict, Any
from loguru import logger

from .registry import BaseTool


class MessageSenderTool(BaseTool):
    """Tool for sending WhatsApp messages."""
    
    name = "message_sender"
    description = "Send a text message to a user via WhatsApp"
    
    def __init__(self):
        from src.clients.whatsapp import WhatsAppClient
        self.whatsapp = WhatsAppClient()
    
    def execute(self, phone: str, message: str, **kwargs) -> Dict[str, Any]:
        """
        Send a message.
        
        Args:
            phone: Recipient phone number
            message: Message text to send
            
        Returns:
            Result with status
        """
        try:
            self.whatsapp.send_text_message(phone, message)
            return {'status': 'success', 'phone': phone}
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return {'status': 'error', 'error': str(e)}
