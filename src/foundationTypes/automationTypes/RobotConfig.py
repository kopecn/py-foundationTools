# =============================================================================
# AUTO-GENERATED FILE — DO NOT EDIT
# Generated from JSON Schema via quicktype. Any manual edits will be
# overwritten the next time codegen runs (make codegen-all).
# To modify, update the source schema in schema/schemas/ and re-run codegen.
# =============================================================================

from enum import Enum
from dataclasses import dataclass
from foundationTypes.data_model_helper import (
    DataModelHelper,
    from_dict,
    from_float,
    from_list,
    from_none,
    from_str,
    from_union,
    to_class,
    to_enum,
    to_float,
)
from typing import Optional, Any, Union, List, Dict, TypeVar, Type, Callable, cast

T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


class ComponentKind(Enum):
    SUBMECHANISM = "submechanism"


@dataclass
class Mount(DataModelHelper):
    """Where this component attaches within its parent, by frame and/or named interface."""

    frame: Optional[str] = None
    """The parent-side frame this component is mounted at."""

    interface: Optional[str] = None
    """The parent-side named interface this component is mounted at."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Mount":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        frame = from_union([from_str, from_none], obj.get("frame"))
        interface = from_union([from_str, from_none], obj.get("interface"))
        return Mount(frame, interface)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.frame is not None:
            result["frame"] = from_union([from_str, from_none], self.frame)
        if self.interface is not None:
            result["interface"] = from_union([from_str, from_none], self.interface)
        return result


class Unit(Enum):
    """Supported physical units. A mechanism's top-level `units` establishes the default unit
    system; individual quantities may override it.

    The unit this coordinate's value is expressed in.

    The default unit for angle quantities.

    The default unit for length quantities.

    The default unit for mass quantities.

    The default unit for time quantities.
    """

    DEG = "deg"
    KG = "kg"
    M = "m"
    MM = "mm"
    N = "N"
    NM = "Nm"
    RAD = "rad"
    S = "s"


@dataclass
class Quantity(DataModelHelper):
    value: float
    unit: Optional[Unit] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "Quantity":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        value = from_float(obj.get("value"))
        unit = from_union([Unit, from_none], obj.get("unit"))
        return Quantity(value, unit)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["value"] = to_float(self.value)
        if self.unit is not None:
            result["unit"] = from_union([lambda x: to_enum(Unit, x), from_none], self.unit)
        return result


@dataclass
class AxisAngle(DataModelHelper):
    """A rotation expressed as a unit axis and an angle of rotation about it."""

    angle: Union[float, Quantity]
    """The angle of rotation about the axis."""

    axis: List[float]
    """The rotation axis, expressed in the local frame appropriate to its context."""

    @classmethod
    def from_dict(cls, obj: Any) -> "AxisAngle":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        angle = from_union([from_float, Quantity.from_dict], obj.get("angle"))
        axis = from_list(from_float, obj.get("axis"))
        return AxisAngle(angle, axis)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["angle"] = from_union([to_float, lambda x: to_class(Quantity, x)], self.angle)
        result["axis"] = from_list(to_float, self.axis)
        return result


@dataclass
class Quaternion(DataModelHelper):
    """A unit quaternion rotation, in x/y/z/w (vector, scalar) order."""

    w: float
    """The scalar (real) component."""

    x: float
    """The x (vector) component."""

    y: float
    """The y (vector) component."""

    z: float
    """The z (vector) component."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Quaternion":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        w = from_float(obj.get("w"))
        x = from_float(obj.get("x"))
        y = from_float(obj.get("y"))
        z = from_float(obj.get("z"))
        return Quaternion(w, x, y, z)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["w"] = to_float(self.w)
        result["x"] = to_float(self.x)
        result["y"] = to_float(self.y)
        result["z"] = to_float(self.z)
        return result


@dataclass
class RotationMatrix(DataModelHelper):
    values: List[float]
    """Row-major 3x3 rotation matrix: [r00, r01, r02, r10, r11, r12, r20, r21, r22]."""

    @classmethod
    def from_dict(cls, obj: Any) -> "RotationMatrix":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        values = from_list(from_float, obj.get("values"))
        return RotationMatrix(values)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["values"] = from_list(to_float, self.values)
        return result


