"""Tier-2 shared abstraction for uniformly-sampled 1D scalar waveforms.

See ``.claude/specs/mathTypeTiers.md``. A scalar waveform is a uniformly-sampled
1D signal anchored at ``t0`` with sample interval ``dt``.
"""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from foundationTypes.data_model_helper import DataModelHelper
from foundationTypes.mathTypes.precisionTimeABC import (
    PrecisionTimeIntervalABC,
    PrecisionTimestampABC,
)


class Waveform1dABC(ABC, DataModelHelper):
    """Shared abstraction for a uniformly-sampled 1D scalar time series."""

    @property
    @abstractmethod
    def waveform(self) -> Sequence[float]:
        """The uniformly-sampled scalar values, in chronological order."""

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
            "waveform": list(self.waveform),
            "t0": self.t0.to_dict(),
            "dt": self.dt.to_dict(),
        }

    @classmethod
    @abstractmethod
    def from_dict(cls, obj: Any) -> "Waveform1dABC":
        """Construct from a ``{"waveform", "t0", "dt"}`` dict."""
