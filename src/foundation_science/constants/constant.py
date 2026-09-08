"""The ``Constant`` leaf type: a float that carries its own metrology.

A physical constant is a float first — it must survive arithmetic at native speed
and satisfy every signature that accepts a ``float``. It is metrology second: the
unit, the standard uncertainty, the distribution that uncertainty came from, and
the provenance of the value all have to travel with the number so a downstream
uncertainty budget can read them.

``Constant`` subclasses ``float`` to get both. Arithmetic on a ``Constant``
deliberately returns a plain ``float`` and drops the metadata: propagating it
automatically would have to propagate it *wrongly*, because naive quadrature
assumes the inputs are independent and silently under-reports the moment two
expressions share a term. Metadata lives at the leaf; combining it is the explicit
job of a propagation layer.

See ``.claude/specs/physicalConstants.md`` for the full contract.
"""

import math
from enum import Enum
from typing import Any

_RECTANGULAR_DIVISOR = 3.0**0.5
"""Half-width to standard uncertainty for a rectangular distribution: u = a/√3."""

_TRIANGULAR_DIVISOR = 6.0**0.5
"""Half-width to standard uncertainty for a triangular distribution: u = a/√6."""


class Distribution(Enum):
    """How a constant's stated uncertainty is distributed.

    This is a genuine closed set of mutually exclusive choices, which is why it is
    an ``Enum`` while the constants themselves are not.
    """

    EXACT = "exact"
    """Defined by convention or by the SI; no error by construction."""

    NORMAL = "normal"
    """Gaussian; the stored standard uncertainty is the standard deviation (k=1)."""

    RECTANGULAR = "rectangular"
    """Uniform over a ±a half-width; u = a/√3."""

    TRIANGULAR = "triangular"
    """Triangular over a ±a half-width; u = a/√6."""

    UNKNOWN = "unknown"
    """A representative value whose error is real but has not been quantified."""


_BOUNDED = frozenset({Distribution.NORMAL, Distribution.RECTANGULAR, Distribution.TRIANGULAR})
"""Distributions that require a positive, finite standard uncertainty."""


def _validate(distribution: Distribution, std_uncertainty: float | None) -> None:
    """Reject an incoherent ``(distribution, std_uncertainty)`` pairing.

    Raises: ValueError: If the pairing violates the three-state rule.
    """
    if distribution is Distribution.EXACT:
        if std_uncertainty != 0.0:
            raise ValueError(
                "Distribution.EXACT requires std_uncertainty=0.0 (exact by definition), "
                f"got {std_uncertainty!r}. Use Distribution.UNKNOWN with None if the "
                "error is real but unquantified."
            )
        return

    if distribution is Distribution.UNKNOWN:
        if std_uncertainty is not None:
            raise ValueError(
                "Distribution.UNKNOWN requires std_uncertainty=None (error unstated), "
                f"got {std_uncertainty!r}. Use 0.0 only for values that are exact by "
                "definition."
            )
        return

    if std_uncertainty is None:
        raise ValueError(
            f"{distribution} requires a positive std_uncertainty, got None. "
            "None means 'unknown' and pairs only with Distribution.UNKNOWN."
        )
    if not math.isfinite(std_uncertainty):
        raise ValueError(
            f"{distribution} requires a finite std_uncertainty, got {std_uncertainty!r}."
        )
    if std_uncertainty <= 0.0:
        raise ValueError(f"{distribution} requires std_uncertainty > 0.0, got {std_uncertainty!r}.")


def _rebuild_constant(
    value: float,
    unit: str,
    std_uncertainty: float | None,
    distribution: Distribution,
    source: str,
) -> "Constant":
    """Module-level reconstructor for ``pickle`` / ``copy`` (see ``Constant.__reduce__``)."""
    return Constant(
        value,
        unit=unit,
        std_uncertainty=std_uncertainty,
        distribution=distribution,
        source=source,
    )


