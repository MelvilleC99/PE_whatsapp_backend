"""
Insight generator for property CRM database
"""
import psycopg2
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from loguru import logger

from src.config import settings


class InsightGenerator:
    """Generate insights from property CRM database"""
    
    def __init__(self):
        """Initialize database connection"""
        self.connection = None
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(
                host=settings.database_host,
                port=settings.database_port,
                database=settings.database_name,
                user=settings.database_user,
                password=settings.database_password
            )
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def generate_insights_for_user(self, user_id: str) -> Dict:
        """
        Generate insights for a specific user
        
        NOTE: This is a template - customize queries for your database schema
        
        Args:
            user_id: User identifier from your system
            
        Returns:
            Dictionary of insight metrics
        """
        try:
            cursor = self.connection.cursor()
            
            # EXAMPLE QUERIES - Customize these for your database schema
            
            # 1. Get sales change (last 7 days vs previous 7 days)
            sales_change = self._calculate_sales_change(cursor, user_id)
            
            # 2. Get active listings count
            active_listings = self._get_active_listings(cursor, user_id)
            
            # 3. Get average price
            avg_price = self._get_average_price(cursor, user_id)
            
            # 4. Get sales velocity (days to sell)
            sales_velocity = self._get_sales_velocity(cursor, user_id)
            
            cursor.close()
            
            insights = {
                "sales_change": sales_change,
                "active_listings": active_listings,
                "avg_price": avg_price,
                "sales_velocity": sales_velocity,
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info(f"Generated insights for user {user_id}")
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate insights: {e}")
            raise
    
    def _calculate_sales_change(self, cursor, user_id: str) -> str:
        """
        Calculate sales change percentage
        
        CUSTOMIZE THIS QUERY FOR YOUR DATABASE SCHEMA
        """
        try:
            # Example query - adjust table/column names
            query = """
                SELECT 
                    COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '7 days') as current_week,
                    COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '14 days' 
                                     AND created_at < NOW() - INTERVAL '7 days') as previous_week
                FROM sales
                WHERE user_id = %s
            """
            
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            
            current, previous = result[0], result[1]
            
            if previous == 0:
                return "+100%" if current > 0 else "No change"
            
            change = ((current - previous) / previous) * 100
            sign = "+" if change > 0 else ""
            return f"{sign}{change:.1f}%"
            
        except Exception as e:
            logger.warning(f"Could not calculate sales change: {e}")
            return "N/A"
    
    def _get_active_listings(self, cursor, user_id: str) -> int:
        """Get count of active listings"""
        try:
            query = """
                SELECT COUNT(*) 
                FROM listings 
                WHERE user_id = %s AND status = 'active'
            """
            cursor.execute(query, (user_id,))
            return cursor.fetchone()[0]
        except Exception as e:
            logger.warning(f"Could not get active listings: {e}")
            return 0

    def _get_average_price(self, cursor, user_id: str) -> str:
        """Get average listing price"""
        try:
            query = """
                SELECT AVG(price) 
                FROM listings 
                WHERE user_id = %s AND status = 'active'
            """
            cursor.execute(query, (user_id,))
            avg = cursor.fetchone()[0]
            
            if avg:
                return f"R{avg:,.0f}"
            return "N/A"
        except Exception as e:
            logger.warning(f"Could not calculate average price: {e}")
            return "N/A"
    
    def _get_sales_velocity(self, cursor, user_id: str) -> str:
        """Get average days to sell"""
        try:
            query = """
                SELECT AVG(EXTRACT(DAY FROM (sold_date - listed_date))) 
                FROM listings 
                WHERE user_id = %s 
                  AND status = 'sold' 
                  AND sold_date >= NOW() - INTERVAL '90 days'
            """
            cursor.execute(query, (user_id,))
            avg_days = cursor.fetchone()[0]
            
            if avg_days:
                return f"{avg_days:.0f} days"
            return "N/A"
        except Exception as e:
            logger.warning(f"Could not calculate sales velocity: {e}")
            return "N/A"
    
    def generate_mock_insights(self) -> Dict:
        """
        Generate mock insights for testing without database
        
        Returns:
            Dictionary of mock insight data
        """
        import random
        
        sales_changes = ["+5%", "+12%", "-3%", "+8%", "+15%"]
        
        return {
            "sales_change": random.choice(sales_changes),
            "active_listings": random.randint(20, 100),
            "avg_price": f"R{random.randint(300, 800)}K",
            "sales_velocity": f"{random.randint(10, 30)} days",
            "generated_at": datetime.now().isoformat()
        }


if __name__ == "__main__":
    # Test insight generator
    print("Testing Insight Generator...\n")
    
    # Test with mock data (no database required)
    generator = InsightGenerator()
    mock_insights = generator.generate_mock_insights()
    
    print("✅ Mock insights generated:")
    for key, value in mock_insights.items():
        print(f"  {key}: {value}")
    
    generator.close()
