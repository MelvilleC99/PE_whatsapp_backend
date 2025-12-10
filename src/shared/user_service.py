"""
User service for managing WhatsApp users
"""
from typing import List, Dict, Optional
from loguru import logger
from datetime import datetime
from google.cloud.firestore_v1.base_query import FieldFilter

from src.integrations.firebase_client import FirebaseClient
from src.utils.formatters import format_phone_number
from src.utils.validators import validate_whatsapp_number


class UserService:
    """Service for managing WhatsApp users"""
    
    def __init__(self):
        """Initialize user service with Firebase"""
        self.firebase = FirebaseClient()
        self.users_collection = self.firebase.get_collection('whatsapp_users')
    
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
    
    def deactivate_user(self, user_id: str):
        """
        Deactivate a user (soft delete)
        
        Args:
            user_id: User's Firebase document ID
        """
        self.users_collection.document(user_id).update({'active': False})
        logger.info(f"Deactivated user {user_id}")
    
    def reactivate_user(self, user_id: str):
        """
        Reactivate a user
        
        Args:
            user_id: User's Firebase document ID
        """
        self.users_collection.document(user_id).update({'active': True})
        logger.info(f"Reactivated user {user_id}")
