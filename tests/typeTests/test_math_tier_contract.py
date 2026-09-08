"""Contracts between generated Math carriers and structural Math protocols."""

from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any, get_args, get_type_hints

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

_QUATERNION: dict[str, Any] = {"w": 1.0, "x": 0.5, "y": -0.5, "z": 0.25}
_QUATERNION_2: dict[str, Any] = {"w": 0.0, "x": 1.0, "y": 0.0, "z": 0.0}
_POSITION: dict[str, Any] = {"x": 1.0, "y": -2.0, "z": 3.5}
_POSITION_2: dict[str, Any] = {"x": -1.5, "y": 0.0, "z": 2.25}
_TIME_INTERVAL: dict[str, Any] = {
    "attoseconds": 123456789012345678,
    "seconds": 42,
    "sign": "positive",
}
_TIMESTAMP_MINIMAL: dict[str, Any] = {"attoseconds": 0, "seconds": 1_000, "sign": "positive"}
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

# (wire name, constructor field) for every schema-required field.
REQUIRED_FIELDS: dict[type[DataModelHelper], tuple[tuple[str, str], ...]] = {
    QuaternionType: (("w", "w"), ("x", "x"), ("y", "y"), ("z", "z")),
    PositionType: (("x", "x"), ("y", "y"), ("z", "z")),
    SpatialTransformType: (("orientation", "orientation"), ("position", "position")),
    PrecisionTimeIntervalType: (
        ("attoseconds", "attoseconds"),
        ("seconds", "seconds"),
        ("sign", "sign"),
    ),
    PrecisionTimestampType: (
        ("attoseconds", "attoseconds"),
        ("seconds", "seconds"),
        ("sign", "sign"),
    ),
    UnitSphericalArcType: (
        ("arcLength", "arc_length"),
        ("azimuth", "azimuth"),
        ("orient", "orient"),
        ("polar", "polar"),
    ),
    UnitSphericalSmallCircleType: (
        ("azimuth", "azimuth"),
        ("polar", "polar"),
        ("radiusAngle", "radius_angle"),
    ),
    PositionWaveformType: (("dt", "dt"), ("positions", "positions"), ("t0", "t0")),
    QuaternionWaveformType: (
        ("dt", "dt"),
        ("quaternions", "quaternions"),
        ("t0", "t0"),
    ),
    SpatialTransformWaveformType: (
        ("dt", "dt"),
        ("positions", "positions"),
        ("quaternions", "quaternions"),
        ("t0", "t0"),
    ),
    ScalarWaveformType: (("dt", "dt"), ("t0", "t0"), ("waveform", "waveform")),
    UnitSphericalArcWaveformType: (("arcs", "arcs"), ("dt", "dt"), ("t0", "t0")),
    UnitSphericalSmallCircleWaveformType: (
        ("dt", "dt"),
        ("smallCircles", "small_circles"),
        ("t0", "t0"),
    ),
}

assert len(PAIRS) == len(REQUIRED_FIELDS) == 13


def _protocol_conformance(
    quaternion: QuaternionType,
    position: PositionType,
    transform: SpatialTransformType,
    interval: PrecisionTimeIntervalType,
    timestamp: PrecisionTimestampType,
    arc: UnitSphericalArcType,
    circle: UnitSphericalSmallCircleType,
    position_waveform: PositionWaveformType,
    quaternion_waveform: QuaternionWaveformType,
    spatial_waveform: SpatialTransformWaveformType,
    scalar_waveform: ScalarWaveformType,
    arc_waveform: UnitSphericalArcWaveformType,
    circle_waveform: UnitSphericalSmallCircleWaveformType,
) -> tuple[
    QuaternionABC,
    PositionABC,
    SpatialTransformABC,
    PrecisionTimeIntervalABC,
    PrecisionTimestampABC,
    UnitSphericalArcABC,
    UnitSphericalSmallCircleABC,
    PositionWaveformABC,
    QuaternionWaveformABC,
    WaveformSpatialABC,
    Waveform1dABC,
    WaveformUnitSphericalArcABC,
    WaveformUnitSphericalSmallCircleABC,
]:
    """Compile-time proof that carriers structurally satisfy every protocol."""
    return (
        quaternion,
        position,
        transform,
        interval,
        timestamp,
        arc,
        circle,
        position_waveform,
        quaternion_waveform,
        spatial_waveform,
        scalar_waveform,
        arc_waveform,
        circle_waveform,
    )


def _pair_id(value: Any) -> str | None:
    return value.__name__ if isinstance(value, type) else None


@pytest.mark.parametrize("type_cls,protocol_cls,payload", PAIRS, ids=_pair_id)
def test_carrier_is_independent_data_model_helper(
    type_cls: type[DataModelHelper], protocol_cls: type[Any], payload: dict[str, Any]
) -> None:
    """Carriers retain IO behavior without inheriting field protocols."""
    instance = type_cls.from_dict(payload)
    assert isinstance(instance, DataModelHelper)
    assert protocol_cls not in type_cls.__mro__
    assert instance.to_dict() == payload


@pytest.mark.parametrize("type_cls,_protocol_cls,payload", PAIRS, ids=_pair_id)
def test_direct_constructor_requires_every_schema_required_field(
    type_cls: type[DataModelHelper], _protocol_cls: type[Any], payload: dict[str, Any]
) -> None:
    """Every required field is non-optional and has no constructor default."""
    instance = type_cls.from_dict(payload)
    parameters = inspect.signature(type_cls).parameters
    hints = get_type_hints(type_cls)
    required = REQUIRED_FIELDS[type_cls]
    complete = {field_name: getattr(instance, field_name) for _, field_name in required}

    for _, field_name in required:
        assert parameters[field_name].default is inspect.Parameter.empty
        assert type(None) not in get_args(hints[field_name])
        incomplete = complete.copy()
        del incomplete[field_name]
        with pytest.raises(TypeError):
            type_cls(**incomplete)


@pytest.mark.parametrize("type_cls,_protocol_cls,payload", PAIRS, ids=_pair_id)
def test_from_dict_rejects_each_missing_required_field(
    type_cls: type[DataModelHelper], _protocol_cls: type[Any], payload: dict[str, Any]
) -> None:
    """Deserialization rejects every required field when it is absent."""
    for wire_name, _ in REQUIRED_FIELDS[type_cls]:
        incomplete = payload.copy()
        del incomplete[wire_name]
        with pytest.raises((TypeError, ValueError)):
            type_cls.from_dict(incomplete)


def test_schema_optional_timestamp_fields_remain_optional() -> None:
    minimal = PrecisionTimestampType.from_dict(_TIMESTAMP_MINIMAL)
    full = PrecisionTimestampType.from_dict(_TIMESTAMP_FULL)
    assert minimal.reference_frame is None
    assert minimal.timescale is None
    assert minimal.uncertainty is None
    assert full.to_dict() == _TIMESTAMP_FULL


def test_generated_source_pins_decoupled_regeneration_strategy() -> None:
    source = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "foundationTypes"
        / "mathTypes"
        / "MathTypes.py"
    ).read_text(encoding="utf-8")

    assert source.count("Type(DataModelHelper):") == len(PAIRS)
    assert "# type: ignore[assignment]" not in source
    assert "from foundation_abc.math.spatialABCs" not in source
    assert "from foundation_abc.math.sphericalABCs" not in source
    assert "from foundation_abc.math.waveformABCs" not in source
    assert "from foundation_abc.math.precisionTimeABC" not in source
