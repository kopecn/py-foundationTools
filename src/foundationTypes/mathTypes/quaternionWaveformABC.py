"""Tier-2 shared abstraction for uniformly-sampled quaternion waveforms.

See ``.claude/specs/mathTypeTiers.md``. A quaternion waveform is a
uniformly-sampled time series of unit quaternions anchored at ``t0`` with sample
interval ``dt``.
"""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from foundationTypes.dataModelHelper import DataModelHelper
from foundationTypes.mathTypes.precisionTimeIntervalABC import PrecisionTimeIntervalABC
from foundationTypes.mathTypes.precisionTimestampABC import PrecisionTimestampABC
from foundationTypes.mathTypes.quaternionABC import QuaternionABC


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
