"""Tier-2 shared abstraction for uniformly-sampled 6-DOF pose waveforms.

See ``.claude/specs/mathTypeTiers.md``. A spatial-pose waveform is a
uniformly-sampled time series of 6-DOF poses represented as *parallel* position
and quaternion arrays (not an array of poses), anchored at ``t0`` with sample
interval ``dt``.
"""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from foundationTypes.dataModelHelper import DataModelHelper
from foundationTypes.mathTypes.positionABC import PositionABC
from foundationTypes.mathTypes.precisionTimeIntervalABC import PrecisionTimeIntervalABC
from foundationTypes.mathTypes.precisionTimestampABC import PrecisionTimestampABC
from foundationTypes.mathTypes.quaternionABC import QuaternionABC


class WaveformSpatialABC(ABC, DataModelHelper):
    """Shared abstraction for a uniformly-sampled 6-DOF pose time series.

    ``positions`` and ``quaternions`` are parallel (same length, same sample
    index): sample ``i`` is the pose ``(positions[i], quaternions[i])``.
    """

    @property
    @abstractmethod
    def positions(self) -> Sequence[PositionABC]:
        """The sampled position values, in chronological order (parallel to quaternions)."""

    @property
    @abstractmethod
    def quaternions(self) -> Sequence[QuaternionABC]:
        """The sampled orientation values, in chronological order (parallel to positions)."""

    @property
    @abstractmethod
    def t0(self) -> PrecisionTimestampABC:
        """The timestamp of the first sample."""

    @property
    @abstractmethod
    def dt(self) -> PrecisionTimeIntervalABC:
        """The fixed interval between consecutive samples."""

    def to_dict(self) -> dict[str, Any]:
        return {
            "positions": [p.to_dict() for p in self.positions],
            "quaternions": [q.to_dict() for q in self.quaternions],
            "t0": self.t0.to_dict(),
            "dt": self.dt.to_dict(),
        }

    @classmethod
    @abstractmethod
    def from_dict(cls, obj: Any) -> "WaveformSpatialABC":
        """Construct from a ``{"positions", "quaternions", "t0", "dt"}`` dict."""
