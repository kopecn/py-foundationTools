"""Tier-2 shared abstraction for quaternions.

See ``.claude/specs/mathTypeTiers.md``. :class:`QuaternionABC` is the shared,
storage-independent accessor + serialization contract; the codegen concrete
``QuaternionType`` (in ``MathTypes.py``) inherits it. The math-operation contract
lives in :mod:`foundationTypes.mathTypes.quaternionMathLike`.
"""

from abc import ABC, abstractmethod
from typing import Any

from foundationTypes.dataModelHelper import DataModelHelper


class QuaternionABC(ABC, DataModelHelper):
    """Shared, storage-independent abstraction for a quaternion.

    A quaternion has a scalar (real) component ``w`` and a vector (imaginary)
    part ``x``, ``y``, ``z``. Implementations may back these with plain fields
    (the codegen ``QuaternionType``) or a native representation such as
    ``np.quaternion`` (a downstream math engine); this contract does not care.
    """

    @property
    @abstractmethod
    def w(self) -> float:
        """The scalar (real) component of the quaternion."""

    @property
    @abstractmethod
    def x(self) -> float:
        """The x component of the quaternion's vector (imaginary) part."""

    @property
    @abstractmethod
    def y(self) -> float:
        """The y component of the quaternion's vector (imaginary) part."""

    @property
    @abstractmethod
    def z(self) -> float:
        """The z component of the quaternion's vector (imaginary) part."""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain ``{"w", "x", "y", "z"}`` dict."""
        return {"w": self.w, "x": self.x, "y": self.y, "z": self.z}

    @classmethod
    @abstractmethod
    def from_dict(cls, obj: Any) -> "QuaternionABC":
        """Construct from a ``{"w", "x", "y", "z"}`` dict."""
