#!/usr/bin/env python3
"""
Send WhatsApp messages using insights already saved in Firebase
No database connection needed - perfect for testing!
"""
import sys
sys.path.insert(0, '/Users/melville/Documents/PE_whatsapp_backend')

from src.firebase_manager import FirebaseManager
from src.whatsapp_sender import WhatsAppSender
from src.utils import format_insight_message, setup_logging
from loguru import logger
import time

setup_logging("INFO")

print("=" * 70)
print("Sending WhatsApp Messages from Firebase")
print("=" * 70)
print()

try:
    # Initialize
    firebase = FirebaseManager()
    whatsapp = WhatsAppSender()
    
    # Get all active users
    users = firebase.get_all_active_users()
    logger.info(f"Found {len(users)} active users")
    
    if len(users) == 0:
        print("❌ No active users found!")
        print()
        print("Run this first:")
        print("  python setup_melville.py")
        exit(1)
    
    success_count = 0
    fail_count = 0
    
    for user in users:
        try:
            print(f"📤 Processing: {user['name']} ({user['phone']})")
            
            # Get saved insights from Firebase
            saved_insights = firebase.get_insights(user['id'])
            
            if not saved_insights or not saved_insights.get('data'):
                logger.warning(f"No insights found for {user['name']}, skipping")
                print(f"   ⚠️  No insights saved in Firebase")
                fail_count += 1
                continue
            
            insights = saved_insights['data']
            
            # Format message
            message = format_insight_message(insights, user['name'])
            
            # Send via WhatsApp
            whatsapp.send_text_message(user['phone'], message)
            
            # Update last_sent
            firebase.update_user_last_sent(user['id'])
            
            success_count += 1
            print(f"   ✅ Sent successfully!")
            print()
            
            # Small delay to avoid rate limiting
            time.sleep(1)
            
        except Exception as e:
            fail_count += 1
            logger.error(f"Failed to send to {user.get('name', 'Unknown')}: {e}")
            print(f"   ❌ Failed: {e}")
            print()
            continue
    
    print("=" * 70)
    print(f"Complete: {success_count} sent, {fail_count} failed")
    print("=" * 70)
    print()
    
    if success_count > 0:
        print("✅ Check your WhatsApp!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