class Constant(float):
    """A float carrying its unit, standard uncertainty (k=1), distribution, and source.

    Every keyword argument is required. There are no defaults, which makes "I did
    not think about the uncertainty" unrepresentable at the definition site.

    ``std_uncertainty`` has three states, and ``None`` is not ``0.0``:

    - ``0.0`` — exact by definition (a defined convention or an SI-exact value)
    - ``> 0.0`` — measured, Type B (CODATA, a calibration certificate, a spec band)
    - ``None`` — unknown; the error is real but has not been quantified

    Conflating the last two is the failure this type exists to prevent: a value of
    ``0.0`` for an unquantified constant claims perfection and silently shrinks
    every budget that consumes it.
    """

    __slots__ = ("unit", "std_uncertainty", "distribution", "source")

    unit: str
    std_uncertainty: float | None
    distribution: Distribution
    source: str

    def __new__(
        cls,
        value: float,
        *,
        unit: str,
        std_uncertainty: float | None,
        distribution: Distribution,
        source: str,
    ) -> "Constant":
        """Construct a constant, rejecting an incoherent uncertainty pairing.

        - value: The numeric value, in the units given by ``unit``
        - unit: SI unit string; ``"1"`` for dimensionless quantities
        - std_uncertainty: Standard uncertainty at k=1, per the three-state rule
        - distribution: How that uncertainty is distributed
        - source: Citation for the value (the docstring carries the prose)

        Raises: ValueError: If ``distribution`` and ``std_uncertainty`` disagree.
        """
        _validate(distribution, std_uncertainty)

        obj = super().__new__(cls, value)
        obj.unit = unit
        obj.std_uncertainty = std_uncertainty
        obj.distribution = distribution
        obj.source = source
        return obj

    @classmethod
    def from_half_width(
        cls,
        value: float,
        *,
        half_width: float,
        unit: str,
        source: str,
        distribution: Distribution = Distribution.RECTANGULAR,
    ) -> "Constant":
        """Build a constant from a ``±a`` half-width, normalizing to k=1 on entry.

        Converting here rather than at the point of use is deliberate: the
        distribution is known at the definition site and forgotten everywhere else.

        - value: The central value
        - half_width: The ``a`` in ``±a``; must be positive
        - unit: SI unit string
        - source: Citation for the value and its band
        - distribution: ``RECTANGULAR`` (u = a/√3) or ``TRIANGULAR`` (u = a/√6)

        Raises: ValueError: If ``half_width`` is not positive, or ``distribution``
            is not a half-width distribution.
        """
        if half_width <= 0.0:
            raise ValueError(f"half_width must be > 0.0, got {half_width!r}.")

        if distribution is Distribution.RECTANGULAR:
            divisor = _RECTANGULAR_DIVISOR
        elif distribution is Distribution.TRIANGULAR:
            divisor = _TRIANGULAR_DIVISOR
        else:
            raise ValueError(
                "from_half_width accepts Distribution.RECTANGULAR or "
                f"Distribution.TRIANGULAR, got {distribution}."
            )

        return cls(
            value,
            unit=unit,
            std_uncertainty=half_width / divisor,
            distribution=distribution,
            source=source,
        )

    @classmethod
    def from_expanded(
        cls,
        value: float,
        *,
        expanded: float,
        unit: str,
        source: str,
        k: float = 2.0,
    ) -> "Constant":
        """Build a constant from an expanded uncertainty ``U``, storing ``U/k``.

        Vendors and calibration certificates quote ``U`` at k=2. Dividing here keeps
        the stored value unambiguously k=1, so nothing downstream has to guess
        whether a coverage factor has already been applied.

        - value: The central value
        - expanded: The expanded uncertainty ``U``; must be positive
        - unit: SI unit string
        - source: Citation for the value and its stated uncertainty
        - k: Coverage factor the source used, conventionally 2.0

        Raises: ValueError: If ``expanded`` or ``k`` is not positive.
        """
        if expanded <= 0.0:
            raise ValueError(f"expanded must be > 0.0, got {expanded!r}.")
        if k <= 0.0:
            raise ValueError(f"k must be > 0.0, got {k!r}.")

        return cls(
            value,
            unit=unit,
            std_uncertainty=expanded / k,
            distribution=Distribution.NORMAL,
            source=source,
        )

    @property
    def relative_std_uncertainty(self) -> float | None:
        """Standard uncertainty as a fraction of the value, or ``None`` if unknown.

        Returns ``None`` for an unknown uncertainty and for a zero value, since
        neither has a meaningful relative form.
        """
        if self.std_uncertainty is None:
            return None
        value = float(self)
        if value == 0.0:
            return None
        return self.std_uncertainty / abs(value)

    def __reduce__(self) -> tuple[Any, ...]:
        """Support ``pickle`` and ``copy``.

        The inherited float path cannot reconstruct this type because ``__new__``
        takes required keyword-only arguments, so reconstruction is routed through
        a module-level function that supplies them.
        """
        return (
            _rebuild_constant,
            (float(self), self.unit, self.std_uncertainty, self.distribution, self.source),
        )
