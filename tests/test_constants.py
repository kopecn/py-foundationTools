"""Tests for ``foundation_science.constants``.

Two things are under test. First, that ``Constant`` really is a float — if it is not
transparently substitutable, every consumer pays for the metadata at every call
site. Second, the three-state uncertainty rule, which is the invariant the whole
type exists to enforce: ``None`` (unknown) must never be confusable with ``0.0``
(exact), because that confusion silently shrinks any budget built on it.
"""

import copy
import math
import pickle

import pytest

from foundation_science.constants.constant import Constant, Distribution
from foundation_science.constants.materials.dry_air import DryAir
from foundation_science.constants.registry import iter_constants
from foundation_science.constants.standards.isa import ISA


def _exact(value: float) -> Constant:
    """Build a throwaway exact constant."""
    return Constant(
        value,
        unit="1",
        std_uncertainty=0.0,
        distribution=Distribution.EXACT,
        source="test fixture",
    )


# --- float substitutability -------------------------------------------------


def test_constant_is_a_float() -> None:
    assert isinstance(_exact(2.5), float)


def test_arithmetic_returns_plain_float() -> None:
    """Metadata is deliberately dropped by arithmetic, not propagated."""
    result = _exact(2.5) * 2

    assert result == 5.0
    assert type(result) is float


def test_interoperates_with_stdlib_math() -> None:
    assert math.sqrt(_exact(9.0)) == 3.0


def test_compares_equal_to_its_literal() -> None:
    assert _exact(2.5) == 2.5


# --- the three-state rule ---------------------------------------------------


def test_exact_accepts_zero_uncertainty() -> None:
    assert _exact(1.0).std_uncertainty == 0.0


def test_unknown_accepts_none() -> None:
    constant = Constant(
        1.4,
        unit="1",
        std_uncertainty=None,
        distribution=Distribution.UNKNOWN,
        source="test fixture",
    )

    assert constant.std_uncertainty is None


@pytest.mark.parametrize(
    ("distribution", "std_uncertainty"),
    [
        # Exact must not claim a nonzero error, nor an unknown one.
        (Distribution.EXACT, 1e-9),
        (Distribution.EXACT, None),
        # Unknown must not be pinned to a number — 0.0 especially, which would
        # claim the value is perfect.
        (Distribution.UNKNOWN, 0.0),
        (Distribution.UNKNOWN, 1e-9),
        # A bounded distribution needs a real, positive uncertainty.
        (Distribution.NORMAL, None),
        (Distribution.NORMAL, 0.0),
        (Distribution.NORMAL, -1e-9),
        (Distribution.RECTANGULAR, None),
        (Distribution.RECTANGULAR, 0.0),
        (Distribution.TRIANGULAR, None),
        (Distribution.TRIANGULAR, 0.0),
        # A bounded distribution must also reject non-finite uncertainty: NaN and
        # +inf pass a bare `<= 0.0` check, and -inf is included for completeness.
        (Distribution.NORMAL, math.nan),
        (Distribution.NORMAL, math.inf),
        (Distribution.NORMAL, -math.inf),
        (Distribution.RECTANGULAR, math.nan),
        (Distribution.RECTANGULAR, math.inf),
        (Distribution.RECTANGULAR, -math.inf),
        (Distribution.TRIANGULAR, math.nan),
        (Distribution.TRIANGULAR, math.inf),
        (Distribution.TRIANGULAR, -math.inf),
    ],
)
def test_incoherent_pairing_is_rejected(
    distribution: Distribution, std_uncertainty: float | None
) -> None:
    with pytest.raises(ValueError):
        Constant(
            1.0,
            unit="1",
            std_uncertainty=std_uncertainty,
            distribution=distribution,
            source="test fixture",
        )


def test_bounded_accepts_an_ordinary_positive_finite_value() -> None:
    """The valid bounded state — a real, finite, positive uncertainty — still works."""
    constant = Constant(
        1.0,
        unit="1",
        std_uncertainty=0.05,
        distribution=Distribution.NORMAL,
        source="test fixture",
    )

    assert constant.std_uncertainty == 0.05


# --- entry-time normalization to k=1 ----------------------------------------


def test_from_half_width_rectangular() -> None:
    constant = Constant.from_half_width(43.0, half_width=0.6, unit="J/kg", source="test fixture")

    assert constant.std_uncertainty == pytest.approx(0.6 / math.sqrt(3.0))
    assert constant.distribution is Distribution.RECTANGULAR


def test_from_half_width_triangular() -> None:
    constant = Constant.from_half_width(
        43.0,
        half_width=0.6,
        unit="J/kg",
        source="test fixture",
        distribution=Distribution.TRIANGULAR,
    )

    assert constant.std_uncertainty == pytest.approx(0.6 / math.sqrt(6.0))
    assert constant.distribution is Distribution.TRIANGULAR


