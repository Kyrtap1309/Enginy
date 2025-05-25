from datetime import datetime
from typing import Any

from bson import ObjectId

from enginy.database import get_db
from enginy.engine_parts.engine_part import EnginePart as BaseEnginePart
from enginy.models import EnginePart


class EnginePartRepository:
    """Repository for engine part CRUD operations"""

    @staticmethod
    def save_part(part_dict: dict[str, Any], user_id: str | None = None) -> str:
        """
        Save an engine part to the database

        Args:
            part_dict: Dictionary containing part data
            user_id: Optional user ID to associate with the part

        Returns:
            ID of the saved part
        """
        db = get_db()
        if db is None:
            raise RuntimeError("Database not available")
        mongo_doc = EnginePart.to_mongodb_format(part_dict, user_id)
        result = db.engine_parts.insert_one(mongo_doc)
        return str(result.inserted_id)

    @staticmethod
    def get_part(part_id: str) -> dict[str, Any] | None:
        """
        Get an engine part by ID

        Args:
            part_id: ID of the part to retrieve

        Returns:
            Dictionary containing part data
        """
        db = get_db()
        if db is None:
            return None
        mongo_doc = db.engine_parts.find_one({"_id": ObjectId(part_id)})
        if mongo_doc:
            return EnginePart.from_mongodb_format(mongo_doc)
        return None

    @staticmethod
    def get_part_with_dependencies(
        part_id: str,
    ) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
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
    def get_part_object(part_id: str) -> BaseEnginePart | None:
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

        dep_objects = {}

        for dep in direct_dependencies:
            dep_part_id = dep["id"]
            dep_type = dep["name"].lower()

            dep_object = EnginePartRepository.get_part_object(dep_part_id)
            if dep_object:
                dep_objects[dep_type] = dep_object

        return EnginePart.reconstruct_part_object(part, dep_objects)

    @staticmethod
    def get_all_parts(user_id: str | None = None) -> list[dict[str, Any]]:
        """
        Get all engine parts, optionally filtered by user

        Args:
            user_id: Optional user ID to filter by

        Returns:
            List of dictionaries containing part data
        """
        db = get_db()
        if db is None:
            return []
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
        if db is None:
            return False
        result = db.engine_parts.delete_one({"_id": ObjectId(part_id)})
        return result.deleted_count > 0

    @staticmethod
    def get_parts_by_type(
        part_type: str, user_id: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Get all parts of a specific type, optionally filtered by user

        Args:
            part_type: Type of parts to retrieve
            user_id: Optional user ID to filter by

        Returns:
            List of dictionaries containing part data
        """
        db = get_db()
        if db is None:
            return []
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
            if db is None:
                return False
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
    def get_analysis_result(part_id: str) -> str | None:
        """
        Get the analysis result for a part by ID

        Args:
            part_id: ID of the part

        Returns:
            JSON-encoded analysis data or None
        """
        db = get_db()
        if db is None:
            return None
        part = db.engine_parts.find_one({"_id": ObjectId(part_id)})
        if part and "analysis_result" in part:
            analysis_result = part["analysis_result"]
            return str(analysis_result) if analysis_result is not None else None
        return None