class Convention(Enum):
    """The explicit rotation-order convention roll/pitch/yaw are composed under. Required to
    disambiguate RPY, which has no universal convention.
    """

    EXTRINSIC_XYZ = "extrinsic_xyz"
    INTRINSIC_ZYX = "intrinsic_zyx"


@dataclass
class Rpy(DataModelHelper):
    """A roll/pitch/yaw rotation, with an explicit composition convention."""

    pitch: Union[float, Quantity]
    """Rotation about the pitch axis."""

    roll: Union[float, Quantity]
    """Rotation about the roll axis."""

    yaw: Union[float, Quantity]
    """Rotation about the yaw axis."""

    convention: Optional[Convention] = None
    """The explicit rotation-order convention roll/pitch/yaw are composed under. Required to
    disambiguate RPY, which has no universal convention.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "Rpy":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        pitch = from_union([from_float, Quantity.from_dict], obj.get("pitch"))
        roll = from_union([from_float, Quantity.from_dict], obj.get("roll"))
        yaw = from_union([from_float, Quantity.from_dict], obj.get("yaw"))
        convention = from_union([Convention, from_none], obj.get("convention"))
        return Rpy(pitch, roll, yaw, convention)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["pitch"] = from_union([to_float, lambda x: to_class(Quantity, x)], self.pitch)
        result["roll"] = from_union([to_float, lambda x: to_class(Quantity, x)], self.roll)
        result["yaw"] = from_union([to_float, lambda x: to_class(Quantity, x)], self.yaw)
        if self.convention is not None:
            result["convention"] = from_union(
                [lambda x: to_enum(Convention, x), from_none], self.convention
            )
        return result


@dataclass
class Rotation(DataModelHelper):
    """The rotation component of this transform.

    Exactly one unambiguous rotation representation.
    """

    quaternion: Optional[Quaternion] = None
    rotation_matrix: Optional[RotationMatrix] = None
    axis_angle: Optional[AxisAngle] = None
    rpy: Optional[Rpy] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "Rotation":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        quaternion = from_union([Quaternion.from_dict, from_none], obj.get("quaternion"))
        rotation_matrix = from_union(
            [RotationMatrix.from_dict, from_none], obj.get("rotation_matrix")
        )
        axis_angle = from_union([AxisAngle.from_dict, from_none], obj.get("axis_angle"))
        rpy = from_union([Rpy.from_dict, from_none], obj.get("rpy"))
        return Rotation(quaternion, rotation_matrix, axis_angle, rpy)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.quaternion is not None:
            result["quaternion"] = from_union(
                [lambda x: to_class(Quaternion, x), from_none], self.quaternion
            )
        if self.rotation_matrix is not None:
            result["rotation_matrix"] = from_union(
                [lambda x: to_class(RotationMatrix, x), from_none], self.rotation_matrix
            )
        if self.axis_angle is not None:
            result["axis_angle"] = from_union(
                [lambda x: to_class(AxisAngle, x), from_none], self.axis_angle
            )
        if self.rpy is not None:
            result["rpy"] = from_union([lambda x: to_class(Rpy, x), from_none], self.rpy)
        return result


@dataclass
class Transform(DataModelHelper):
    """The relative pose of this component with respect to its mount point.

    The single canonical transform model, reused everywhere a relative pose is needed.

    The relative pose between the parent and child interfaces at this connection.

    The relative pose of this frame with respect to its attachment point.
    """

    rotation: Optional[Rotation] = None
    """The rotation component of this transform."""

    translation: Optional[List[float]] = None
    """The translation component of this transform."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Transform":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        rotation = from_union([Rotation.from_dict, from_none], obj.get("rotation"))
        translation = from_union(
            [lambda x: from_list(from_float, x), from_none], obj.get("translation")
        )
        return Transform(rotation, translation)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.rotation is not None:
            result["rotation"] = from_union(
                [lambda x: to_class(Rotation, x), from_none], self.rotation
            )
        if self.translation is not None:
            result["translation"] = from_union(
                [lambda x: from_list(to_float, x), from_none], self.translation
            )
        return result


