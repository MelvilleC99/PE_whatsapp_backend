"""
Feature Mapper Tool - Map text features to database feature codes

Implements hybrid approach:
- Hardcoded mapping for common terms (fast)
- LLM fallback for fuzzy matching (flexible)
"""
from typing import Dict, Any, List, Tuple, Optional
from loguru import logger

from .registry import BaseTool


class FeatureMapperTool(BaseTool):
    """Tool for mapping feature text to database codes."""
    
    name = "feature_mapper"
    description = "Map feature descriptions to database feature codes"
    
    def __init__(self):
        # Hardcoded feature mappings
        self.feature_map = {
            # mainFeaturesIds
            "pool": ("mainFeaturesIds", "pool"),
            "swimming pool": ("mainFeaturesIds", "pool"),
            "garden": ("mainFeaturesIds", "garden"),
            "pet friendly": ("mainFeaturesIds", "petFriendly"),
            "pets allowed": ("mainFeaturesIds", "petFriendly"),
            "braai": ("mainFeaturesIds", "builtInBraai"),
            "built-in braai": ("mainFeaturesIds", "builtInBraai"),
            "built in braai": ("mainFeaturesIds", "builtInBraai"),
            "fireplace": ("mainFeaturesIds", "fireplace"),
            "cupboards": ("mainFeaturesIds", "builtInCupboards"),
            "built-in cupboards": ("mainFeaturesIds", "builtInCupboards"),
            
            # waterIds
            "borehole": ("waterIds", "borehole"),
            "bore hole": ("waterIds", "borehole"),
            "jojo": ("waterIds", "waterTank"),
            "jojo tank": ("waterIds", "waterTank"),
            "water tank": ("waterIds", "waterTank"),
            "well point": ("waterIds", "wellPoint"),
            "wellpoint": ("waterIds", "wellPoint"),
            
            # securityIds
            "alarm": ("securityIds", "alarmSystem"),
            "alarm system": ("securityIds", "alarmSystem"),
            "electric fence": ("securityIds", "electricFencing"),
            "electric fencing": ("securityIds", "electricFencing"),
            "security gate": ("securityIds", "securityGate"),
            "24 hour": ("securityIds", "24HourAccess"),
            "24hr": ("securityIds", "24HourAccess"),
            "24 hour access": ("securityIds", "24HourAccess"),
            "intercom": ("securityIds", "intercom"),
            
            # solarBackupIds
            "solar": ("solarBackupIds", "solarPanels"),
            "solar panels": ("solarBackupIds", "solarPanels"),
            "generator": ("solarBackupIds", "generator"),
            "genny": ("solarBackupIds", "generator"),
            "gennie": ("solarBackupIds", "generator"),
            "inverter": ("solarBackupIds", "backupBatteryInverter"),
            "battery backup": ("solarBackupIds", "backupBatteryInverter"),
            "solar geyser": ("solarBackupIds", "solarGeyser"),
            
            # internetIds
            "fiber": ("internetIds", "fibre"),
            "fibre": ("internetIds", "fibre"),
            "satellite": ("internetIds", "satellite"),
            
            # sceneryViewIds
            "sea view": ("sceneryViewIds", "seaView"),
            "ocean view": ("sceneryViewIds", "seaView"),
            "mountain view": ("sceneryViewIds", "mountainView"),
            "garden view": ("sceneryViewIds", "gardenView"),
        }
        
        # Valid feature codes for LLM matching
        self.valid_codes = {
            "mainFeaturesIds": ["pool", "garden", "petFriendly", "builtInBraai", 
                               "builtInCupboards", "fireplace", "greenBuilding"],
            "securityIds": ["securityGate", "24HourAccess", "intercom", 
                           "alarmSystem", "electricFencing"],
            "waterIds": ["borehole", "wellPoint", "waterTank"],
            "solarBackupIds": ["solarPanels", "backupBatteryInverter", 
                              "solarGeyser", "generator"],
            "internetIds": ["fibre", "satellite", "adsl", "wireless"],
            "sceneryViewIds": ["seaView", "mountainView", "gardenView", "cityView"],
        }
    
    def execute(self, features: List[str], **kwargs) -> Dict[str, Any]:
        """
        Map feature texts to database codes.
        
        Args:
            features: List of feature texts to map
            
        Returns:
            Mapped features and any unmatched items
        """
        mapped = []
        unmatched = []
        
        for feature in features:
            result = self._map_feature(feature.lower().strip())
            if result:
                mapped.append({
                    'original': feature,
                    'code': result[0],
                    'value': result[1]
                })
            else:
                unmatched.append(feature)
        
        # Try LLM for unmatched features
        if unmatched:
            llm_mapped = self._llm_fuzzy_match(unmatched)
            mapped.extend(llm_mapped['mapped'])
            unmatched = llm_mapped['still_unmatched']
        
        return {
            'status': 'success',
            'mapped': mapped,
            'unmatched': unmatched,
            'total': len(features),
            'matched_count': len(mapped)
        }
    
    def _map_feature(self, text: str) -> Optional[Tuple[str, str]]:
        """Try to map a feature using hardcoded mapping."""
        return self.feature_map.get(text)
    
    def _llm_fuzzy_match(self, unmatched: List[str]) -> Dict[str, Any]:
        """
        Use LLM to fuzzy match unmatched features.
        
        Args:
            unmatched: List of unmatched feature texts
            
        Returns:
            Newly mapped features and remaining unmatched
        """
        # TODO: Implement LLM-based fuzzy matching
        logger.info(f"LLM fuzzy match requested for: {unmatched}")
        
        return {
            'mapped': [],
            'still_unmatched': unmatched
        }
