"""
Test script for insights_summary WhatsApp template
Run this to send yourself a test message
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import requests
from src.config import settings
from src.utils import format_phone_number

def send_insights_summary(
    to: str,
    name: str,
    leads: str,
    portal: str,
    offer: str,
    sale: str,
    revenue: str,
    commission: str
):
    """
    Send the insights_summary template
    
    Template variables (in order):
    {{1}} = name
    {{2}} = leads
    {{3}} = portal
    {{4}} = offer
    {{5}} = sale
    {{6}} = revenue
    {{7}} = commission
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
            "name": "insights_summary",
            "language": {
                "code": "en"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": str(name)},
                        {"type": "text", "text": str(leads)},
                        {"type": "text", "text": str(portal)},
                        {"type": "text", "text": str(offer)},
                        {"type": "text", "text": str(sale)},
                        {"type": "text", "text": str(revenue)},
                        {"type": "text", "text": str(commission)}
                    ]
                }
            ]
        }
    }
    
    print(f"📱 Sending to: {formatted_phone}")
    print(f"📊 Template: insights_summary")
    print(f"📝 Data:")
    print(f"   Name: {name}")
    print(f"   Leads: {leads}")
    print(f"   Portal: {portal}")
    print(f"   Offers: {offer}")
    print(f"   Sales: {sale}")
    print(f"   Revenue: {revenue}")
    print(f"   Commission: {commission}")
    print()
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        msg_id = result.get('messages', [{}])[0].get('id', 'N/A')
        
        print(f"✅ Success! Message ID: {msg_id}")
        print(f"📱 Check your WhatsApp!")
        return result
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error: {e}")
        print(f"   Response: {e.response.text}")
        raise
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    # Test with sample data
    send_insights_summary(
        to="27727377590",
        name="Melville",
        leads="123",
        portal="P24 34%",
        offer="2",
        sale="3",
        revenue="R4mil",
        commission="R300k"
    )