@dataclass
class Inertia(DataModelHelper):
    """This body's rotational inertia tensor about its own frame. Optional; not required for a
    purely kinematic definition.
    """

    ixx: Optional[Union[float, Quantity]] = None
    """The xx moment of inertia."""

    ixy: Optional[Union[float, Quantity]] = None
    """The xy product of inertia."""

    ixz: Optional[Union[float, Quantity]] = None
    """The xz product of inertia."""

    iyy: Optional[Union[float, Quantity]] = None
    """The yy moment of inertia."""

    iyz: Optional[Union[float, Quantity]] = None
    """The yz product of inertia."""

    izz: Optional[Union[float, Quantity]] = None
    """The zz moment of inertia."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Inertia":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        ixx = from_union([from_float, Quantity.from_dict, from_none], obj.get("ixx"))
        ixy = from_union([from_float, Quantity.from_dict, from_none], obj.get("ixy"))
        ixz = from_union([from_float, Quantity.from_dict, from_none], obj.get("ixz"))
        iyy = from_union([from_float, Quantity.from_dict, from_none], obj.get("iyy"))
        iyz = from_union([from_float, Quantity.from_dict, from_none], obj.get("iyz"))
        izz = from_union([from_float, Quantity.from_dict, from_none], obj.get("izz"))
        return Inertia(ixx, ixy, ixz, iyy, iyz, izz)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.ixx is not None:
            result["ixx"] = from_union(
                [to_float, lambda x: to_class(Quantity, x), from_none], self.ixx
            )
        if self.ixy is not None:
            result["ixy"] = from_union(
                [to_float, lambda x: to_class(Quantity, x), from_none], self.ixy
            )
        if self.ixz is not None:
            result["ixz"] = from_union(
                [to_float, lambda x: to_class(Quantity, x), from_none], self.ixz
            )
        if self.iyy is not None:
            result["iyy"] = from_union(
                [to_float, lambda x: to_class(Quantity, x), from_none], self.iyy
            )
        if self.iyz is not None:
            result["iyz"] = from_union(
                [to_float, lambda x: to_class(Quantity, x), from_none], self.iyz
            )
        if self.izz is not None:
            result["izz"] = from_union(
                [to_float, lambda x: to_class(Quantity, x), from_none], self.izz
            )
        return result


class BodyKind(Enum):
    BODY = "body"


@dataclass
class Body(DataModelHelper):
    """A rigid body (link) in a mechanism."""

    id: str
    """Stable identifier for this body."""

    collision: Optional[Dict[str, Any]] = None
    """Application-defined collision-geometry data for this body."""

    inertia: Optional[Inertia] = None
    """This body's rotational inertia tensor about its own frame. Optional; not required for a
    purely kinematic definition.
    """
    kind: Optional[BodyKind] = None
    """Self-describing discriminator; always "body" for a Body."""

    mass: Optional[Union[float, Quantity]] = None
    """This body's mass. Optional; not required for a purely kinematic definition."""

    metadata: Optional[Dict[str, Any]] = None
    """Opaque, application-defined data carried alongside this body."""

    name: Optional[str] = None
    """A human-readable name for this body."""

    visual: Optional[Dict[str, Any]] = None
    """Application-defined visual representation data for this body (e.g. a mesh reference)."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Body":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        id = from_str(obj.get("id"))
        collision = from_union(
            [lambda x: from_dict(lambda x: x, x), from_none], obj.get("collision")
        )
        inertia = from_union([Inertia.from_dict, from_none], obj.get("inertia"))
        kind = from_union([BodyKind, from_none], obj.get("kind"))
        mass = from_union([from_float, Quantity.from_dict, from_none], obj.get("mass"))
        metadata = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("metadata"))
        name = from_union([from_str, from_none], obj.get("name"))
        visual = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("visual"))
        return Body(id, collision, inertia, kind, mass, metadata, name, visual)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["id"] = from_str(self.id)
        if self.collision is not None:
            result["collision"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.collision
            )
        if self.inertia is not None:
            result["inertia"] = from_union(
                [lambda x: to_class(Inertia, x), from_none], self.inertia
            )
        if self.kind is not None:
            result["kind"] = from_union([lambda x: to_enum(BodyKind, x), from_none], self.kind)
        if self.mass is not None:
            result["mass"] = from_union(
                [to_float, lambda x: to_class(Quantity, x), from_none], self.mass
            )
        if self.metadata is not None:
            result["metadata"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.metadata
            )
        if self.name is not None:
            result["name"] = from_union([from_str, from_none], self.name)
        if self.visual is not None:
            result["visual"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.visual
            )
        return result


class Topology(Enum):
    """The mechanism's high-level kinematic topology."""

    CLOSED_CHAIN = "closed_chain"
    COMPOSITE = "composite"
    HYBRID = "hybrid"
    OPEN_CHAIN = "open_chain"
    PARALLEL = "parallel"


