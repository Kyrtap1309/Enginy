from typing import List, Dict, Any, Optional
from bson import ObjectId
from .database import get_db
from .models import EnginePart

class EnginePartRepository:
    """Repository for engine part CRUD operations"""

    @staticmethod
    def save_part(part_dict: Dict[str, Any], user_id: Optional[str] = None) -> str:
        """
        Save an engine part to the database

        Args:
            part_dict: Dictionary containing part data
            user_id: Optional user ID to associate with the part

        Returns:
            ID of the saved part
        """
        db = get_db()
        mongo_doc = EnginePart.to_mongodb_format(part_dict, user_id)
        result = db.engine_parts.insert_one(mongo_doc)
        return str(result.inserted_id)
    
    @staticmethod
    def get_part(part_id: str) -> Dict[str, Any]:
        """
        Get an engine part by its ID

        Args:
            part_id: ID of the part

        Returns:
            Dictionary containing the part data
        """
        db = get_db()
        mongo_doc = db.engine_parts.find_one({'_id': ObjectId(part_id)})
        if mongo_doc:
            return EnginePart.from_mongodb_format(mongo_doc)
        return None
    
    @staticmethod
    def get_all_parts(user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all engine parts, optionally filtered by user

        Args:
            user_id: Optional user ID to filter parts

        Returns:
            List of dictionaries containing part data
        """
        db = get_db()
        query = {'user_id': user_id} if user_id else {}
        cursor = db.engine_parts.find(query).sort('created_at', -1)
        return [EnginePart.from_mongodb_format(doc) for doc in cursor]
    
    @staticmethod
    def delete_part(part_id: str) -> bool:
        """
        Get an engine part by ID
        
        Args:
            part_id: ID of the part to retrieve
            
        Returns:
            Dictionary containing part data
        """
        db = get_db()
        result = db.engine_parts.delete_one({'_id': ObjectId(part_id)})
        return result.deleted_count > 0
    
    @staticmethod
    def get_parts_by_type(part_type: str, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all engine parts of a specific type, optionally filtered by user

        Args:
            part_type: Type of part to filter
            user_id: Optional user ID to filter parts

        Returns:
            List of dictionaries containing part data
        """
        db = get_db()
        query = {'name': part_type}
        if user_id:
            query['user_id'] = user_id
        cursor = db.engine_parts.find(query).sort('created_at', -1)
        return [EnginePart.from_mongodb_format(doc) for doc in cursor] 