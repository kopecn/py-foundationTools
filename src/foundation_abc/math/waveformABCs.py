"""Structural interfaces for uniformly-sampled waveforms.

See ``.claude/specs/mathTypeTiers.md``. Each ``XxxxWaveformABC`` (or
``WaveformXxxxABC``) below is a structural accessor + serialization protocol for a
uniformly-sampled time series anchored at ``t0`` with sample interval ``dt``
(code-generated carriers conform without inheritance). :class:`PositionWaveformABC`
and :class:`QuaternionWaveformABC` are the translation-only and rotation-only
projections of an SE(3) trajectory (see :mod:`foundation_abc.math.spatialABCs`);
:class:`WaveformSpatialABC` carries both as parallel arrays.
"""

from abc import abstractmethod
from collections.abc import Sequence
from typing import Any, Protocol

from foundation_abc.math.precisionTimeABC import (
    PrecisionTimeIntervalABC,
    PrecisionTimestampABC,
)
from foundation_abc.math.spatialABCs import PositionABC, QuaternionABC
from foundation_abc.math.sphericalABCs import (
    UnitSphericalArcABC,
    UnitSphericalSmallCircleABC,
)


class Waveform1dABC(Protocol):
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

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Serialize this waveform."""

    @classmethod
    @abstractmethod
    def from_dict(cls, obj: Any) -> "Waveform1dABC":
        """Construct from a ``{"waveform", "t0", "dt"}`` dict."""


class PositionWaveformABC(Protocol):
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

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Serialize this waveform."""

    @classmethod
    @abstractmethod
    def from_dict(cls, obj: Any) -> "PositionWaveformABC":
        """Construct from a ``{"positions", "t0", "dt"}`` dict."""


class QuaternionWaveformABC(Protocol):
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

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Serialize this waveform."""

    @classmethod
    @abstractmethod
    def from_dict(cls, obj: Any) -> "QuaternionWaveformABC":
        """Construct from a ``{"quaternions", "t0", "dt"}`` dict."""


class WaveformSpatialABC(Protocol):
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

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Serialize this waveform."""

    @classmethod
    @abstractmethod
    def from_dict(cls, obj: Any) -> "WaveformSpatialABC":
        """Construct from a ``{"positions", "quaternions", "t0", "dt"}`` dict."""


class WaveformUnitSphericalArcABC(Protocol):
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

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Serialize this waveform."""

    @classmethod
    @abstractmethod
    def from_dict(cls, obj: Any) -> "WaveformUnitSphericalArcABC":
        """Construct from an ``{"arcs", "t0", "dt"}`` dict."""


class WaveformUnitSphericalSmallCircleABC(Protocol):
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

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Serialize this waveform."""

    @classmethod
    @abstractmethod
    def from_dict(cls, obj: Any) -> "WaveformUnitSphericalSmallCircleABC":
        """Construct from a ``{"smallCircles", "t0", "dt"}`` dict."""
