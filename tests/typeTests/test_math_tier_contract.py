"""Tier-1 <-> Tier-2 contract tests for the Math type family.

Pins two invariants from ``.claude/specs/mathTypeTiers.md`` across all 13
``(XxxxType, XxxxABC)`` pairs (mirrors ``TYPE_TO_LIKE`` in
``schema/scripts/reuse/postprocess_mathtypes.py``):

- **Invariant 4 (structural).** ``XxxxLike`` (the hand-written ABC) must come
  before ``DataModelHelper`` in ``XxxxType``'s base list / MRO. The
  post-processor emits this correctly today, but a regression would only
  surface as subtle MRO behavior, not a loud failure -- see chunk 22 finding
  F2.

- **Serialization parity (F1).** Every ``XxxxABC`` carries a concrete
  ``to_dict`` built on its abstract accessors -- the serialization contract
  Tier-3 implementers inherit. Every generated ``XxxxType`` shadows it with
  its own quicktype-generated ``to_dict``, so the ABC version never runs in
  normal use and the wire shape is defined twice with nothing pinning them
  together. This module calls the ABC's ``to_dict`` explicitly (unbound, on a
  concrete instance) so the shadowed code path actually executes, and asserts
  it agrees with the generated ``to_dict``.
"""

from __future__ import annotations

from typing import Any

import pytest

from foundation_abc.math.precisionTimeABC import (
    PrecisionTimeIntervalABC,
    PrecisionTimestampABC,
)
from foundation_abc.math.spatialABCs import PositionABC, QuaternionABC, SpatialTransformABC
from foundation_abc.math.sphericalABCs import UnitSphericalArcABC, UnitSphericalSmallCircleABC
from foundation_abc.math.waveformABCs import (
    PositionWaveformABC,
    QuaternionWaveformABC,
    Waveform1dABC,
    WaveformSpatialABC,
    WaveformUnitSphericalArcABC,
    WaveformUnitSphericalSmallCircleABC,
)
from foundationTypes.data_model_helper import DataModelHelper
from foundationTypes.mathTypes.MathTypes import (
    PositionType,
    PositionWaveformType,
    PrecisionTimeIntervalType,
    PrecisionTimestampType,
    QuaternionType,
    QuaternionWaveformType,
    ScalarWaveformType,
    SpatialTransformType,
    SpatialTransformWaveformType,
    UnitSphericalArcType,
    UnitSphericalArcWaveformType,
    UnitSphericalSmallCircleType,
    UnitSphericalSmallCircleWaveformType,
)

# Representative payloads, built bottom-up so nested waveform payloads can reuse
# the leaf position/quaternion/timestamp/interval dicts.
_QUATERNION: dict[str, Any] = {"w": 1.0, "x": 0.5, "y": -0.5, "z": 0.25}
_QUATERNION_2: dict[str, Any] = {"w": 0.0, "x": 1.0, "y": 0.0, "z": 0.0}
_POSITION: dict[str, Any] = {"x": 1.0, "y": -2.0, "z": 3.5}
_POSITION_2: dict[str, Any] = {"x": -1.5, "y": 0.0, "z": 2.25}
_TIME_INTERVAL: dict[str, Any] = {
    "attoseconds": 123456789012345678,
    "seconds": 42,
    "sign": "positive",
}
# Optionals absent -- this is also the shape nested waveform payloads reuse.
_TIMESTAMP_MINIMAL: dict[str, Any] = {"attoseconds": 0, "seconds": 1_000, "sign": "positive"}
# Optionals present -- referenceFrame / timescale / uncertainty all populated.
_TIMESTAMP_FULL: dict[str, Any] = {
    "attoseconds": 5,
    "seconds": 10,
    "sign": "negative",
    "referenceFrame": "EarthCenter",
    "timescale": "TAI",
    "uncertainty": 7,
}
_ARC: dict[str, Any] = {"arcLength": 1.0, "azimuth": 0.5, "orient": 0.2, "polar": 0.3}
_SMALL_CIRCLE: dict[str, Any] = {"azimuth": 0.5, "polar": 0.3, "radiusAngle": 0.1}

