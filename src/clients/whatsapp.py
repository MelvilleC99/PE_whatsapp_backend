"""
WhatsApp client for Meta's WhatsApp Business API
"""
import requests
from typing import Optional, Dict, List
from loguru import logger

from src.config import settings
from src.shared.formatters import format_phone_number


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
                                       buttons: List[Dict],
                                       header: str = None,
                                       footer: str = None) -> Dict:
        """
        Send an interactive message with reply buttons
        
        Args:
            to: Recipient phone number
            body_text: Main message text
            buttons: List of button dicts with 'id' and 'title'
            header: Optional header text
            footer: Optional footer text (appears greyed out)
        
        Returns:
            API response dictionary
        """
        formatted_phone = format_phone_number(to)
        
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
        
        interactive = {
            "type": "button",
            "body": {"text": body_text},
            "action": {"buttons": button_objects}
        }
        
        if header:
            interactive["header"] = {"type": "text", "text": header}
        if footer:
            interactive["footer"] = {"text": footer}
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": formatted_phone,
            "type": "interactive",
            "interactive": interactive
        }
        
        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            logger.success(f"Interactive message sent to {formatted_phone}")
            return result
            
        except requests.exceptions.HTTPError as e:
            # Log the actual error response from WhatsApp
            error_body = ""
            try:
                error_body = response.json()
            except:
                error_body = response.text
            logger.error(f"Failed to send interactive message: {e}")
            logger.error(f"WhatsApp error response: {error_body}")
            logger.error(f"Payload sent: {payload}")
            raise

    def send_interactive_list_message(
        self, 
        to: str, 
        body_text: str,
        button_text: str,
        sections: List[Dict],
        header: str = None,
        footer: str = None
    ) -> Dict:
        """
        Send an interactive list message (dropdown menu style)
        
        Args:
            to: Recipient phone number
            body_text: Main message text
            button_text: Text on the button that opens the list (max 20 chars)
            sections: List of section dicts, each with 'title' and 'rows'
                     Each row has 'id', 'title', and optional 'description'
            header: Optional header text
            footer: Optional footer text
        
        Example sections:
            [
                {
                    "title": "Services",
                    "rows": [
                        {"id": "insights", "title": "📊 Insights", "description": "Weekly performance reports"},
                        {"id": "listings", "title": "🏠 Listings", "description": "Create property listings"}
                    ]
                }
            ]
        
        Returns:
            API response dictionary
        """
        formatted_phone = format_phone_number(to)
        
        interactive = {
            "type": "list",
            "body": {"text": body_text},
            "action": {
                "button": button_text[:20],  # Max 20 chars
                "sections": sections
            }
        }
        
        if header:
            interactive["header"] = {"type": "text", "text": header}
        if footer:
            interactive["footer"] = {"text": footer}
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": formatted_phone,
            "type": "interactive",
            "interactive": interactive
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
        """Test if WhatsApp API credentials are working"""
        try:
            url = f"{settings.meta_graph_api_url}/{self.phone_number_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            info = response.json()
            logger.success(f"✅ Connection successful! Phone: {info.get('display_phone_number', 'N/A')}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            return False
    
    def get_media_url(self, media_id: str) -> Optional[str]:
        """
        Get the download URL for a media file.
        
        Args:
            media_id: WhatsApp media ID
            
        Returns:
            URL to download the media file, or None if failed
        """
        try:
            url = f"{settings.meta_graph_api_url}/{media_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            media_url = result.get('url')
            
            logger.info(f"Got media URL for {media_id}")
            return media_url
            
        except Exception as e:
            logger.error(f"Failed to get media URL: {e}")
            return None
    
    def download_media(self, media_id: str) -> Optional[bytes]:
        """
        Download a media file from WhatsApp.
        
        Args:
            media_id: WhatsApp media ID
            
        Returns:
            File content as bytes, or None if failed
        """
        try:
            # Step 1: Get the media URL
            media_url = self.get_media_url(media_id)
            
            if not media_url:
                return None
            
            # Step 2: Download the file (needs auth header)
            response = requests.get(media_url, headers=self.headers)
            response.raise_for_status()
            
            logger.info(f"Downloaded media {media_id}: {len(response.content)} bytes")
            return response.content
            
        except Exception as e:
            logger.error(f"Failed to download media: {e}")
            return None
