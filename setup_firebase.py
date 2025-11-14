#!/usr/bin/env python3
"""
Firebase Setup Helper
Sets up the required Firestore collections with proper structure
"""
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("Firebase Collection Setup")
print("=" * 70)
print()

# Build Firebase credentials from .env
firebase_creds = {
    "type": "service_account",
    "project_id": os.getenv("ADMIN_PROJECT_ID"),
    "private_key_id": "dummy",  # Not needed for basic operations
    "private_key": os.getenv("ADMIN_PRIVATE_KEY", "").replace('\\n', '\n'),
    "client_email": os.getenv("ADMIN_CLIENT_EMAIL"),
    "client_id": "dummy",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
}

try:
    # Initialize Firebase
    cred = credentials.Certificate(firebase_creds)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    
    print("✅ Connected to Firebase!")
    print(f"   Project: {firebase_creds['project_id']}")
    print()
    
except Exception as e:
    print(f"❌ Firebase connection failed: {e}")
    print()
    print("Check your .env file has:")
    print("  - ADMIN_PROJECT_ID")
    print("  - ADMIN_CLIENT_EMAIL")
    print("  - ADMIN_PRIVATE_KEY")
    exit(1)

# Show what collections we'll create
print("📁 Collections to create:")
print()
print("1. whatsapp_users")
print("   Purpose: Store user information and preferences")
print("   Fields:")
print("     - name: User's name")
print("     - phone: WhatsApp number (E.164 format)")
print("     - frequency: weekly/daily/monthly")
print("     - active: true/false")
print("     - created_at: timestamp")
print("     - last_sent: timestamp (when last message was sent)")
print()
print("2. insights")
print("   Purpose: Store generated insights for each user")
print("   Fields:")
print("     - user_id: Reference to user document")
print("     - generated_at: timestamp")
print("     - data: object with insight metrics")
print("       - sales_change: e.g. '+5%'")
print("       - active_listings: number")
print("       - avg_price: e.g. 'R450K'")
print("       - sales_velocity: e.g. '12 days'")
print()
print("=" * 70)
print()

proceed = input("Create example documents? (y/n): ")

if proceed.lower() != 'y':
    print("Cancelled. Collections will be auto-created when you add first user.")
    exit(0)

print()
print("Creating example documents...")
print()

# Create example user
example_user = {
    "name": "Example User",
    "phone": "27821234567",
    "frequency": "weekly",
    "active": False,  # Inactive so it doesn't actually send
    "created_at": datetime.now(),
    "last_sent": None
}

user_ref = db.collection('whatsapp_users').add(example_user)
user_id = user_ref[1].id

print(f"✅ Created example user (ID: {user_id})")

# Create example insights
example_insights = {
    "user_id": user_id,
    "generated_at": datetime.now(),
    "data": {
        "sales_change": "+5%",
        "active_listings": 45,
        "avg_price": "R450K",
        "sales_velocity": "12 days"
    }
}

db.collection('insights').document(user_id).set(example_insights)
print(f"✅ Created example insights for user")

print()
print("=" * 70)
print("🎉 Firebase Setup Complete!")
print("=" * 70)
print()
print("Collections created:")
print(f"  📁 whatsapp_users (1 example document)")
print(f"  📁 insights (1 example document)")
print()
print("View in Firebase Console:")
print(f"  https://console.firebase.google.com/project/{firebase_creds['project_id']}/firestore")
print()
print("Next steps:")
print("  1. Delete example user if needed (it's inactive)")
print("  2. Run: python add_test_user.py")
print("  3. Add your real WhatsApp number")
print()
