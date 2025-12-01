"""
Data model for unit spherical small circles.

This module provides structured data models for representing small circles
on a unit sphere using spherical coordinates (azimuth, polar angle, and radius).
"""

from dataclasses import dataclass
from typing import Any

from foundationDataModelHelpers.dataModelHelper import DataModelHelper


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def to_float(x: Any) -> float:
    assert isinstance(x, (int, float))
    return x


@dataclass
class UnitSphericalSmallCircle(DataModelHelper):
    """
    Represents a small circle on a unit sphere in spherical coordinates.

    A small circle is formed by intersecting the sphere with a plane that does not
    pass through the sphere's center, creating a circular path at a constant
    angular distance from a reference point.

    Attributes:
    -----------
    azimuth : float
        Azimuthal angle in radians (0 to 2*pi).
        Represents the longitudinal position around the sphere.
    polar : float
        Polar angle in radians (-pi/2 to pi/2).
        Represents the latitudinal position, where 0 is the equator,
        pi/2 is the north pole, and -pi/2 is the south pole.
    radius : float
        Angular radius of the small circle in radians.
        Represents the angular distance from the center point.
    """

    azimuth: float
    polar: float
    radius: float

    def to_array(self):
        """Convert to array format [azimuth, polar, radius]."""
        return [self.azimuth, self.polar, self.radius]

    @staticmethod
    def from_dict(obj: Any) -> "UnitSphericalSmallCircle":
        assert isinstance(obj, dict)
        azimuth = from_float(obj.get("azimuth"))
        polar = from_float(obj.get("polar"))
        radius = from_float(obj.get("radius"))
        return UnitSphericalSmallCircle(azimuth, polar, radius)

    def to_dict(self) -> dict:
        result: dict = {}
        result["azimuth"] = to_float(self.azimuth)
        result["polar"] = to_float(self.polar)
        result["radius"] = to_float(self.radius)
        return result
