"""
User Registration Tool - Create and manage users in Firebase

Handles:
- Creating new users with permissions
- Linking agent info (agency, office)
- Checking if user exists
- Updating user permissions
"""
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger

from .registry import BaseTool, ToolParameter


class UserRegistrationTool(BaseTool):
    """Tool for registering new users in Firebase."""
    
    name = "user_registration"
    
    description = """Create a new user in Firebase with specified permissions.
    Use this tool when completing the registration workflow."""
    
    parameters = [
        ToolParameter(
            name="phone",
            type="string",
            description="User's phone number (will be used as document ID)",
            required=True
        ),
        ToolParameter(
            name="name",
            type="string",
            description="User's full name",
            required=True
        ),
        ToolParameter(
            name="permissions",
            type="object",
            description="Permissions object with insights, listing_intake, listing_query",
            required=True
        ),
        ToolParameter(
            name="agent_id",
            type="string",
            description="Agent ID from agents collection",
            required=False
        ),
        ToolParameter(
            name="agency_id",
            type="string",
            description="Agency ID",
            required=False
        ),
        ToolParameter(
            name="agency_name",
            type="string",
            description="Agency name",
            required=False
        ),
        ToolParameter(
            name="office_id",
            type="string",
            description="Office ID",
            required=False
        ),
        ToolParameter(
            name="office_name",
            type="string",
            description="Office name",
            required=False
        ),
    ]
    
    examples = [
        {"when": "User completes registration and selects their services"},
    ]
    
    output_description = """Returns dict with:
    - status: 'success', 'exists', or 'error'
    - user_id: Phone number (document ID)
    - message: Human-readable result"""

    def __init__(self):
        """Initialize with Firebase client."""
        from src.clients.firebase import FirebaseClient
        self.firebase = FirebaseClient()
    
    def execute(
        self,
        phone: str,
        name: str,
        permissions: Dict[str, Any],
        first_name: str = None,
        agent_id: str = None,
        agency_id: str = None,
        agency_name: str = None,
        office_id: str = None,
        office_name: str = None,
        email: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new user in Firebase.
        
        Args:
            phone: User's phone number
            name: User's full name
            permissions: Permissions configuration
            first_name: User's first name
            agent_id: Optional agent ID
            agency_id: Optional agency ID
            agency_name: Optional agency name
            office_id: Optional office ID
            office_name: Optional office name
            email: Optional email
            
        Returns:
            Result dict
        """
        logger.info(f"Registering new user: {name} ({phone})")
        
        try:
            # Check if user already exists
            existing = self.firebase.get_document("whatsapp_users", phone)
            if existing:
                logger.warning(f"User already exists: {phone}")
                return {
                    'status': 'exists',
                    'user_id': phone,
                    'message': f"User {name} is already registered",
                    'user': existing
                }
            
            # Build user document
            now = datetime.now().isoformat()
            
            user_doc = {
                'phone': phone,
                'name': name,
                'first_name': first_name or name.split()[0],
                'active': True,
                'status': 'active',
                'created_at': now,
                'registered_at': now,
                'permissions': permissions
            }
            
            # Add agent info if provided
            if agent_id:
                user_doc['agent_id'] = agent_id
            if agency_id:
                user_doc['agency_id'] = agency_id
            if agency_name:
                user_doc['agency_name'] = agency_name
            if office_id:
                user_doc['office_id'] = office_id
            if office_name:
                user_doc['office_name'] = office_name
            if email:
                user_doc['email'] = email
            
            # Write to Firebase
            success = self.firebase.set_document(
                collection="whatsapp_users",
                doc_id=phone,
                data=user_doc,
                merge=False
            )
            
            if success:
                logger.success(f"User registered: {name} ({phone})")
                if agent_id:
                    logger.info(f"  Agent ID: {agent_id}, Agency: {agency_name}, Office: {office_name}")
                
                return {
                    'status': 'success',
                    'user_id': phone,
                    'message': f"Successfully registered {name}",
                    'user': user_doc
                }
            else:
                return {
                    'status': 'error',
                    'user_id': phone,
                    'message': "Failed to save user to database"
                }
                
        except Exception as e:
            logger.error(f"Registration failed: {e}")
            return {
                'status': 'error',
                'user_id': phone,
                'message': str(e)
            }
    
    def user_exists(self, phone: str) -> bool:
        """Check if a user exists."""
        user = self.firebase.get_document("whatsapp_users", phone)
        return user is not None
    
    def get_user(self, phone: str) -> Optional[Dict[str, Any]]:
        """Get user by phone number."""
        return self.firebase.get_document("whatsapp_users", phone)
    
    def update_permissions(
        self,
        phone: str,
        permissions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update user permissions."""
        try:
            success = self.firebase.set_document(
                collection="whatsapp_users",
                doc_id=phone,
                data={
                    'permissions': permissions,
                    'updated_at': datetime.now().isoformat()
                },
                merge=True
            )
            
            if success:
                return {'status': 'success', 'message': 'Permissions updated'}
            else:
                return {'status': 'error', 'message': 'Failed to update'}
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def deactivate_user(self, phone: str) -> Dict[str, Any]:
        """Deactivate a user."""
        try:
            success = self.firebase.set_document(
                collection="whatsapp_users",
                doc_id=phone,
                data={
                    'active': False,
                    'status': 'inactive',
                    'deactivated_at': datetime.now().isoformat()
                },
                merge=True
            )
            
            if success:
                return {'status': 'success', 'message': 'User deactivated'}
            else:
                return {'status': 'error', 'message': 'Failed to deactivate'}
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
