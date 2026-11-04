# =============================================================================
# AUTO-GENERATED FILE — DO NOT EDIT
# Generated from JSON Schema via quicktype. Any manual edits will be
# overwritten the next time codegen runs (make codegen-all).
# To modify, update the source schema in schema/schemas/ and re-run codegen.
# =============================================================================

from dataclasses import dataclass
from foundationTypes.data_model_helper import (
    DataModelHelper,
    from_bool,
    from_list,
    from_none,
    from_str,
    from_union,
    to_class,
    to_enum,
)
from typing import Optional, Any, List, TypeVar, Type, Callable, cast
from enum import Enum

T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


@dataclass
class ClassDefElement(DataModelHelper):
    """A named style class (Mermaid `classDef name style`), bound to class nodes by name through
    their `classes` field.
    """

    name: str
    """The class name referenced by a class node's `classes` entry. The reserved name `default`
    applies to every node without an explicit class.
    """
    style: Optional[str] = None
    """The style declarations, comma-separated as Mermaid writes them, e.g.
    `fill:#f9f,stroke:#333,stroke-width:4px`.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ClassDefElement":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        name = from_str(obj.get("name"))
        style = from_union([from_str, from_none], obj.get("style"))
        return ClassDefElement(name, style)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["name"] = from_str(self.name)
        if self.style is not None:
            result["style"] = from_union([from_str, from_none], self.style)
        return result


class Visibility(Enum):
    """The visibility (encapsulation) of a class member. `public` (Mermaid `+`); `private`
    (`-`); `protected` (`#`); `package` (package/internal, `~`).
    """

    PACKAGE = "package"
    PRIVATE = "private"
    PROTECTED = "protected"
    PUBLIC = "public"


@dataclass
class AttributeElement(DataModelHelper):
    """A class attribute (a member without parentheses). Rendered in the middle compartment."""

    name: str
    """The attribute name."""

    static: Optional[bool] = None
    """Whether the attribute is static (the Mermaid `$` classifier)."""

    type: Optional[str] = None
    """The attribute's data type. May carry a generic, written with tildes, e.g. `List~int~`."""

    visibility: Optional[Visibility] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "AttributeElement":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        name = from_str(obj.get("name"))
        static = from_union([from_bool, from_none], obj.get("static"))
        type = from_union([from_str, from_none], obj.get("type"))
        visibility = from_union([Visibility, from_none], obj.get("visibility"))
        return AttributeElement(name, static, type, visibility)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["name"] = from_str(self.name)
        if self.static is not None:
            result["static"] = from_union([from_bool, from_none], self.static)
        if self.type is not None:
            result["type"] = from_union([from_str, from_none], self.type)
        if self.visibility is not None:
            result["visibility"] = from_union(
                [lambda x: to_enum(Visibility, x), from_none], self.visibility
            )
        return result


class Classifier(Enum):
    """An optional method classifier. `abstract` (the Mermaid `*` suffix); `static` (the `$`
    suffix).
    """

    ABSTRACT = "abstract"
    STATIC = "static"


@dataclass
class MethodElement(DataModelHelper):
    """A class method or function (a member with parentheses). Rendered in the bottom
    compartment.
    """

    name: str
    """The method name, without the parentheses."""

    classifier: Optional[Classifier] = None
    """An optional method classifier. `abstract` (the Mermaid `*` suffix); `static` (the `$`
    suffix).
    """
    parameters: Optional[str] = None
    """The raw parameter list as written between the parentheses, e.g. `amount` or `List~int~
    points`. Empty or omitted means no parameters.
    """
    return_type: Optional[str] = None
    """The returned data type, if any. May carry a generic written with tildes, e.g. `List~int~`."""

    visibility: Optional[Visibility] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "MethodElement":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        name = from_str(obj.get("name"))
        classifier = from_union([Classifier, from_none], obj.get("classifier"))
        parameters = from_union([from_str, from_none], obj.get("parameters"))
        return_type = from_union([from_str, from_none], obj.get("returnType"))
        visibility = from_union([Visibility, from_none], obj.get("visibility"))
        return MethodElement(name, classifier, parameters, return_type, visibility)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["name"] = from_str(self.name)
        if self.classifier is not None:
            result["classifier"] = from_union(
                [lambda x: to_enum(Classifier, x), from_none], self.classifier
            )
        if self.parameters is not None:
            result["parameters"] = from_union([from_str, from_none], self.parameters)
        if self.return_type is not None:
            result["returnType"] = from_union([from_str, from_none], self.return_type)
        if self.visibility is not None:
            result["visibility"] = from_union(
                [lambda x: to_enum(Visibility, x), from_none], self.visibility
            )
        return result


