"""
Command handler for processing WhatsApp messages and commands
"""
from typing import Dict, Optional
from loguru import logger

from src.services.user_service import UserService
from src.services.insights_service import InsightsService
from src.integrations.whatsapp_client import WhatsAppClient
from src.templates.insights_template import format_insight_message


class CommandHandler:
    """Handle incoming WhatsApp commands and messages"""
    
    def __init__(self):
        """Initialize command handler with required services"""
        self.user_service = UserService()
        self.insights_service = InsightsService()
        self.whatsapp = WhatsAppClient()
    
    def handle_message(self, message: dict, value: dict):
        """
        Process a single incoming message
        
        Args:
            message: Message object from webhook
            value: Value object containing metadata
        """
        try:
            # Extract details
            from_number = message.get('from')
            message_type = message.get('type')
            
            # Only handle text messages for now
            if message_type != 'text':
                logger.info(f"Ignoring non-text message type: {message_type}")
                return
            
            text = message.get('text', {}).get('body', '').strip().lower()
            
            logger.info(f"Message from {from_number}: {text}")
            
            # Look up user
            user = self.user_service.get_user_by_phone(from_number)
            
            if not user:
                self._handle_unregistered_user(from_number, text)
                return
            
            # User exists - handle their request
            self._handle_registered_user(user, text, from_number)
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    def _handle_registered_user(self, user: Dict, text: str, phone: str):
        """
        Handle message from registered user
        
        Args:
            user: User document from database
            text: Message text (lowercase)
            phone: User's phone number
        """
        # ONLY respond to insights requests - ignore everything else
        if 'insight' in text or 'report' in text or 'stats' in text:
            self._send_user_insights(user, phone)
        else:
            # Log but don't respond to any other messages
            logger.info(f"Ignoring non-insights message from {user['name']}: {text}")
    
    def _send_user_insights(self, user: Dict, phone: str):
        """
        Send insights to registered user
        
        Args:
            user: User document
            phone: User's phone number
        """
        try:
            # Get saved insights
            insights_doc = self.insights_service.get_user_insights(user['id'])
            
            if not insights_doc or not insights_doc.get('data'):
                self.whatsapp.send_text_message(
                    phone,
                    f"Hi {user['name']}! 👋\n\nNo insights available yet. We'll send your first report soon!"
                )
                return
            
            # Format and send insights
            insights = insights_doc['data']
            message = format_insight_message(insights, user['name'])
            
            self.whatsapp.send_text_message(phone, message)
            logger.success(f"Sent insights to {user['name']} ({phone})")
            
        except Exception as e:
            logger.error(f"Failed to send insights: {e}")
            self.whatsapp.send_text_message(
                phone,
                "Sorry, there was an error retrieving your insights. Please try again later."
            )
    
    def _handle_unregistered_user(self, phone: str, text: str):
        """
        Handle message from unregistered user
        
        Args:
            phone: User's phone number
            text: Message text (lowercase)
        """
        # Ignore all messages from unregistered users
        logger.info(f"Ignoring message from unregistered user {phone}: {text}")
    
    def send_help_message(self, phone: str, name: Optional[str] = None):
        """
        Send help/commands list
        
        Args:
            phone: User's phone number
            name: Optional user name for personalization
        """
        greeting = f"Hi {name}!" if name else "Hi there!"
        
        message = f"""
{greeting} 👋

*Available Commands:*

📊 *insights* - Get your latest insights
❓ *help* - Show this message
🛑 *stop* - Unsubscribe from insights

Just send me a message anytime and I'll send your latest insights!
        """.strip()
        
        self.whatsapp.send_text_message(phone, message)
    
    def handle_unsubscribe(self, user: Dict, phone: str):
        """
        Handle unsubscribe request
        
        Args:
            user: User document
            phone: User's phone number
        """
        try:
            # Deactivate user
            self.user_service.deactivate_user(user['id'])
            
            self.whatsapp.send_text_message(
                phone,
                f"Sorry to see you go, {user['name']}! 👋\n\nYou've been unsubscribed from weekly insights.\n\nReply *SIGNUP* anytime to re-subscribe."
            )
            
            logger.info(f"Unsubscribed user: {user['name']} ({phone})")
            
        except Exception as e:
            logger.error(f"Failed to unsubscribe user: {e}")
