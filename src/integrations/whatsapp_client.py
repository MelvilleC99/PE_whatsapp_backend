"""
WhatsApp client for Meta's WhatsApp Business API
"""
import requests
from typing import Optional, Dict, List
from loguru import logger

from src.config import settings
from src.utils.formatters import format_phone_number


class WhatsAppClient:
    """Client for sending WhatsApp messages via Meta's Business API"""
    
    def __init__(self):
        """Initialize WhatsApp client with Meta credentials"""
        self.access_token = settings.whatsapp_access_token
        self.phone_number_id = settings.whatsapp_phone_number_id
        self.base_url = f"{settings.meta_graph_api_url}/{self.phone_number_id}/messages"
        
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"WhatsApp client initialized with phone ID: {self.phone_number_id}")
    
    def send_text_message(self, to: str, message: str) -> Dict:
        """
        Send a text message via WhatsApp
        
        Args:
            to: Recipient phone number (will be formatted to E.164)
            message: Message text to send
            
        Returns:
            API response dictionary
        """
        formatted_phone = format_phone_number(to)
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": formatted_phone,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message
            }
        }
        
        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            logger.success(f"Message sent to {formatted_phone}: {result.get('messages', [{}])[0].get('id', 'unknown')}")
            return result
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to send message to {formatted_phone}: {e}")
            logger.error(f"Response: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending message: {e}")
            raise

    def send_interactive_button_message(self, to: str, body_text: str, 
                                       buttons: List[Dict]) -> Dict:
        """
        Send an interactive message with reply buttons
        
        Args:
            to: Recipient phone number
            body_text: Main message text
            buttons: List of button dicts with 'id' and 'title'
                    Example: [{"id": "btn1", "title": "Yes"}, {"id": "btn2", "title": "No"}]
        
        Returns:
            API response dictionary
        """
        formatted_phone = format_phone_number(to)
        
        # Maximum 3 buttons allowed
        if len(buttons) > 3:
            logger.warning("Maximum 3 buttons allowed, truncating")
            buttons = buttons[:3]
        
        button_objects = [
            {
                "type": "reply",
                "reply": {"id": btn["id"], "title": btn["title"]}
            }
            for btn in buttons
        ]
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": formatted_phone,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": body_text},
                "action": {"buttons": button_objects}
            }
        }
        
        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            logger.success(f"Interactive message sent to {formatted_phone}")
            return result
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to send interactive message: {e}")
            logger.error(f"Response: {e.response.text}")
            raise
    
    def send_list_message(self, to: str, body_text: str, button_text: str, 
                         sections: List[Dict]) -> Dict:
        """
        Send an interactive list message
        
        Args:
            to: Recipient phone number
            body_text: Main message text
            button_text: Text for the list button
            sections: List of section dicts with 'title' and 'rows'
                     Example: [{"title": "Options", "rows": [{"id": "1", "title": "Option 1"}]}]
        
        Returns:
            API response dictionary
        """
        formatted_phone = format_phone_number(to)
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": formatted_phone,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {"text": body_text},
                "action": {
                    "button": button_text,
                    "sections": sections
                }
            }
        }
        
        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            logger.success(f"List message sent to {formatted_phone}")
            return result
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to send list message: {e}")
            logger.error(f"Response: {e.response.text}")
            raise

    def test_connection(self) -> bool:
        """
        Test if WhatsApp API credentials are working
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Try to get phone number info
            url = f"{settings.meta_graph_api_url}/{self.phone_number_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            info = response.json()
            logger.success(f"✅ Connection successful! Phone: {info.get('display_phone_number', 'N/A')}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            return False
