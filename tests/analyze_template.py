"""
Check template details to understand truncation
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import requests
from src.config import settings

def check_template_details(template_name: str):
    """Get detailed info about a specific template"""
    
    url = f"{settings.meta_graph_api_url}/{settings.whatsapp_business_account_id}/message_templates"
    headers = {
        "Authorization": f"Bearer {settings.whatsapp_access_token}",
    }
    
    params = {
        "name": template_name,
        "limit": 1
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        templates = data.get('data', [])
        
        if not templates:
            print(f"❌ Template '{template_name}' not found!")
            return
        
        template = templates[0]
        
        print(f"📋 Template: {template['name']}")
        print(f"   Status: {template['status']}")
        print(f"   Category: {template['category']}")
        print(f"   Language: {template['language']}")
        print()
        
        # Get body component
        components = template.get('components', [])
        for comp in components:
            if comp.get('type') == 'BODY':
                text = comp.get('text', '')
                char_count = len(text)
                line_count = text.count('\n') + 1
                
                print("📝 Body Content:")
                print("-" * 60)
                print(text)
                print("-" * 60)
                print(f"   Characters: {char_count}")
                print(f"   Lines: {line_count}")
                print()
                
                # Analyze truncation risk
                if char_count > 1000:
                    print("⚠️  HIGH RISK: Over 1000 characters")
                elif char_count > 700:
                    print("⚠️  MEDIUM RISK: 700-1000 characters")
                else:
                    print("✅ LOW RISK: Under 700 characters")
                
                if line_count > 15:
                    print("⚠️  Many line breaks may cause truncation")
                
                if template['category'] == 'MARKETING':
                    print("⚠️  MARKETING category more likely to truncate")
                
        print()
        print("💡 Tips to avoid 'Read more':")
        print("   1. Keep message under 700 characters")
        print("   2. Reduce line breaks (use fewer \\n)")
        print("   3. Use UTILITY category if possible")
        print("   4. Make content more concise")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🔍 Analyzing template truncation...\n")
    check_template_details("insights_summary")
