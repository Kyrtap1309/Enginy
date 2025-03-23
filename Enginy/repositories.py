from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Union
from bson import ObjectId

from Enginy.database import get_db
from Enginy.models import EnginePart
from Enginy.engine_parts.engine_part import EnginePart as BaseEnginePart


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
        Get an engine part by ID

        Args:
            part_id: ID of the part to retrieve

        Returns:
            Dictionary containing part data
        """
        db = get_db()
        mongo_doc = db.engine_parts.find_one({"_id": ObjectId(part_id)})
        if mongo_doc:
            return EnginePart.from_mongodb_format(mongo_doc)
        return None

    @staticmethod
    def get_part_with_dependencies(
        part_id: str,
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Get an engine part by ID along with its dependencies

        Args:
            part_id: ID of the part to retrieve

        Returns:
            Tuple containing the part data and list of dependency part data
        """
        part = EnginePartRepository.get_part(part_id)
        if not part:
            return None, []

        dependencies = []
        for dep_id in part.get("dependencies", []):
            dep = EnginePartRepository.get_part(dep_id)
            if dep:
                dependencies.append(dep)

        return part, dependencies

    @staticmethod
    def get_part_object(part_id: str) -> Union[BaseEnginePart, None]:
        """
        Get a fully reconstructed engine part object by ID

        This method retrieves the part data, all its dependencies recursively,
        and reconstructs the complete object hierarchy.

        Args:
            part_id: ID of the part to retrieve

        Returns:
            Reconstructed engine part object
        """
        part, direct_dependencies = EnginePartRepository.get_part_with_dependencies(
            part_id
        )
        if not part:
            return None

        # Build dependency objects recursively
        dep_objects = {}
        dependency_chain = {}

        # Sort dependencies topologically
        for dep in direct_dependencies:
            dep_part_id = dep["id"]
            dep_type = dep["name"].lower()

            # Get the dependency's dependencies recursively
            dep_object = EnginePartRepository.get_part_object(dep_part_id)
            if dep_object:
                dep_objects[dep_type] = dep_object

        # Reconstruct the part object with all dependencies
        return EnginePart.reconstruct_part_object(part, dep_objects)

    @staticmethod
    def get_all_parts(user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all engine parts, optionally filtered by user

        Args:
            user_id: Optional user ID to filter by

        Returns:
            List of dictionaries containing part data
        """
        db = get_db()
        query = {"user_id": user_id} if user_id else {}
        cursor = db.engine_parts.find(query).sort("created_at", -1)
        return [EnginePart.from_mongodb_format(doc) for doc in cursor]

    @staticmethod
    def delete_part(part_id: str) -> bool:
        """
        Delete an engine part by ID

        Args:
            part_id: ID of the part to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        db = get_db()
        result = db.engine_parts.delete_one({"_id": ObjectId(part_id)})
        return result.deleted_count > 0

    @staticmethod
    def get_parts_by_type(
        part_type: str, user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all parts of a specific type, optionally filtered by user

        Args:
            part_type: Type of parts to retrieve
            user_id: Optional user ID to filter by

        Returns:
            List of dictionaries containing part data
        """
        db = get_db()
        query = {"name": part_type}
        if user_id:
            query["user_id"] = user_id
        cursor = db.engine_parts.find(query).sort("created_at", -1)
        return [EnginePart.from_mongodb_format(doc) for doc in cursor]

    @staticmethod
    def save_analysis_result(part_id: str, analysis_data: str) -> bool:
        """
        Save analysis result for a part to the database

        Args:
            part_id: ID of the part
            analysis_data: JSON-encoded analysis data

        Returns:
            True if save was successful
        """
        try:
            db = get_db()
            db.engine_parts.update_one(
                {"_id": ObjectId(part_id)},
                {
                    "$set": {
                        "analysis_result": analysis_data,
                        "analyzed_at": datetime.now(),
                    }
                },
            )
            return True
        except Exception:
            return False

    @staticmethod
    def get_analysis_result(part_id: str) -> Optional[str]:
        """
        Get the analysis result for a part by ID

        Args:
            part_id: ID of the part

        Returns:
            JSON-encoded analysis data or None
        """
        db = get_db()
        part = db.engine_parts.find_one({"_id": ObjectId(part_id)})
        if part and "analysis_result" in part:
            return part["analysis_result"]
        return None
