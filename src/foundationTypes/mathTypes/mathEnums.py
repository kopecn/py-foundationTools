"""Shared Math-domain enumerations.

Hand-written leaf module (depends on nothing in this package) so both the
generated ``MathTypes.py`` and the hand-written tier modules
(``precisionTimeInterval.py`` / ``precisionTimestamp.py``) can import these
without a circular import. Values mirror the JSON Schemas under
``schema/schemas/Math/`` (``NumericSign``, ``Timescale``, ``ReferenceFrame``);
the codegen pipeline strips quicktype's inline copies and imports these instead.
"""

from enum import Enum


class NumericSign(Enum):
    """The sign of a numeric value: positive, negative, or zero."""

    NEGATIVE = "negative"
    POSITIVE = "positive"
    ZERO = "zero"


class ReferenceFrame(Enum):
    """Spatial reference frame for precision timestamps (relativistic effects).

    Mirrors the FoundationTypes Swift ReferenceFrame enum.
    """

    EARTH_CENTER = "EarthCenter"
    HELIOCENTRIC = "Heliocentric"
    LUNAR_CENTER = "LunarCenter"
    SOLAR_SYSTEM_BARYCENTER = "SolarSystemBarycenter"
    TOPOCENTRIC = "Topocentric"


class Timescale(Enum):
    """Time scale specification for precision timestamps (TAI, UTC, GPS-derived).

    Mirrors the FoundationTypes Swift Timescale enum.
    """

    TAI = "TAI"
    TCB = "TCB"
    TCG = "TCG"
    TDB = "TDB"
    TT = "TT"
    UT1 = "UT1"
    UTC = "UTC"
