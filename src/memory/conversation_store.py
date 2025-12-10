"""
Conversation Store - Manage conversation history per user

Stores last N messages and provides context for workflows.
Uses Firebase for persistence (survives restarts).
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from loguru import logger

from src.clients.firebase import FirebaseClient


class ConversationStore:
    """
    Store and retrieve conversation history.
    
    Features:
    - Store last N messages per user
    - Track pending workflow states
    - Provide context for LLM calls
    """
    
    MAX_MESSAGES = 5  # Keep last 5 messages per user
    
    def __init__(self):
        self.firebase = FirebaseClient()
        self._local_cache = {}  # In-memory cache for speed
    
    def add_message(self, phone: str, message: dict) -> None:
        """
        Add a message to conversation history.
        
        Args:
            phone: User's phone number
            message: Message object from WhatsApp
        """
        try:
            # Extract relevant info
            msg_data = {
                'type': message.get('type'),
                'timestamp': datetime.now().isoformat(),
                'direction': 'inbound',
            }
            
            # Extract content based on type
            if message.get('type') == 'text':
                msg_data['content'] = message.get('text', {}).get('body', '')
            elif message.get('type') == 'audio':
                msg_data['content'] = '[AUDIO]'
                msg_data['media_id'] = message.get('audio', {}).get('id')
            elif message.get('type') == 'image':
                msg_data['content'] = '[IMAGE]'
                msg_data['media_id'] = message.get('image', {}).get('id')
            
            # Update local cache
            if phone not in self._local_cache:
                self._local_cache[phone] = {'messages': [], 'pending_workflow': None}
            
            self._local_cache[phone]['messages'].append(msg_data)
            
            # Trim to max messages
            if len(self._local_cache[phone]['messages']) > self.MAX_MESSAGES:
                self._local_cache[phone]['messages'] = \
                    self._local_cache[phone]['messages'][-self.MAX_MESSAGES:]
            
            # Persist to Firebase (async in production)
            self._persist_to_firebase(phone)
            
        except Exception as e:
            logger.error(f"Error adding message to store: {e}")
    
    def add_outbound_message(self, phone: str, content: str) -> None:
        """
        Record an outbound message we sent.
        
        Args:
            phone: User's phone number
            content: Message content we sent
        """
        msg_data = {
            'type': 'text',
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'direction': 'outbound',
        }
        
        if phone not in self._local_cache:
            self._local_cache[phone] = {'messages': [], 'pending_workflow': None}
        
        self._local_cache[phone]['messages'].append(msg_data)
        
        # Trim
        if len(self._local_cache[phone]['messages']) > self.MAX_MESSAGES:
            self._local_cache[phone]['messages'] = \
                self._local_cache[phone]['messages'][-self.MAX_MESSAGES:]
    
    def get_messages(self, phone: str) -> List[Dict]:
        """
        Get conversation history for a user.
        
        Args:
            phone: User's phone number
            
        Returns:
            List of message objects
        """
        if phone in self._local_cache:
            return self._local_cache[phone].get('messages', [])
        
        # Try loading from Firebase
        self._load_from_firebase(phone)
        return self._local_cache.get(phone, {}).get('messages', [])
    
    def get_context(self, phone: str) -> Dict[str, Any]:
        """
        Get full conversation context for LLM.
        
        Args:
            phone: User's phone number
            
        Returns:
            Context dict with messages and metadata
        """
        messages = self.get_messages(phone)
        
        return {
            'messages': messages,
            'message_count': len(messages),
            'last_message_time': messages[-1]['timestamp'] if messages else None,
            'pending_workflow': self.get_pending_workflow(phone),
        }
    
    def set_pending_workflow(self, phone: str, workflow_name: str) -> None:
        """Mark that user is mid-workflow."""
        if phone not in self._local_cache:
            self._local_cache[phone] = {'messages': [], 'pending_workflow': None}
        
        self._local_cache[phone]['pending_workflow'] = workflow_name
        self._persist_to_firebase(phone)
    
    def get_pending_workflow(self, phone: str) -> Optional[str]:
        """Get pending workflow name if any."""
        if phone in self._local_cache:
            return self._local_cache[phone].get('pending_workflow')
        return None
    
    def clear_pending_workflow(self, phone: str) -> None:
        """Clear pending workflow state."""
        if phone in self._local_cache:
            self._local_cache[phone]['pending_workflow'] = None
            self._persist_to_firebase(phone)
    
    def clear_history(self, phone: str) -> None:
        """Clear all history for a user."""
        self._local_cache[phone] = {'messages': [], 'pending_workflow': None}
        self._persist_to_firebase(phone)
    
    def _persist_to_firebase(self, phone: str) -> None:
        """Persist conversation data to Firebase."""
        try:
            data = self._local_cache.get(phone, {})
            self.firebase.set_document(
                collection='conversations',
                doc_id=phone,
                data=data
            )
        except Exception as e:
            logger.error(f"Failed to persist to Firebase: {e}")
    
    def _load_from_firebase(self, phone: str) -> None:
        """Load conversation data from Firebase."""
        try:
            data = self.firebase.get_document('conversations', phone)
            if data:
                self._local_cache[phone] = data
        except Exception as e:
            logger.error(f"Failed to load from Firebase: {e}")
