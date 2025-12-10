"""
Firebase client for database connection
"""
from typing import Optional, Dict, Any, List
import firebase_admin
from firebase_admin import credentials, firestore
from loguru import logger

from src.config import settings


class FirebaseClient:
    """Low-level Firebase connection client (Singleton)"""
    
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
            firebase_admin.get_app()
            logger.info("Firebase already initialized")
        except ValueError:
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
    
    def get_document(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a document from a collection.
        
        Args:
            collection: Collection name
            doc_id: Document ID
            
        Returns:
            Document data or None if not found
        """
        try:
            doc_ref = self._db.collection(collection).document(doc_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            return None
            
        except Exception as e:
            logger.error(f"Error getting document {collection}/{doc_id}: {e}")
            return None
    
    def set_document(
        self, 
        collection: str, 
        doc_id: str, 
        data: Dict[str, Any],
        merge: bool = True
    ) -> bool:
        """
        Set/update a document in a collection.
        
        Args:
            collection: Collection name
            doc_id: Document ID
            data: Document data
            merge: Whether to merge with existing data
            
        Returns:
            True if successful
        """
        try:
            doc_ref = self._db.collection(collection).document(doc_id)
            doc_ref.set(data, merge=merge)
            return True
            
        except Exception as e:
            logger.error(f"Error setting document {collection}/{doc_id}: {e}")
            return False
    
    def delete_document(self, collection: str, doc_id: str) -> bool:
        """
        Delete a document from a collection.
        
        Args:
            collection: Collection name
            doc_id: Document ID
            
        Returns:
            True if successful
        """
        try:
            doc_ref = self._db.collection(collection).document(doc_id)
            doc_ref.delete()
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {collection}/{doc_id}: {e}")
            return False
    
    def query_collection(
        self,
        collection: str,
        field: str,
        operator: str,
        value: Any,
        limit: int = 100,
        order_by: str = None,
        order_direction: str = "DESCENDING"
    ) -> list:
        """
        Query a collection with a filter.
        
        Args:
            collection: Collection name
            field: Field to filter on
            operator: Comparison operator (==, <, >, <=, >=, !=, in, array-contains)
            value: Value to compare against
            limit: Max documents to return
            order_by: Field to order by (optional)
            order_direction: ASCENDING or DESCENDING
            
        Returns:
            List of document dicts
        """
        try:
            query = self._db.collection(collection).where(field, operator, value)
            
            if order_by:
                direction = (
                    firestore.Query.DESCENDING 
                    if order_direction == "DESCENDING" 
                    else firestore.Query.ASCENDING
                )
                query = query.order_by(order_by, direction=direction)
            
            query = query.limit(limit)
            
            results = []
            for doc in query.stream():
                data = doc.to_dict()
                data['_id'] = doc.id
                results.append(data)
            
            return results
            
        except Exception as e:
            logger.error(f"Error querying collection {collection}: {e}")
            return []
    
    def get_all_documents(self, collection: str, limit: int = 100) -> list:
        """
        Get all documents from a collection.
        
        Args:
            collection: Collection name
            limit: Max documents to return
            
        Returns:
            List of document dicts
        """
        try:
            docs = self._db.collection(collection).limit(limit).stream()
            
            results = []
            for doc in docs:
                data = doc.to_dict()
                data['_id'] = doc.id
                results.append(data)
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting all documents from {collection}: {e}")
            return []
