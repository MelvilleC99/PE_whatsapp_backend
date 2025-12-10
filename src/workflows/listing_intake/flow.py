"""
Listing Intake Workflow - Handle new listing creation via WhatsApp

Flow:
1. Receive voice note / text with listing details
2. Parse into structured data (LLM)
3. Map features
4. Save as draft
5. Send formatted confirmation with listing summary
"""
from typing import Dict, Any, Optional
from loguru import logger

from src.workflows.registry import BaseWorkflow
from src.clients.whatsapp import WhatsAppClient
from src.tools.listing_parser import ListingParserTool
from src.tools.feature_mapper import FeatureMapperTool
from src.tools.db_writer import DBWriterTool
from src.memory.session_state import SessionStateManager


class ListingIntakeWorkflow(BaseWorkflow):
    """Workflow for creating listings via WhatsApp."""
    
    name = "listing_intake"
    description = "Create a new property listing from WhatsApp message"
    
    def __init__(self):
        self.whatsapp = WhatsAppClient()
        self.parser = ListingParserTool()
        self.feature_mapper = FeatureMapperTool()
        self.db_writer = DBWriterTool()
        self.session = SessionStateManager()
    
    def execute(
        self, 
        content: str,
        user: Dict,
        phone: str,
        message: dict,
        context: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute the listing intake workflow."""
        logger.info(f"Listing intake for {user.get('name', phone)}")
        
        # Check if we're awaiting confirmation
        state = self.session.get_state(phone)
        
        if state and state.get('workflow') == 'listing_intake':
            if state.get('step') == 'awaiting_confirmation':
                return self._handle_confirmation(content, phone, message, state)
        
        # New listing request
        return self._handle_new_listing(content, user, phone)
    
    def _handle_new_listing(self, content: str, user: Dict, phone: str) -> Dict[str, Any]:
        """Process a new listing request."""
        
        # Clean the input
        text = self._clean_trigger(content)
        
        if not text or len(text) < 10:
            self.whatsapp.send_text_message(
                phone,
                "Please include listing details. Example:\n\n"
                "🏠 *3 bed cluster in Sandton, R2.5m, pool, borehole*"
            )
            return {'status': 'needs_input'}
        
        # Send immediate acknowledgment
        first_name = user.get('first_name', user.get('name', 'there').split()[0])
        self.whatsapp.send_text_message(
            phone,
            f"Hi {first_name} 👋\n\n"
            f"Received your listing request. Processing now...\n\n"
            f"I'll send you the draft details shortly."
        )
        
        # Step 1: Parse listing
        logger.info("Parsing listing...")
        parsed = self.parser.execute(text=text, phone=phone, agent_name=user.get('name'))
        
        if parsed.get('status') == 'error':
            self.whatsapp.send_text_message(
                phone,
                "I couldn't understand that listing. Please include:\n"
                "• Property type (house, apartment, etc)\n"
                "• Location (suburb)\n"
                "• Price\n"
                "• Bedrooms & bathrooms"
            )
            return {'status': 'parse_error'}
        
        listing_data = parsed.get('listing_data', {})
        
        # Step 2: Map features
        features = self._extract_features(text)
        mapped = self.feature_mapper.execute(features=features)
        listing_data['features'] = mapped.get('mapped', [])
        
        # Add agent info
        listing_data['listing_agent_phone'] = phone
        listing_data['listing_agent_name'] = user.get('name')
        listing_data['agent_id'] = user.get('agent_id')
        listing_data['raw_input'] = text
        
        # Step 3: Save draft
        result = self.db_writer.execute(
            listing_data=listing_data,
            phone=phone
        )
        
        if result.get('status') != 'success':
            self.whatsapp.send_text_message(
                phone,
                "❌ Error saving listing. Please try again."
            )
            return {'status': 'error', 'error': result.get('error')}
        
        # Step 4: Send success message with formatted summary
        draft_id = result.get('draft_id')
        self._send_draft_confirmation(phone, listing_data, draft_id)
        
        return {
            'status': 'success',
            'draft_id': draft_id,
            'listing_data': listing_data
        }
    
    def _send_draft_confirmation(self, phone: str, data: Dict, draft_id: str):
        """Send formatted draft confirmation message."""
        
        # Build heading
        bedrooms = data.get('bedrooms', '?')
        property_type = data.get('property_type', 'property').lower()
        suburb = data.get('suburb', 'Unknown')
        
        heading = f"{bedrooms} Bedroom {property_type.title()} in {suburb}"
        
        # Format price
        price = data.get('listing_price')
        if price:
            if price >= 1000000:
                price_str = f"R{price/1000000:.1f}m"
            else:
                price_str = f"R{price:,.0f}"
        else:
            price_str = "Price TBC"
        
        # Key details
        bathrooms = data.get('bathrooms', '-')
        garages = data.get('garages', '-')
        mandate = data.get('mandate_type', 'Not specified')
        listing_type = data.get('residential_listing_type', 'sale').title()
        
        # Build message
        message = f"""✅ *Draft Listing Saved*

The following listing has been saved for you to review and publish.

━━━━━━━━━━━━━━━━━━━━━━
*{heading}*
━━━━━━━━━━━━━━━━━━━━━━

💰 *Price:* {price_str}
🛏️ *Bedrooms:* {bedrooms}
🚿 *Bathrooms:* {bathrooms}
🚗 *Garages:* {garages}
📋 *Mandate:* {mandate}
🏷️ *Type:* For {listing_type}"""

        # Add features if any
        features = data.get('features', [])
        if features:
            feature_list = ', '.join(features[:5])
            message += f"\n✨ *Features:* {feature_list}"
            if len(features) > 5:
                message += f" +{len(features)-5} more"
        
        # Add extra details section
        extras = []
        if data.get('erf_size'):
            extras.append(f"Erf: {data['erf_size']}m²")
        if data.get('floor_size'):
            extras.append(f"Floor: {data['floor_size']}m²")
        if data.get('levies'):
            extras.append(f"Levies: R{data['levies']:,.0f}")
        if data.get('rates'):
            extras.append(f"Rates: R{data['rates']:,.0f}")
        
        if extras:
            message += f"\n\n📎 *Additional:* {' | '.join(extras)}"
        
        message += f"""

━━━━━━━━━━━━━━━━━━━━━━

📝 Type *insights* for reports
🏠 Type *new listing* to add another"""

        self.whatsapp.send_text_message(phone, message)
    
    def _handle_confirmation(self, content: str, phone: str, message: dict, state: Dict) -> Dict[str, Any]:
        """Handle confirmation response (if we add confirmation step later)."""
        # For now, we save immediately without confirmation
        # This method exists for future use
        self.session.clear_state(phone)
        return {'status': 'cancelled'}
    
    def _clean_trigger(self, content: str) -> str:
        """Remove trigger phrases from content."""
        triggers = [
            'new listing:', 'new listing', 
            'create listing:', 'create listing',
            'add listing:', 'add listing',
            'list property:', 'list property'
        ]
        
        text = content.strip()
        text_lower = text.lower()
        
        for trigger in triggers:
            if text_lower.startswith(trigger):
                text = text[len(trigger):].strip()
                break
        
        return text
    
    def _extract_features(self, text: str) -> list:
        """Extract feature keywords from text."""
        keywords = [
            'pool', 'garden', 'borehole', 'solar', 'generator', 'genny',
            'fiber', 'fibre', 'alarm', 'electric fence', 'security',
            'pet friendly', 'braai', 'fireplace', 'sea view', 'mountain view',
            'inverter', 'jojo', 'water tank', 'flatlet', 'cottage',
            'staff quarters', 'granny flat', 'study', 'home office'
        ]
        
        text_lower = text.lower()
        return [k for k in keywords if k in text_lower]
