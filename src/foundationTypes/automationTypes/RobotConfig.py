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
from typing import Optional, Any, Union, Dict, List, TypeVar, Type, cast, Callable
from typing import ClassVar
from foundationTypes.data_model_helper import to_class_abc
from foundationTypes.mathTypes.MathTypes import SpatialTransformType
from foundation_abc.math.spatialABCs import SpatialTransformABC

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
class QuantityClass(DataModelHelper):
    value: float
    unit: Optional[Unit] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "QuantityClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        value = from_float(obj.get("value"))
        unit = from_union([Unit, from_none], obj.get("unit"))
        return QuantityClass(value, unit)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["value"] = to_float(self.value)
        if self.unit is not None:
            result["unit"] = from_union([lambda x: to_enum(Unit, x), from_none], self.unit)
        return result


@dataclass
class Inertia(DataModelHelper):
    """This body's rotational inertia tensor about its own frame. Optional; not required for a
    purely kinematic definition.
    """

    ixx: Optional[Union[float, QuantityClass]] = None
    """The xx moment of inertia."""

    ixy: Optional[Union[float, QuantityClass]] = None
    """The xy product of inertia."""

    ixz: Optional[Union[float, QuantityClass]] = None
    """The xz product of inertia."""

    iyy: Optional[Union[float, QuantityClass]] = None
    """The yy moment of inertia."""

    iyz: Optional[Union[float, QuantityClass]] = None
    """The yz product of inertia."""

    izz: Optional[Union[float, QuantityClass]] = None
    """The zz moment of inertia."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Inertia":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        ixx = from_union([from_float, QuantityClass.from_dict, from_none], obj.get("ixx"))
        ixy = from_union([from_float, QuantityClass.from_dict, from_none], obj.get("ixy"))
        ixz = from_union([from_float, QuantityClass.from_dict, from_none], obj.get("ixz"))
        iyy = from_union([from_float, QuantityClass.from_dict, from_none], obj.get("iyy"))
        iyz = from_union([from_float, QuantityClass.from_dict, from_none], obj.get("iyz"))
        izz = from_union([from_float, QuantityClass.from_dict, from_none], obj.get("izz"))
        return Inertia(ixx, ixy, ixz, iyy, iyz, izz)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.ixx is not None:
            result["ixx"] = from_union(
                [to_float, lambda x: to_class(QuantityClass, x), from_none], self.ixx
            )
        if self.ixy is not None:
            result["ixy"] = from_union(
                [to_float, lambda x: to_class(QuantityClass, x), from_none], self.ixy
            )
        if self.ixz is not None:
            result["ixz"] = from_union(
                [to_float, lambda x: to_class(QuantityClass, x), from_none], self.ixz
            )
        if self.iyy is not None:
            result["iyy"] = from_union(
                [to_float, lambda x: to_class(QuantityClass, x), from_none], self.iyy
            )
        if self.iyz is not None:
            result["iyz"] = from_union(
                [to_float, lambda x: to_class(QuantityClass, x), from_none], self.iyz
            )
        if self.izz is not None:
            result["izz"] = from_union(
                [to_float, lambda x: to_class(QuantityClass, x), from_none], self.izz
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

    mass: Optional[Union[float, QuantityClass]] = None
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
        mass = from_union([from_float, QuantityClass.from_dict, from_none], obj.get("mass"))
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
                [to_float, lambda x: to_class(QuantityClass, x), from_none], self.mass
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
    """Descriptive topology/architecture/function tags for this mechanism (see
    `Classification`). Purely for humans, search, and filtering: it is non-structural,
    meaning it never gates which of `bodies`/`joints`/`constraints`/`components` are valid —
    a Stewart platform and a serial arm differ in those fields, not here.

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

    transform: Optional[SpatialTransformABC] = None
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
        transform = from_union(
            [RobotConfig.SPATIAL_TRANSFORM_IMPL.from_dict, from_none], obj.get("transform")
        )
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
                [lambda x: to_class_abc(SpatialTransformABC, x), from_none], self.transform
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

    transform: Optional[SpatialTransformABC] = None
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
        transform = from_union(
            [RobotConfig.SPATIAL_TRANSFORM_IMPL.from_dict, from_none], obj.get("transform")
        )
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
                [lambda x: to_class_abc(SpatialTransformABC, x), from_none], self.transform
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
    """The kinematic representation(s) of this mechanism (see `Kinematics`). A mechanism may
    carry more than one at once — e.g. a Denavit-Hartenberg (DH) chain and a
    product-of-exponentials (PoE) description — that describe the same structure differently
    for different consumers.

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
    """Required supplier/product-family this definition belongs to, one of the recognized values
    `ur` (Universal Robots), `obsbot`, or `brooksPrecisionFlex`. It groups definitions by
    origin for selection and tooling; it is descriptive and does not change the kinematic
    structure.
    """

    BROOKS_PRECISION_FLEX = "brooksPrecisionFlex"
    OBSBOT = "obsbot"
    UR = "ur"


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
    transform: Optional[SpatialTransformABC] = None
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
        transform = from_union(
            [RobotConfig.SPATIAL_TRANSFORM_IMPL.from_dict, from_none], obj.get("transform")
        )
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
                [lambda x: to_class_abc(SpatialTransformABC, x), from_none], self.transform
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

    SPATIAL_TRANSFORM_IMPL: ClassVar[type[SpatialTransformABC]] = SpatialTransformType
    id: str
    """Stable string handle for this mechanism definition (format defined by the shared Id type;
    not a UUID). It is the anchor of the document's reference graph: a `Component` elsewhere
    names this `id` to instantiate the definition without copying it, so it must be unique
    across the set of definitions that reference each other. Uniqueness is the author's
    responsibility; the schema does not enforce it globally.
    """
    robot_type: RobotType
    """Required supplier/product-family this definition belongs to, one of the recognized values
    `ur` (Universal Robots), `obsbot`, or `brooksPrecisionFlex`. It groups definitions by
    origin for selection and tooling; it is descriptive and does not change the kinematic
    structure.
    """
    bodies: Optional[List[Body]] = None
    """The rigid bodies (links) that make up this mechanism, each carrying its own inertia and
    frames. Joints, frames, and constraints refer to these bodies by their `id`.
    """
    classification: Optional[Classification] = None
    """Descriptive topology/architecture/function tags for this mechanism (see
    `Classification`). Purely for humans, search, and filtering: it is non-structural,
    meaning it never gates which of `bodies`/`joints`/`constraints`/`components` are valid —
    a Stewart platform and a serial arm differ in those fields, not here.
    """
    components: Optional[List[Component]] = None
    """Submechanisms instantiated within this mechanism. Each `Component` references another
    definition by `id` (or nests one inline) and can be placed relative to a mount, giving
    the schema unbounded recursive composition — a mechanism built from mechanisms.
    """
    connections: Optional[List[Connection]] = None
    """Explicit connections that mount this mechanism's `components` to one another by named
    interface, so a child mechanism need not know in advance what it will attach to. Each
    connection links one component's interface to another's.
    """
    constraints: Optional[List[Constraint]] = None
    """Explicit constraints (e.g. loop closures, coincidence) relating bodies or frames by `id`,
    describing the parallel or closed-chain couplings that ordinary joint topology cannot
    express. Descriptive only — the schema records constraints but does not evaluate them.
    """
    frames: Optional[List[Frame]] = None
    """The named coordinate frames this mechanism defines, each explicitly attached to one of
    its bodies, joints, components, or interfaces and located by a relative transform. They
    provide reference points for mounting, measurement, and tool/sensor placement beyond the
    bodies' own frames.
    """
    interfaces: Optional[Dict[str, Interface]] = None
    """This mechanism's named, externally-visible mounting/reference points, keyed by interface
    name (e.g. "base", "tool"). A parent mechanism's `connections` attach to these names, so
    they form this mechanism's public contract for being mounted — a child exposes interfaces
    without knowing its eventual parent.
    """
    joints: Optional[List[Joint]] = None
    """The kinematic joints coupling this mechanism's bodies. Each joint names a `parent` and a
    `child` body by `id` and contributes the mechanism's degrees of freedom; a joint whose
    `type` is not one of the recognized kinds is carried with its base fields only.
    """
    kinematics: Optional[Kinematics] = None
    """The kinematic representation(s) of this mechanism (see `Kinematics`). A mechanism may
    carry more than one at once — e.g. a Denavit-Hartenberg (DH) chain and a
    product-of-exponentials (PoE) description — that describe the same structure differently
    for different consumers.
    """
    metadata: Optional[Dict[str, Any]] = None
    """Opaque, application-defined data carried alongside this mechanism. The schema neither
    constrains nor interprets its contents — a place for consumer-specific annotations that
    survive round-tripping.
    """
    name: Optional[str] = None
    """Human-readable display name for this mechanism, for UIs, logs, and diagrams. Not an
    identifier — references use `id`, and names need not be unique.
    """
    version: Optional[str] = None
    """Optional free-form version string (e.g. a semantic version or build tag) distinguishing
    revisions of the same `id`. The schema does not parse or order it; consumers decide what
    it means.
    """

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
        if self.version is not None:
            result["version"] = from_union([from_str, from_none], self.version)
        return result


def robot_config_from_dict(s: Any) -> RobotConfig:
    return RobotConfig.from_dict(s)


def robot_config_to_dict(x: RobotConfig) -> Any:
    return to_class(RobotConfig, x)
