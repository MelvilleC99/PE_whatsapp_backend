"""
Setup script to create users in Firebase with permissions.
Run this once to populate the whatsapp_users collection.
"""
import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.clients.firebase import FirebaseClient


def create_users():
    """Create users with full permissions."""
    
    firebase = FirebaseClient()
    
    users = [
        {
            "phone": "27765144639",
            "name": "Leon van Onselen",
            "agent_id": None,
            "active": True,
            "created_at": datetime.now().isoformat(),
            "permissions": {
                "insights": {
                    "enabled": True,
                    "frequency": "weekly",
                    "last_sent": None
                },
                "listing_intake": {
                    "enabled": True,
                    "requires_confirmation": True,
                    "max_drafts": 10
                },
                "listing_query": {
                    "enabled": True
                }
            }
        },
        {
            "phone": "27727377590",
            "name": "Melville du Plessis",
            "agent_id": None,
            "active": True,
            "created_at": datetime.now().isoformat(),
            "permissions": {
                "insights": {
                    "enabled": True,
                    "frequency": "weekly",
                    "last_sent": None
                },
                "listing_intake": {
                    "enabled": True,
                    "requires_confirmation": True,
                    "max_drafts": 10
                },
                "listing_query": {
                    "enabled": True
                }
            }
        },
        {
            "phone": "27832640332",
            "name": "Nathan Kettles",
            "agent_id": None,
            "active": True,
            "created_at": datetime.now().isoformat(),
            "permissions": {
                "insights": {
                    "enabled": True,
                    "frequency": "weekly",
                    "last_sent": None
                },
                "listing_intake": {
                    "enabled": True,
                    "requires_confirmation": True,
                    "max_drafts": 10
                },
                "listing_query": {
                    "enabled": True
                }
            }
        }
    ]
    
    print("Creating users in Firebase...")
    print("-" * 50)
    
    for user in users:
        phone = user["phone"]
        try:
            firebase.set_document(
                collection="whatsapp_users",
                doc_id=phone,
                data=user,
                merge=False
            )
            print(f"✅ Created: {user['name']} ({phone})")
            print(f"   Permissions: insights=True, listing_intake=True, listing_query=True")
        except Exception as e:
            print(f"❌ Failed to create {phone}: {e}")
    
    print("-" * 50)
    print("Done!")


if __name__ == "__main__":
    create_users()