@dataclass
class ClassElement(DataModelHelper):
    """A class node: its name, optional annotation and generic, and its attributes and methods."""

    id: str
    """The class name, used to reference it from relationships, notes, and namespaces. Composed
    of alphanumerics (including unicode), underscores, and dashes.
    """
    annotation: Optional[str] = None
    """An optional annotation describing the class's nature, written inside `<<>>` in Mermaid,
    e.g. `interface`, `abstract`, `service`, `enumeration`. Left open: the set of annotations
    is not fixed.
    """
    attributes: Optional[List[AttributeElement]] = None
    """The class's attributes."""

    classes: Optional[List[str]] = None
    """Names of classDefs applied to this class node (Mermaid `cssClass`/`:::`). Each entry must
    match a classDefs[].name.
    """
    generic: Optional[str] = None
    """An optional class-level generic type parameter, written with tildes in Mermaid, e.g. the
    `Shape` in `Square~Shape~`. The generic is not part of the class id used for references.
    """
    label: Optional[str] = None
    """An optional display label shown instead of the id (the Mermaid `class X["label"]` form).
    Lets the rendered name carry characters the id cannot.
    """
    methods: Optional[List[MethodElement]] = None
    """The class's methods."""

    @classmethod
    def from_dict(cls, obj: Any) -> "ClassElement":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        id = from_str(obj.get("id"))
        annotation = from_union([from_str, from_none], obj.get("annotation"))
        attributes = from_union(
            [lambda x: from_list(AttributeElement.from_dict, x), from_none], obj.get("attributes")
        )
        classes = from_union([lambda x: from_list(from_str, x), from_none], obj.get("classes"))
        generic = from_union([from_str, from_none], obj.get("generic"))
        label = from_union([from_str, from_none], obj.get("label"))
        methods = from_union(
            [lambda x: from_list(MethodElement.from_dict, x), from_none], obj.get("methods")
        )
        return ClassElement(id, annotation, attributes, classes, generic, label, methods)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["id"] = from_str(self.id)
        if self.annotation is not None:
            result["annotation"] = from_union([from_str, from_none], self.annotation)
        if self.attributes is not None:
            result["attributes"] = from_union(
                [lambda x: from_list(lambda x: to_class(AttributeElement, x), x), from_none],
                self.attributes,
            )
        if self.classes is not None:
            result["classes"] = from_union(
                [lambda x: from_list(from_str, x), from_none], self.classes
            )
        if self.generic is not None:
            result["generic"] = from_union([from_str, from_none], self.generic)
        if self.label is not None:
            result["label"] = from_union([from_str, from_none], self.label)
        if self.methods is not None:
            result["methods"] = from_union(
                [lambda x: from_list(lambda x: to_class(MethodElement, x), x), from_none],
                self.methods,
            )
        return result


@dataclass
class NamespaceElement(DataModelHelper):
    """A namespace that groups classes. Recursive — a namespace can contain nested namespaces."""

    name: str
    """The namespace name, used internally for nesting and references. Dot notation (e.g.
    `Company.Engineering`) denotes a hierarchy.
    """
    classes: Optional[List[ClassElement]] = None
    """The classes that belong directly to this namespace."""

    label: Optional[str] = None
    """An optional display label shown instead of the name (the Mermaid `namespace X["label"]`
    form, v11.15.0+).
    """
    namespaces: Optional[List["NamespaceElement"]] = None
    """Nested namespaces, each a namespace in its own right."""

    @classmethod
    def from_dict(cls, obj: Any) -> "NamespaceElement":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        name = from_str(obj.get("name"))
        classes = from_union(
            [lambda x: from_list(ClassElement.from_dict, x), from_none], obj.get("classes")
        )
        label = from_union([from_str, from_none], obj.get("label"))
        namespaces = from_union(
            [lambda x: from_list(NamespaceElement.from_dict, x), from_none], obj.get("namespaces")
        )
        return NamespaceElement(name, classes, label, namespaces)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["name"] = from_str(self.name)
        if self.classes is not None:
            result["classes"] = from_union(
                [lambda x: from_list(lambda x: to_class(ClassElement, x), x), from_none],
                self.classes,
            )
        if self.label is not None:
            result["label"] = from_union([from_str, from_none], self.label)
        if self.namespaces is not None:
            result["namespaces"] = from_union(
                [lambda x: from_list(lambda x: to_class(NamespaceElement, x), x), from_none],
                self.namespaces,
            )
        return result


