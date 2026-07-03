"""Tier-2 shared abstraction for arcs on a unit sphere (physics convention).

See ``.claude/specs/mathTypeTiers.md``. :class:`UnitSphericalArcABC` is the
shared accessor + serialization contract (inherited by the codegen
``UnitSphericalArcType``); the math contract is in
:mod:`foundationTypes.mathTypes.unitSphericalArcMathLike`.
"""

from abc import ABC, abstractmethod
from typing import Any

from foundationTypes.data_model_helper import DataModelHelper


class UnitSphericalArcABC(ABC, DataModelHelper):
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