@dataclass
class Classification(DataModelHelper):
    """Descriptive, non-structural classification of this mechanism.

    Descriptive, non-exclusive classification. Multiple architectures/functions/tags may
    apply simultaneously; none of these values gate which structural fields
    (bodies/joints/constraints/...) are usable.
    """

    architecture: Optional[List[str]] = None
    """Extensible; a composite mechanism may list multiple architectures (e.g. ["parallel",
    "serial"]).
    """
    functions: Optional[List[str]] = None
    """Extensible functional roles (e.g. "manipulator")."""

    name: Optional[str] = None
    """A human-readable name for this classification (e.g. "Stewart Platform")."""

    tags: Optional[List[str]] = None
    """Extensible free-form tags (e.g. "gimbal", "wrist")."""

    topology: Optional[Topology] = None
    """The mechanism's high-level kinematic topology."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Classification":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        architecture = from_union(
            [lambda x: from_list(from_str, x), from_none], obj.get("architecture")
        )
        functions = from_union([lambda x: from_list(from_str, x), from_none], obj.get("functions"))
        name = from_union([from_str, from_none], obj.get("name"))
        tags = from_union([lambda x: from_list(from_str, x), from_none], obj.get("tags"))
        topology = from_union([Topology, from_none], obj.get("topology"))
        return Classification(architecture, functions, name, tags, topology)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.architecture is not None:
            result["architecture"] = from_union(
                [lambda x: from_list(from_str, x), from_none], self.architecture
            )
        if self.functions is not None:
            result["functions"] = from_union(
                [lambda x: from_list(from_str, x), from_none], self.functions
            )
        if self.name is not None:
            result["name"] = from_union([from_str, from_none], self.name)
        if self.tags is not None:
            result["tags"] = from_union([lambda x: from_list(from_str, x), from_none], self.tags)
        if self.topology is not None:
            result["topology"] = from_union(
                [lambda x: to_enum(Topology, x), from_none], self.topology
            )
        return result


@dataclass
class Connection(DataModelHelper):
    """An explicit connection between two components, by named interface, so a child mechanism
    need not know in advance what it will be mounted on.
    """

    child: str
    """Id of the child-side component being connected."""

    id: str
    """Stable identifier for this connection."""

    parent: str
    """Id of the parent-side component being connected."""

    child_interface: Optional[str] = None
    """Name of the interface on the child component this connection attaches to."""

    metadata: Optional[Dict[str, Any]] = None
    """Opaque, application-defined data carried alongside this connection."""

    parent_interface: Optional[str] = None
    """Name of the interface on the parent component this connection attaches to."""

    transform: Optional[Transform] = None
    """The relative pose between the parent and child interfaces at this connection."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Connection":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        child = from_str(obj.get("child"))
        id = from_str(obj.get("id"))
        parent = from_str(obj.get("parent"))
        child_interface = from_union([from_str, from_none], obj.get("child_interface"))
        metadata = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("metadata"))
        parent_interface = from_union([from_str, from_none], obj.get("parent_interface"))
        transform = from_union([Transform.from_dict, from_none], obj.get("transform"))
        return Connection(child, id, parent, child_interface, metadata, parent_interface, transform)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["child"] = from_str(self.child)
        result["id"] = from_str(self.id)
        result["parent"] = from_str(self.parent)
        if self.child_interface is not None:
            result["child_interface"] = from_union([from_str, from_none], self.child_interface)
        if self.metadata is not None:
            result["metadata"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.metadata
            )
        if self.parent_interface is not None:
            result["parent_interface"] = from_union([from_str, from_none], self.parent_interface)
        if self.transform is not None:
            result["transform"] = from_union(
                [lambda x: to_class(Transform, x), from_none], self.transform
            )
        return result


