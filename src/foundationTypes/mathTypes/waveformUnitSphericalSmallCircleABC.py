"""Tier-2 shared abstraction for uniformly-sampled unit-spherical-small-circle waveforms.

See ``.claude/specs/mathTypeTiers.md``. A uniformly-sampled time series of
``UnitSphericalSmallCircle`` samples anchored at ``t0`` with sample interval ``dt``.
"""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from foundationTypes.dataModelHelper import DataModelHelper
from foundationTypes.mathTypes.precisionTimeIntervalABC import PrecisionTimeIntervalABC
from foundationTypes.mathTypes.precisionTimestampABC import PrecisionTimestampABC
from foundationTypes.mathTypes.unitSphericalSmallCircleABC import UnitSphericalSmallCircleABC


class WaveformUnitSphericalSmallCircleABC(ABC, DataModelHelper):
    """Shared abstraction for a uniformly-sampled small-circle time series."""

    @property
    @abstractmethod
    def small_circles(self) -> Sequence[UnitSphericalSmallCircleABC]:
        """The uniformly-sampled small-circle values, in chronological order."""

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
            "smallCircles": [c.to_dict() for c in self.small_circles],
            "t0": self.t0.to_dict(),
            "dt": self.dt.to_dict(),
        }

    @classmethod
    @abstractmethod
    def from_dict(cls, obj: Any) -> "WaveformUnitSphericalSmallCircleABC":
        """Construct from a ``{"smallCircles", "t0", "dt"}`` dict."""