def test_from_half_width_rejects_a_non_half_width_distribution() -> None:
    with pytest.raises(ValueError):
        Constant.from_half_width(
            1.0,
            half_width=0.1,
            unit="1",
            source="test fixture",
            distribution=Distribution.NORMAL,
        )


def test_from_half_width_rejects_a_nonpositive_width() -> None:
    with pytest.raises(ValueError):
        Constant.from_half_width(1.0, half_width=0.0, unit="1", source="test fixture")


@pytest.mark.parametrize("half_width", [math.nan, math.inf, -math.inf])
def test_from_half_width_rejects_a_non_finite_width(half_width: float) -> None:
    """NaN/inf survive the `half_width <= 0.0` guard but must not reach a Constant."""
    with pytest.raises(ValueError):
        Constant.from_half_width(1.0, half_width=half_width, unit="1", source="test fixture")


def test_from_expanded_divides_by_the_coverage_factor() -> None:
    constant = Constant.from_expanded(10.0, expanded=0.4, unit="m", source="test fixture")

    assert constant.std_uncertainty == pytest.approx(0.2)
    assert constant.distribution is Distribution.NORMAL


def test_from_expanded_honours_a_non_default_k() -> None:
    constant = Constant.from_expanded(10.0, expanded=0.9, unit="m", source="test fixture", k=3.0)

    assert constant.std_uncertainty == pytest.approx(0.3)


@pytest.mark.parametrize("expanded", [math.nan, math.inf, -math.inf])
def test_from_expanded_rejects_a_non_finite_expanded_value(expanded: float) -> None:
    """NaN/inf survive the `expanded <= 0.0` guard but must not reach a Constant."""
    with pytest.raises(ValueError):
        Constant.from_expanded(1.0, expanded=expanded, unit="1", source="test fixture")


def test_relative_std_uncertainty() -> None:
    constant = Constant.from_expanded(10.0, expanded=0.4, unit="m", source="test fixture")

    assert constant.relative_std_uncertainty == pytest.approx(0.02)


def test_relative_std_uncertainty_is_none_when_unknown() -> None:
    assert DryAir.GAMMA.relative_std_uncertainty is None


def test_relative_std_uncertainty_is_none_for_a_zero_value() -> None:
    assert _exact(0.0).relative_std_uncertainty is None


# --- serialization ----------------------------------------------------------


@pytest.mark.parametrize("roundtrip", [lambda c: pickle.loads(pickle.dumps(c)), copy.deepcopy])
def test_roundtrip_preserves_every_field(roundtrip) -> None:  # type: ignore[no-untyped-def]
    original = Constant.from_half_width(43.0, half_width=0.6, unit="J/kg", source="test fixture")

    restored = roundtrip(original)

    assert restored == original
    assert restored.unit == original.unit
    assert restored.std_uncertainty == original.std_uncertainty
    assert restored.distribution is original.distribution
    assert restored.source == original.source


# --- package audit ----------------------------------------------------------


def test_every_declared_constant_is_coherent() -> None:
    """Re-validate every shipped constant through the same rule ``__new__`` applies.

    Construction already enforces this, so a failure here means a constant was built
    by some path that bypassed validation.
    """
    for name, constant in iter_constants():
        if constant.distribution is Distribution.EXACT:
            assert constant.std_uncertainty == 0.0, name
        elif constant.distribution is Distribution.UNKNOWN:
            assert constant.std_uncertainty is None, name
        else:
            assert constant.std_uncertainty is not None and constant.std_uncertainty > 0.0, name


def test_every_declared_constant_has_a_unit_and_source() -> None:
    for name, constant in iter_constants():
        assert constant.unit, name
        assert constant.source, name


def test_audit_actually_found_the_constants() -> None:
    """Guard against a bad walk silently passing every assertion above."""
    discovered = dict(iter_constants())

    assert len(discovered) >= 10, discovered
    assert "foundation_science.constants.universal.R_UNIVERSAL" in discovered


# --- migrated values --------------------------------------------------------


def test_isa_density_is_consistent_with_the_derived_value() -> None:
    """The migration preserved values, not just types."""
    derived = ISA.P_SL / (DryAir.R * ISA.T_SL)

    assert derived == pytest.approx(ISA.RHO_SL, rel=1e-3)


def test_speed_of_sound_at_isa_sea_level() -> None:
    speed = math.sqrt(DryAir.GAMMA * DryAir.R * ISA.T_SL)

    assert speed == pytest.approx(340.3, abs=0.5)
