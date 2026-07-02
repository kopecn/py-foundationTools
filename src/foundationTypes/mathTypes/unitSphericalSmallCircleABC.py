"""Tier-2 shared abstraction for small circles on a unit sphere.

See ``.claude/specs/mathTypeTiers.md``. :class:`UnitSphericalSmallCircleABC` is
the shared accessor + serialization contract (inherited by the codegen
``UnitSphericalSmallCircleType``); the math contract is in
:mod:`foundationTypes.mathTypes.unitSphericalSmallCircleMathLike`.
"""

from abc import ABC, abstractmethod
from typing import Any

from foundationTypes.dataModelHelper import DataModelHelper


class UnitSphericalSmallCircleABC(ABC, DataModelHelper):
    """Shared abstraction for a unit-sphere small circle.

    A small circle is the sphere intersected with a plane not through its
    center: a circular path at a constant angular distance from a reference
    point. Angles follow ISO 80000-2:2019 physics convention.
    """

    @property
    @abstractmethod
    def azimuth(self) -> float:
        """Azimuthal angle in radians (0 to 2*pi)."""

    @property
    @abstractmethod
    def polar(self) -> float:
        """Polar angle (colatitude) in radians (0 to pi), from the +z axis."""

    @property
    @abstractmethod
    def radius_angle(self) -> float:
        """Angular radius of the small circle in radians."""

    def to_dict(self) -> dict[str, Any]:
        return {
            "azimuth": self.azimuth,
            "polar": self.polar,
            "radiusAngle": self.radius_angle,
        }

    @classmethod
    @abstractmethod
    def from_dict(cls, obj: Any) -> "UnitSphericalSmallCircleABC":
        """Construct from a small-circle dict (camelCase wire keys)."""
