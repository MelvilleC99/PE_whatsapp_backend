"""
Firebase client for database connection
"""
import firebase_admin
from firebase_admin import credentials, firestore
from loguru import logger

from src.config import settings


class FirebaseClient:
    """Low-level Firebase connection client"""
    
    _instance = None
    _db = None
    
    def __new__(cls):
        """Singleton pattern to ensure single Firebase connection"""
        if cls._instance is None:
            cls._instance = super(FirebaseClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize Firebase connection"""
        try:
            # Check if already initialized
            firebase_admin.get_app()
            logger.info("Firebase already initialized")
        except ValueError:
            # Initialize Firebase
            cred = credentials.Certificate(settings.firebase_credentials_dict)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase initialized successfully")
        
        self._db = firestore.client()
    
    @property
    def db(self):
        """Get Firestore database client"""
        return self._db
    
    def get_collection(self, collection_name: str):
        """
        Get a Firestore collection reference
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Collection reference
        """
        return self._db.collection(collection_name)
