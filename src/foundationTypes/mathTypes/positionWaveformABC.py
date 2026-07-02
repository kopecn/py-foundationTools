"""Tier-2 shared abstraction for uniformly-sampled 3D position waveforms.

See ``.claude/specs/mathTypeTiers.md``. A position waveform is a uniformly-sampled
time series of 3D positions anchored at ``t0`` with sample interval ``dt``.
"""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from foundationTypes.dataModelHelper import DataModelHelper
from foundationTypes.mathTypes.positionABC import PositionABC
from foundationTypes.mathTypes.precisionTimeIntervalABC import PrecisionTimeIntervalABC
from foundationTypes.mathTypes.precisionTimestampABC import PrecisionTimestampABC


class PositionWaveformABC(ABC, DataModelHelper):
    """Shared abstraction for a uniformly-sampled 3D position time series."""

    @property
    @abstractmethod
    def positions(self) -> Sequence[PositionABC]:
        """The uniformly-sampled position values, in chronological order."""

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
            "t0": self.t0.to_dict(),
            "dt": self.dt.to_dict(),
        }

    @classmethod
    @abstractmethod
    def from_dict(cls, obj: Any) -> "PositionWaveformABC":
        """Construct from a ``{"positions", "t0", "dt"}`` dict."""
