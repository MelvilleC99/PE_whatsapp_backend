"""
Insights Workflow - Handle insights requests

This workflow:
1. Receives insights request from user
2. Retrieves user's stored insights from Firebase
3. Formats and sends insights message
"""
from typing import Dict, Any, Optional
from loguru import logger

from src.workflows.registry import BaseWorkflow
from src.clients.whatsapp import WhatsAppClient
from src.clients.firebase import FirebaseClient
from .templates import format_insight_message


class InsightsWorkflow(BaseWorkflow):
    """Workflow for handling insights requests."""
    
    name = "insights"
    description = "Retrieve and send user insights"
    
    def __init__(self):
        self.whatsapp = WhatsAppClient()
        self.firebase = FirebaseClient()
    
    def execute(
        self, 
        content: str,
        user: Dict,
        phone: str,
        message: dict,
        context: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute the insights workflow.
        
        Args:
            content: Message content
            user: User information
            phone: User's phone number
            message: Original message object
            context: Conversation context
            
        Returns:
            Workflow result
        """
        logger.info(f"Executing insights workflow for {user.get('name', phone)}")
        
        try:
            # Get user's insights from Firebase
            insights_doc = self._get_insights(user['id'])
            
            if not insights_doc or not insights_doc.get('data'):
                self._send_no_insights_message(phone, user.get('name', 'there'))
                return {
                    'status': 'success',
                    'action': 'no_insights_available'
                }
            
            # Format and send insights
            insights_data = insights_doc['data']
            message_text = format_insight_message(insights_data, user.get('name', 'there'))
            
            self.whatsapp.send_text_message(phone, message_text)
            
            logger.success(f"Sent insights to {user.get('name')} ({phone})")
            
            return {
                'status': 'success',
                'action': 'insights_sent'
            }
            
        except Exception as e:
            logger.error(f"Insights workflow error: {e}")
            self._send_error_message(phone)
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _get_insights(self, user_id: str) -> Optional[Dict]:
        """Retrieve insights from Firebase."""
        try:
            collection = self.firebase.get_collection('insights')
            doc = collection.document(user_id).get()
            
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            logger.error(f"Failed to get insights: {e}")
            return None
    
    def _send_no_insights_message(self, phone: str, name: str) -> None:
        """Send message when no insights available."""
        message = f"Hi {name}! 👋\n\nNo insights available yet. We'll send your first report soon!"
        self.whatsapp.send_text_message(phone, message)
    
    def _send_error_message(self, phone: str) -> None:
        """Send error message."""
        self.whatsapp.send_text_message(
            phone,
            "Sorry, there was an error retrieving your insights. Please try again later."
        )
