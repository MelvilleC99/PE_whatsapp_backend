"""
DB Writer Tool - Write listing drafts to Firebase

Takes structured listing data and writes it to the listing_drafts collection.
Handles:
- Adding metadata (status, timestamps, IDs)
- Validating required fields
- Creating the draft document
"""
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger

from .registry import BaseTool, ToolParameter


class DBWriterTool(BaseTool):
    """Tool for writing listing drafts to Firebase."""
    
    name = "db_writer"
    
    description = """Write a parsed listing to Firebase as a draft.
    Use this tool after listing_parser has extracted structured data
    and the user has confirmed they want to save the listing."""
    
    parameters = [
        ToolParameter(
            name="listing_data",
            type="object",
            description="Structured listing data from listing_parser",
            required=True
        ),
        ToolParameter(
            name="phone",
            type="string",
            description="Agent's phone number",
            required=True
        ),
        ToolParameter(
            name="agent_name",
            type="string",
            description="Agent's name",
            required=False
        ),
        ToolParameter(
            name="agent_id",
            type="integer",
            description="Agent's MySQL ID (for future DB sync)",
            required=False
        ),
        ToolParameter(
            name="status",
            type="string",
            description="Draft status: draft, pending_confirmation, confirmed",
            required=False,
            default="draft"
        ),
    ]
    
    examples = [
        {"when": "After user confirms listing details"},
        {"when": "Saving a parsed listing as draft for later review"},
    ]
    
    output_description = """Returns dict with:
    - status: 'success' or 'error'
    - draft_id: Firebase document ID
    - message: Human-readable result message"""

    def __init__(self):
        """Initialize with Firebase client."""
        from src.clients.firebase import FirebaseClient
        
        self.firebase = FirebaseClient()
    
    def execute(
        self,
        listing_data: Dict[str, Any],
        phone: str,
        agent_name: str = None,
        agent_id: int = None,
        status: str = "draft",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Write listing data to Firebase.
        
        Args:
            listing_data: Structured listing data
            phone: Agent's phone number
            agent_name: Agent's name
            agent_id: Agent's MySQL ID
            status: Draft status
            
        Returns:
            Result with draft_id
        """
        logger.info(f"Writing listing draft for {phone}")
        
        try:
            # Generate document ID
            now = datetime.now()
            draft_id = f"draft_{phone}_{now.strftime('%Y%m%d_%H%M%S')}"
            
            # Build the document
            document = self._build_document(
                draft_id=draft_id,
                listing_data=listing_data,
                phone=phone,
                agent_name=agent_name,
                agent_id=agent_id,
                status=status,
                timestamp=now
            )
            
            # Write to Firebase
            self.firebase.set_document(
                collection="listing_drafts",
                doc_id=draft_id,
                data=document,
                merge=False
            )
            
            logger.success(f"Created listing draft: {draft_id}")
            
            # Build summary for response
            summary = self._build_summary(listing_data)
            
            return {
                'status': 'success',
                'draft_id': draft_id,
                'message': f"Draft listing created successfully!",
                'summary': summary
            }
            
        except Exception as e:
            logger.error(f"Failed to write listing draft: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'draft_id': None,
                'message': f"Failed to save listing: {str(e)}"
            }
    
    def _build_document(
        self,
        draft_id: str,
        listing_data: Dict[str, Any],
        phone: str,
        agent_name: str,
        agent_id: int,
        status: str,
        timestamp: datetime
    ) -> Dict[str, Any]:
        """Build the complete document for Firebase."""
        
        # Start with listing data
        document = dict(listing_data)
        
        # Add/override metadata
        document['id'] = draft_id
        document['status'] = status
        document['source'] = 'whatsapp'
        document['listing_agent_phone'] = phone
        document['listing_agent_name'] = agent_name
        document['agent_id'] = agent_id
        document['created_at'] = timestamp.isoformat()
        document['updated_at'] = timestamp.isoformat()
        
        # Ensure property_category has a default
        if 'property_category' not in document:
            document['property_category'] = 'residential'
        
        return document
    
    def _build_summary(self, listing_data: Dict[str, Any]) -> str:
        """Build a human-readable summary of the listing."""
        parts = []
        
        # Property type and beds
        property_type = listing_data.get('property_type', 'Property')
        bedrooms = listing_data.get('bedrooms')
        if bedrooms:
            parts.append(f"{bedrooms} bed {property_type}")
        else:
            parts.append(property_type.title())
        
        # Location
        suburb = listing_data.get('suburb')
        city = listing_data.get('city')
        if suburb:
            location = suburb
            if city:
                location += f", {city}"
            parts.append(f"in {location}")
        
        # Price
        price = listing_data.get('listing_price')
        listing_type = listing_data.get('residential_listing_type', 'sale')
        if price:
            if price >= 1000000:
                price_str = f"R{price/1000000:.1f}m"
            else:
                price_str = f"R{price:,.0f}"
            
            if listing_type == 'rent':
                price_str += " pm"
            
            parts.append(price_str)
        
        return " ".join(parts)
    
    def update_status(
        self,
        draft_id: str,
        new_status: str
    ) -> Dict[str, Any]:
        """
        Update the status of an existing draft.
        
        Args:
            draft_id: Firebase document ID
            new_status: New status value
            
        Returns:
            Result dict
        """
        try:
            self.firebase.set_document(
                collection="listing_drafts",
                doc_id=draft_id,
                data={
                    'status': new_status,
                    'updated_at': datetime.now().isoformat()
                },
                merge=True
            )
            
            logger.info(f"Updated draft {draft_id} status to {new_status}")
            
            return {
                'status': 'success',
                'draft_id': draft_id,
                'new_status': new_status
            }
            
        except Exception as e:
            logger.error(f"Failed to update draft status: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def get_draft(self, draft_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a draft by ID.
        
        Args:
            draft_id: Firebase document ID
            
        Returns:
            Draft document or None
        """
        try:
            return self.firebase.get_document(
                collection="listing_drafts",
                doc_id=draft_id
            )
        except Exception as e:
            logger.error(f"Failed to get draft: {e}")
            return None
    
    def get_drafts_by_phone(self, phone: str, limit: int = 10) -> list:
        """
        Get all drafts for a specific agent.
        
        Args:
            phone: Agent's phone number
            limit: Max drafts to return
            
        Returns:
            List of draft documents
        """
        try:
            # Query drafts by phone
            # Note: This requires the Firebase client to support queries
            # For now, we'll use a simple approach
            return self.firebase.query_collection(
                collection="listing_drafts",
                field="listing_agent_phone",
                operator="==",
                value=phone,
                limit=limit
            )
        except Exception as e:
            logger.error(f"Failed to get drafts for {phone}: {e}")
            return []