@dataclass
class Constraint(DataModelHelper):
    """A generic, extensible constraint. This schema describes constraints; it does not evaluate
    them mathematically.
    """

    id: str
    """Stable identifier for this constraint."""

    type: str
    """Recommended values: loop_closure, coincident, fixed_distance, fixed_orientation.
    Additional application-defined constraint types are permitted.
    """
    metadata: Optional[Dict[str, Any]] = None
    """Opaque, application-defined data carried alongside this constraint."""

    parameters: Optional[Dict[str, Any]] = None
    """Constraint-specific numeric or configuration data (e.g. a fixed_distance value)."""

    references: Optional[List[str]] = None
    """Ids of the bodies, frames, or other entities this constraint relates."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Constraint":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        id = from_str(obj.get("id"))
        type = from_str(obj.get("type"))
        metadata = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("metadata"))
        parameters = from_union(
            [lambda x: from_dict(lambda x: x, x), from_none], obj.get("parameters")
        )
        references = from_union(
            [lambda x: from_list(from_str, x), from_none], obj.get("references")
        )
        return Constraint(id, type, metadata, parameters, references)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["id"] = from_str(self.id)
        result["type"] = from_str(self.type)
        if self.metadata is not None:
            result["metadata"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.metadata
            )
        if self.parameters is not None:
            result["parameters"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.parameters
            )
        if self.references is not None:
            result["references"] = from_union(
                [lambda x: from_list(from_str, x), from_none], self.references
            )
        return result


@dataclass
class Frame(DataModelHelper):
    """A first-class frame, explicitly attached to exactly one of a body, a joint, a component,
    or an interface.
    """

    id: str
    """Stable identifier for this frame."""

    body: Optional[str] = None
    """Id of the body this frame is attached to."""

    component: Optional[str] = None
    """Id of the component this frame is attached to."""

    interface: Optional[str] = None
    """Id of the interface this frame is attached to."""

    joint: Optional[str] = None
    """Id of the joint this frame is attached to."""

    metadata: Optional[Dict[str, Any]] = None
    """Opaque, application-defined data carried alongside this frame."""

    transform: Optional[Transform] = None
    """The relative pose of this frame with respect to its attachment point."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Frame":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        id = from_str(obj.get("id"))
        body = from_union([from_str, from_none], obj.get("body"))
        component = from_union([from_str, from_none], obj.get("component"))
        interface = from_union([from_str, from_none], obj.get("interface"))
        joint = from_union([from_str, from_none], obj.get("joint"))
        metadata = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("metadata"))
        transform = from_union([Transform.from_dict, from_none], obj.get("transform"))
        return Frame(id, body, component, interface, joint, metadata, transform)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["id"] = from_str(self.id)
        if self.body is not None:
            result["body"] = from_union([from_str, from_none], self.body)
        if self.component is not None:
            result["component"] = from_union([from_str, from_none], self.component)
        if self.interface is not None:
            result["interface"] = from_union([from_str, from_none], self.interface)
        if self.joint is not None:
            result["joint"] = from_union([from_str, from_none], self.joint)
        if self.metadata is not None:
            result["metadata"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.metadata
            )
        if self.transform is not None:
            result["transform"] = from_union(
                [lambda x: to_class(Transform, x), from_none], self.transform
            )
        return result


@dataclass
class Interface(DataModelHelper):
    """A named, explicit mounting/reference point on a mechanism, exposed by frame so other
    mechanisms can connect to it without relying on naming conventions.
    """

    frame: str
    """Id of the frame this interface exposes."""

    metadata: Optional[Dict[str, Any]] = None
    """Opaque, application-defined data carried alongside this interface."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Interface":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        frame = from_str(obj.get("frame"))
        metadata = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("metadata"))
        return Interface(frame, metadata)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["frame"] = from_str(self.frame)
        if self.metadata is not None:
            result["metadata"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.metadata
            )
        return result


@dataclass
class JointCoordinate(DataModelHelper):
    """One generalized coordinate (degree of freedom variable) of a joint."""

    id: str
    """Stable identifier for this coordinate, referenced elsewhere (e.g. by a DH parameter's
    `variable`).
    """
    unit: Optional[Unit] = None
    """The unit this coordinate's value is expressed in."""

    @classmethod
    def from_dict(cls, obj: Any) -> "JointCoordinate":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        id = from_str(obj.get("id"))
        unit = from_union([Unit, from_none], obj.get("unit"))
        return JointCoordinate(id, unit)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["id"] = from_str(self.id)
        if self.unit is not None:
            result["unit"] = from_union([lambda x: to_enum(Unit, x), from_none], self.unit)
        return result