# (XxxxType, XxxxABC, representative from_dict payload) for all 13 Math types.
PAIRS: list[tuple[type[DataModelHelper], type[Any], dict[str, Any]]] = [
    (QuaternionType, QuaternionABC, _QUATERNION),
    (PositionType, PositionABC, _POSITION),
    (
        SpatialTransformType,
        SpatialTransformABC,
        {"orientation": _QUATERNION, "position": _POSITION},
    ),
    (PrecisionTimeIntervalType, PrecisionTimeIntervalABC, _TIME_INTERVAL),
    (PrecisionTimestampType, PrecisionTimestampABC, _TIMESTAMP_MINIMAL),
    (UnitSphericalArcType, UnitSphericalArcABC, _ARC),
    (UnitSphericalSmallCircleType, UnitSphericalSmallCircleABC, _SMALL_CIRCLE),
    (
        PositionWaveformType,
        PositionWaveformABC,
        {"dt": _TIME_INTERVAL, "positions": [_POSITION, _POSITION_2], "t0": _TIMESTAMP_MINIMAL},
    ),
    (
        QuaternionWaveformType,
        QuaternionWaveformABC,
        {
            "dt": _TIME_INTERVAL,
            "quaternions": [_QUATERNION, _QUATERNION_2],
            "t0": _TIMESTAMP_MINIMAL,
        },
    ),
    (
        SpatialTransformWaveformType,
        WaveformSpatialABC,
        {
            "dt": _TIME_INTERVAL,
            "positions": [_POSITION, _POSITION_2],
            "quaternions": [_QUATERNION, _QUATERNION_2],
            "t0": _TIMESTAMP_MINIMAL,
        },
    ),
    (
        ScalarWaveformType,
        Waveform1dABC,
        {"dt": _TIME_INTERVAL, "t0": _TIMESTAMP_MINIMAL, "waveform": [1.0, 2.0, 3.0]},
    ),
    (
        UnitSphericalArcWaveformType,
        WaveformUnitSphericalArcABC,
        {"arcs": [_ARC], "dt": _TIME_INTERVAL, "t0": _TIMESTAMP_MINIMAL},
    ),
    (
        UnitSphericalSmallCircleWaveformType,
        WaveformUnitSphericalSmallCircleABC,
        {"dt": _TIME_INTERVAL, "smallCircles": [_SMALL_CIRCLE], "t0": _TIMESTAMP_MINIMAL},
    ),
]

assert len(PAIRS) == 13, f"expected all 13 Math types, found {len(PAIRS)}"


def _pair_id(value: Any) -> str | None:
    """pytest calls this once per parametrized value, not once per tuple; only
    name the ``XxxxType`` column, and let pytest auto-derive the rest."""
    return value.__name__ if isinstance(value, type) else None


@pytest.mark.parametrize("type_cls,abc_cls,_payload", PAIRS, ids=_pair_id)
def test_abc_precedes_data_model_helper_in_mro(
    type_cls: type[DataModelHelper], abc_cls: type[Any], _payload: dict[str, Any]
) -> None:
    """Invariant 4: XxxxLike (the ABC) must come before DataModelHelper in the MRO."""
    assert issubclass(type_cls, abc_cls)
    assert issubclass(type_cls, DataModelHelper)
    mro = type_cls.__mro__
    assert mro.index(abc_cls) < mro.index(DataModelHelper)


@pytest.mark.parametrize("type_cls,abc_cls,payload", PAIRS, ids=_pair_id)
def test_abc_to_dict_matches_generated_to_dict(
    type_cls: type[DataModelHelper], abc_cls: type[Any], payload: dict[str, Any]
) -> None:
    """F1: the ABC's concrete to_dict (accessor-based) must match the generated
    to_dict shadowing it -- otherwise the wire shape silently drifts between the
    hand-written Tier-2 contract and the quicktype-generated Tier-1 carrier."""
    instance = type_cls.from_dict(payload)
    assert abc_cls.to_dict(instance) == instance.to_dict()


def test_precision_timestamp_parity_with_optionals_present() -> None:
    """F1, optionals-present variant: referenceFrame/timescale/uncertainty all set.

    (The optionals-absent variant is covered by the PAIRS table above via
    _TIMESTAMP_MINIMAL.)
    """
    instance = PrecisionTimestampType.from_dict(_TIMESTAMP_FULL)
    assert PrecisionTimestampABC.to_dict(instance) == instance.to_dict()
