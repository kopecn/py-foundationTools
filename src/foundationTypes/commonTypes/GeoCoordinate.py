# =============================================================================
# AUTO-GENERATED FILE — DO NOT EDIT
# Generated from JSON Schema via quicktype. Any manual edits will be
# overwritten the next time codegen runs (make codegen-all).
# To modify, update the source schema in schema/schemas/ and re-run codegen.
# =============================================================================

from dataclasses import dataclass
from typing import Any, TypeVar

from foundationTypes.data_model_helper import (
    DataModelHelper,
    from_float,
    to_class,
    to_float,
)

T = TypeVar("T")


@dataclass
class GeoCoordinate(DataModelHelper):
    """A geographical coordinate"""

    latitude: float
    longitude: float

    @classmethod
    def from_dict(cls, obj: Any) -> "GeoCoordinate":
        assert isinstance(obj, dict)
        latitude = from_float(obj.get("latitude"))
        longitude = from_float(obj.get("longitude"))
        return GeoCoordinate(latitude, longitude)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["latitude"] = to_float(self.latitude)
        result["longitude"] = to_float(self.longitude)
        return result


def geo_coordinate_from_dict(s: Any) -> GeoCoordinate:
    return GeoCoordinate.from_dict(s)


def geo_coordinate_to_dict(x: GeoCoordinate) -> Any:
    return to_class(GeoCoordinate, x)
