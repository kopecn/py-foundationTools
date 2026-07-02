"""Tier-2 shared abstraction for full 6-DOF spatial poses.

See ``.claude/specs/mathTypeTiers.md``. A pose is a Cartesian position composed
with a quaternion orientation. :class:`SpatialPoseABC` is the shared accessor +
serialization contract (inherited by the codegen ``SpatialPoseType``); the math
contract is in :mod:`foundationTypes.mathTypes.spatialPoseMathLike`.
"""

from abc import ABC, abstractmethod
from typing import Any

from foundationTypes.dataModelHelper import DataModelHelper
from foundationTypes.mathTypes.positionABC import PositionABC
from foundationTypes.mathTypes.quaternionABC import QuaternionABC


class SpatialPoseABC(ABC, DataModelHelper):
    """Shared abstraction for a 6-DOF pose (position + orientation)."""

    @property
    @abstractmethod
    def position(self) -> PositionABC:
        """The Cartesian position component of the pose."""

    @property
    @abstractmethod
    def orientation(self) -> QuaternionABC:
        """The quaternion orientation component of the pose."""

    def to_dict(self) -> dict[str, Any]:
        return {
            "position": self.position.to_dict(),
            "orientation": self.orientation.to_dict(),
        }

    @classmethod
    @abstractmethod
    def from_dict(cls, obj: Any) -> "SpatialPoseABC":
        """Construct from a ``{"position", "orientation"}`` dict."""
