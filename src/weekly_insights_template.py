"""
WhatsApp weekly_insights Template Support
Once approved, use this to send your insights!
"""
from typing import Dict
import requests
from loguru import logger

from src.config import settings
from src.utils import format_phone_number


def send_weekly_insights_template(
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
    
    url = f"{settings.meta_graph_api_url}/{settings.whatsapp_phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {settings.whatsapp_access_token}",
        "Content-Type": "application/json"
    }
    
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
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        logger.success(f"weekly_insights template sent to {formatted_phone}")
        return result
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"Failed to send template: {e}")
        logger.error(f"Response: {e.response.text}")
        raise


if __name__ == "__main__":
    # Test the template
    print("Testing weekly_insights template...")
    print()
    
    try:
        result = send_weekly_insights_template(
            to="27727377590",
            name="Melville",
            leads="230",
            portal="P24 - 60%",
            offer="3",
            sale="2",
            revenue="R8mil",
            commission="R150k"
        )
        
        msg_id = result.get('messages', [{}])[0].get('id', 'N/A')
        print(f"✅ Template sent successfully!")
        print(f"   Message ID: {msg_id}")
        print()
        print("📱 Check WhatsApp!")
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        print()
        print("Common reasons:")
        print("  1. Template not approved yet (check Meta Business Manager)")
        print("  2. Template name changed during approval")
        print("  3. Wrong number of parameters")