@dataclass
class Joint(DataModelHelper):
    """A kinematic joint. Structural fields beyond the base shape are activated by `type` for
    the recognized joint types; unrecognized types receive only the base shape.

    Fields common to every joint, regardless of type.
    """

    id: str
    """Stable identifier for this joint."""

    type: str
    """Recommended values: revolute, prismatic, helical, spherical, universal, planar, fixed.
    Additional application-defined joint types are permitted; a joint of an unrecognized type
    is validated against this base shape only, with any type-specific data carried in
    `metadata`.
    """
    child: Optional[str] = None
    """Id of the body on the child side of this joint."""

    coordinates: Optional[List[JointCoordinate]] = None
    """This joint's generalized coordinates (its degrees of freedom's variables)."""

    metadata: Optional[Dict[str, Any]] = None
    """Opaque, application-defined data carried alongside this joint."""

    parent: Optional[str] = None
    """Id of the body on the parent side of this joint."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Joint":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        id = from_str(obj.get("id"))
        type = from_str(obj.get("type"))
        child = from_union([from_str, from_none], obj.get("child"))
        coordinates = from_union(
            [lambda x: from_list(JointCoordinate.from_dict, x), from_none], obj.get("coordinates")
        )
        metadata = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("metadata"))
        parent = from_union([from_str, from_none], obj.get("parent"))
        return Joint(id, type, child, coordinates, metadata, parent)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["id"] = from_str(self.id)
        result["type"] = from_str(self.type)
        if self.child is not None:
            result["child"] = from_union([from_str, from_none], self.child)
        if self.coordinates is not None:
            result["coordinates"] = from_union(
                [lambda x: from_list(lambda x: to_class(JointCoordinate, x), x), from_none],
                self.coordinates,
            )
        if self.metadata is not None:
            result["metadata"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.metadata
            )
        if self.parent is not None:
            result["parent"] = from_union([from_str, from_none], self.parent)
        return result


@dataclass
class KinematicRepresentation(DataModelHelper):
    """One kinematic representation of the enclosing mechanism. A mechanism may carry more than
    one representation simultaneously.

    Fields common to every kinematic representation, regardless of type.
    """

    type: str
    """Recommended values: dh, modified_dh, poe, constraint_based. Additional
    application-defined representations are permitted.
    """
    metadata: Optional[Dict[str, Any]] = None
    """Opaque, application-defined data carried alongside this representation."""

    @classmethod
    def from_dict(cls, obj: Any) -> "KinematicRepresentation":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        type = from_str(obj.get("type"))
        metadata = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("metadata"))
        return KinematicRepresentation(type, metadata)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["type"] = from_str(self.type)
        if self.metadata is not None:
            result["metadata"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.metadata
            )
        return result


@dataclass
class Kinematics(DataModelHelper):
    """The kinematic representation(s) (DH, PoE, constraint-based, ...) describing this
    mechanism.

    The kinematic description(s) of a mechanism.
    """

    representations: Optional[List[KinematicRepresentation]] = None
    """The kinematic representations carried by this mechanism; a mechanism may carry more than
    one simultaneously (e.g. both a DH chain and a PoE description).
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "Kinematics":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        representations = from_union(
            [lambda x: from_list(KinematicRepresentation.from_dict, x), from_none],
            obj.get("representations"),
        )
        return Kinematics(representations)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.representations is not None:
            result["representations"] = from_union(
                [lambda x: from_list(lambda x: to_class(KinematicRepresentation, x), x), from_none],
                self.representations,
            )
        return result


class RobotType(Enum):
    """The type/supplier/grouping this mechanism describes, when applicable."""

    BROOKS_PRECISION_FLEX = "brooksPrecisionFlex"
    OBSBOT = "obsbot"
    UR = "ur"


