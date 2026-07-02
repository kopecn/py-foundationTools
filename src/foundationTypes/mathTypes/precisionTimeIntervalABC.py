"""Tier-2 shared abstraction for attosecond-precision time intervals.

See ``.claude/specs/mathTypeTiers.md``. :class:`PrecisionTimeIntervalABC` is the
shared accessor + serialization contract (inherited by the codegen
``PrecisionTimeIntervalType``); the math contract is in
:mod:`foundationTypes.mathTypes.precisionTimeIntervalMathLike`.
"""

from abc import ABC, abstractmethod
from typing import Any

from foundationTypes.dataModelHelper import DataModelHelper
from foundationTypes.mathTypes.mathEnums import NumericSign

#: Number of attoseconds (10^-18 s) in one second.
ATTOSECONDS_PER_SECOND = 1_000_000_000_000_000_000


class PrecisionTimeIntervalABC(ABC, DataModelHelper):
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

    @property
    def is_zero(self) -> bool:
        """Whether this interval is exactly zero."""
        return self.sign == NumericSign.ZERO

    @property
    def is_positive(self) -> bool:
        """Whether this interval is strictly positive."""
        return self.sign == NumericSign.POSITIVE

    @property
    def is_negative(self) -> bool:
        """Whether this interval is strictly negative."""
        return self.sign == NumericSign.NEGATIVE

    def to_dict(self) -> dict[str, Any]:
        return {
            "attoseconds": self.attoseconds,
            "seconds": self.seconds,
            "sign": self.sign.value,
        }

    @classmethod
    @abstractmethod
    def from_dict(cls, obj: Any) -> "PrecisionTimeIntervalABC":
        """Construct from a ``{"attoseconds", "seconds", "sign"}`` dict."""
