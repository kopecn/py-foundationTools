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
class UnitSphericalArc(DataModelHelper):
    """Represents an arc on a unit sphere in spherical coordinates using physics convention.
    This arc is formed by a spherical reference point and then projected from that start
    point along the unit circle for the length of the arc in radians.
    """

    arc_length: float
    """The arc length in radians (-2*pi to 2*pi."""

    azimuth: float
    """Azimuthal angle in radians (0 to 2*pi).  Represents the longitudinal position around the
    sphere.
    """
    polar: float
    """Polar angle in radians (-pi/2 to pi/2).  Represents the latitudinal position, where 0 is
    the equator,  pi/2 is the north pole, and -pi/2 is the south pole.
    """

    @staticmethod
    def from_dict(obj: Any) -> "UnitSphericalArc":
        assert isinstance(obj, dict)
        arc_length = from_float(obj.get("arcLength"))
        azimuth = from_float(obj.get("azimuth"))
        polar = from_float(obj.get("polar"))
        return UnitSphericalArc(arc_length, azimuth, polar)

    def to_dict(self) -> dict:
        result: dict = {}
        result["arcLength"] = to_float(self.arc_length)
        result["azimuth"] = to_float(self.azimuth)
        result["polar"] = to_float(self.polar)
        return result


def unit_spherical_arc_from_dict(s: Any) -> UnitSphericalArc:
    return UnitSphericalArc.from_dict(s)


def unit_spherical_arc_to_dict(x: UnitSphericalArc) -> Any:
    return to_class(UnitSphericalArc, x)