@dataclass
class Units(DataModelHelper):
    """The default unit system for this mechanism's quantities.

    Default unit system for this mechanism. Individual quantities may override these via an
    explicit value/unit pair.
    """

    angle: Optional[Unit] = None
    """The default unit for angle quantities."""

    length: Optional[Unit] = None
    """The default unit for length quantities."""

    mass: Optional[Unit] = None
    """The default unit for mass quantities."""

    time: Optional[Unit] = None
    """The default unit for time quantities."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Units":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        angle = from_union([Unit, from_none], obj.get("angle"))
        length = from_union([Unit, from_none], obj.get("length"))
        mass = from_union([Unit, from_none], obj.get("mass"))
        time = from_union([Unit, from_none], obj.get("time"))
        return Units(angle, length, mass, time)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.angle is not None:
            result["angle"] = from_union([lambda x: to_enum(Unit, x), from_none], self.angle)
        if self.length is not None:
            result["length"] = from_union([lambda x: to_enum(Unit, x), from_none], self.length)
        if self.mass is not None:
            result["mass"] = from_union([lambda x: to_enum(Unit, x), from_none], self.mass)
        if self.time is not None:
            result["time"] = from_union([lambda x: to_enum(Unit, x), from_none], self.time)
        return result


@dataclass
class Component(DataModelHelper):
    """An instantiation of a mechanism definition within a parent mechanism. `definition` is
    either a stable id referencing a reusable mechanism defined elsewhere (permitting the
    same definition to be instantiated multiple times without duplication), or a mechanism
    definition nested inline.
    """

    definition: Union["RobotConfig", str]
    """The mechanism this component instantiates: either a stable id referencing a mechanism
    defined elsewhere, or a MechanismDefinition nested inline.
    """
    id: str
    """Stable identifier for this component instance within its parent mechanism."""

    kind: Optional[ComponentKind] = None
    """Self-describing discriminator; always "submechanism" for a Component."""

    metadata: Optional[Dict[str, Any]] = None
    """Opaque, application-defined data carried alongside this component."""

    mount: Optional[Mount] = None
    """Where this component attaches within its parent, by frame and/or named interface."""

    parameters: Optional[Dict[str, Any]] = None
    """Free-form parameter overrides applied to the referenced mechanism definition for this
    instance.
    """
    transform: Optional[Transform] = None
    """The relative pose of this component with respect to its mount point."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Component":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        definition = from_union([RobotConfig.from_dict, from_str], obj.get("definition"))
        id = from_str(obj.get("id"))
        kind = from_union([ComponentKind, from_none], obj.get("kind"))
        metadata = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("metadata"))
        mount = from_union([Mount.from_dict, from_none], obj.get("mount"))
        parameters = from_union(
            [lambda x: from_dict(lambda x: x, x), from_none], obj.get("parameters")
        )
        transform = from_union([Transform.from_dict, from_none], obj.get("transform"))
        return Component(definition, id, kind, metadata, mount, parameters, transform)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["definition"] = from_union(
            [lambda x: to_class(RobotConfig, x), from_str], self.definition
        )
        result["id"] = from_str(self.id)
        if self.kind is not None:
            result["kind"] = from_union([lambda x: to_enum(ComponentKind, x), from_none], self.kind)
        if self.metadata is not None:
            result["metadata"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.metadata
            )
        if self.mount is not None:
            result["mount"] = from_union([lambda x: to_class(Mount, x), from_none], self.mount)
        if self.parameters is not None:
            result["parameters"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.parameters
            )
        if self.transform is not None:
            result["transform"] = from_union(
                [lambda x: to_class(Transform, x), from_none], self.transform
            )
        return result


