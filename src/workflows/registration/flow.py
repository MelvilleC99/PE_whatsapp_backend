"""
Registration Workflow - Handle new user registration

Flow:
1. User says "register"
2. If known agent: Show "Hi [First Name]" + Confirm button
   If unknown: Ask for first name
3. Show service selection (visible buttons)
4. Create user in Firebase
5. Send success message
"""
import os
import yaml
from typing import Dict, Any, Optional
from loguru import logger

from src.clients.whatsapp import WhatsAppClient
from src.clients.firebase import FirebaseClient
from src.tools.user_registration import UserRegistrationTool
from src.memory.session_state import SessionStateManager


class RegistrationWorkflow:
    """Handles new user registration via WhatsApp."""
    
    name = "registration"
    description = "Register new users via WhatsApp"
    
    def __init__(self):
        """Initialize workflow with dependencies."""
        self.whatsapp = WhatsAppClient()
        self.firebase = FirebaseClient()
        self.user_tool = UserRegistrationTool()
        self.session = SessionStateManager()
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load workflow configuration from YAML."""
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "prompts", "workflows", "registration.yaml"
        )
        
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load registration config: {e}")
            return {}
    
    def execute(
        self,
        content: str,
        phone: str,
        message: dict,
        user: Optional[Dict] = None,
        context: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute the registration workflow."""
        logger.info(f"Registration workflow for {phone}")
        
        # Already registered?
        if user and user.get('active'):
            return self._handle_already_registered(phone, user, content, message)
        
        # Get current session state
        state = self.session.get_state(phone)
        
        # New registration or continue?
        if not state or state.get('workflow') != 'registration':
            return self._step_welcome(phone)
        
        current_step = state.get('step', 'awaiting_name')
        
        if current_step == 'awaiting_name':
            return self._step_receive_name(phone, content, message, state)
        elif current_step == 'awaiting_service_selection':
            return self._step_receive_service(phone, content, message, state)
        elif current_step == 'awaiting_cancel_confirmation':
            # Handle cancel confirmation - pass to already_registered handler
            user_data = state.get('data', {}).get('user', {})
            return self._handle_already_registered(phone, user_data, content, message)
        else:
            return self._step_welcome(phone)
    
    def _lookup_agent(self, phone: str) -> Optional[Dict[str, Any]]:
        """Lookup agent info by phone number."""
        try:
            agent = self.firebase.get_document("agents", phone)
            if agent and agent.get('status') == 'active':
                logger.info(f"Found agent: {agent.get('full_name')}")
                return agent
            return None
        except Exception as e:
            logger.error(f"Agent lookup failed: {e}")
            return None
    
    def _get_first_name(self, agent: Dict) -> str:
        """Get first name from agent data."""
        if agent.get('first_name'):
            return agent['first_name']
        # Fall back to splitting full name
        full_name = agent.get('full_name', agent.get('name', 'there'))
        return full_name.split()[0] if full_name else 'there'
    
    def _step_welcome(self, phone: str) -> Dict[str, Any]:
        """Step 1: Welcome message with confirm button."""
        logger.info(f"Registration: welcome for {phone}")
        
        agent = self._lookup_agent(phone)
        
        if agent:
            # Known agent - show first name + confirm button
            first_name = self._get_first_name(agent)
            msg = self.config.get('messages', {}).get('welcome_agent', {})
            
            body = msg.get('body', 'Hi {first_name}!')
            body = body.replace('{first_name}', first_name)
            body = body.replace('{agency}', agent.get('agency_name', ''))
            body = body.replace('{office}', agent.get('office_name', ''))
            
            buttons = msg.get('buttons', [{"id": "confirm_name", "title": "✓ Confirm"}])
            
            self.whatsapp.send_interactive_button_message(
                to=phone,
                body_text=body.strip(),
                buttons=buttons
            )
            
            self.session.set_state(phone, {
                'workflow': 'registration',
                'step': 'awaiting_name',
                'data': {
                    'agent': agent, 
                    'first_name': first_name,
                    'full_name': agent.get('full_name', first_name)
                }
            })
        else:
            # New user - ask for first name
            msg = self.config.get('messages', {}).get('welcome_new', {})
            body = msg.get('body', 'Welcome! What\'s your first name?')
            
            self.whatsapp.send_text_message(phone, body.strip())
            
            self.session.set_state(phone, {
                'workflow': 'registration',
                'step': 'awaiting_name',
                'data': {}
            })
        
        return {'status': 'awaiting_input', 'step': 'awaiting_name'}
    
    def _step_receive_name(self, phone: str, content: str, message: dict, state: Dict) -> Dict[str, Any]:
        """Step 2: Receive name/confirmation, show service selection."""
        logger.info(f"Registration: receive_name for {phone}")
        
        data = state.get('data', {})
        agent = data.get('agent')
        
        # Check if they clicked confirm button
        button_id = self._extract_button_id(message)
        logger.info(f"Button ID: {button_id}, Content: {content}, Data: {data}")
        
        # If known agent clicked confirm, use stored name
        if button_id == 'confirm_name':
            first_name = data.get('first_name')
            full_name = data.get('full_name', first_name)
            if not first_name:
                logger.warning("Confirm clicked but no first_name in session")
                first_name = "there"
                full_name = first_name
        elif data.get('first_name') and content.lower() in ['yes', 'confirm', 'correct']:
            # They typed YES instead of clicking button
            first_name = data['first_name']
            full_name = data.get('full_name', first_name)
        else:
            # They typed a new name (unknown user flow)
            first_name = content.strip().split()[0]
            full_name = content.strip()
        
        # Validate
        if len(first_name) < 2 or len(first_name) > 50:
            self.whatsapp.send_text_message(phone, "Please enter a valid name.")
            return {'status': 'awaiting_input', 'step': 'awaiting_name'}
        
        # Send service selection with visible buttons
        msg = self.config.get('messages', {}).get('service_selection', {})
        
        body = msg.get('body', 'Which services would you like?')
        body = body.replace('{first_name}', first_name)
        
        buttons = msg.get('buttons', [
            {"id": "reg_both", "title": "📊🏠 Both"}
        ])
        
        self.whatsapp.send_interactive_button_message(
            to=phone,
            body_text=body.strip(),
            buttons=buttons
        )
        
        # Update session
        self.session.set_state(phone, {
            'workflow': 'registration',
            'step': 'awaiting_service_selection',
            'data': {
                'first_name': first_name,
                'full_name': full_name,
                'agent': agent
            }
        })
        
        return {'status': 'awaiting_input', 'step': 'awaiting_service_selection'}
    
    def _step_receive_service(self, phone: str, content: str, message: dict, state: Dict) -> Dict[str, Any]:
        """Step 3: Receive service selection, create user."""
        logger.info(f"Registration: receive_service for {phone}")
        
        # Extract selection from button
        selection_id = self._extract_button_id(message) or self._parse_service_from_text(content)
        
        if not selection_id or selection_id not in self.config.get('service_options', {}):
            self.whatsapp.send_text_message(phone, "Please tap one of the buttons above.")
            return {'status': 'awaiting_input', 'step': 'awaiting_service_selection'}
        
        # Get service config
        service_config = self.config['service_options'][selection_id]
        service_name = service_config['name']
        permissions = service_config['permissions']
        
        # Get data from session
        data = state.get('data', {})
        first_name = data.get('first_name', 'User')
        full_name = data.get('full_name', first_name)
        agent = data.get('agent')
        
        # Build user data
        user_data = {
            'phone': phone,
            'name': full_name,
            'first_name': first_name,
            'permissions': permissions
        }
        
        if agent:
            user_data.update({
                'agent_id': agent.get('agent_id'),
                'agency_id': agent.get('agency_id'),
                'agency_name': agent.get('agency_name'),
                'office_id': agent.get('office_id'),
                'office_name': agent.get('office_name'),
                'email': agent.get('email')
            })
        
        # Create user
        result = self.user_tool.execute(**user_data)
        
        if result['status'] in ('success', 'exists'):
            # Send success message
            if agent:
                msg = self.config.get('messages', {}).get('success', {})
                body = msg.get('body', '✅ Registration complete!')
                agency_line = f"{agent.get('agency_name')} · {agent.get('office_name')}"
                body = body.replace('{first_name}', first_name)
                body = body.replace('{agency_line}', agency_line)
            else:
                msg = self.config.get('messages', {}).get('success_no_agency', {})
                body = msg.get('body', '✅ You\'re all set!')
                body = body.replace('{first_name}', first_name)
            
            self.whatsapp.send_text_message(phone, body.strip())
            self.session.clear_state(phone)
            
            return {'status': 'complete', 'user': result.get('user')}
        else:
            msg = self.config.get('messages', {}).get('error', {})
            self.whatsapp.send_text_message(phone, msg.get('body', 'Registration failed.').strip())
            self.session.clear_state(phone)
            
            return {'status': 'error', 'message': result.get('message')}
    
    def _handle_already_registered(self, phone: str, user: Dict, content: str, message: dict) -> Dict[str, Any]:
        """Handle already registered user with action buttons."""
        
        # Check if they clicked a button
        button_id = self._extract_button_id(message)
        logger.info(f"Already registered handler - button: {button_id}")
        
        if button_id == 'edit_registration':
            # For now, just tell them to contact support
            self.whatsapp.send_text_message(
                phone, 
                "To edit your registration, please contact support."
            )
            return {'status': 'edit_requested'}
        
        elif button_id == 'cancel_registration':
            # Show confirmation message
            msg = self.config.get('messages', {}).get('cancel_confirmation', {})
            body = msg.get('body', 'Are you sure you want to cancel?')
            buttons = msg.get('buttons', [
                {"id": "confirm_cancel", "title": "Yes, Cancel"},
                {"id": "keep_registration", "title": "No, Keep It"}
            ])
            
            self.whatsapp.send_interactive_button_message(
                to=phone,
                body_text=body.strip(),
                buttons=buttons
            )
            
            # Save state so we can handle the confirmation
            self.session.set_state(phone, {
                'workflow': 'registration',
                'step': 'awaiting_cancel_confirmation',
                'data': {'user': user}
            })
            return {'status': 'awaiting_cancel_confirmation'}
        
        elif button_id == 'confirm_cancel':
            # Actually cancel the registration
            try:
                self.firebase.set_document(
                    collection="whatsapp_users",
                    doc_id=phone,
                    data={'active': False, 'status': 'cancelled'},
                    merge=True
                )
                msg = self.config.get('messages', {}).get('cancelled', {})
                self.whatsapp.send_text_message(phone, msg.get('body', 'Registration cancelled.').strip())
                self.session.clear_state(phone)
                return {'status': 'cancelled'}
            except Exception as e:
                logger.error(f"Failed to cancel registration: {e}")
                self.whatsapp.send_text_message(phone, "Sorry, something went wrong. Please try again.")
                return {'status': 'error'}
        
        elif button_id == 'keep_registration':
            # Keep the registration
            msg = self.config.get('messages', {}).get('kept', {})
            self.whatsapp.send_text_message(phone, msg.get('body', 'Your registration is still active.').strip())
            self.session.clear_state(phone)
            return {'status': 'kept'}
        
        # Show already registered message with buttons
        first_name = user.get('first_name', user.get('name', 'there').split()[0])
        
        msg = self.config.get('messages', {}).get('already_registered', {})
        body = msg.get('body', 'You\'re already registered.')
        body = body.replace('{first_name}', first_name)
        
        buttons = msg.get('buttons', [
            {"id": "edit_registration", "title": "✏️ Edit Registration"},
            {"id": "cancel_registration", "title": "❌ Cancel Registration"}
        ])
        
        self.whatsapp.send_interactive_button_message(
            to=phone,
            body_text=body.strip(),
            buttons=buttons
        )
        
        return {'status': 'already_registered'}
    
    def _extract_button_id(self, message: dict) -> Optional[str]:
        """Extract button ID from interactive reply."""
        try:
            if message.get('type') == 'interactive':
                interactive = message.get('interactive', {})
                if interactive.get('type') == 'button_reply':
                    return interactive.get('button_reply', {}).get('id')
                elif interactive.get('type') == 'list_reply':
                    return interactive.get('list_reply', {}).get('id')
        except Exception as e:
            logger.error(f"Error extracting button: {e}")
        return None
    
    def _parse_service_from_text(self, content: str) -> Optional[str]:
        """Parse service from text input."""
        content_lower = content.lower()
        
        if 'both' in content_lower:
            return 'reg_both'
        elif 'insight' in content_lower:
            return 'reg_insights'
        elif 'listing' in content_lower:
            return 'reg_listings'
        
        return None
