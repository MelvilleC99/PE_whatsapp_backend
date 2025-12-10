"""
Confirmation Tool - Handle user confirmations (YES/NO flows)
"""
from typing import Dict, Any, Optional
from loguru import logger

from .registry import BaseTool


class ConfirmationTool(BaseTool):
    """Tool for handling confirmation flows."""
    
    name = "confirmation"
    description = "Handle user confirmation responses (YES/NO)"
    
    # Words that mean YES
    YES_WORDS = ['yes', 'y', 'yep', 'yeah', 'correct', 'confirm', 'ok', 'okay', 'sure']
    
    # Words that mean NO
    NO_WORDS = ['no', 'n', 'nope', 'cancel', 'stop', 'wrong', 'incorrect']
    
    def execute(self, response: str, **kwargs) -> Dict[str, Any]:
        """
        Parse a confirmation response.
        
        Args:
            response: User's response text
            
        Returns:
            Parsed confirmation status
        """
        response_lower = response.lower().strip()
        
        # Check for YES
        if any(word in response_lower for word in self.YES_WORDS):
            return {
                'status': 'confirmed',
                'action': 'proceed',
                'original': response
            }
        
        # Check for NO
        if any(word in response_lower for word in self.NO_WORDS):
            return {
                'status': 'rejected',
                'action': 'cancel',
                'original': response
            }
        
        # Unclear response
        return {
            'status': 'unclear',
            'action': 'ask_again',
            'original': response,
            'message': 'Please reply YES to confirm or NO to cancel.'
        }
    
    def format_confirmation_message(
        self, 
        parsed_data: Dict[str, Any],
        workflow: str = 'listing'
    ) -> str:
        """
        Format a confirmation message for the user.
        
        Args:
            parsed_data: Data to confirm
            workflow: Workflow name for context
            
        Returns:
            Formatted confirmation message
        """
        if workflow == 'listing':
            return self._format_listing_confirmation(parsed_data)
        
        return "Please confirm: Reply YES to proceed or NO to cancel."
    
    def _format_listing_confirmation(self, data: Dict) -> str:
        """Format listing confirmation message."""
        lines = ["📋 *Here's what I captured:*\n"]
        
        # Property basics
        if data.get('property_type'):
            lines.append(f"🏠 Type: {data['property_type']}")
        
        if data.get('listing_type'):
            lines.append(f"📌 For: {data['listing_type'].upper()}")
        
        # Rooms
        rooms = []
        if data.get('bedrooms'):
            rooms.append(f"{data['bedrooms']} bed")
        if data.get('bathrooms'):
            rooms.append(f"{data['bathrooms']} bath")
        if rooms:
            lines.append(f"🛏️ Rooms: {', '.join(rooms)}")
        
        # Price
        if data.get('sale_price'):
            lines.append(f"💰 Price: R{data['sale_price']:,.0f}")
        elif data.get('rental_price'):
            lines.append(f"💰 Rent: R{data['rental_price']:,.0f}/month")
        
        # Location
        if data.get('suburb'):
            lines.append(f"📍 Location: {data['suburb']}")
        
        # Features
        if data.get('features'):
            features = [f['original'] for f in data['features'][:5]]
            lines.append(f"✨ Features: {', '.join(features)}")
        
        lines.append("\n*Reply YES to save as draft, or NO to cancel.*")
        
        return "\n".join(lines)