@dataclass
class RobotConfig(DataModelHelper):
    """Recursive, compositional, representation-independent schema for describing robots and
    robotic mechanisms: joints, bodies, frames, constraints, and recursive submechanism
    composition. Named architectures (serial/parallel/gimbal/SCARA/Stewart/etc.) are
    classifications, not structural schema branches. Split across multiple files by concept;
    this file is the entry point.

    The fundamental, recursive object. A robot is a mechanism; a mechanism may also be a
    reusable submechanism referenced by other mechanisms' components.
    """

    id: str
    """Stable identifier for this mechanism definition, referenced by other mechanisms'
    components.
    """
    robot_type: RobotType
    """The type/supplier/grouping this mechanism describes, when applicable."""

    bodies: Optional[List[Body]] = None
    """The rigid bodies (links) that make up this mechanism."""

    classification: Optional[Classification] = None
    """Descriptive, non-structural classification of this mechanism."""

    components: Optional[List[Component]] = None
    """Submechanisms instantiated within this mechanism, enabling recursive composition."""

    connections: Optional[List[Connection]] = None
    """Explicit connections mounting this mechanism's components to one another."""

    constraints: Optional[List[Constraint]] = None
    """Explicit constraints (e.g. loop closures) for parallel or closed-chain mechanisms."""

    frames: Optional[List[Frame]] = None
    """The frames defined by this mechanism."""

    interfaces: Optional[Dict[str, Interface]] = None
    """This mechanism's named, explicit mounting/reference points, keyed by interface name (e.g.
    "base", "tool").
    """
    joints: Optional[List[Joint]] = None
    """The kinematic joints connecting this mechanism's bodies."""

    kinematics: Optional[Kinematics] = None
    """The kinematic representation(s) (DH, PoE, constraint-based, ...) describing this
    mechanism.
    """
    metadata: Optional[Dict[str, Any]] = None
    """Opaque, application-defined data carried alongside this mechanism."""

    name: Optional[str] = None
    """A human-readable name for this mechanism."""

    units: Optional[Units] = None
    """The default unit system for this mechanism's quantities."""

    version: Optional[str] = None
    """An optional version string for this mechanism definition."""

    @classmethod
    def from_dict(cls, obj: Any) -> "RobotConfig":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        id = from_str(obj.get("id"))
        robot_type = RobotType(obj.get("robot_type"))
        bodies = from_union([lambda x: from_list(Body.from_dict, x), from_none], obj.get("bodies"))
        classification = from_union(
            [Classification.from_dict, from_none], obj.get("classification")
        )
        components = from_union(
            [lambda x: from_list(Component.from_dict, x), from_none], obj.get("components")
        )
        connections = from_union(
            [lambda x: from_list(Connection.from_dict, x), from_none], obj.get("connections")
        )
        constraints = from_union(
            [lambda x: from_list(Constraint.from_dict, x), from_none], obj.get("constraints")
        )
        frames = from_union([lambda x: from_list(Frame.from_dict, x), from_none], obj.get("frames"))
        interfaces = from_union(
            [lambda x: from_dict(Interface.from_dict, x), from_none], obj.get("interfaces")
        )
        joints = from_union([lambda x: from_list(Joint.from_dict, x), from_none], obj.get("joints"))
        kinematics = from_union([Kinematics.from_dict, from_none], obj.get("kinematics"))
        metadata = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("metadata"))
        name = from_union([from_str, from_none], obj.get("name"))
        units = from_union([Units.from_dict, from_none], obj.get("units"))
        version = from_union([from_str, from_none], obj.get("version"))
        return RobotConfig(
            id,
            robot_type,
            bodies,
            classification,
            components,
            connections,
            constraints,
            frames,
            interfaces,
            joints,
            kinematics,
            metadata,
            name,
            units,
            version,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["id"] = from_str(self.id)
        result["robot_type"] = to_enum(RobotType, self.robot_type)
        if self.bodies is not None:
            result["bodies"] = from_union(
                [lambda x: from_list(lambda x: to_class(Body, x), x), from_none], self.bodies
            )
        if self.classification is not None:
            result["classification"] = from_union(
                [lambda x: to_class(Classification, x), from_none], self.classification
            )
        if self.components is not None:
            result["components"] = from_union(
                [lambda x: from_list(lambda x: to_class(Component, x), x), from_none],
                self.components,
            )
        if self.connections is not None:
            result["connections"] = from_union(
                [lambda x: from_list(lambda x: to_class(Connection, x), x), from_none],
                self.connections,
            )
        if self.constraints is not None:
            result["constraints"] = from_union(
                [lambda x: from_list(lambda x: to_class(Constraint, x), x), from_none],
                self.constraints,
            )
        if self.frames is not None:
            result["frames"] = from_union(
                [lambda x: from_list(lambda x: to_class(Frame, x), x), from_none], self.frames
            )
        if self.interfaces is not None:
            result["interfaces"] = from_union(
                [lambda x: from_dict(lambda x: to_class(Interface, x), x), from_none],
                self.interfaces,
            )
        if self.joints is not None:
            result["joints"] = from_union(
                [lambda x: from_list(lambda x: to_class(Joint, x), x), from_none], self.joints
            )
        if self.kinematics is not None:
            result["kinematics"] = from_union(
                [lambda x: to_class(Kinematics, x), from_none], self.kinematics
            )
        if self.metadata is not None:
            result["metadata"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.metadata
            )
        if self.name is not None:
            result["name"] = from_union([from_str, from_none], self.name)
        if self.units is not None:
            result["units"] = from_union([lambda x: to_class(Units, x), from_none], self.units)
        if self.version is not None:
            result["version"] = from_union([from_str, from_none], self.version)
        return result


def robot_config_from_dict(s: Any) -> RobotConfig:
    return RobotConfig.from_dict(s)


def robot_config_to_dict(x: RobotConfig) -> Any:
    return to_class(RobotConfig, x)
