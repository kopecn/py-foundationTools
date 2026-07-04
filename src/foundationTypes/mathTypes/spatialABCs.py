"""Tier-2 shared abstractions for positions, quaternions, and 6-DOF poses.

The goal of this module is to give **SE(3), the Lie group of 3D rigid body
transformations (rotation + translation)**, a storage-independent data
contract. :class:`PositionABC` is the translation part (:math:`\\mathbb{R}^3`),
:class:`QuaternionABC` is the rotation part (a unit quaternion is the standard
double cover of :math:`SO(3)`, the rotation subgroup), and
:class:`SpatialTransformABC` composes the two into one SE(3) group element — a pose.
(SE(3) itself is the group; its Lie algebra, conventionally written
lowercase ``se(3)``, is the tangent space at the identity — e.g. a
twist/velocity — and is out of scope for these accessor contracts.)

See ``.claude/specs/mathTypeTiers.md``. :class:`PositionABC`, :class:`QuaternionABC`,
and :class:`SpatialTransformABC` are the shared accessor + serialization contracts
(inherited by the codegen ``PositionType`` / ``QuaternionType`` /
``SpatialTransformType``). The math contracts (group composition, inverse, etc.)
are in :mod:`foundationTypes.mathTypes.positionVectorMathLike`,
:mod:`foundationTypes.mathTypes.quaternionMathLike`, and
:mod:`foundationTypes.mathTypes.spatialPoseMathLike`.
"""

from abc import ABC, abstractmethod
from typing import Any

from foundationTypes.data_model_helper import DataModelHelper


class PositionABC(ABC, DataModelHelper):
    """Shared, storage-independent abstraction for a 3D position (``x``, ``y``, ``z``).

    This is the translation component of an SE(3) rigid body transformation —
    a point/offset in :math:`\\mathbb{R}^3`.
    """

    @property
    @abstractmethod
    def x(self) -> float:
        """The x-axis (first Cartesian) component."""

    @property
    @abstractmethod
    def y(self) -> float:
        """The y-axis (second Cartesian) component."""

    @property
    @abstractmethod
    def z(self) -> float:
        """The z-axis (third Cartesian) component."""

    def to_dict(self) -> dict[str, Any]:
        return {"x": self.x, "y": self.y, "z": self.z}

    @classmethod
    @abstractmethod
    def from_dict(cls, obj: Any) -> "PositionABC":
        """Construct from a ``{"x", "y", "z"}`` dict."""


class QuaternionABC(ABC, DataModelHelper):
    """Shared, storage-independent abstraction for a quaternion.

    A quaternion has a scalar (real) component ``w`` and a vector (imaginary)
    part ``x``, ``y``, ``z``. Implementations may back these with plain fields
    (the codegen ``QuaternionType``) or a native representation such as
    ``np.quaternion`` (a downstream math engine); this contract does not care.

    This is the rotation component of an SE(3) rigid body transformation. A
    unit quaternion is the standard double cover of :math:`SO(3)`, the
    rotation subgroup of SE(3) — every rotation corresponds to exactly two
    antipodal unit quaternions (``q`` and ``-q``).
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


class SpatialTransformABC(ABC, DataModelHelper):
    """Shared abstraction for a 6-DOF pose (position + orientation).

    A pose is one element of SE(3), the Lie group of 3D rigid body
    transformations: a translation (:class:`PositionABC`) composed with a
    rotation (:class:`QuaternionABC`).
    """

    @property
    @abstractmethod
    def position(self) -> PositionABC:
        """The Cartesian position component of the pose."""

    @property
    @abstractmethod
    def orientation(self) -> QuaternionABC:
        """The quaternion orientation component of the pose."""

    def to_dict(self) -> dict[str, Any]:
        return {
            "position": self.position.to_dict(),
            "orientation": self.orientation.to_dict(),
        }

    @classmethod
    @abstractmethod
    def from_dict(cls, obj: Any) -> "SpatialTransformABC":
        """Construct from a ``{"position", "orientation"}`` dict."""
