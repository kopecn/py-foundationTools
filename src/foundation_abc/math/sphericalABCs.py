"""Tier-2 shared abstractions for arcs and small circles on a unit sphere.

See ``.claude/specs/mathTypeTiers.md``. :class:`UnitSphericalArcABC` and
:class:`UnitSphericalSmallCircleABC` are the shared accessor + serialization
contracts (inherited by the codegen ``UnitSphericalArcType`` /
``UnitSphericalSmallCircleType``). Angles follow ISO 80000-2:2019 physics
convention. The math contracts are in
:mod:`foundationTypes.mathTypes.unitSphericalArcMathLike` and
:mod:`foundationTypes.mathTypes.unitSphericalSmallCircleMathLike`.
"""

from abc import ABC, abstractmethod
from typing import Any


class UnitSphericalArcABC(ABC):
    """Shared abstraction for a unit-sphere arc.

    An arc is a spherical reference point projected along the unit circle for a
    given arc length. Angles follow ISO 80000-2:2019 physics convention.
    """

    @property
    @abstractmethod
    def azimuth(self) -> float:
        """Azimuthal angle in radians (0 to 2*pi)."""

    @property
    @abstractmethod
    def arc_length(self) -> float:
        """The arc length in radians (-2*pi to 2*pi)."""

    @property
    @abstractmethod
    def orient(self) -> float:
        """Rotated orientation about the origin->start vector, in radians (-pi to pi)."""

    @property
    @abstractmethod
    def polar(self) -> float:
        """Polar angle (colatitude) in radians (0 to pi), from the +z axis."""

    def to_dict(self) -> dict[str, Any]:
        return {
            "azimuth": self.azimuth,
            "arcLength": self.arc_length,
            "orient": self.orient,
            "polar": self.polar,
        }

    @classmethod
    @abstractmethod
    def from_dict(cls, obj: Any) -> "UnitSphericalArcABC":
        """Construct from an arc dict (camelCase wire keys)."""


class UnitSphericalSmallCircleABC(ABC):
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
