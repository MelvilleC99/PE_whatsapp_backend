#!/usr/bin/env python3
"""
Helper script to add a test user to Firebase
Run: python add_test_user.py
"""
from src.firebase_manager import FirebaseManager

print("=" * 60)
print("Add Test User to Firebase")
print("=" * 60)
print()

# Get user input
name = input("Enter user name: ")
phone = input("Enter WhatsApp phone (e.g., 27821234567 or 0821234567): ")
frequency = input("Insight frequency (weekly/daily/monthly) [weekly]: ").strip() or "weekly"

print()
print(f"Adding user: {name}")
print(f"Phone: {phone}")
print(f"Frequency: {frequency}")
print()

confirm = input("Proceed? (y/n): ")

if confirm.lower() == 'y':
    try:
        fm = FirebaseManager()
        user_id = fm.add_user(phone, name, frequency)
        print()
        print(f"✅ User added successfully!")
        print(f"   User ID: {user_id}")
        print()
        print("Next step:")
        print("  python -m src.scheduler --once --mock")
    except Exception as e:
        print(f"❌ Failed to add user: {e}")
else:
    print("Cancelled")
