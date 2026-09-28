"""Contract for Robot geometry reuse of the Math canonical types.

Robot geometry `$ref`s the canonical Math schemas; codegen strips the inlined
carriers, types the fields to the `foundation_abc.math` protocols, and constructs
the concrete Math carriers at deserialization. These tests pin that two-tier wiring
(see `.claude/specs/mathTypeTiers.md`).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from foundation_abc.math.spatialABCs import (
    PositionABC,
    QuaternionABC,
    SpatialTransformABC,
)
from foundationTypes.automationTypes.RobotConfig import (
    Component,
    Connection,
    Frame,
    RobotConfig,
)
from foundationTypes.mathTypes.MathTypes import SpatialTransformType

_TRANSFORM: dict[str, Any] = {
    "position": {"x": 1.0, "y": -2.0, "z": 3.5},
    "orientation": {"w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0},
}


@dataclass
class _MyTransform:
    """A caller's own SpatialTransformABC implementation (test double)."""

    position: PositionABC
    orientation: QuaternionABC

    def to_dict(self) -> dict[str, Any]:
        return {"position": self.position, "orientation": self.orientation}

    @classmethod
    def from_dict(cls, obj: Any) -> "_MyTransform":
        return cls(obj["position"], obj["orientation"])


def _consume(transform: SpatialTransformABC) -> SpatialTransformABC:
    """Compile-time proof (mypy) that a Robot transform field is a protocol."""
    return transform


def test_connection_transform_is_math_carrier_typed_as_protocol() -> None:
    conn = Connection.from_dict(
        {"id": "c1", "parent": "p1", "child": "ch1", "transform": _TRANSFORM}
    )
    assert conn.transform is not None
    # Runtime value is the concrete Math carrier ...
    assert isinstance(conn.transform, SpatialTransformType)
    # ... typed to the protocol contract (mypy-checked).
    _consume(conn.transform)
    assert conn.transform.to_dict() == _TRANSFORM


def test_frame_transform_round_trips_through_math_carrier() -> None:
    frame = Frame.from_dict({"id": "f1", "body": "b1", "transform": _TRANSFORM})
    assert isinstance(frame.transform, SpatialTransformType)
    assert frame.transform.to_dict() == _TRANSFORM


def test_component_transform_round_trips_through_math_carrier() -> None:
    comp = Component.from_dict(
        {"id": "comp1", "definition": "def1", "transform": _TRANSFORM}
    )
    assert isinstance(comp.transform, SpatialTransformType)
    assert comp.transform.to_dict() == _TRANSFORM


def test_default_impl_knob_is_the_math_carrier() -> None:
    assert RobotConfig.SPATIAL_TRANSFORM_IMPL is SpatialTransformType


def test_transform_impl_is_overridable_by_downstream() -> None:
    """A user injects their own SpatialTransformABC implementation via the knob."""
    original = RobotConfig.SPATIAL_TRANSFORM_IMPL
    try:
        RobotConfig.SPATIAL_TRANSFORM_IMPL = _MyTransform
        conn = Connection.from_dict(
            {"id": "c1", "parent": "p1", "child": "ch1", "transform": _TRANSFORM}
        )
        assert isinstance(conn.transform, _MyTransform)
        # Serialization goes through the protocol, so the custom type round-trips.
        assert conn.transform is not None
        _consume(conn.transform)
        assert conn.to_dict()["transform"]["position"] == _TRANSFORM["position"]
    finally:
        RobotConfig.SPATIAL_TRANSFORM_IMPL = original
    assert RobotConfig.SPATIAL_TRANSFORM_IMPL is SpatialTransformType


def test_generated_source_reuses_math_types_and_protocols() -> None:
    source = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "foundationTypes"
        / "automationTypes"
        / "RobotConfig.py"
    ).read_text(encoding="utf-8")

    # Concrete geometry carriers are imported from Math, not redefined locally.
    assert "from foundationTypes.mathTypes.MathTypes import SpatialTransformType" in source
    assert "from foundation_abc.math.spatialABCs import SpatialTransformABC" in source
    assert "class SpatialTransformType" not in source
    assert "class PositionType" not in source
    assert "class QuaternionType" not in source
    # Fields are typed to the protocol, not the concrete carrier.
    assert "transform: Optional[SpatialTransformABC]" in source
    # Construction routes through the user-overridable knob; serialization through
    # the protocol-aware helper. The concrete carrier appears only as the default.
    assert (
        "SPATIAL_TRANSFORM_IMPL: ClassVar[type[SpatialTransformABC]] = SpatialTransformType"
        in source
    )
    assert "RobotConfig.SPATIAL_TRANSFORM_IMPL.from_dict" in source
    assert "to_class_abc(SpatialTransformABC, x)" in source
    assert "to_class(SpatialTransformType" not in source
    # Collapsed rotation representations no longer exist.
    for gone in ("class AxisAngle", "class Rpy", "class RotationMatrix", "class Rotation("):
        assert gone not in source
