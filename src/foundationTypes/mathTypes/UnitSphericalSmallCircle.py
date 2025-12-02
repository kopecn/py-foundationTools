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
class UnitSphericalSmallCircle(DataModelHelper):
    """Represents a small circle on a unit sphere in spherical coordinates using physics
    convention.  A small circle is formed by intersecting the sphere with a plane that does
    notpass through the sphere's center, creating a circular path at a constantangular
    distance from a reference point.
    """

    azimuth: float
    """Azimuthal angle in radians (0 to 2*pi).  Represents the longitudinal position around the
    sphere.
    """
    polar: float
    """Polar angle in radians (-pi/2 to pi/2).  Represents the latitudinal position, where 0 is
    the equator,  pi/2 is the north pole, and -pi/2 is the south pole.
    """
    radius_angle: float
    """Angular radius of the small circle in radians.  Represents the angular distance from the
    center point.
    """

    @staticmethod
    def from_dict(obj: Any) -> "UnitSphericalSmallCircle":
        assert isinstance(obj, dict)
        azimuth = from_float(obj.get("azimuth"))
        polar = from_float(obj.get("polar"))
        radius_angle = from_float(obj.get("radiusAngle"))
        return UnitSphericalSmallCircle(azimuth, polar, radius_angle)

    def to_dict(self) -> dict:
        result: dict = {}
        result["azimuth"] = to_float(self.azimuth)
        result["polar"] = to_float(self.polar)
        result["radiusAngle"] = to_float(self.radius_angle)
        return result


def unit_spherical_small_circle_from_dict(s: Any) -> UnitSphericalSmallCircle:
    return UnitSphericalSmallCircle.from_dict(s)


def unit_spherical_small_circle_to_dict(x: UnitSphericalSmallCircle) -> Any:
    return to_class(UnitSphericalSmallCircle, x)
