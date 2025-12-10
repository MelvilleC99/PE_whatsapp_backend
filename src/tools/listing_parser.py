"""
Listing Parser Tool - Extract structured listing data from text

Takes raw text (transcribed or typed) and extracts structured fields
using LLM with prompts defined in YAML.
"""
import os
import yaml
from typing import Dict, Any, List, Optional
from loguru import logger

from .registry import BaseTool, ToolParameter


class ListingParserTool(BaseTool):
    """Tool for parsing listing details from natural language text."""
    
    name = "listing_parser"
    
    description = """Extract structured property listing data from natural language text.
    Use this tool when you have raw text (from transcription or direct input) that 
    describes a property listing and need to convert it to structured fields."""
    
    parameters = [
        ToolParameter(
            name="text",
            type="string",
            description="Raw listing text to parse (transcribed voice note or typed message)",
            required=True
        ),
        ToolParameter(
            name="phone",
            type="string",
            description="Agent's phone number (for metadata)",
            required=True
        ),
        ToolParameter(
            name="agent_name",
            type="string",
            description="Agent's name (for metadata)",
            required=False
        ),
    ]
    
    examples = [
        {"when": "After transcribing a voice note about a new listing"},
        {"when": "User sends text message with listing details"},
    ]
    
    output_description = """Returns dict with:
    - status: 'success' or 'error'
    - listing_data: Structured listing fields
    - confidence: How confident the parser is (0-1)
    - missing_fields: Required fields that couldn't be extracted
    - raw_input: Original text"""

    def __init__(self):
        """Initialize the listing parser with LLM client and load prompts."""
        from src.config import settings
        
        self.openai_api_key = settings.openai_api_key
        
        if not self.openai_api_key:
            logger.warning("OpenAI API key not configured - parser will fail")
        
        # Load prompts from YAML
        self.prompts = self._load_prompts()
    
    def _load_prompts(self) -> Dict[str, Any]:
        """Load prompts from YAML file."""
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "prompts", "workflows", "listing_parser.yaml"
        )
        
        try:
            with open(prompt_path, 'r') as f:
                prompts = yaml.safe_load(f)
                logger.info(f"Loaded listing parser prompts from {prompt_path}")
                return prompts
        except Exception as e:
            logger.error(f"Failed to load prompts: {e}")
            return {}
    
    def execute(
        self,
        text: str,
        phone: str,
        agent_name: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Parse listing text into structured data.
        
        Args:
            text: Raw listing text
            phone: Agent's phone number
            agent_name: Agent's name
            
        Returns:
            Parsed listing data with confidence score
        """
        logger.info(f"Parsing listing from {phone}: {text[:100]}...")
        
        try:
            # Call LLM to extract structured data
            listing_data = self._extract_with_llm(text)
            
            if not listing_data:
                return {
                    'status': 'error',
                    'error': 'Failed to parse listing text',
                    'raw_input': text,
                    'listing_data': None,
                    'confidence': 0.0,
                    'missing_fields': self.prompts.get('required_fields', [])
                }
            
            # Add metadata
            listing_data['listing_agent_phone'] = phone
            listing_data['listing_agent_name'] = agent_name
            listing_data['raw_input'] = text
            
            # Check for missing required fields
            required = self.prompts.get('required_fields', [])
            missing = [f for f in required if f not in listing_data or listing_data[f] is None]
            
            # Calculate confidence
            confidence = self._calculate_confidence(listing_data, missing)
            
            logger.success(f"Parsed listing: {len(listing_data)} fields, confidence: {confidence:.2f}")
            
            return {
                'status': 'success',
                'listing_data': listing_data,
                'confidence': confidence,
                'missing_fields': missing,
                'raw_input': text
            }
            
        except Exception as e:
            logger.error(f"Listing parser failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'raw_input': text,
                'listing_data': None,
                'confidence': 0.0,
                'missing_fields': []
            }
    
    def _extract_with_llm(self, text: str) -> Optional[Dict[str, Any]]:
        """Use LLM to extract structured listing data."""
        if not self.openai_api_key:
            logger.error("OpenAI API key not configured")
            return None
        
        try:
            import openai
            import json
            
            client = openai.OpenAI(api_key=self.openai_api_key)
            
            # Get prompts from YAML
            system_prompt = self.prompts.get('system_prompt', '')
            extraction_template = self.prompts.get('extraction_prompt', '')
            extraction_prompt = extraction_template.replace('{text}', text)
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": extraction_prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            listing_data = json.loads(result)
            
            # Clean and validate the data
            listing_data = self._clean_extracted_data(listing_data)
            
            return listing_data
            
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return None
    
    def _clean_extracted_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and validate extracted data."""
        cleaned = {}
        
        # Integer fields
        int_fields = [
            'bedrooms', 'bathrooms', 'garages', 'erf_size', 'floor_size',
            'build_year', 'kitchens', 'lounges', 'dining_rooms', 'family_rooms',
            'studies', 'parking_bays', 'carports'
        ]
        
        # Decimal fields
        decimal_fields = ['listing_price', 'levies', 'rates']
        
        # Boolean fields
        bool_fields = [
            'is_security_estate', 'is_retirement', 'is_furnished',
            'is_price_on_application', 'is_no_transfer_duty', 'is_distress_sale',
            'is_bank_repossessed', 'is_public_tender', 'is_auction',
            'has_flatlet', 'has_domestic_accommodation', 'has_entrance_hall',
            'has_balcony', 'has_patio', 'has_laundry', 'has_braai_room',
            'has_storeroom', 'has_pool', 'has_garden', 'is_pet_friendly',
            'has_built_in_braai', 'has_built_in_cupboards', 'has_fireplace',
            'has_solar_panels', 'has_backup_battery', 'has_solar_geyser',
            'has_generator', 'has_borehole', 'has_wellpoint', 'has_water_tank',
            'has_sea_view', 'has_mountain_view', 'has_fairway_view',
            'has_near_beach', 'has_forest_view', 'has_river_view',
            'has_riverfront', 'has_marina', 'has_lakefront',
            'has_24hr_access', 'has_electric_fencing', 'has_security_gate',
            'has_alarm', 'has_cctv'
        ]
        
        for key, value in data.items():
            # Skip null/None values
            if value is None:
                continue
            
            # Integer fields
            if key in int_fields:
                try:
                    cleaned[key] = int(value)
                except (ValueError, TypeError):
                    continue
            
            # Decimal fields
            elif key in decimal_fields:
                try:
                    cleaned[key] = float(value)
                except (ValueError, TypeError):
                    continue
            
            # Boolean fields - only include if True
            elif key in bool_fields:
                if value is True or value == 'true' or value == True:
                    cleaned[key] = True
            
            # String fields
            elif isinstance(value, str) and value.strip():
                cleaned[key] = value.strip()
            
            # Other non-null values
            elif value:
                cleaned[key] = value
        
        return cleaned
    
    def _calculate_confidence(self, data: Dict[str, Any], missing: List[str]) -> float:
        """Calculate confidence score based on extracted fields."""
        weights = self.prompts.get('field_weights', {})
        
        # Start at 100%
        confidence = 1.0
        
        # Penalize for missing required fields
        penalty = weights.get('tier_1_missing_penalty', 0.15)
        confidence -= len(missing) * penalty
        
        # Count tier 2 and tier 3 fields present
        tier_2_fields = [
            'street_number', 'street_name', 'complex_name', 'city', 'postal_code',
            'province', 'property_title', 'property_headline', 'erf_size',
            'floor_size', 'build_year', 'levies', 'rates', 'mandate_type',
            'kitchens', 'lounges', 'dining_rooms', 'family_rooms', 'studies',
            'parking_bays', 'carports', 'is_security_estate', 'is_retirement',
            'is_furnished', 'is_price_on_application', 'is_distress_sale',
            'is_bank_repossessed', 'is_auction', 'has_flatlet',
            'has_domestic_accommodation', 'has_entrance_hall', 'has_balcony',
            'has_patio', 'has_braai_room', 'has_storeroom'
        ]
        
        tier_3_fields = [
            'has_pool', 'has_garden', 'is_pet_friendly', 'has_built_in_braai',
            'has_built_in_cupboards', 'has_fireplace', 'has_solar_panels',
            'has_backup_battery', 'has_solar_geyser', 'has_generator',
            'has_borehole', 'has_wellpoint', 'has_water_tank', 'has_sea_view',
            'has_mountain_view', 'has_fairway_view', 'has_near_beach',
            'has_forest_view', 'has_river_view', 'has_riverfront', 'has_marina',
            'has_lakefront', 'has_24hr_access', 'has_electric_fencing',
            'has_security_gate', 'has_alarm', 'has_cctv'
        ]
        
        tier_2_bonus = weights.get('tier_2_bonus', 0.01)
        tier_3_bonus = weights.get('tier_3_bonus', 0.01)
        
        tier_2_count = sum(1 for f in tier_2_fields if f in data)
        tier_3_count = sum(1 for f in tier_3_fields if f in data)
        
        confidence += min(tier_2_count * tier_2_bonus, 0.1)
        confidence += min(tier_3_count * tier_3_bonus, 0.1)
        
        return max(0.0, min(1.0, confidence))
