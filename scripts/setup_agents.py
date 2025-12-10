"""
Setup script to create agents in Firebase.
Run this once to populate the agents collection.

This collection is used during registration to:
1. Verify if a phone number belongs to a known agent
2. Auto-populate agent_id, office, agency details
"""
import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.clients.firebase import FirebaseClient


def create_agents():
    """Create agent records in Firebase."""
    
    firebase = FirebaseClient()
    
    agents = [
        {
            "phone": "27765144639",
            "agent_id": "A001",
            "first_name": "Leon",
            "last_name": "van Onselen",
            "full_name": "Leon van Onselen",
            "email": "leon@betterhome.co.za",
            "office_id": "OFF001",
            "office_name": "Cape Town",
            "agency_id": "AG001",
            "agency_name": "Betterhome",
            "status": "active",
            "created_at": datetime.now().isoformat()
        },
        {
            "phone": "27727377590",
            "agent_id": "A002",
            "first_name": "Melville",
            "last_name": "du Plessis",
            "full_name": "Melville du Plessis",
            "email": "melville@betterhome.co.za",
            "office_id": "OFF001",
            "office_name": "Cape Town",
            "agency_id": "AG001",
            "agency_name": "Betterhome",
            "status": "active",
            "created_at": datetime.now().isoformat()
        },
        {
            "phone": "27832640332",
            "agent_id": "A003",
            "first_name": "Nathan",
            "last_name": "Kettles",
            "full_name": "Nathan Kettles",
            "email": "nathan@betterhome.co.za",
            "office_id": "OFF002",
            "office_name": "Fish Hoek",
            "agency_id": "AG001",
            "agency_name": "Betterhome",
            "status": "active",
            "created_at": datetime.now().isoformat()
        }
    ]
    
    print("Creating agents in Firebase...")
    print("-" * 60)
    
    for agent in agents:
        phone = agent["phone"]
        try:
            firebase.set_document(
                collection="agents",
                doc_id=phone,
                data=agent,
                merge=False
            )
            print(f"✅ Created: {agent['full_name']} ({agent['agent_id']})")
            print(f"   Phone: {phone}")
            print(f"   Agency: {agent['agency_name']}")
            print(f"   Office: {agent['office_name']}")
            print()
        except Exception as e:
            print(f"❌ Failed to create {phone}: {e}")
    
    print("-" * 60)
    print("Done!")
    print()
    print("Agents collection ready. These agents will be auto-linked")
    print("when they register via WhatsApp.")


if __name__ == "__main__":
    create_agents()
