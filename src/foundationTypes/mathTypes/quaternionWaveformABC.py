"""Tier-2 shared abstraction for uniformly-sampled quaternion waveforms.

See ``.claude/specs/mathTypeTiers.md``. A quaternion waveform is a
uniformly-sampled time series of unit quaternions anchored at ``t0`` with sample
interval ``dt`` — the rotation-only projection of an SE(3) trajectory (see
:mod:`foundationTypes.mathTypes.spatialABCs`).
"""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from foundationTypes.data_model_helper import DataModelHelper
from foundationTypes.mathTypes.precisionTimeABC import (
    PrecisionTimeIntervalABC,
    PrecisionTimestampABC,
)
from foundationTypes.mathTypes.spatialABCs import QuaternionABC


class QuaternionWaveformABC(ABC, DataModelHelper):
    """Shared abstraction for a uniformly-sampled quaternion time series."""

    @property
    @abstractmethod
    def quaternions(self) -> Sequence[QuaternionABC]:
        """The uniformly-sampled orientation values, in chronological order."""

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
            "quaternions": [q.to_dict() for q in self.quaternions],
            "t0": self.t0.to_dict(),
            "dt": self.dt.to_dict(),
        }

    @classmethod
    @abstractmethod
    def from_dict(cls, obj: Any) -> "QuaternionWaveformABC":
        """Construct from a ``{"quaternions", "t0", "dt"}`` dict."""
