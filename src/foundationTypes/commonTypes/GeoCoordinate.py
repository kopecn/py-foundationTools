from dataclasses import dataclass
from foundationTypes.dataModelHelper import DataModelHelper
from typing import Any, TypeVar, Type, cast


T = TypeVar("T")


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def to_float(x: Any) -> float:
    assert isinstance(x, (int, float))
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


@dataclass
class GeoCoordinate(DataModelHelper):
    """A geographical coordinate"""

    latitude: float
    longitude: float

    @staticmethod
    def from_dict(obj: Any) -> "GeoCoordinate":
        assert isinstance(obj, dict)
        latitude = from_float(obj.get("latitude"))
        longitude = from_float(obj.get("longitude"))
        return GeoCoordinate(latitude, longitude)

    def to_dict(self) -> dict:
        result: dict = {}
        result["latitude"] = to_float(self.latitude)
        result["longitude"] = to_float(self.longitude)
        return result


def geo_coordinate_from_dict(s: Any) -> GeoCoordinate:
    return GeoCoordinate.from_dict(s)


def geo_coordinate_to_dict(x: GeoCoordinate) -> Any:
    return to_class(GeoCoordinate, x)
