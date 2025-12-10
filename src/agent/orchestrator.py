"""
Orchestrator - Routes incoming messages to appropriate workflows

This is the entry point for all incoming WhatsApp messages.
It determines intent and routes to the correct workflow.
"""
from typing import Dict, Optional, Tuple
from loguru import logger

from src.clients.whatsapp import WhatsAppClient
from src.clients.firebase import FirebaseClient
from src.memory.conversation_store import ConversationStore
from src.memory.session_state import SessionStateManager
from src.workflows.registry import WorkflowRegistry
from src.tools.transcription import TranscriptionTool


class Orchestrator:
    """
    Main orchestrator that routes messages to workflows.
    
    Responsibilities:
    - Authenticate/identify sender
    - Handle registration for new users
    - Determine message intent (via LLM or keyword matching)
    - Route to appropriate workflow
    - Handle unknown intents gracefully
    """
    
    def __init__(self):
        self.firebase = FirebaseClient()
        self.whatsapp = WhatsAppClient()
        self.conversation_store = ConversationStore()
        self.session_state = SessionStateManager()
        self.workflow_registry = WorkflowRegistry()
        self.transcription_tool = TranscriptionTool()
        
        # Intent keywords for quick matching (before LLM)
        self.intent_keywords = {
            'insights': ['insight', 'insights', 'report', 'stats', 'statistics'],
            'listing_intake': ['new listing', 'create listing', 'add listing', 'list property'],
            'registration': ['register', 'sign up', 'signup', 'start', 'get started'],
        }
    
    def handle_message(self, message: dict, value: dict) -> None:
        """
        Main entry point for processing incoming messages.
        
        Args:
            message: Message object from webhook
            value: Value object containing metadata (includes contacts)
        """
        try:
            from_number = message.get('from')
            message_type = message.get('type')
            
            logger.info(f"Processing message from {from_number}, type: {message_type}")
            
            # Extract profile info from contacts
            profile_name = self._extract_profile_name(value)
            
            # Get user (may be None for unregistered)
            user = self._get_user(from_number)
            
            # Extract content based on message type
            content = self._extract_content(message, from_number, profile_name)
            
            if not content:
                logger.info(f"No extractable content from message type: {message_type}")
                return
            
            # Check if user is in a registration workflow (even if unregistered)
            session = self.session_state.get_state(from_number)
            if session and session.get('workflow') == 'registration':
                logger.info(f"User {from_number} is mid-registration")
                self._route_to_workflow(
                    intent='registration',
                    content=content,
                    user=user,
                    phone=from_number,
                    message=message
                )
                return
            
            # Handle unregistered users
            if not user:
                self._handle_unregistered_user(from_number, content, message)
                return
            
            # Check if user is active
            if not user.get('active', False):
                self._handle_inactive_user(from_number, user)
                return
            
            # Store message in conversation history
            self.conversation_store.add_message(from_number, message)
            
            # Determine intent and route
            intent, confidence = self._determine_intent(content, from_number, user)
            
            logger.info(f"Detected intent: {intent} (confidence: {confidence})")
            
            # Check permissions before routing
            if not self._check_permission(user, intent):
                self._handle_no_permission(from_number, user, intent)
                return
            
            # Route to workflow
            self._route_to_workflow(intent, content, user, from_number, message)
            
        except Exception as e:
            logger.error(f"Error in orchestrator: {e}")
            self._send_error_response(message.get('from'))
    
    def _get_user(self, phone: str) -> Optional[Dict]:
        """Get user from Firebase."""
        try:
            return self.firebase.get_document("whatsapp_users", phone)
        except Exception as e:
            logger.error(f"Error getting user {phone}: {e}")
            return None
    
    def _extract_profile_name(self, value: dict) -> Optional[str]:
        """Extract profile name from WhatsApp contacts."""
        contacts = value.get('contacts', [])
        if contacts:
            return contacts[0].get('profile', {}).get('name')
        return None
    
    def _extract_content(
        self, 
        message: dict, 
        phone: str, 
        profile_name: str
    ) -> Optional[str]:
        """
        Extract text content from message based on type.
        
        For audio messages, transcribes via Whisper.
        """
        message_type = message.get('type')
        
        if message_type == 'text':
            return message.get('text', {}).get('body', '').strip()
        
        elif message_type == 'interactive':
            # Handle button replies
            interactive = message.get('interactive', {})
            if interactive.get('type') == 'button_reply':
                return interactive.get('button_reply', {}).get('id', '')
            elif interactive.get('type') == 'list_reply':
                return interactive.get('list_reply', {}).get('id', '')
            return None
        
        elif message_type == 'audio':
            # Transcribe audio via Whisper
            audio_data = message.get('audio', {})
            audio_id = audio_data.get('id')
            mime_type = audio_data.get('mime_type', 'audio/ogg')
            
            logger.info(f"Transcribing audio: {audio_id}")
            
            result = self.transcription_tool.execute(
                audio_id=audio_id,
                phone=phone,
                profile_name=profile_name,
                message_id=message.get('id'),
                timestamp=message.get('timestamp'),
                mime_type=mime_type
            )
            
            if result['status'] == 'success':
                logger.success(f"Transcription successful: {result['text'][:50]}...")
                return result['text']
            else:
                logger.error(f"Transcription failed: {result.get('error')}")
                logger.error(f"Full result: {result}")
                self.whatsapp.send_text_message(
                    phone,
                    "Sorry, I couldn't process that voice note. Please try again or send a text message."
                )
                return None
        
        elif message_type == 'image':
            # Images are handled within workflows
            return f"[IMAGE:{message.get('image', {}).get('id')}]"
        
        return None
    
    def _determine_intent(
        self, 
        content: str, 
        phone: str,
        user: Optional[Dict] = None
    ) -> Tuple[str, float]:
        """
        Determine the intent of the message.
        
        Returns:
            Tuple of (intent_name, confidence_score)
        """
        content_lower = content.lower()
        
        # Check for keyword matches first (fast path)
        for intent, keywords in self.intent_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    return (intent, 1.0)
        
        # Check if user is mid-workflow (has pending state)
        session = self.session_state.get_state(phone)
        if session and session.get('workflow'):
            return (session['workflow'], 0.9)
        
        # Check conversation store for pending workflow
        pending_workflow = self.conversation_store.get_pending_workflow(phone)
        if pending_workflow:
            return (pending_workflow, 0.9)
        
        # TODO: LLM-based intent detection for ambiguous messages
        return ('unknown', 0.0)
    
    def _check_permission(self, user: Dict, intent: str) -> bool:
        """Check if user has permission for the intent."""
        if intent == 'registration':
            return True  # Anyone can register
        
        if intent == 'unknown':
            return True  # Unknown intent doesn't need permission
        
        permissions = user.get('permissions', {})
        
        # Map intent to permission key
        permission_map = {
            'insights': 'insights',
            'listing_intake': 'listing_intake',
            'listing_query': 'listing_query',
        }
        
        permission_key = permission_map.get(intent)
        if not permission_key:
            return True  # No permission needed for unmapped intents
        
        permission = permissions.get(permission_key, {})
        return permission.get('enabled', False)
    
    def _route_to_workflow(
        self, 
        intent: str, 
        content: str, 
        user: Optional[Dict], 
        phone: str,
        message: dict
    ) -> None:
        """Route to the appropriate workflow based on intent."""
        
        if intent == 'unknown':
            self._handle_unknown_intent(phone, user)
            return
        
        # Get workflow from registry
        workflow = self.workflow_registry.get_workflow(intent)
        
        if not workflow:
            logger.warning(f"No workflow registered for intent: {intent}")
            self._handle_unknown_intent(phone, user)
            return
        
        # Execute workflow
        workflow.execute(
            content=content,
            user=user,
            phone=phone,
            message=message,
            context=self.conversation_store.get_context(phone) if user else None
        )
    
    def _handle_unregistered_user(
        self, 
        phone: str, 
        content: str,
        message: dict
    ) -> None:
        """Handle message from unregistered user - route to registration."""
        logger.info(f"Unregistered user {phone}, routing to registration")
        
        # Route to registration workflow
        workflow = self.workflow_registry.get_workflow('registration')
        
        if workflow:
            workflow.execute(
                content=content,
                user=None,
                phone=phone,
                message=message,
                context=None
            )
        else:
            # Fallback if registration workflow not available
            self.whatsapp.send_text_message(
                phone,
                "Welcome! Please say 'register' to get started."
            )
    
    def _handle_inactive_user(self, phone: str, user: Dict) -> None:
        """Handle message from inactive/deactivated user."""
        name = user.get('name', 'there')
        
        self.whatsapp.send_text_message(
            phone,
            f"Hi {name}, your account is currently inactive. "
            f"Please contact support to reactivate your account."
        )
    
    def _handle_no_permission(
        self, 
        phone: str, 
        user: Dict, 
        intent: str
    ) -> None:
        """Handle case where user lacks permission for requested action."""
        name = user.get('name', 'there')
        
        intent_names = {
            'insights': 'insights',
            'listing_intake': 'create listings',
            'listing_query': 'query listings',
        }
        
        action_name = intent_names.get(intent, intent)
        
        self.whatsapp.send_text_message(
            phone,
            f"Hi {name}, you don't have access to {action_name}. "
            f"Please contact support to upgrade your account."
        )
    
    def _handle_unknown_intent(self, phone: str, user: Optional[Dict]) -> None:
        """Handle message with unknown intent."""
        if not user:
            return
        
        name = user.get('name', 'there')
        permissions = user.get('permissions', {})
        
        # Build help message based on permissions
        options = []
        
        if permissions.get('insights', {}).get('enabled'):
            options.append("📊 *Insights* - Just say 'insights'")
        
        if permissions.get('listing_intake', {}).get('enabled'):
            options.append("🏠 *New Listing* - Record a voice note starting with 'New listing...'")
        
        if not options:
            options.append("Contact support to enable features for your account.")
        
        options_text = "\n".join(options)
        
        message = f"""Hi {name}! 👋

I'm not sure what you'd like to do. Here's what you can do:

{options_text}

Just let me know what you need!"""
        
        self.whatsapp.send_text_message(phone, message)
    
    def _send_error_response(self, phone: str) -> None:
        """Send error response to user."""
        if phone:
            self.whatsapp.send_text_message(
                phone,
                "Sorry, something went wrong. Please try again later."
            )
