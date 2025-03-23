import json
import importlib
from bson import ObjectId
from datetime import datetime
from typing import Dict, Any, List, Optional, Type, Union

from Enginy.engine_parts.engine_part import EnginePart as BaseEnginePart
from Enginy.engine_config import DATA_CLASS_MAP, CLASS_MAP, extract_part_data


class EnginePart:
    """Model representing an engine part in the database"""

    @staticmethod
    def to_mongodb_format(
        part_dict: Dict[str, Any], user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convert an engine part dictionary to MongoDB format

        Args:
            part_dict: Dictionary containing part data
            user_id: Optional user ID to associate with the part

        Returns:
            MongoDB-ready document
        """
        # Extract data from the part object
        part_obj = part_dict.get("part")
        part_class = part_obj.__class__.__name__

        # Store part data based on its type
        part_data = extract_part_data(part_obj)

        # Create MongoDB document
        mongo_doc = {
            "name": part_dict.get("name"),
            "user_part_name": part_dict.get("user_part_name"),
            "part_type": part_class,
            "part_data": part_data,
            "created_at": datetime.now(),
            "dependencies": [],
        }

        if user_id:
            mongo_doc["user_id"] = user_id

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
            {"_id": ObjectId(part_id)}, {"$push": {"dependencies": dependency_id}}
        )

    @staticmethod
    def from_mongodb_format(mongo_doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert MongoDB document to a dictionary format for the application

        Args:
            mongo_doc: MongoDB document

        Returns:
            Dictionary in the format expected by the application
        """
        return {
            "id": str(mongo_doc.get("_id")),
            "name": mongo_doc.get("name"),
            "user_part_name": mongo_doc.get("user_part_name"),
            "part_type": mongo_doc.get("part_type"),
            "created_at": mongo_doc.get("created_at"),
            "part_data": mongo_doc.get("part_data", {}),
            "dependencies": mongo_doc.get("dependencies", []),
        }

    @classmethod
    def reconstruct_part_object(
        cls, part_dict: Dict[str, Any], dependencies: Dict[str, Any] = None
    ) -> Union[BaseEnginePart, None]:
        """
        Reconstruct a part object from stored data and its dependencies

        Args:
            part_dict: Dictionary containing part data
            dependencies: Dictionary of reconstructed dependency objects

        Returns:
            Reconstructed engine part object
        """
        part_type = part_dict.get("part_type")
        part_data = part_dict.get("part_data", {})

        # Get the appropriate data class
        data_class = DATA_CLASS_MAP.get(part_type)
        if not data_class:
            return None

        # Create an instance of the data class with stored data
        data_instance = data_class(**part_data)

        # Get the part class
        part_class = CLASS_MAP.get(part_type)
        if not part_class:
            return None

        # Instantiate the part with its data and dependencies
        if dependencies:
            return part_class(data_instance, **dependencies)
        else:
            return part_class(data_instance)
