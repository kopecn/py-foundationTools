"""Tier-2 shared abstraction for attosecond-precision absolute timestamps.

See ``.claude/specs/mathTypeTiers.md``. :class:`PrecisionTimestampABC` is the
shared accessor + serialization contract (inherited by the codegen
``PrecisionTimestampType``); the math contract is in
:mod:`foundationTypes.mathTypes.precisionTimestampMathLike`.
"""

from abc import ABC, abstractmethod
from typing import Any

from foundationTypes.dataModelHelper import DataModelHelper
from foundationTypes.mathTypes.mathEnums import NumericSign, ReferenceFrame, Timescale


class PrecisionTimestampABC(ABC, DataModelHelper):
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

    @property
    def is_epoch(self) -> bool:
        """Whether this timestamp is exactly the Unix epoch."""
        return self.sign == NumericSign.ZERO

    @property
    def is_after_epoch(self) -> bool:
        """Whether this timestamp is strictly after the Unix epoch."""
        return self.sign == NumericSign.POSITIVE

    @property
    def is_before_epoch(self) -> bool:
        """Whether this timestamp is strictly before the Unix epoch."""
        return self.sign == NumericSign.NEGATIVE

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "attoseconds": self.attoseconds,
            "seconds": self.seconds,
            "sign": self.sign.value,
        }
        if self.reference_frame is not None:
            result["referenceFrame"] = self.reference_frame.value
        if self.timescale is not None:
            result["timescale"] = self.timescale.value
        if self.uncertainty is not None:
            result["uncertainty"] = self.uncertainty
        return result

    @classmethod
    @abstractmethod
    def from_dict(cls, obj: Any) -> "PrecisionTimestampABC":
        """Construct from a timestamp dict (camelCase wire keys)."""