@dataclass
class NoteElement(DataModelHelper):
    """A note on the diagram (Mermaid `note` / `note for <class>`)."""

    text: str
    """The note text. Newlines are written with `\n` and carried as a raw string."""

    for_class: Optional[str] = None
    """The id of the class this note is attached to. Omitted means a general note not tied to a
    class.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "NoteElement":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        text = from_str(obj.get("text"))
        for_class = from_union([from_str, from_none], obj.get("forClass"))
        return NoteElement(text, for_class)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["text"] = from_str(self.text)
        if self.for_class is not None:
            result["forClass"] = from_union([from_str, from_none], self.for_class)
        return result


class Orientation(Enum):
    """The orientation of the diagram (the Mermaid `direction` statement). `TB` top to bottom;
    `TD` top-down (same as top to bottom); `BT` bottom to top; `RL` right to left; `LR` left
    to right.
    """

    BT = "BT"
    LR = "LR"
    RL = "RL"
    TB = "TB"
    TD = "TD"


class FromMarker(Enum):
    """The marker drawn at one end of a relationship. Its UML meaning is the marker shape
    together with the line style (see `relationship`). `triangle` inheritance/realization
    head (`|>`); `filledDiamond` composition (`*`); `hollowDiamond` aggregation (`o`);
    `arrow` association/dependency head (`>`); `lollipop` interface (`()`); `none` a plain
    link end.
    """

    ARROW = "arrow"
    FILLED_DIAMOND = "filledDiamond"
    HOLLOW_DIAMOND = "hollowDiamond"
    LOLLIPOP = "lollipop"
    NONE = "none"
    TRIANGLE = "triangle"


class Line(Enum):
    """The line style. `solid` (Mermaid `--`); `dashed` (`..`). Distinguishes inheritance from
    realization and association from dependency.
    """

    DASHED = "dashed"
    SOLID = "solid"


@dataclass
class RelationshipElement(DataModelHelper):
    """A relationship (edge) between two classes. One decomposed model expresses every case: the
    eight standard UML relations, two-way relations, and lollipop interfaces.
    Standard-relation presets a serializer recognizes: inheritance = line solid + toMarker
    triangle; realization = line dashed + toMarker triangle; composition = solid +
    filledDiamond; aggregation = solid + hollowDiamond; association = solid + arrow;
    dependency = dashed + arrow; solid link = solid + none/none; dashed link = dashed +
    none/none. A two-way relation sets both markers; a lollipop interface sets a lollipop
    marker at one end.
    """

    class_diagram_schema_from: str
    """The id of the class the relationship starts from."""

    to: str
    """The id of the class the relationship points to."""

    cardinality_from: Optional[str] = None
    """Optional multiplicity near the `from` end, e.g. `1`, `0..1`, `1..*`, `*`, `n`."""

    cardinality_to: Optional[str] = None
    """Optional multiplicity near the `to` end, e.g. `1`, `0..1`, `1..*`, `*`, `n`."""

    from_marker: Optional[FromMarker] = None
    label: Optional[str] = None
    """Optional text describing the relationship, rendered on the edge."""

    line: Optional[Line] = None
    """The line style. `solid` (Mermaid `--`); `dashed` (`..`). Distinguishes inheritance from
    realization and association from dependency.
    """
    to_marker: Optional[FromMarker] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "RelationshipElement":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        class_diagram_schema_from = from_str(obj.get("from"))
        to = from_str(obj.get("to"))
        cardinality_from = from_union([from_str, from_none], obj.get("cardinalityFrom"))
        cardinality_to = from_union([from_str, from_none], obj.get("cardinalityTo"))
        from_marker = from_union([FromMarker, from_none], obj.get("fromMarker"))
        label = from_union([from_str, from_none], obj.get("label"))
        line = from_union([Line, from_none], obj.get("line"))
        to_marker = from_union([FromMarker, from_none], obj.get("toMarker"))
        return RelationshipElement(
            class_diagram_schema_from,
            to,
            cardinality_from,
            cardinality_to,
            from_marker,
            label,
            line,
            to_marker,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["from"] = from_str(self.class_diagram_schema_from)
        result["to"] = from_str(self.to)
        if self.cardinality_from is not None:
            result["cardinalityFrom"] = from_union([from_str, from_none], self.cardinality_from)
        if self.cardinality_to is not None:
            result["cardinalityTo"] = from_union([from_str, from_none], self.cardinality_to)
        if self.from_marker is not None:
            result["fromMarker"] = from_union(
                [lambda x: to_enum(FromMarker, x), from_none], self.from_marker
            )
        if self.label is not None:
            result["label"] = from_union([from_str, from_none], self.label)
        if self.line is not None:
            result["line"] = from_union([lambda x: to_enum(Line, x), from_none], self.line)
        if self.to_marker is not None:
            result["toMarker"] = from_union(
                [lambda x: to_enum(FromMarker, x), from_none], self.to_marker
            )
        return result


@dataclass
class ClassDiagram(DataModelHelper):
    """The class diagram body: its orientation, the classes, the relationships between them, the
    namespaces that group them, free notes, and style classes. A sibling of the flowchart
    body in this folder; it reuses the same structural principles (self-contained $defs,
    readable enums, a recursive grouping container, and diagram-global style classes).
    """

    class_defs: Optional[List[ClassDefElement]] = None
    """The diagram's style classes. Declared at the top level because classDef is
    diagram-global: a class binds by name to any class node from anywhere in the diagram.
    """
    classes: Optional[List[ClassElement]] = None
    """The classes in the diagram."""

    namespaces: Optional[List[NamespaceElement]] = None
    """The namespaces that group classes. Recursive — a namespace can contain nested namespaces."""

    notes: Optional[List[NoteElement]] = None
    """Free notes on the diagram, each general or attached to a class."""

    orientation: Optional[Orientation] = None
    relationships: Optional[List[RelationshipElement]] = None
    """The relationships (edges) between classes."""

    @classmethod
    def from_dict(cls, obj: Any) -> "ClassDiagram":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        class_defs = from_union(
            [lambda x: from_list(ClassDefElement.from_dict, x), from_none], obj.get("classDefs")
        )
        classes = from_union(
            [lambda x: from_list(ClassElement.from_dict, x), from_none], obj.get("classes")
        )
        namespaces = from_union(
            [lambda x: from_list(NamespaceElement.from_dict, x), from_none], obj.get("namespaces")
        )
        notes = from_union(
            [lambda x: from_list(NoteElement.from_dict, x), from_none], obj.get("notes")
        )
        orientation = from_union([Orientation, from_none], obj.get("orientation"))
        relationships = from_union(
            [lambda x: from_list(RelationshipElement.from_dict, x), from_none],
            obj.get("relationships"),
        )
        return ClassDiagram(class_defs, classes, namespaces, notes, orientation, relationships)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.class_defs is not None:
            result["classDefs"] = from_union(
                [lambda x: from_list(lambda x: to_class(ClassDefElement, x), x), from_none],
                self.class_defs,
            )
        if self.classes is not None:
            result["classes"] = from_union(
                [lambda x: from_list(lambda x: to_class(ClassElement, x), x), from_none],
                self.classes,
            )
        if self.namespaces is not None:
            result["namespaces"] = from_union(
                [lambda x: from_list(lambda x: to_class(NamespaceElement, x), x), from_none],
                self.namespaces,
            )
        if self.notes is not None:
            result["notes"] = from_union(
                [lambda x: from_list(lambda x: to_class(NoteElement, x), x), from_none], self.notes
            )
        if self.orientation is not None:
            result["orientation"] = from_union(
                [lambda x: to_enum(Orientation, x), from_none], self.orientation
            )
        if self.relationships is not None:
            result["relationships"] = from_union(
                [lambda x: from_list(lambda x: to_class(RelationshipElement, x), x), from_none],
                self.relationships,
            )
        return result


def class_diagram_from_dict(s: Any) -> ClassDiagram:
    return ClassDiagram.from_dict(s)


def class_diagram_to_dict(x: ClassDiagram) -> Any:
    return to_class(ClassDiagram, x)
