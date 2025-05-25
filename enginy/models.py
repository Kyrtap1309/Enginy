from datetime import datetime
from typing import Any

from bson import ObjectId

from enginy.engine_config import CLASS_MAP, DATA_CLASS_MAP, extract_part_data
from enginy.engine_parts.engine_part import EnginePart as BaseEnginePart


class EnginePart:
    """Model representing an engine part in the database"""

    @staticmethod
    def to_mongodb_format(
        part_dict: dict[str, Any], user_id: str | None = None
    ) -> dict[str, Any]:
        """
        Convert an engine part dictionary to MongoDB format

        Args:
            part_dict: Dictionary containing part data
            user_id: Optional user ID to associate with the part

        Returns:
            MongoDB-ready document
        """
        part_obj = part_dict.get("part")
        if part_obj is None:
            raise ValueError("Part object is required")

        part_class = part_obj.__class__.__name__

        part_data = extract_part_data(part_obj)

        mongo_doc: dict[str, Any] = {
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
        from enginy.database import get_db

        db = get_db()
        if db is None:
            raise RuntimeError("Database not available")

        db.engine_parts.update_one(
            {"_id": ObjectId(part_id)}, {"$push": {"dependencies": dependency_id}}
        )

    @staticmethod
    def from_mongodb_format(mongo_doc: dict[str, Any]) -> dict[str, Any]:
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
        cls, part_dict: dict[str, Any], dependencies: dict[str, Any] | None = None
    ) -> BaseEnginePart | None:
        """
        Reconstruct a part object from stored data and its dependencies

        Args:
            part_dict: Dictionary containing part data
            dependencies: Dictionary of reconstructed dependency objects

        Returns:
            Reconstructed engine part object
        """
        if dependencies is None:
            dependencies = {}

        part_type = part_dict.get("part_type")
        part_data = part_dict.get("part_data", {})

        if part_type is None:
            return None

        data_class = DATA_CLASS_MAP.get(part_type)
        if not data_class:
            return None

        data_instance = data_class(**part_data)

        part_class = CLASS_MAP.get(part_type)
        if not part_class:
            return None

        if dependencies:
            return part_class(data_instance, **dependencies)
        else:
            return part_class(data_instance)
