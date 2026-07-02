"""Tier-2 shared abstraction for 3D Cartesian position vectors.

See ``.claude/specs/mathTypeTiers.md``. :class:`PositionABC` is the shared
accessor + serialization contract (inherited by the codegen
``PositionVectorType``); the math contract is in
:mod:`foundationTypes.mathTypes.positionVectorMathLike`.
"""

from abc import ABC, abstractmethod
from typing import Any

from foundationTypes.dataModelHelper import DataModelHelper


class PositionABC(ABC, DataModelHelper):
    """Shared, storage-independent abstraction for a 3D position (``x``, ``y``, ``z``)."""

    @property
    @abstractmethod
    def x(self) -> float:
        """The x-axis (first Cartesian) component."""

    @property
    @abstractmethod
    def y(self) -> float:
        """The y-axis (second Cartesian) component."""

    @property
    @abstractmethod
    def z(self) -> float:
        """The z-axis (third Cartesian) component."""

    def to_dict(self) -> dict[str, Any]:
        return {"x": self.x, "y": self.y, "z": self.z}

    @classmethod
    @abstractmethod
    def from_dict(cls, obj: Any) -> "PositionABC":
        """Construct from a ``{"x", "y", "z"}`` dict."""
