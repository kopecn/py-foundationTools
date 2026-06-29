# =============================================================================
# AUTO-GENERATED FILE — DO NOT EDIT
# Generated from JSON Schema via quicktype. Any manual edits will be
# overwritten the next time codegen runs (make codegen-all).
# To modify, update the source schema in schema/schemas/ and re-run codegen.
# =============================================================================

from dataclasses import dataclass
from typing import Any, TypeVar

from foundationTypes.dataModelHelper import (
    DataModelHelper,
    from_float,
    to_class,
    to_float,
)

T = TypeVar("T")


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
    """Polar angle (colatitude/zenith angle) in radians (0 to pi), measured from the positive
    z-axis following ISO 80000-2:2019 physics convention. 0 is the north pole (+z axis), pi/2
    is the equator (xy-plane), and pi is the south pole (-z axis).
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

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["azimuth"] = to_float(self.azimuth)
        result["polar"] = to_float(self.polar)
        result["radiusAngle"] = to_float(self.radius_angle)
        return result


def unit_spherical_small_circle_from_dict(s: Any) -> UnitSphericalSmallCircle:
    return UnitSphericalSmallCircle.from_dict(s)


def unit_spherical_small_circle_to_dict(x: UnitSphericalSmallCircle) -> Any:
    return to_class(UnitSphericalSmallCircle, x)
