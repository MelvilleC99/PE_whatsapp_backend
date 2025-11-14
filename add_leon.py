#!/usr/bin/env python3
"""
Add Leon van Onselen to Firebase
"""
import sys
sys.path.insert(0, '/Users/melville/Documents/PE_whatsapp_backend')

from src.firebase_manager import FirebaseManager
from datetime import datetime

print("Adding Leon van Onselen to Firebase...")
print()

try:
    fm = FirebaseManager()
    
    # Add Leon
    user_id = fm.add_user(
        phone="+27765144639",
        name="Leon van Onselen",
        frequency="weekly",
        active=True
    )
    
    print(f"✅ User created: {user_id}")
    print()
    
    # Copy same insights as Melville
    insights = {
        "leads": 230,
        "most_active_portal": "P24 - 60% of leads",
        "new_offers": 3,
        "sales": 2,
        "revenue": "R8mil",
        "commission": "R150k"
    }
    
    fm.save_insights(user_id, insights)
    
    print("✅ Insights saved")
    print()
    print("Leon van Onselen is ready!")
    print(f"  Phone: +27765144639")
    print(f"  User ID: {user_id}")
    
except Exception as e:
    print(f"❌ Error: {e}")
