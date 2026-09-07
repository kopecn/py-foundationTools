"""Structural interfaces for arcs and small circles on a unit sphere.

See ``.claude/specs/mathTypeTiers.md``. :class:`UnitSphericalArcABC` and
:class:`UnitSphericalSmallCircleABC` are structural accessor + serialization
protocols. Code-generated carriers satisfy them without inheritance. Angles
follow ISO 80000-2:2019 physics convention. Spherical operations belong in
higher-level implementations, not here.
"""

from abc import abstractmethod
from typing import Any, Protocol


class UnitSphericalArcABC(Protocol):
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

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Serialize this arc."""

    @classmethod
    @abstractmethod
    def from_dict(cls, obj: Any) -> "UnitSphericalArcABC":
        """Construct from an arc dict (camelCase wire keys)."""


class UnitSphericalSmallCircleABC(Protocol):
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

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Serialize this small circle."""

    @classmethod
    @abstractmethod
    def from_dict(cls, obj: Any) -> "UnitSphericalSmallCircleABC":
        """Construct from a small-circle dict (camelCase wire keys)."""
