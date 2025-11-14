#!/usr/bin/env python3
"""
Final attempt - using exact Meta template format
Based on the screenshot showing {{name}} variable
"""
import sys
sys.path.insert(0, '/Users/melville/Documents/PE_whatsapp_backend')

import requests
import json
from src.config import settings

print("=" * 70)
print("Sending Template - Final Attempt")
print("=" * 70)
print()

# Based on your screenshot:
# Header: "Insights summary"
# Body: "Hi {{name}} View your weekly insights summary"
# Button: "Visit website" (static URL)

phone = "27727377590"
name = "Melville"

url = f"{settings.meta_graph_api_url}/{settings.whatsapp_phone_number_id}/messages"
headers = {
    "Authorization": f"Bearer {settings.whatsapp_access_token}",
    "Content-Type": "application/json"
}

# The correct payload based on Meta documentation
payload = {
    "messaging_product": "whatsapp",
    "to": phone,
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
            }
        ]
    }
}

print("Sending with payload:")
print(json.dumps(payload, indent=2))
print()

try:
    response = requests.post(url, headers=headers, json=payload)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    
    if response.status_code == 200:
        msg_id = response.json().get('messages', [{}])[0].get('id', 'N/A')
        print("✅ SUCCESS!")
        print(f"   Message ID: {msg_id}")
        print()
        print("📱 Check WhatsApp at +27727377590")
        print()
        print("You should receive:")
        print("┌────────────────────────────────────┐")
        print("│ Insights summary                   │")
        print("│                                    │")
        print(f"│ Hi {name}                           │")
        print("│ View your weekly insights summary  │")
        print("│                                    │")
        print("│ [Visit website]                    │")
        print("└────────────────────────────────────┘")
    else:
        error = response.json().get('error', {})
        print("❌ FAILED")
        print(f"   Error: {error.get('message')}")
        print(f"   Details: {error.get('error_data', {}).get('details')}")
        print()
        
        # Additional debugging
        if "parameter" in error.get('message', '').lower():
            print("💡 This is a parameter issue. Let me check the template...")
            print()
            
            # Get template details
            template_url = f"{settings.meta_graph_api_url}/{settings.whatsapp_business_account_id}/message_templates"
            template_response = requests.get(
                template_url, 
                headers=headers,
                params={"name": "insights_dashboard", "status": "APPROVED"}
            )
            
            if template_response.status_code == 200:
                templates = template_response.json().get('data', [])
                if templates:
                    t = templates[0]
                    print("Template details:")
                    print(f"  Name: {t.get('name')}")
                    print(f"  Status: {t.get('status')}")
                    print(f"  Language: {t.get('language')}")
                    print()
                    print("  Components:")
                    for comp in t.get('components', []):
                        print(f"    Type: {comp.get('type')}")
                        if comp.get('text'):
                            print(f"    Text: {comp.get('text')}")
                        if comp.get('format'):
                            print(f"    Format: {comp.get('format')}")

except Exception as e:
    print(f"❌ Exception: {e}")
    import traceback
    traceback.print_exc()
