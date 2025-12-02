from abc import ABC, abstractmethod
from foundationTypes.dataModelHelper import DataModelHelper
from typing import Any, TypeVar, Type


T = TypeVar("T", bound="QuaternionType")


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def to_float(x: Any) -> float:
    assert isinstance(x, (int, float))
    return x


class QuaternionType(ABC, DataModelHelper):
    """Abstract base class for quaternion representations.

    A quaternion is a mathematical entity used to represent rotations in 3D space.
    It consists of four components: w (scalar/real part) and x, y, z (vector/imaginary parts).

    This ABC defines the interface that all quaternion implementations must follow,
    providing standard serialization/deserialization through DataModelHelper.
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

    @classmethod
    @abstractmethod
    def from_components(cls: Type[T], w: float, x: float, y: float, z: float) -> T:
        """Create a quaternion instance from individual w, x, y, z components.

        Args:
            w: The scalar (real) component
            x: The x component of the vector part
            y: The y component of the vector part
            z: The z component of the vector part

        Returns:
            A concrete QuaternionType instance of the calling class type
        """

    @staticmethod
    def from_dict(obj: Any) -> "QuaternionType":
        """
        Must be implemented by child class.  dictionary would have the following structure:
        {w:float,x:float,y:float,z:float}
        """
        raise NotImplementedError("from_dict must be implemented by subclasses")

    def to_dict(self) -> dict:
        """Convert the quaternion instance to a dictionary representation.

        Returns:
            Dictionary with 'w', 'x', 'y', 'z' keys
        """
        result: dict = {}
        result["w"] = to_float(self.w)
        result["x"] = to_float(self.x)
        result["y"] = to_float(self.y)
        result["z"] = to_float(self.z)
        return result
