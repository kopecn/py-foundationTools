"""Structural interfaces for attosecond-precision intervals and timestamps.

See ``.claude/specs/mathTypeTiers.md``. :class:`PrecisionTimeIntervalABC` and
:class:`PrecisionTimestampABC` are structural accessor + serialization protocols.
Code-generated carriers satisfy them without inheritance. Time arithmetic belongs
in higher-level implementations, not here.
"""

from abc import abstractmethod
from typing import Any, Protocol

from foundation_abc.math.mathEnums import NumericSign, ReferenceFrame, Timescale

#: Number of attoseconds (10^-18 s) in one second.
ATTOSECONDS_PER_SECOND = 1_000_000_000_000_000_000


class PrecisionTimeIntervalABC(Protocol):
    """Shared abstraction for an attosecond-precision time interval.

    Carries an unsigned ``(seconds, attoseconds)`` magnitude and an explicit
    :class:`NumericSign`, avoiding floating-point precision loss across both very
    large and very small spans.
    """

    @property
    @abstractmethod
    def attoseconds(self) -> int:
        """The sub-second component in attoseconds (0 .. 999_999_999_999_999_999)."""

    @property
    @abstractmethod
    def seconds(self) -> int:
        """The whole-seconds component of the interval (unsigned)."""

    @property
    @abstractmethod
    def sign(self) -> NumericSign:
        """The sign of the time interval."""

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Serialize this interval."""

    @classmethod
    @abstractmethod
    def from_dict(cls, obj: Any) -> "PrecisionTimeIntervalABC":
        """Construct from a ``{"attoseconds", "seconds", "sign"}`` dict."""


class PrecisionTimestampABC(Protocol):
    """Shared abstraction for an attosecond-precision absolute timestamp.

    Represents an offset from the Unix epoch (1970-01-01 00:00:00 UTC) as an
    unsigned ``(seconds, attoseconds)`` magnitude with explicit
    :class:`NumericSign` (positive after epoch, negative before). Optionally
    carries a :class:`Timescale`, :class:`ReferenceFrame`, and a measurement
    ``uncertainty`` in attoseconds.
    """

    @property
    @abstractmethod
    def attoseconds(self) -> int:
        """The sub-second component in attoseconds (0 .. 999_999_999_999_999_999)."""

    @property
    @abstractmethod
    def seconds(self) -> int:
        """The whole-seconds component of the timestamp (unsigned)."""

    @property
    @abstractmethod
    def sign(self) -> NumericSign:
        """The sign of the timestamp relative to the Unix epoch."""

    @property
    @abstractmethod
    def reference_frame(self) -> ReferenceFrame | None:
        """Optional spatial reference frame for the timestamp."""

    @property
    @abstractmethod
    def timescale(self) -> Timescale | None:
        """Optional timescale of the timestamp."""

    @property
    @abstractmethod
    def uncertainty(self) -> int | None:
        """Optional measurement uncertainty, in attoseconds."""

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Serialize this timestamp."""

    @classmethod
    @abstractmethod
    def from_dict(cls, obj: Any) -> "PrecisionTimestampABC":
        """Construct from a timestamp dict (camelCase wire keys)."""
