"""Tier-2 abstract contract for attosecond-precision time intervals.

`PrecisionTimeInterval` inherits the generated wire/serialization carrier
``_PrecisionTimeIntervalType`` (fields ``seconds`` / ``attoseconds`` / ``sign``
plus ``from_dict`` / ``to_dict`` from :class:`DataModelHelper`) and layers on the
*math contract*: the arithmetic, comparison and conversion operations a concrete
implementation must provide.

A downstream math repository subclasses this ABC and implements the abstract
members — the Python analogue of the Swift
``Extensions/PrecisionTimeInterval/+Arithmetic.swift``, ``+Comparable.swift`` and
``+BaseExtensions.swift``. The data shape is defined once (JSON Schema -> generated
``_PrecisionTimeIntervalType``); this layer never redeclares it.
"""

from abc import ABC, abstractmethod
from typing import TypeVar

from foundationTypes.mathTypes.PrecisionTime import (
    NumericSign,
    _PrecisionTimeIntervalType,
)

T = TypeVar("T", bound="PrecisionTimeInterval")

#: Number of attoseconds (10^-18 s) in one second.
ATTOSECONDS_PER_SECOND = 1_000_000_000_000_000_000


class PrecisionTimeInterval(_PrecisionTimeIntervalType, ABC):
    """Abstract attosecond-precision time interval.

    Carries an unsigned ``(seconds, attoseconds)`` magnitude and an explicit
    :class:`NumericSign`, avoiding floating-point precision loss across both very
    large and very small spans. Concrete subclasses implement the math contract
    below.
    """

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    @classmethod
    def from_components(
        cls: type[T], seconds: int, attoseconds: int, sign: NumericSign
    ) -> T:
        """Build an interval from its components.

        Args:
            seconds: Whole-seconds component (unsigned, ``>= 0``).
            attoseconds: Sub-second component (``0 .. 999_999_999_999_999_999``).
            sign: The sign of the interval.

        Returns:
            A concrete instance of the calling subclass.
        """
        return cls(attoseconds=attoseconds, seconds=seconds, sign=sign)

    @classmethod
    def zero(cls: type[T]) -> T:
        """The additive identity: ``0`` seconds, ``0`` attoseconds, sign zero."""
        return cls.from_components(0, 0, NumericSign.ZERO)

    # ------------------------------------------------------------------
    # Sign predicates (derived once from `sign`; not part of the math contract)
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Math contract — implemented by the downstream math repo.
    # Mirrors Swift PrecisionTimeInterval +Arithmetic / +Comparable / +BaseExtensions.
    # ------------------------------------------------------------------

    @abstractmethod
    def normalized(self: T) -> T:
        """Return an equivalent interval with ``attoseconds < ATTOSECONDS_PER_SECOND``
        and the sign collapsed to zero when the magnitude is zero."""

    @abstractmethod
    def seconds_as_double(self) -> float:
        """Signed value as a ``float`` (lossy; attosecond precision is not retained)."""

    @abstractmethod
    def __add__(self: T, other: "PrecisionTimeInterval") -> T:
        """Signed sum of two intervals."""

    @abstractmethod
    def __sub__(self: T, other: "PrecisionTimeInterval") -> T:
        """Signed difference of two intervals."""

    @abstractmethod
    def __neg__(self: T) -> T:
        """The additive inverse (sign flipped; zero stays zero)."""

    @abstractmethod
    def __mul__(self: T, scalar: float) -> T:
        """Scale the interval by a real scalar."""

    @abstractmethod
    def __lt__(self, other: "PrecisionTimeInterval") -> bool:
        """Signed ordering."""

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        """Signed, normalized value equality."""

    @abstractmethod
    def __hash__(self) -> int:
        """Hash consistent with :meth:`__eq__` (normalized value)."""
