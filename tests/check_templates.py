"""
Fetch and display all your WhatsApp templates from Meta
This will show the exact template names and their status
"""
import sys
from pathlib import Path
import requests

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import settings

def list_templates():
    """Fetch all templates from Meta"""
    
    url = f"{settings.meta_graph_api_url}/{settings.whatsapp_business_account_id}/message_templates"
    headers = {
        "Authorization": f"Bearer {settings.whatsapp_access_token}",
    }
    
    params = {
        "limit": 100
    }
    
    print("🔍 Fetching your WhatsApp templates from Meta...\n")
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        templates = data.get('data', [])
        
        if not templates:
            print("❌ No templates found!")
            return
        
        print(f"Found {len(templates)} template(s):\n")
        print("="*80)
        
        for i, template in enumerate(templates, 1):
            name = template.get('name', 'N/A')
            status = template.get('status', 'N/A')
            language = template.get('language', 'N/A')
            category = template.get('category', 'N/A')
            
            print(f"\n{i}. Template Name: {name}")
            print(f"   Status: {status}")
            print(f"   Language: {language}")
            print(f"   Category: {category}")
            
            # Show components
            components = template.get('components', [])
            if components:
                print(f"   Components:")
                for comp in components:
                    comp_type = comp.get('type', 'unknown')
                    print(f"     - {comp_type}")
                    
                    # Show variables in body
                    if comp_type == 'BODY':
                        text = comp.get('text', '')
                        # Count variables
                        import re
                        variables = re.findall(r'\{\{(\d+)\}\}', text)
                        print(f"       Variables: {len(variables)}")
                        print(f"       Text preview: {text[:100]}...")
            
            print("-"*80)
        
        # Check specifically for weekly_insights
        print("\n" + "="*80)
        weekly = next((t for t in templates if t['name'] == 'weekly_insights'), None)
        if weekly:
            print("✅ Found 'weekly_insights' template!")
            print(f"   Status: {weekly['status']}")
            if weekly['status'] != 'APPROVED':
                print(f"   ⚠️  Template is {weekly['status']}, not APPROVED!")
        else:
            print("❌ 'weekly_insights' template NOT FOUND!")
            print("   Available names:", [t['name'] for t in templates])
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ API Error: {e}")
        print(f"   Response: {e.response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    list_templates()
