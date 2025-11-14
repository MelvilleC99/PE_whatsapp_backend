#!/usr/bin/env python3
"""
Discover all WhatsApp templates in your account
"""
import sys
sys.path.insert(0, '/Users/melville/Documents/PE_whatsapp_backend')

import requests
from src.config import settings

print("=" * 70)
print("Discovering Your WhatsApp Templates")
print("=" * 70)
print()

# Get WhatsApp Business Account templates
url = f"{settings.meta_graph_api_url}/{settings.whatsapp_business_account_id}/message_templates"
headers = {"Authorization": f"Bearer {settings.whatsapp_access_token}"}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    
    if 'data' in data and len(data['data']) > 0:
        print(f"✅ Found {len(data['data'])} template(s):")
        print()
        
        for idx, template in enumerate(data['data'], 1):
            print(f"Template #{idx}:")
            print(f"  Name: {template.get('name')}")
            print(f"  Status: {template.get('status')}")
            print(f"  Language: {template.get('language')}")
            print(f"  Category: {template.get('category')}")
            print()
            
            # Show components
            if 'components' in template:
                for component in template['components']:
                    comp_type = component.get('type')
                    print(f"  Component: {comp_type}")
                    
                    if comp_type == 'HEADER':
                        print(f"    Format: {component.get('format')}")
                        if component.get('text'):
                            print(f"    Text: {component.get('text')}")
                    
                    elif comp_type == 'BODY':
                        print(f"    Text: {component.get('text')}")
                    
                    elif comp_type == 'FOOTER':
                        print(f"    Text: {component.get('text')}")
                    
                    elif comp_type == 'BUTTONS':
                        for button in component.get('buttons', []):
                            print(f"    Button: {button.get('text')} ({button.get('type')})")
                    
                    print()
            
            print("-" * 70)
            print()
    else:
        print("❌ No templates found")
        print()
        print("To create a template:")
        print("  1. Go to: https://business.facebook.com")
        print("  2. WhatsApp Manager → Message Templates")
        print("  3. Create Template")

except Exception as e:
    print(f"❌ Error: {e}")
    print()
    print("Possible issues:")
    print("  1. Wrong Business Account ID")
    print("  2. Access token doesn't have template permissions")
    print("  3. Not logged into correct WhatsApp account")
