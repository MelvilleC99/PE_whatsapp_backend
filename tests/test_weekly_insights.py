"""
Test script for weekly_insights WhatsApp template
Run this to send yourself a test message
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.weekly_insights_template import send_weekly_insights_template

# 📝 EDIT THESE VALUES
TEST_PHONE = "27727377590"  # Your phone number (with country code)
TEST_NAME = "Melville"

# Sample metrics - customize these
TEST_DATA = {
    "leads": "150",
    "portal": "Property24 - 55%",
    "offer": "5",
    "sale": "3",
    "revenue": "R12.5mil",
    "commission": "R200k"
}

if __name__ == "__main__":
    print("🧪 Testing weekly_insights template...")
    print(f"📱 Sending to: {TEST_PHONE}")
    print(f"📊 Data: {TEST_DATA}")
    print()
    
    try:
        result = send_weekly_insights_template(
            to=TEST_PHONE,
            name=TEST_NAME,
            **TEST_DATA
        )
        
        msg_id = result.get('messages', [{}])[0].get('id', 'N/A')
        print(f"✅ Success! Message ID: {msg_id}")
        print(f"📱 Check your WhatsApp!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Is your template approved in Meta Business Manager?")
        print("  2. Check template name: should be 'weekly_insights'")
        print("  3. Verify you have 7 parameters (name + 6 metrics)")
        print("  4. Check your .env file has correct tokens")
