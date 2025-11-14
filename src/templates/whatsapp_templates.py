"""
WhatsApp Template Message Manager
For sending approved Meta templates
"""
import requests
from typing import Optional, Dict, List
from loguru import logger

from src.config import settings
from src.utils.formatters import format_phone_number


class WhatsAppTemplateManager:
    """Send WhatsApp template messages (no 24-hour window needed!)"""
    
    def __init__(self):
        """Initialize template manager with Meta credentials"""
        self.access_token = settings.whatsapp_access_token
        self.phone_number_id = settings.whatsapp_phone_number_id
        self.base_url = f"{settings.meta_graph_api_url}/{self.phone_number_id}/messages"
        
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        logger.info("WhatsApp template manager initialized")
    
    def send_weekly_insights_template(
        self,
        to: str,
        name: str,
        leads: str,
        portal: str,
        offer: str,
        sale: str,
        revenue: str,
        commission: str
    ) -> Dict:
        """
        Send the 'weekly_insights' template with all metrics
        
        Args:
            to: Recipient phone number
            name: User's name
            leads: Number of leads (e.g., "230")
            portal: Most active portal (e.g., "P24 - 60%")
            offer: New offers (e.g., "3")
            sale: Sales (e.g., "2")
            revenue: Revenue (e.g., "R8mil")
            commission: Commission (e.g., "R150k")
            
        Returns:
            API response dictionary
        """
        formatted_phone = format_phone_number(to)
        
        payload = {
            "messaging_product": "whatsapp",
            "to": formatted_phone,
            "type": "template",
            "template": {
                "name": "weekly_insights",
                "language": {
                    "code": "en"
                },
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": name},
                            {"type": "text", "text": str(leads)},
                            {"type": "text", "text": portal},
                            {"type": "text", "text": str(offer)},
                            {"type": "text", "text": str(sale)},
                            {"type": "text", "text": revenue},
                            {"type": "text", "text": commission}
                        ]
                    }
                ]
            }
        }
        
        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            logger.success(f"weekly_insights template sent to {formatted_phone}")
            return result
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to send template: {e}")
            logger.error(f"Response: {e.response.text}")
            raise
    
    def send_insights_dashboard_template(self, to: str, name: str, 
                                        dashboard_url: str) -> Dict:
        """
        Send the 'insights_dashboard' template
        
        Template structure:
        - Header: "Insights summary"
        - Body: "Hi {{name}} View your weekly insights summary"
        - Button: "Visit website" → dashboard_url
        
        Args:
            to: Recipient phone number
            name: User's name (replaces {{name}} in template)
            dashboard_url: URL for the dashboard button
            
        Returns:
            API response dictionary
        """
        formatted_phone = format_phone_number(to)
        
        payload = {
            "messaging_product": "whatsapp",
            "to": formatted_phone,
            "type": "template",
            "template": {
                "name": "insights_dashboard",
                "language": {
                    "code": "en"
                },
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {
                                "type": "text",
                                "text": name
                            }
                        ]
                    },
                    {
                        "type": "button",
                        "sub_type": "url",
                        "index": "0",
                        "parameters": [
                            {
                                "type": "text",
                                "text": dashboard_url
                            }
                        ]
                    }
                ]
            }
        }
        
        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            logger.success(f"Template message sent to {formatted_phone}")
            return result
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to send template: {e}")
            logger.error(f"Response: {e.response.text}")
            raise
    
    def send_generic_template(self, to: str, template_name: str, 
                             language_code: str = "en",
                             body_params: Optional[List[str]] = None,
                             header_params: Optional[List[str]] = None) -> Dict:
        """
        Send any template message (generic version)
        
        Args:
            to: Recipient phone number
            template_name: Name of the approved template
            language_code: Template language (en, es, etc.)
            body_params: List of parameters for body {{1}}, {{2}}, etc.
            header_params: List of parameters for header
            
        Returns:
            API response dictionary
        """
        formatted_phone = format_phone_number(to)
        
        components = []
        
        # Add header parameters if provided
        if header_params:
            components.append({
                "type": "header",
                "parameters": [
                    {"type": "text", "text": param} 
                    for param in header_params
                ]
            })
        
        # Add body parameters if provided
        if body_params:
            components.append({
                "type": "body",
                "parameters": [
                    {"type": "text", "text": param} 
                    for param in body_params
                ]
            })
        
        payload = {
            "messaging_product": "whatsapp",
            "to": formatted_phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code},
                "components": components
            }
        }
        
        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            logger.success(f"Template '{template_name}' sent to {formatted_phone}")
            return result
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to send template: {e}")
            logger.error(f"Response: {e.response.text}")
            raise
