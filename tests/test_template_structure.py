"""
Diagnostic script to test WhatsApp template structure
This will help identify the correct template format
"""
import sys
from pathlib import Path
import requests

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import settings
from src.utils import format_phone_number

def test_template_structure(test_number: str = "27727377590"):
    """Test different template structures to find the right one"""
    
    formatted_phone = format_phone_number(test_number)
    url = f"{settings.meta_graph_api_url}/{settings.whatsapp_phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {settings.whatsapp_access_token}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Just body parameters (current approach)
    print("Test 1: Body only with 7 parameters...")
    payload1 = {
        "messaging_product": "whatsapp",
        "to": formatted_phone,
        "type": "template",
        "template": {
            "name": "weekly_insights",
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": "TestName"},
                        {"type": "text", "text": "150"},
                        {"type": "text", "text": "Property24"},
                        {"type": "text", "text": "5"},
                        {"type": "text", "text": "3"},
                        {"type": "text", "text": "R12.5mil"},
                        {"type": "text", "text": "R200k"}
                    ]
                }
            ]
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload1)
        if response.status_code == 200:
            print("✅ Test 1 PASSED - Body only works!")
            return
        else:
            print(f"❌ Test 1 Failed: {response.status_code}")
            print(f"   Error: {response.json()}")
    except Exception as e:
        print(f"❌ Test 1 Error: {e}")
    
    print("\n" + "="*60 + "\n")
    
    # Test 2: With header parameter
    print("Test 2: With header + body parameters...")
    payload2 = {
        "messaging_product": "whatsapp",
        "to": formatted_phone,
        "type": "template",
        "template": {
            "name": "weekly_insights",
            "language": {"code": "en"},
            "components": [
                {
                    "type": "header",
                    "parameters": [
                        {"type": "text", "text": "TestName"}
                    ]
                },
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": "150"},
                        {"type": "text", "text": "Property24"},
                        {"type": "text", "text": "5"},
                        {"type": "text", "text": "3"},
                        {"type": "text", "text": "R12.5mil"},
                        {"type": "text", "text": "R200k"}
                    ]
                }
            ]
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload2)
        if response.status_code == 200:
            print("✅ Test 2 PASSED - Header + Body works!")
            print("   👉 The 'name' parameter should be in HEADER, not body!")
            return
        else:
            print(f"❌ Test 2 Failed: {response.status_code}")
            print(f"   Error: {response.json()}")
    except Exception as e:
        print(f"❌ Test 2 Error: {e}")
    
    print("\n" + "="*60 + "\n")
    
    # Test 3: Body only with 6 parameters (no name)
    print("Test 3: Body with only 6 parameters (no name)...")
    payload3 = {
        "messaging_product": "whatsapp",
        "to": formatted_phone,
        "type": "template",
        "template": {
            "name": "weekly_insights",
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": "150"},
                        {"type": "text", "text": "Property24"},
                        {"type": "text", "text": "5"},
                        {"type": "text", "text": "3"},
                        {"type": "text", "text": "R12.5mil"},
                        {"type": "text", "text": "R200k"}
                    ]
                }
            ]
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload3)
        if response.status_code == 200:
            print("✅ Test 3 PASSED - 6 parameters only works!")
            print("   👉 The template doesn't use the 'name' parameter!")
            return
        else:
            print(f"❌ Test 3 Failed: {response.status_code}")
            print(f"   Error: {response.json()}")
    except Exception as e:
        print(f"❌ Test 3 Error: {e}")
    
    print("\n" + "="*60 + "\n")
    print("All tests failed. Please check:")
    print("1. Template name in Meta: Is it exactly 'weekly_insights'?")
    print("2. Template status: Is it approved?")
    print("3. Share the template text from Meta Business Manager")

if __name__ == "__main__":
    print("🔍 Testing WhatsApp Template Structure...")
    print("="*60)
    print()
    test_template_structure()
