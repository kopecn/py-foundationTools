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
    orient: float
    """The rotated orientation about the vector from the sphere's origin through the start point
    in radians (-pi to pi.
    """
    polar: float
    """Polar angle (colatitude/zenith angle) in radians (0 to pi), measured from the positive
    z-axis following ISO 80000-2:2019 physics convention. 0 is the north pole (+z axis), pi/2
    is the equator (xy-plane), and pi is the south pole (-z axis).
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "UnitSphericalArc":
        assert isinstance(obj, dict)
        arc_length = from_float(obj.get("arcLength"))
        azimuth = from_float(obj.get("azimuth"))
        orient = from_float(obj.get("orient"))
        polar = from_float(obj.get("polar"))
        return UnitSphericalArc(arc_length, azimuth, orient, polar)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["arcLength"] = to_float(self.arc_length)
        result["azimuth"] = to_float(self.azimuth)
        result["orient"] = to_float(self.orient)
        result["polar"] = to_float(self.polar)
        return result


def unit_spherical_arc_from_dict(s: Any) -> UnitSphericalArc:
    return UnitSphericalArc.from_dict(s)


def unit_spherical_arc_to_dict(x: UnitSphericalArc) -> Any:
    return to_class(UnitSphericalArc, x)
