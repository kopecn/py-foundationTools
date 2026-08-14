# =============================================================================
# AUTO-GENERATED FILE — DO NOT EDIT
# Generated from JSON Schema via quicktype. Any manual edits will be
# overwritten the next time codegen runs (make codegen-all).
# To modify, update the source schema in schema/schemas/ and re-run codegen.
# =============================================================================

from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Any, TypeVar

from foundation_abc.math.mathEnums import NumericSign, ReferenceFrame, Timescale
from foundation_abc.math.precisionTimeABC import PrecisionTimeIntervalABC, PrecisionTimestampABC
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
from foundationTypes.data_model_helper import (
    DataModelHelper,
    from_float,
    from_int,
    from_list,
    from_none,
    from_union,
    to_class,
    to_enum,
    to_float,
)

T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


@dataclass
class QuaternionType(QuaternionABC, DataModelHelper):
    """A quaternion representation of a 3D rotation: a scalar (real) part w and a vector
    (imaginary) part x, y, z. The schema does not enforce unit length; normalization is the
    concern of the downstream math implementation.

    The quaternion orientation component of the pose.
    """

    w: float = 0.0
    """The scalar (real) component of the quaternion."""

    x: float = 0.0
    """The x component of the quaternion's vector (imaginary) part."""

    y: float = 0.0
    """The y component of the quaternion's vector (imaginary) part."""

    z: float = 0.0
    """The z component of the quaternion's vector (imaginary) part."""

    @classmethod
    def from_dict(cls, obj: Any) -> "QuaternionType":
        assert isinstance(obj, dict)
        w = from_float(obj.get("w"))
        x = from_float(obj.get("x"))
        y = from_float(obj.get("y"))
        z = from_float(obj.get("z"))
        return QuaternionType(w, x, y, z)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["w"] = to_float(self.w)
        result["x"] = to_float(self.x)
        result["y"] = to_float(self.y)
        result["z"] = to_float(self.z)
        return result


@dataclass
class PositionType(PositionABC, DataModelHelper):
    """A 3D Cartesian position vector using right-handed (x, y, z) coordinates, in a
    caller-defined consistent length unit.

    The Cartesian position component of the pose.
    """

    x: float = 0.0
    """The x-axis (first Cartesian) component of the position."""

    y: float = 0.0
    """The y-axis (second Cartesian) component of the position."""

    z: float = 0.0
    """The z-axis (third Cartesian) component of the position."""

    @classmethod
    def from_dict(cls, obj: Any) -> "PositionType":
        assert isinstance(obj, dict)
        x = from_float(obj.get("x"))
        y = from_float(obj.get("y"))
        z = from_float(obj.get("z"))
        return PositionType(x, y, z)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["x"] = to_float(self.x)
        result["y"] = to_float(self.y)
        result["z"] = to_float(self.z)
        return result


@dataclass
class SpatialTransformType(SpatialTransformABC, DataModelHelper):
    """A full 6-degree-of-freedom rigid body state: a Cartesian position composed with a
    quaternion orientation.
    """

    orientation: QuaternionType | None = None  # type: ignore[assignment]
    """The quaternion orientation component of the pose."""

    position: PositionType | None = None  # type: ignore[assignment]
    """The Cartesian position component of the pose."""

    @classmethod
    def from_dict(cls, obj: Any) -> "SpatialTransformType":
        assert isinstance(obj, dict)
        orientation = QuaternionType.from_dict(obj.get("orientation"))
        position = PositionType.from_dict(obj.get("position"))
        return SpatialTransformType(orientation, position)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["orientation"] = to_class(QuaternionType, self.orientation)
        result["position"] = to_class(PositionType, self.position)
        return result


@dataclass
class PrecisionTimeIntervalType(PrecisionTimeIntervalABC, DataModelHelper):
    """A time interval with attosecond precision. Stores seconds and attoseconds as unsigned
    integers with an explicit sign, avoiding floating-point precision loss over large spans.

    The fixed interval between consecutive samples.
    """

    attoseconds: int = 0
    """The sub-second component in attoseconds (10^-18 s). Valid range: 0 to
    999_999_999_999_999_999.
    """
    seconds: int = 0
    """The whole-seconds component of the interval (unsigned)."""

    sign: NumericSign = NumericSign.ZERO
    """The sign of the time interval."""

    @classmethod
    def from_dict(cls, obj: Any) -> "PrecisionTimeIntervalType":
        assert isinstance(obj, dict)
        attoseconds = from_int(obj.get("attoseconds"))
        seconds = from_int(obj.get("seconds"))
        sign = NumericSign(obj.get("sign"))
        return PrecisionTimeIntervalType(attoseconds, seconds, sign)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["attoseconds"] = from_int(self.attoseconds)
        result["seconds"] = from_int(self.seconds)
        result["sign"] = to_enum(NumericSign, self.sign)
        return result


