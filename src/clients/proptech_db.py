"""
PropTech Database Client - MySQL connection for proptech database
"""
import os
from typing import Dict, Any, Optional, List
from loguru import logger

try:
    import mysql.connector
    from mysql.connector import Error
except ImportError:
    mysql = None


class PropTechDBClient:
    """
    Client for PropTech MySQL database.
    
    Handles connections to the proptech database for:
    - Reading property data
    - Writing draft listings
    - Lookups (property types, suburbs, etc.)
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern for database connection."""
        if cls._instance is None:
            cls._instance = super(PropTechDBClient, cls).__new__(cls)
            cls._instance._connection = None
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._config = {
                'host': os.getenv('PROPTECH_DB_HOST', '127.0.0.1'),
                'port': int(os.getenv('PROPTECH_DB_PORT', '3307')),
                'database': os.getenv('PROPTECH_DB_NAME', 'proptech'),
                'user': os.getenv('PROPTECH_DB_USER', 'root'),
                'password': os.getenv('PROPTECH_DB_PASSWORD', ''),
            }
            self._initialized = True
    
    def connect(self) -> bool:
        """
        Establish database connection.
        
        Returns:
            True if connected successfully
        """
        if mysql is None:
            raise ImportError("mysql-connector-python not installed. Run: pip install mysql-connector-python")
        
        try:
            self._connection = mysql.connector.connect(**self._config)
            
            if self._connection.is_connected():
                logger.info(f"Connected to PropTech database at {self._config['host']}:{self._config['port']}")
                return True
            return False
            
        except Error as e:
            logger.error(f"Failed to connect to PropTech database: {e}")
            return False
    
    def disconnect(self) -> None:
        """Close database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            logger.info("Disconnected from PropTech database")
    
    def execute_query(
        self, 
        query: str, 
        params: tuple = None,
        fetch: bool = True
    ) -> Optional[List[Dict]]:
        """
        Execute a query and return results.
        
        Args:
            query: SQL query
            params: Query parameters
            fetch: Whether to fetch results
            
        Returns:
            List of result dicts or None
        """
        if not self._connection or not self._connection.is_connected():
            self.connect()
        
        try:
            cursor = self._connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch:
                results = cursor.fetchall()
                cursor.close()
                return results
            else:
                self._connection.commit()
                last_id = cursor.lastrowid
                cursor.close()
                return [{'last_insert_id': last_id}]
                
        except Error as e:
            logger.error(f"Query execution error: {e}")
            return None
    
    def get_property_types(self) -> List[Dict]:
        """Get all property types."""
        query = "SELECT id, name, code FROM property_type ORDER BY name"
        return self.execute_query(query) or []
    
    def get_property_type_by_name(self, name: str) -> Optional[Dict]:
        """Get property type by name (case insensitive)."""
        query = "SELECT id, name, code FROM property_type WHERE LOWER(name) = LOWER(%s)"
        results = self.execute_query(query, (name,))
        return results[0] if results else None
    
    def get_property_categories(self) -> List[Dict]:
        """Get all property categories."""
        query = "SELECT id, name, code FROM property_category ORDER BY sequence"
        return self.execute_query(query) or []
    
    def search_suburbs(self, search: str, limit: int = 10) -> List[Dict]:
        """Search suburbs by name."""
        query = """
            SELECT id, name, type, path 
            FROM geo_location 
            WHERE name LIKE %s AND type = 'suburb'
            LIMIT %s
        """
        return self.execute_query(query, (f"%{search}%", limit)) or []
    
    def insert_unit(self, data: Dict[str, Any]) -> Optional[int]:
        """
        Insert a new unit record.
        
        Args:
            data: Unit data dictionary
            
        Returns:
            Created unit ID or None
        """
        # Build insert query dynamically based on provided fields
        fields = list(data.keys())
        placeholders = ', '.join(['%s'] * len(fields))
        columns = ', '.join(fields)
        
        query = f"INSERT INTO dummy_unit ({columns}) VALUES ({placeholders})"
        
        result = self.execute_query(query, tuple(data.values()), fetch=False)
        
        if result:
            return result[0].get('last_insert_id')
        return None
