"""Tier-2 shared abstraction for uniformly-sampled unit-spherical-arc waveforms.

See ``.claude/specs/mathTypeTiers.md``. A uniformly-sampled time series of
``UnitSphericalArc`` samples anchored at ``t0`` with sample interval ``dt``.
"""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from foundationTypes.dataModelHelper import DataModelHelper
from foundationTypes.mathTypes.precisionTimeIntervalABC import PrecisionTimeIntervalABC
from foundationTypes.mathTypes.precisionTimestampABC import PrecisionTimestampABC
from foundationTypes.mathTypes.unitSphericalArcABC import UnitSphericalArcABC


class WaveformUnitSphericalArcABC(ABC, DataModelHelper):
    """Shared abstraction for a uniformly-sampled unit-sphere-arc time series."""

    @property
    @abstractmethod
    def arcs(self) -> Sequence[UnitSphericalArcABC]:
        """The uniformly-sampled arc values, in chronological order."""

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
            "arcs": [a.to_dict() for a in self.arcs],
            "t0": self.t0.to_dict(),
            "dt": self.dt.to_dict(),
        }

    @classmethod
    @abstractmethod
    def from_dict(cls, obj: Any) -> "WaveformUnitSphericalArcABC":
        """Construct from an ``{"arcs", "t0", "dt"}`` dict."""
