#!/usr/bin/env python3
"""
Setup Melville's user account with sample insights
"""
import sys
sys.path.insert(0, '/Users/melville/Documents/PE_whatsapp_backend')

from src.firebase_manager import FirebaseManager
from datetime import datetime

print("=" * 70)
print("Setting Up Melville's WhatsApp Account")
print("=" * 70)
print()

try:
    # Initialize Firebase
    fm = FirebaseManager()
    
    # Add Melville as user
    print("Adding user: Melville du Plessis")
    user_id = fm.add_user(
        phone="+27727377590",
        name="Melville du Plessis",
        frequency="weekly",
        active=True
    )
    
    print(f"✅ User created with ID: {user_id}")
    print()
    
    # Create sample insights for Melville
    print("Adding sample insights...")
    sample_insights = {
        "leads": 230,
        "most_active_portal": "P24 - 60% of leads",
        "new_offers": 3,
        "sales": 2,
        "revenue": "R8mil",
        "commission": "R150k"
    }
    
    fm.save_insights(user_id, sample_insights)
    
    print("✅ Insights saved")
    print()
    
    print("=" * 70)
    print("Setup Complete! 🎉")
    print("=" * 70)
    print()
    print("User Details:")
    print(f"  Name: Melville du Plessis")
    print(f"  Phone: +27727377590")
    print(f"  Frequency: Weekly")
    print(f"  Status: Active")
    print()
    print("Sample Insights:")
    print(f"  📈 Leads: 230")
    print(f"  🌐 Most Active Portal: P24 - 60% of leads")
    print(f"  💼 New Offers: 3")
    print(f"  🏠 Sales: 2")
    print(f"  💰 Revenue: R8mil")
    print(f"  🎯 Commission: R150k")
    print()
    print("Next Step:")
    print("  python -m src.scheduler --once")
    print()
    print("This will send you a WhatsApp message with these insights!")
    print()

except Exception as e:
    print(f"❌ Error: {e}")
    print()
    print("Make sure:")
    print("  1. Firebase credentials are correct in .env")
    print("  2. You have internet connection")
    print("  3. Project 'proptech-email-management' exists in Firebase")
