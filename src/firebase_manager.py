"""
Firebase Manager for user and insights data
"""
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from typing import List, Dict, Optional
from loguru import logger
from datetime import datetime

from src.config import settings


class FirebaseManager:
    """Manage Firebase operations for WhatsApp users and insights"""
    
    def __init__(self):
        """Initialize Firebase connection"""
        try:
            # Check if already initialized
            firebase_admin.get_app()
            logger.info("Firebase already initialized")
        except ValueError:
            # Initialize Firebase
            cred = credentials.Certificate(settings.firebase_credentials_dict)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase initialized successfully")
        
        self.db = firestore.client()
        self.users_collection = self.db.collection('whatsapp_users')
        self.insights_collection = self.db.collection('insights')
    
    # USER MANAGEMENT
    
    def add_user(self, phone: str, name: str, frequency: str = "weekly", 
                 active: bool = True) -> str:
        """
        Add a new user to Firebase
        
        Args:
            phone: WhatsApp phone number (E.164 format)
            name: User's name
            frequency: Insight frequency (weekly, daily, monthly)
            active: Whether user is active
            
        Returns:
            User document ID
        """
        from src.utils import format_phone_number, validate_whatsapp_number
        
        formatted_phone = format_phone_number(phone)
        
        if not validate_whatsapp_number(formatted_phone):
            raise ValueError(f"Invalid phone number: {phone}")
        
        user_data = {
            "name": name,
            "phone": formatted_phone,
            "frequency": frequency,
            "active": active,
            "created_at": datetime.now(),
            "last_sent": None
        }
        
        doc_ref = self.users_collection.add(user_data)
        user_id = doc_ref[1].id
        
        logger.info(f"Added user {name} ({formatted_phone}) with ID: {user_id}")
        return user_id

    def get_all_active_users(self) -> List[Dict]:
        """
        Get all active users
        
        Returns:
            List of user dictionaries with IDs
        """
        users = []
        docs = self.users_collection.where(filter=FieldFilter('active', '==', True)).stream()
        
        for doc in docs:
            user_data = doc.to_dict()
            user_data['id'] = doc.id
            users.append(user_data)
        
        logger.info(f"Retrieved {len(users)} active users")
        return users
    
    def get_user_by_phone(self, phone: str) -> Optional[Dict]:
        """
        Get user by phone number
        
        Args:
            phone: Phone number to search for
            
        Returns:
            User dictionary with ID, or None if not found
        """
        from src.utils import format_phone_number
        
        formatted_phone = format_phone_number(phone)
        docs = self.users_collection.where(filter=FieldFilter('phone', '==', formatted_phone)).limit(1).stream()
        
        for doc in docs:
            user_data = doc.to_dict()
            user_data['id'] = doc.id
            return user_data
        
        return None
    
    def update_user_last_sent(self, user_id: str):
        """
        Update the last_sent timestamp for a user
        
        Args:
            user_id: Firebase document ID
        """
        self.users_collection.document(user_id).update({
            'last_sent': datetime.now()
        })
        logger.debug(f"Updated last_sent for user {user_id}")
    
    # INSIGHTS MANAGEMENT
    
    def save_insights(self, user_id: str, insights_data: Dict):
        """
        Save insights for a specific user
        
        Args:
            user_id: User's Firebase document ID
            insights_data: Dictionary of insight metrics
        """
        insight_doc = {
            "user_id": user_id,
            "generated_at": datetime.now(),
            "data": insights_data
        }
        
        # Use user_id as document ID to easily overwrite weekly
        self.insights_collection.document(user_id).set(insight_doc)
        logger.info(f"Saved insights for user {user_id}")
    
    def get_insights(self, user_id: str) -> Optional[Dict]:
        """
        Get insights for a specific user
        
        Args:
            user_id: User's Firebase document ID
            
        Returns:
            Insights dictionary or None
        """
        doc = self.insights_collection.document(user_id).get()
        
        if doc.exists:
            return doc.to_dict()
        return None
    
    def delete_user(self, user_id: str):
        """
        Delete a user (soft delete by setting active=False)
        
        Args:
            user_id: User's Firebase document ID
        """
        self.users_collection.document(user_id).update({'active': False})
        logger.info(f"Deactivated user {user_id}")


if __name__ == "__main__":
    # Test Firebase connection
    try:
        fm = FirebaseManager()
        print("✅ Firebase connection successful!")
        
        # Test getting users
        users = fm.get_all_active_users()
        print(f"Found {len(users)} active users")
    except Exception as e:
        print(f"❌ Firebase connection failed: {e}")