@dataclass
class PrecisionTimestampType(PrecisionTimestampABC, DataModelHelper):
    """An absolute timestamp with attosecond precision. Stores seconds and attoseconds as
    unsigned integers with an explicit sign. Optionally carries a timescale, reference frame,
    and measurement uncertainty (in attoseconds).

    The timestamp of the first sample.
    """

    attoseconds: int = 0
    """The sub-second component in attoseconds (10^-18 s). Valid range: 0 to
    999_999_999_999_999_999.
    """
    seconds: int = 0
    """The whole-seconds component of the timestamp (unsigned)."""

    sign: NumericSign = NumericSign.ZERO
    """The sign of the timestamp."""

    reference_frame: ReferenceFrame | None = None
    """The reference frame for the timestamp (e.g. 'EarthCenter', 'SolarSystemBarycenter')."""

    timescale: Timescale | None = None
    """The timescale of the timestamp (e.g. 'TAI', 'UTC', 'GPS')."""

    uncertainty: int | None = None
    """The measurement uncertainty of the timestamp, expressed as a non-negative magnitude in
    attoseconds (10^-18 s).
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "PrecisionTimestampType":
        assert isinstance(obj, dict)
        attoseconds = from_int(obj.get("attoseconds"))
        seconds = from_int(obj.get("seconds"))
        sign = NumericSign(obj.get("sign"))
        reference_frame = from_union([ReferenceFrame, from_none], obj.get("referenceFrame"))
        timescale = from_union([Timescale, from_none], obj.get("timescale"))
        uncertainty = from_union([from_int, from_none], obj.get("uncertainty"))
        return PrecisionTimestampType(
            attoseconds, seconds, sign, reference_frame, timescale, uncertainty
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["attoseconds"] = from_int(self.attoseconds)
        result["seconds"] = from_int(self.seconds)
        result["sign"] = to_enum(NumericSign, self.sign)
        if self.reference_frame is not None:
            result["referenceFrame"] = from_union(
                [lambda x: to_enum(ReferenceFrame, x), from_none], self.reference_frame
            )
        if self.timescale is not None:
            result["timescale"] = from_union(
                [lambda x: to_enum(Timescale, x), from_none], self.timescale
            )
        if self.uncertainty is not None:
            result["uncertainty"] = from_union([from_int, from_none], self.uncertainty)
        return result


@dataclass
class PositionWaveformType(PositionWaveformABC, DataModelHelper):
    """A uniformly-sampled time series of 3D Cartesian positions, anchored at a start timestamp
    and sampled at a fixed interval.
    """

    dt: PrecisionTimeIntervalType | None = None  # type: ignore[assignment]
    """The fixed interval between consecutive samples."""

    positions: Sequence[PositionType] = ()
    """The uniformly-sampled position values, in chronological order."""

    t0: PrecisionTimestampType | None = None  # type: ignore[assignment]
    """The timestamp of the first sample."""

    @classmethod
    def from_dict(cls, obj: Any) -> "PositionWaveformType":
        assert isinstance(obj, dict)
        dt = PrecisionTimeIntervalType.from_dict(obj.get("dt"))
        positions = from_list(PositionType.from_dict, obj.get("positions"))
        t0 = PrecisionTimestampType.from_dict(obj.get("t0"))
        return PositionWaveformType(dt, positions, t0)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["dt"] = to_class(PrecisionTimeIntervalType, self.dt)
        result["positions"] = from_list(lambda x: to_class(PositionType, x), self.positions)
        result["t0"] = to_class(PrecisionTimestampType, self.t0)
        return result


@dataclass
class QuaternionWaveformType(QuaternionWaveformABC, DataModelHelper):
    """A uniformly-sampled time series of quaternion orientations, anchored at a start timestamp
    and sampled at a fixed interval.
    """

    dt: PrecisionTimeIntervalType | None = None  # type: ignore[assignment]
    """The fixed interval between consecutive samples."""

    quaternions: Sequence[QuaternionType] = ()
    """The uniformly-sampled orientation values, in chronological order."""

    t0: PrecisionTimestampType | None = None  # type: ignore[assignment]
    """The timestamp of the first sample."""

    @classmethod
    def from_dict(cls, obj: Any) -> "QuaternionWaveformType":
        assert isinstance(obj, dict)
        dt = PrecisionTimeIntervalType.from_dict(obj.get("dt"))
        quaternions = from_list(QuaternionType.from_dict, obj.get("quaternions"))
        t0 = PrecisionTimestampType.from_dict(obj.get("t0"))
        return QuaternionWaveformType(dt, quaternions, t0)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["dt"] = to_class(PrecisionTimeIntervalType, self.dt)
        result["quaternions"] = from_list(lambda x: to_class(QuaternionType, x), self.quaternions)
        result["t0"] = to_class(PrecisionTimestampType, self.t0)
        return result


@dataclass
class SpatialTransformWaveformType(WaveformSpatialABC, DataModelHelper):
    """A uniformly-sampled time series of 6-DOF poses, represented as parallel position and
    quaternion arrays (not an array of SpatialTransform), anchored at a start timestamp and
    sampled at a fixed interval.
    """

    dt: PrecisionTimeIntervalType | None = None  # type: ignore[assignment]
    """The fixed interval between consecutive samples."""

    positions: Sequence[PositionType] = ()
    """The uniformly-sampled position values, in chronological order, parallel to quaternions."""

    quaternions: Sequence[QuaternionType] = ()
    """The uniformly-sampled orientation values, in chronological order, parallel to positions."""

    t0: PrecisionTimestampType | None = None  # type: ignore[assignment]
    """The timestamp of the first sample."""

    @classmethod
    def from_dict(cls, obj: Any) -> "SpatialTransformWaveformType":
        assert isinstance(obj, dict)
        dt = PrecisionTimeIntervalType.from_dict(obj.get("dt"))
        positions = from_list(PositionType.from_dict, obj.get("positions"))
        quaternions = from_list(QuaternionType.from_dict, obj.get("quaternions"))
        t0 = PrecisionTimestampType.from_dict(obj.get("t0"))
        return SpatialTransformWaveformType(dt, positions, quaternions, t0)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["dt"] = to_class(PrecisionTimeIntervalType, self.dt)
        result["positions"] = from_list(lambda x: to_class(PositionType, x), self.positions)
        result["quaternions"] = from_list(lambda x: to_class(QuaternionType, x), self.quaternions)
        result["t0"] = to_class(PrecisionTimestampType, self.t0)
        return result


@dataclass
class ScalarWaveformType(Waveform1dABC, DataModelHelper):
    """A uniformly-sampled time series of a single scalar signal, anchored at a start timestamp
    and sampled at a fixed interval.
    """

    dt: PrecisionTimeIntervalType | None = None  # type: ignore[assignment]
    """The fixed interval between consecutive samples."""

    t0: PrecisionTimestampType | None = None  # type: ignore[assignment]
    """The timestamp of the first sample."""

    waveform: Sequence[float] = ()
    """The uniformly-sampled scalar values, in chronological order."""

    @classmethod
    def from_dict(cls, obj: Any) -> "ScalarWaveformType":
        assert isinstance(obj, dict)
        dt = PrecisionTimeIntervalType.from_dict(obj.get("dt"))
        t0 = PrecisionTimestampType.from_dict(obj.get("t0"))
        waveform = from_list(from_float, obj.get("waveform"))
        return ScalarWaveformType(dt, t0, waveform)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["dt"] = to_class(PrecisionTimeIntervalType, self.dt)
        result["t0"] = to_class(PrecisionTimestampType, self.t0)
        result["waveform"] = from_list(to_float, self.waveform)
        return result


@dataclass
class UnitSphericalArcType(UnitSphericalArcABC, DataModelHelper):
    """Represents an arc on a unit sphere in spherical coordinates using physics convention.
    This arc is formed by a spherical reference point and then projected from that start
    point along the unit circle for the length of the arc in radians.
    """

    arc_length: float = 0.0
    """The arc length in radians (-2*pi to 2*pi."""

    azimuth: float = 0.0
    """Azimuthal angle in radians (0 to 2*pi).  Represents the longitudinal position around the
    sphere.
    """
    orient: float = 0.0
    """The rotated orientation about the vector from the sphere's origin through the start point
    in radians (-pi to pi.
    """
    polar: float = 0.0
    """Polar angle (colatitude/zenith angle) in radians (0 to pi), measured from the positive
    z-axis following ISO 80000-2:2019 physics convention. 0 is the north pole (+z axis), pi/2
    is the equator (xy-plane), and pi is the south pole (-z axis).
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "UnitSphericalArcType":
        assert isinstance(obj, dict)
        arc_length = from_float(obj.get("arcLength"))
        azimuth = from_float(obj.get("azimuth"))
        orient = from_float(obj.get("orient"))
        polar = from_float(obj.get("polar"))
        return UnitSphericalArcType(arc_length, azimuth, orient, polar)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["arcLength"] = to_float(self.arc_length)
        result["azimuth"] = to_float(self.azimuth)
        result["orient"] = to_float(self.orient)
        result["polar"] = to_float(self.polar)
        return result


@dataclass
class UnitSphericalArcWaveformType(WaveformUnitSphericalArcABC, DataModelHelper):
    """A uniformly-sampled time series of UnitSphericalArc samples, anchored at a start
    timestamp and sampled at a fixed interval.
    """

    arcs: Sequence[UnitSphericalArcType] = ()
    """The uniformly-sampled arc values, in chronological order."""

    dt: PrecisionTimeIntervalType | None = None  # type: ignore[assignment]
    """The fixed interval between consecutive samples."""

    t0: PrecisionTimestampType | None = None  # type: ignore[assignment]
    """The timestamp of the first sample."""

    @classmethod
    def from_dict(cls, obj: Any) -> "UnitSphericalArcWaveformType":
        assert isinstance(obj, dict)
        arcs = from_list(UnitSphericalArcType.from_dict, obj.get("arcs"))
        dt = PrecisionTimeIntervalType.from_dict(obj.get("dt"))
        t0 = PrecisionTimestampType.from_dict(obj.get("t0"))
        return UnitSphericalArcWaveformType(arcs, dt, t0)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["arcs"] = from_list(lambda x: to_class(UnitSphericalArcType, x), self.arcs)
        result["dt"] = to_class(PrecisionTimeIntervalType, self.dt)
        result["t0"] = to_class(PrecisionTimestampType, self.t0)
        return result


@dataclass
class UnitSphericalSmallCircleType(UnitSphericalSmallCircleABC, DataModelHelper):
    """Represents a small circle on a unit sphere in spherical coordinates using physics
    convention.  A small circle is formed by intersecting the sphere with a plane that does
    notpass through the sphere's center, creating a circular path at a constantangular
    distance from a reference point.
    """

    azimuth: float = 0.0
    """Azimuthal angle in radians (0 to 2*pi).  Represents the longitudinal position around the
    sphere.
    """
    polar: float = 0.0
    """Polar angle (colatitude/zenith angle) in radians (0 to pi), measured from the positive
    z-axis following ISO 80000-2:2019 physics convention. 0 is the north pole (+z axis), pi/2
    is the equator (xy-plane), and pi is the south pole (-z axis).
    """
    radius_angle: float = 0.0
    """Angular radius of the small circle in radians.  Represents the angular distance from the
    center point.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "UnitSphericalSmallCircleType":
        assert isinstance(obj, dict)
        azimuth = from_float(obj.get("azimuth"))
        polar = from_float(obj.get("polar"))
        radius_angle = from_float(obj.get("radiusAngle"))
        return UnitSphericalSmallCircleType(azimuth, polar, radius_angle)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["azimuth"] = to_float(self.azimuth)
        result["polar"] = to_float(self.polar)
        result["radiusAngle"] = to_float(self.radius_angle)
        return result


@dataclass
class UnitSphericalSmallCircleWaveformType(WaveformUnitSphericalSmallCircleABC, DataModelHelper):
    """A uniformly-sampled time series of UnitSphericalSmallCircle samples, anchored at a start
    timestamp and sampled at a fixed interval.
    """

    dt: PrecisionTimeIntervalType | None = None  # type: ignore[assignment]
    """The fixed interval between consecutive samples."""

    small_circles: Sequence[UnitSphericalSmallCircleType] = ()
    """The uniformly-sampled small-circle values, in chronological order."""

    t0: PrecisionTimestampType | None = None  # type: ignore[assignment]
    """The timestamp of the first sample."""

    @classmethod
    def from_dict(cls, obj: Any) -> "UnitSphericalSmallCircleWaveformType":
        assert isinstance(obj, dict)
        dt = PrecisionTimeIntervalType.from_dict(obj.get("dt"))
        small_circles = from_list(UnitSphericalSmallCircleType.from_dict, obj.get("smallCircles"))
        t0 = PrecisionTimestampType.from_dict(obj.get("t0"))
        return UnitSphericalSmallCircleWaveformType(dt, small_circles, t0)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["dt"] = to_class(PrecisionTimeIntervalType, self.dt)
        result["smallCircles"] = from_list(
            lambda x: to_class(UnitSphericalSmallCircleType, x), self.small_circles
        )
        result["t0"] = to_class(PrecisionTimestampType, self.t0)
        return result


def numeric_sign_from_dict(s: Any) -> NumericSign:
    return NumericSign(s)


def numeric_sign_to_dict(x: NumericSign) -> Any:
    return to_enum(NumericSign, x)


def timescale_from_dict(s: Any) -> Timescale:
    return Timescale(s)


def timescale_to_dict(x: Timescale) -> Any:
    return to_enum(Timescale, x)


def reference_frame_from_dict(s: Any) -> ReferenceFrame:
    return ReferenceFrame(s)


def reference_frame_to_dict(x: ReferenceFrame) -> Any:
    return to_enum(ReferenceFrame, x)


def precision_time_interval_type_from_dict(s: Any) -> PrecisionTimeIntervalType:
    return PrecisionTimeIntervalType.from_dict(s)


def precision_time_interval_type_to_dict(x: PrecisionTimeIntervalType) -> Any:
    return to_class(PrecisionTimeIntervalType, x)


def precision_timestamp_type_from_dict(s: Any) -> PrecisionTimestampType:
    return PrecisionTimestampType.from_dict(s)


def precision_timestamp_type_to_dict(x: PrecisionTimestampType) -> Any:
    return to_class(PrecisionTimestampType, x)


def position_type_from_dict(s: Any) -> PositionType:
    return PositionType.from_dict(s)


def position_type_to_dict(x: PositionType) -> Any:
    return to_class(PositionType, x)


def quaternion_type_from_dict(s: Any) -> QuaternionType:
    return QuaternionType.from_dict(s)


def quaternion_type_to_dict(x: QuaternionType) -> Any:
    return to_class(QuaternionType, x)


def unit_spherical_arc_type_from_dict(s: Any) -> UnitSphericalArcType:
    return UnitSphericalArcType.from_dict(s)


def unit_spherical_arc_type_to_dict(x: UnitSphericalArcType) -> Any:
    return to_class(UnitSphericalArcType, x)


def unit_spherical_small_circle_type_from_dict(s: Any) -> UnitSphericalSmallCircleType:
    return UnitSphericalSmallCircleType.from_dict(s)


def unit_spherical_small_circle_type_to_dict(x: UnitSphericalSmallCircleType) -> Any:
    return to_class(UnitSphericalSmallCircleType, x)


def spatial_transform_type_from_dict(s: Any) -> SpatialTransformType:
    return SpatialTransformType.from_dict(s)


def spatial_transform_type_to_dict(x: SpatialTransformType) -> Any:
    return to_class(SpatialTransformType, x)


def position_waveform_type_from_dict(s: Any) -> PositionWaveformType:
    return PositionWaveformType.from_dict(s)


def position_waveform_type_to_dict(x: PositionWaveformType) -> Any:
    return to_class(PositionWaveformType, x)


def quaternion_waveform_type_from_dict(s: Any) -> QuaternionWaveformType:
    return QuaternionWaveformType.from_dict(s)


def quaternion_waveform_type_to_dict(x: QuaternionWaveformType) -> Any:
    return to_class(QuaternionWaveformType, x)


def spatial_transform_waveform_type_from_dict(s: Any) -> SpatialTransformWaveformType:
    return SpatialTransformWaveformType.from_dict(s)


def spatial_transform_waveform_type_to_dict(x: SpatialTransformWaveformType) -> Any:
    return to_class(SpatialTransformWaveformType, x)


def scalar_waveform_type_from_dict(s: Any) -> ScalarWaveformType:
    return ScalarWaveformType.from_dict(s)


def scalar_waveform_type_to_dict(x: ScalarWaveformType) -> Any:
    return to_class(ScalarWaveformType, x)


def unit_spherical_arc_waveform_type_from_dict(s: Any) -> UnitSphericalArcWaveformType:
    return UnitSphericalArcWaveformType.from_dict(s)


def unit_spherical_arc_waveform_type_to_dict(x: UnitSphericalArcWaveformType) -> Any:
    return to_class(UnitSphericalArcWaveformType, x)


def unit_spherical_small_circle_waveform_type_from_dict(
    s: Any,
) -> UnitSphericalSmallCircleWaveformType:
    return UnitSphericalSmallCircleWaveformType.from_dict(s)


def unit_spherical_small_circle_waveform_type_to_dict(
    x: UnitSphericalSmallCircleWaveformType,
) -> Any:
    return to_class(UnitSphericalSmallCircleWaveformType, x)
