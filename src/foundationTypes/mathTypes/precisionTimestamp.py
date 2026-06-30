"""Tier-2 abstract contract for attosecond-precision absolute timestamps.

`PrecisionTimestamp` inherits the generated wire/serialization carrier
``_PrecisionTimestampType`` (fields ``seconds`` / ``attoseconds`` / ``sign`` plus
optional ``timescale`` / ``referenceFrame`` / ``uncertainty``, and ``from_dict`` /
``to_dict`` from :class:`DataModelHelper`) and layers on the *math contract*.

A downstream math repository subclasses this ABC and implements the abstract
members — the Python analogue of the Swift
``Extensions/PrecisionTimestamp/+Arithmetic.swift``, ``+Comparable.swift`` and
``+BaseExtensions.swift``. Timestamp arithmetic is expressed against
:class:`PrecisionTimeInterval`: ``timestamp ± interval -> timestamp`` and
``timestamp - timestamp -> interval``.
"""

from abc import ABC, abstractmethod
from typing import TypeVar

from foundationTypes.mathTypes.PrecisionTime import (
    NumericSign,
    ReferenceFrame,
    Timescale,
    _PrecisionTimestampType,
)
from foundationTypes.mathTypes.precisionTimeInterval import PrecisionTimeInterval

T = TypeVar("T", bound="PrecisionTimestamp")


class PrecisionTimestamp(_PrecisionTimestampType, ABC):
    """Abstract attosecond-precision absolute timestamp.

    Represents an offset from the Unix epoch (1970-01-01 00:00:00 UTC) as an
    unsigned ``(seconds, attoseconds)`` magnitude with explicit
    :class:`NumericSign` (positive after epoch, negative before). Optionally
    carries a :class:`Timescale`, :class:`ReferenceFrame`, and a measurement
    ``uncertainty`` in attoseconds. Concrete subclasses implement the math
    contract below.
    """

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    @classmethod
    def from_components(
        cls: type[T],
        seconds: int,
        attoseconds: int,
        sign: NumericSign,
        timescale: Timescale | None = None,
        reference_frame: ReferenceFrame | None = None,
        uncertainty: int | None = None,
    ) -> T:
        """Build a timestamp from its components.

        Args:
            seconds: Whole-seconds component (unsigned, ``>= 0``).
            attoseconds: Sub-second component (``0 .. 999_999_999_999_999_999``).
            sign: The sign relative to the Unix epoch.
            timescale: Optional timescale of the timestamp.
            reference_frame: Optional spatial reference frame.
            uncertainty: Optional measurement uncertainty, in attoseconds.

        Returns:
            A concrete instance of the calling subclass.
        """
        return cls(
            attoseconds=attoseconds,
            seconds=seconds,
            sign=sign,
            reference_frame=reference_frame,
            timescale=timescale,
            uncertainty=uncertainty,
        )

    @classmethod
    def epoch(cls: type[T]) -> T:
        """The Unix epoch: ``0`` seconds, ``0`` attoseconds, sign zero."""
        return cls.from_components(0, 0, NumericSign.ZERO)

    # ------------------------------------------------------------------
    # Epoch predicates (derived once from `sign`; not part of the math contract)
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Math contract — implemented by the downstream math repo.
    # Mirrors Swift PrecisionTimestamp +Arithmetic / +Comparable / +BaseExtensions.
    # ------------------------------------------------------------------

    @abstractmethod
    def adding(self: T, interval: PrecisionTimeInterval) -> T:
        """Return this timestamp advanced by ``interval`` (``timestamp + interval``)."""

    @abstractmethod
    def subtracting(self: T, interval: PrecisionTimeInterval) -> T:
        """Return this timestamp moved back by ``interval`` (``timestamp - interval``)."""

    @abstractmethod
    def interval_since(self, other: "PrecisionTimestamp") -> PrecisionTimeInterval:
        """Signed interval from ``other`` to ``self`` (``self - other``)."""

    @abstractmethod
    def __lt__(self, other: "PrecisionTimestamp") -> bool:
        """Chronological ordering."""

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        """Normalized value equality (including metadata)."""

    @abstractmethod
    def __hash__(self) -> int:
        """Hash consistent with :meth:`__eq__`."""
