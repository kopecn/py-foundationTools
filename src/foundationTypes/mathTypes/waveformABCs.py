"""Tier-2 shared abstractions for uniformly-sampled waveforms.

See ``.claude/specs/mathTypeTiers.md``. Each ``XxxxWaveformABC`` (or
``WaveformXxxxABC``) below is a shared accessor + serialization contract for a
uniformly-sampled time series anchored at ``t0`` with sample interval ``dt``
(inherited by the matching codegen ``XxxxWaveformType``). :class:`PositionWaveformABC`
and :class:`QuaternionWaveformABC` are the translation-only and rotation-only
projections of an SE(3) trajectory (see :mod:`foundationTypes.mathTypes.spatialABCs`);
:class:`WaveformSpatialABC` carries both as parallel arrays. The math contracts are
in the sibling ``XxxxMathLike`` modules.
"""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from foundationTypes.data_model_helper import DataModelHelper
from foundationTypes.mathTypes.precisionTimeABC import (
    PrecisionTimeIntervalABC,
    PrecisionTimestampABC,
)
from foundationTypes.mathTypes.spatialABCs import PositionABC, QuaternionABC
from foundationTypes.mathTypes.unitSphericalArcABC import UnitSphericalArcABC
from foundationTypes.mathTypes.unitSphericalSmallCircleABC import UnitSphericalSmallCircleABC


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
