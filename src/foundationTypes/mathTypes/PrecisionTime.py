# =============================================================================
# AUTO-GENERATED FILE — DO NOT EDIT
# Generated from JSON Schema via quicktype. Any manual edits will be
# overwritten the next time codegen runs (make codegen-all).
# To modify, update the source schema in schema/schemas/ and re-run codegen.
# =============================================================================

from dataclasses import dataclass
from enum import Enum
from typing import Any, TypeVar

from foundationTypes.dataModelHelper import (
    DataModelHelper,
    from_int,
    from_none,
    from_union,
    to_class,
    to_enum,
)

T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


class NumericSign(Enum):
    """The sign of a numeric value: positive, negative, or zero.

    The sign of the time interval.

    The sign of the timestamp.
    """

    NEGATIVE = "negative"
    POSITIVE = "positive"
    ZERO = "zero"


@dataclass
class _PrecisionTimeIntervalType(DataModelHelper):
    """A time interval with attosecond precision. Stores seconds and attoseconds as unsigned
    integers with an explicit sign, avoiding floating-point precision loss over large spans.
    """

    attoseconds: int
    """The sub-second component in attoseconds (10^-18 s). Valid range: 0 to
    999_999_999_999_999_999.
    """
    seconds: int
    """The whole-seconds component of the interval (unsigned)."""

    sign: NumericSign
    """The sign of the time interval."""

    @classmethod
    def from_dict(cls, obj: Any) -> "_PrecisionTimeIntervalType":
        assert isinstance(obj, dict)
        attoseconds = from_int(obj.get("attoseconds"))
        seconds = from_int(obj.get("seconds"))
        sign = NumericSign(obj.get("sign"))
        return _PrecisionTimeIntervalType(attoseconds, seconds, sign)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["attoseconds"] = from_int(self.attoseconds)
        result["seconds"] = from_int(self.seconds)
        result["sign"] = to_enum(NumericSign, self.sign)
        return result


class ReferenceFrame(Enum):
    """Spatial reference frame for precision timestamps, accounting for relativistic effects.
    Mirrors the FoundationTypes Swift ReferenceFrame enum.

    The reference frame for the timestamp (e.g. 'EarthCenter', 'SolarSystemBarycenter').
    """

    EARTH_CENTER = "EarthCenter"
    HELIOCENTRIC = "Heliocentric"
    LUNAR_CENTER = "LunarCenter"
    SOLAR_SYSTEM_BARYCENTER = "SolarSystemBarycenter"
    TOPOCENTRIC = "Topocentric"


class Timescale(Enum):
    """Time scale specification for precision timestamps (e.g. TAI, UTC, GPS-derived scales).
    Mirrors the FoundationTypes Swift Timescale enum.

    The timescale of the timestamp (e.g. 'TAI', 'UTC', 'GPS').
    """

    TAI = "TAI"
    TCB = "TCB"
    TCG = "TCG"
    TDB = "TDB"
    TT = "TT"
    UT1 = "UT1"
    UTC = "UTC"


@dataclass
class _PrecisionTimestampType(DataModelHelper):
    """An absolute timestamp with attosecond precision. Stores seconds and attoseconds as
    unsigned integers with an explicit sign. Optionally carries a timescale, reference frame,
    and measurement uncertainty (in attoseconds).
    """

    attoseconds: int
    """The sub-second component in attoseconds (10^-18 s). Valid range: 0 to
    999_999_999_999_999_999.
    """
    seconds: int
    """The whole-seconds component of the timestamp (unsigned)."""

    sign: NumericSign
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
    def from_dict(cls, obj: Any) -> "_PrecisionTimestampType":
        assert isinstance(obj, dict)
        attoseconds = from_int(obj.get("attoseconds"))
        seconds = from_int(obj.get("seconds"))
        sign = NumericSign(obj.get("sign"))
        reference_frame = from_union([ReferenceFrame, from_none], obj.get("referenceFrame"))
        timescale = from_union([Timescale, from_none], obj.get("timescale"))
        uncertainty = from_union([from_int, from_none], obj.get("uncertainty"))
        return _PrecisionTimestampType(
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


def precision_time_interval_type_from_dict(s: Any) -> _PrecisionTimeIntervalType:
    return _PrecisionTimeIntervalType.from_dict(s)


def precision_time_interval_type_to_dict(x: _PrecisionTimeIntervalType) -> Any:
    return to_class(_PrecisionTimeIntervalType, x)


def precision_timestamp_type_from_dict(s: Any) -> _PrecisionTimestampType:
    return _PrecisionTimestampType.from_dict(s)


def precision_timestamp_type_to_dict(x: _PrecisionTimestampType) -> Any:
    return to_class(_PrecisionTimestampType, x)
