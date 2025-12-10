#!/usr/bin/env python3
"""
Last attempt: Maybe template needs to be recreated without named params
"""
import sys
sys.path.insert(0, '/Users/melville/Documents/PE_whatsapp_backend')

import requests
import json
from src.config import settings

print("=" * 70)
print("DIAGNOSIS: Template Configuration Issue")
print("=" * 70)
print()

print("The issue:")
print("  - Template has 'body_text_named_params' (named parameters)")
print("  - But Meta API says 'Parameter name is missing or empty'")
print("  - Adding 'name' field gives 'Unexpected key' error")
print()
print("This is a Meta API inconsistency!")
print()
print("SOLUTION:")
print("  The template was created with named parameters {{name}}")
print("  But Meta's sending API expects positional parameters {{1}}")
print()
print("You need to recreate the template with {{1}} instead of {{name}}")
print()
print("=" * 70)
print()

print("Steps to fix:")
print()
print("1. Go to: https://business.facebook.com")
print("2. WhatsApp Manager → Message Templates")
print("3. Delete 'insights_dashboard' template")
print("4. Create NEW template:")
print()
print("   Name: insights_dashboard")
print("   Header: Insights summary")
print("   Body: Hi {{1}} View your weekly insights summary")
print("         ^^^")
print("         Use {{1}} not {{name}}")
print()
print("   Button: Visit website → https://propengine-leads.vercel.app/sales")
print()
print("5. Submit for approval")
print("6. Wait ~15 minutes")
print("7. Test again")
print()
print("=" * 70)
print()

print("OR use your 'weekly_insights' template once it's approved!")
print()
print("To check status of weekly_insights:")
print()

headers = {
    "Authorization": f"Bearer {settings.whatsapp_access_token}",
    "Content-Type": "application/json"
}

template_url = f"{settings.meta_graph_api_url}/{settings.whatsapp_business_account_id}/message_templates"
params = {"name": "weekly_insights"}

response = requests.get(template_url, headers=headers, params=params)

if response.status_code == 200:
    templates = response.json().get('data', [])
    if templates:
        template = templates[0]
        status = template.get('status')
        print(f"weekly_insights status: {status}")
        
        if status == 'APPROVED':
            print()
            print("✅ weekly_insights is APPROVED! You can use it now!")
            print()
            print("Run: python test_weekly_insights.py")
        elif status == 'PENDING':
            print()
            print("⏳ Still pending approval...")
            print("   Usually takes 15-30 minutes")
        else:
            print(f"   Status: {status}")
            if template.get('rejected_reason'):
                print(f"   Reason: {template.get('rejected_reason')}")
    else:
        print("weekly_insights template not found")
else:
    print(f"Error checking template: {response.json()}")

print()
print("=" * 70)
print("Bottom line:")
print("=" * 70)
print()
print("The 'insights_dashboard' template has a configuration issue.")
print("Named parameters ({{name}}) don't work with Meta's sending API.")
print()
print("Best solution:")
print("  Wait for 'weekly_insights' to be approved (better template anyway!)")
print()
