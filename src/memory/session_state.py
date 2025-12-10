"""
Session State Manager - Manage workflow state for users

Tracks where users are in multi-step workflows (e.g., awaiting confirmation).
Stores state in Firebase with local caching.
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger

from src.clients.firebase import FirebaseClient


class SessionStateManager:
    """
    Manage workflow session state.
    
    Stores temporary state when users are mid-workflow,
    e.g., waiting for confirmation or registration steps.
    
    Usage:
        session = SessionStateManager()
        
        # Set state
        session.set_state("27821234567", {
            "workflow": "registration",
            "step": "awaiting_name",
            "data": {}
        })
        
        # Get state
        state = session.get_state("27821234567")
        
        # Clear state
        session.clear_state("27821234567")
    """
    
    # State expires after this many minutes of inactivity
    STATE_EXPIRY_MINUTES = 30
    
    def __init__(self):
        self.firebase = FirebaseClient()
        self._local_cache: Dict[str, Dict] = {}
    
    def set_state(self, phone: str, state: Dict[str, Any]) -> bool:
        """
        Set workflow state for a user.
        
        Args:
            phone: User's phone number
            state: State data to store (should include 'workflow' and 'step')
            
        Returns:
            True if successful
        """
        now = datetime.now()
        
        state_data = {
            **state,
            'phone': phone,
            'updated_at': now.isoformat(),
            'expires_at': (now + timedelta(minutes=self.STATE_EXPIRY_MINUTES)).isoformat(),
        }
        
        # Set started_at only if not already present
        if 'started_at' not in state_data:
            state_data['started_at'] = now.isoformat()
        
        # Update local cache
        self._local_cache[phone] = state_data
        
        # Persist to Firebase
        try:
            success = self.firebase.set_document(
                collection='session_state',
                doc_id=phone,
                data=state_data,
                merge=False
            )
            
            if success:
                logger.debug(f"Session state saved for {phone}: {state.get('workflow')}/{state.get('step')}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to persist session state for {phone}: {e}")
            return False
    
    def get_state(self, phone: str) -> Optional[Dict[str, Any]]:
        """
        Get workflow state for a user.
        
        Args:
            phone: User's phone number
            
        Returns:
            State data or None if not found/expired
        """
        # Check local cache first
        if phone in self._local_cache:
            state = self._local_cache[phone]
            if self._is_valid(state):
                return state
            else:
                # Expired - clean up
                self.clear_state(phone)
                return None
        
        # Try loading from Firebase
        try:
            state = self.firebase.get_document('session_state', phone)
            
            if state and self._is_valid(state):
                self._local_cache[phone] = state
                return state
            elif state:
                # Expired - clean up
                self.clear_state(phone)
                
        except Exception as e:
            logger.error(f"Failed to load session state for {phone}: {e}")
        
        return None
    
    def clear_state(self, phone: str) -> bool:
        """
        Clear workflow state for a user.
        
        Args:
            phone: User's phone number
            
        Returns:
            True if successful
        """
        # Clear local cache
        if phone in self._local_cache:
            del self._local_cache[phone]
        
        # Clear from Firebase
        try:
            success = self.firebase.delete_document('session_state', phone)
            logger.debug(f"Session state cleared for {phone}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to clear session state for {phone}: {e}")
            return False
    
    def update_step(self, phone: str, step: str, data: Dict = None) -> bool:
        """
        Update just the step and optionally data for existing state.
        
        Args:
            phone: User's phone number
            step: New step name
            data: Additional data to merge
            
        Returns:
            True if successful
        """
        current = self.get_state(phone)
        
        if not current:
            logger.warning(f"Cannot update step - no state for {phone}")
            return False
        
        # Update step
        current['step'] = step
        
        # Merge data if provided
        if data:
            current_data = current.get('data', {})
            current_data.update(data)
            current['data'] = current_data
        
        return self.set_state(phone, current)
    
    def get_workflow(self, phone: str) -> Optional[str]:
        """
        Get the current workflow name for a user.
        
        Args:
            phone: User's phone number
            
        Returns:
            Workflow name or None
        """
        state = self.get_state(phone)
        return state.get('workflow') if state else None
    
    def get_step(self, phone: str) -> Optional[str]:
        """
        Get the current step for a user.
        
        Args:
            phone: User's phone number
            
        Returns:
            Step name or None
        """
        state = self.get_state(phone)
        return state.get('step') if state else None
    
    def _is_valid(self, state: Dict) -> bool:
        """Check if state is still valid (not expired)."""
        expires_at = state.get('expires_at')
        
        if not expires_at:
            return True
        
        try:
            expiry = datetime.fromisoformat(expires_at)
            return datetime.now() < expiry
        except:
            return True


# Backwards compatibility alias
SessionState = SessionStateManager
