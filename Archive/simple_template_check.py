#!/usr/bin/env python3
"""
Simple template status checker - no config needed
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("Checking weekly_insights Template Status")
print("=" * 70)
print()

# Get credentials directly from .env
access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
business_account_id = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID")

if not access_token or not business_account_id:
    print("❌ Missing credentials in .env file")
    print()
    print("Make sure you have:")
    print("  WHATSAPP_ACCESS_TOKEN")
    print("  WHATSAPP_BUSINESS_ACCOUNT_ID")
    exit(1)

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# Check template status
url = f"https://graph.facebook.com/v18.0/{business_account_id}/message_templates"
params = {"name": "weekly_insights"}

try:
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    templates = response.json().get('data', [])
    
    if not templates:
        print("❌ Template 'weekly_insights' not found")
        print()
        print("Make sure you created it in Meta Business Manager")
        exit(1)
    
    template = templates[0]
    status = template.get('status')
    
    print(f"✅ Template found!")
    print(f"   Name: {template.get('name')}")
    print(f"   Status: {status}")
    print(f"   Language: {template.get('language')}")
    print(f"   Category: {template.get('category')}")
    print()
    
    if status == 'APPROVED':
        print("🎉 Template is APPROVED!")
        print()
        print("Ready to use! Run:")
        print("  python test_weekly_insights.py")
        
    elif status == 'PENDING':
        print("⏳ Template is PENDING approval")
        print()
        print("Meta's template approval can take:")
        print("  • 15 minutes (fast)")
        print("  • 30-60 minutes (normal)")
        print("  • Up to 24 hours (sometimes)")
        print()
        print("Factors that slow approval:")
        print("  • Complex templates with many variables")
        print("  • Marketing category (vs Utility)")
        print("  • First template from new account")
        print("  • Weekend/holiday submissions")
        print()
        print("Check again later:")
        print("  python simple_template_check.py")
        
    elif status == 'REJECTED':
        print("❌ Template was REJECTED")
        print()
        reason = template.get('rejected_reason', 'No reason provided')
        print(f"Reason: {reason}")
        print()
        print("Common rejection reasons:")
        print("  • Contains promotional content")
        print("  • Variables not clearly explained")
        print("  • Grammar/spelling issues")
        print("  • Violates Meta policies")
        print()
        print("Edit and resubmit in Meta Business Manager")
        
    elif status == 'IN_APPEAL':
        print("🔄 Template is IN_APPEAL")
        print("   You appealed a rejection, waiting for review")
        
    elif status == 'PAUSED':
        print("⏸️  Template is PAUSED")
        print("   You can unpause it in Meta Business Manager")
        
    else:
        print(f"⚠️  Unknown status: {status}")
        
except requests.exceptions.HTTPError as e:
    print(f"❌ API Error: {e}")
    print(f"Response: {e.response.text}")
    
except Exception as e:
    print(f"❌ Error: {e}")

print()
print("=" * 70)
print()

# Also check insights_dashboard status
print("Bonus: Checking insights_dashboard status too...")
print()

params2 = {"name": "insights_dashboard"}

try:
    response2 = requests.get(url, headers=headers, params=params2)
    
    if response2.status_code == 200:
        templates2 = response2.json().get('data', [])
        if templates2:
            t = templates2[0]
            print(f"insights_dashboard: {t.get('status')}")
            
            if t.get('status') == 'APPROVED':
                print("  (Has parameter issues - can't use)")
        else:
            print("insights_dashboard: Not found")
except:
    pass

print()
