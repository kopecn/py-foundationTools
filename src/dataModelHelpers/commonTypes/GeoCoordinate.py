from dataclasses import dataclass
from dataModelHelpers.dataModelHelper import DataModelHelper
from typing import Optional, Any, TypeVar, Type, cast


T = TypeVar("T")


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def to_float(x: Any) -> float:
    assert isinstance(x, (int, float))
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


@dataclass
class GeoCoordinate(DataModelHelper):
    """A geographical coordinate"""

    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @staticmethod
    def from_dict(obj: Any) -> "GeoCoordinate":
        assert isinstance(obj, dict)
        latitude = from_union([from_float, from_none], obj.get("latitude"))
        longitude = from_union([from_float, from_none], obj.get("longitude"))
        return GeoCoordinate(latitude, longitude)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.latitude is not None:
            result["latitude"] = from_union([to_float, from_none], self.latitude)
        if self.longitude is not None:
            result["longitude"] = from_union([to_float, from_none], self.longitude)
        return result


def geo_coordinate_from_dict(s: Any) -> GeoCoordinate:
    return GeoCoordinate.from_dict(s)


def geo_coordinate_to_dict(x: GeoCoordinate) -> Any:
    return to_class(GeoCoordinate, x)
