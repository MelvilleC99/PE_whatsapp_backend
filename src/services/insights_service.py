"""
Insights service for managing user insights
"""
from typing import Dict, Optional
from loguru import logger
from datetime import datetime

from src.integrations.firebase_client import FirebaseClient
from src.insight_generator import InsightGenerator


class InsightsService:
    """Service for generating and managing user insights"""
    
    def __init__(self):
        """Initialize insights service"""
        self.firebase = FirebaseClient()
        self.insights_collection = self.firebase.get_collection('insights')
        self.generator = InsightGenerator()
    
    def generate_and_save_insights(self, user_id: str, use_mock: bool = False) -> Dict:
        """
        Generate insights for a user and save to Firebase
        
        Args:
            user_id: User's Firebase document ID
            use_mock: If True, generate mock data instead of querying database
            
        Returns:
            Generated insights dictionary
        """
        try:
            # Generate insights
            if use_mock:
                insights_data = self.generator.generate_mock_insights()
            else:
                insights_data = self.generator.generate_insights_for_user(user_id)
            
            # Save to Firebase
            self.save_insights(user_id, insights_data)
            
            return insights_data
            
        except Exception as e:
            logger.error(f"Failed to generate and save insights for user {user_id}: {e}")
            raise
    
    def save_insights(self, user_id: str, insights_data: Dict):
        """
        Save insights for a specific user
        
        Args:
            user_id: User's Firebase document ID
            insights_data: Dictionary of insight metrics
        """
        insight_doc = {
            "user_id": user_id,
            "generated_at": datetime.now(),
            "data": insights_data
        }
        
        # Use user_id as document ID to easily overwrite weekly
        self.insights_collection.document(user_id).set(insight_doc)
        logger.info(f"Saved insights for user {user_id}")
    
    def get_insights(self, user_id: str) -> Optional[Dict]:
        """
        Get insights for a specific user
        
        Args:
            user_id: User's Firebase document ID
            
        Returns:
            Insights dictionary or None
        """
        doc = self.insights_collection.document(user_id).get()
        
        if doc.exists:
            return doc.to_dict()
        return None
    
    def get_latest_insights_data(self, user_id: str) -> Optional[Dict]:
        """
        Get just the insights data (not the metadata) for a user
        
        Args:
            user_id: User's Firebase document ID
            
        Returns:
            Insights data dictionary or None
        """
        insights = self.get_insights(user_id)
        if insights and 'data' in insights:
            return insights['data']
        return None
    
    def close(self):
        """Close database connection"""
        if hasattr(self.generator, 'close'):
            self.generator.close()
