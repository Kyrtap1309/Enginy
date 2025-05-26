from collections.abc import Callable
from enum import Enum
from typing import Any

from enginy.engine_parts.combustor import Combustor, CombustorData
from enginy.engine_parts.compressor import Compressor, CompressorData
from enginy.engine_parts.engine_part import EnginePart as BaseEnginePart
from enginy.engine_parts.inlet import Inlet, InletData
from enginy.engine_parts.turbine import Turbine, TurbineData


class EnginePartType(Enum):
    INLET = "Inlet"
    COMPRESSOR = "Compressor"
    COMBUSTOR = "Combustor"
    TURBINE = "Turbine"


AVAILABLE_PARTS = [e.value for e in EnginePartType]

CLASS_MAP: dict[str, Callable[..., BaseEnginePart]] = {
    "Inlet": Inlet,
    "Compressor": Compressor,
    "Combustor": Combustor,
    "Turbine": Turbine,
}

DATA_CLASS_MAP: dict[str, type] = {
    "Inlet": InletData,
    "Compressor": CompressorData,
    "Combustor": CombustorData,
    "Turbine": TurbineData,
}

PART_ICONS: dict[str, str] = {
    "Inlet": "fas fa-sign-in-alt",
    "Compressor": "fas fa-compress-arrows-alt",
    "Combustor": "fas fa-fire",
    "Turbine": "fas fa-fan",
}


def get_available_parts_with_icons() -> list[dict[str, str]]:
    """Return list of available parts with their icons"""
    return [
        {"name": part, "icon": PART_ICONS.get(part, "fas fa-cog")}
        for part in AVAILABLE_PARTS
    ]


def extract_part_data(part_obj: BaseEnginePart) -> dict[str, Any]:
    """
    Extract data from the part object based on its type.

    Args:
        part_obj: Engine part object.

    Returns:
        Dictionary containing part data.
    """
    part_class_name = part_obj.__class__.__name__.lower()
    data_attr_name = f"{part_class_name}_data"

    if hasattr(part_obj, data_attr_name):
        data_obj = getattr(part_obj, data_attr_name)
        result: dict[str, Any] = vars(data_obj)
        return result
    return {}
