import json
from bson import ObjectId
from datetime import datetime
from typing import Dict, Any, List, Optional

class EnginePart:
    """Model representing an engine part in the database"""

    @staticmethod
    def to_mongodb_format(part_dict: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Convert an engine part dictionary to MongoDB format
        
        Args:
            part_dict: Dictionary containing part data
            user_id: Optional user ID to associate with the part
            
        Returns:
            MongoDB-ready document
        """
        part_obj = part_dict.get('part')
        part_class = part_obj.__class__.__name__


        if hasattr(part_obj, 'inlet_data'):
            part_data = vars(part_obj.inlet_data)
        elif hasattr(part_obj, 'compressor_data'):
            part_data = vars(part_obj.compressor_data)
        elif hasattr(part_obj, 'combustor_data'):
            part_data = vars(part_obj.combustor_data)
        else:
            part_data = {}
        
        mongo_doc = {
            'name': part_dict.get('name'),
            'user_part_name': part_dict.get('user_part_name'),
            'part_type': part_class,
            'part_data': part_data,
            'created_at': datetime.now(),
            'dependencies': []
        }

        if user_id:
            mongo_doc['user_id'] = user_id

        return mongo_doc
     
    @staticmethod
    def add_dependency(part_id: str, dependency_id: str) -> None:
        """
        Add a dependency between two parts
        
        Args:
            part_id: ID of the part
            dependency_id: ID of the dependency
        """
        from Enginy.database import get_db
        db = get_db()

        db.engine_parts.update_one(
            {'_id': ObjectId(part_id)},
            {'$push': {'dependencies': ObjectId(dependency_id)}}
        )

    @staticmethod
    def from_mongodb_format(mongo_doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert MongoDB document back to the format expected by the application
        
        This is a placeholder - actual implementation would need to recreate
        the part objects from the stored data
        
        Args:
            mongo_doc: MongoDB document
            
        Returns:
            Dictionary in the format expected by the application
        """

        return {
            'id': str(mongo_doc.get('_id')),
            'name': mongo_doc.get('name'),
            'user_part_name': mongo_doc.get('user_part_name'),
            'part_type': mongo_doc.get('part_type'),
            'created_at': mongo_doc.get('created_at'),
        }
