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
    from_bool,
    from_dict,
    from_float,
    from_int,
    from_list,
    from_none,
    from_str,
    from_union,
    to_class,
    to_enum,
    to_float,
)
from typing import List, Optional, Any, Dict, Union, TypeVar, Callable, Type, cast

T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


class RoleElement(Enum):
    """The sender or recipient of messages and data in a conversation."""

    ASSISTANT = "assistant"
    USER = "user"


@dataclass
class AudiocontentAnnotations(DataModelHelper):
    """Optional annotations for the client. The client can use annotations to inform how objects
    are used or displayed

    Optional annotations for the client.
    """

    audience: Optional[List[RoleElement]] = None
    """Describes who the intended audience of this object or data is.
    
    It can include multiple entries to indicate content useful for multiple audiences (e.g.,
    `["user", "assistant"]`).
    """
    last_modified: Optional[str] = None
    """The moment the resource was last modified, as an ISO 8601 formatted string.
    
    Should be an ISO 8601 formatted string (e.g., "2025-01-12T15:00:58Z").
    
    Examples: last activity timestamp in an open file, timestamp when the resource
    was attached, etc.
    """
    priority: Optional[float] = None
    """Describes how important this data is for operating the server.
    
    A value of 1 means "most important," and indicates that the data is
    effectively required, while 0 means "least important," and indicates that
    the data is entirely optional.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "AudiocontentAnnotations":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        audience = from_union([lambda x: from_list(RoleElement, x), from_none], obj.get("audience"))
        last_modified = from_union([from_str, from_none], obj.get("lastModified"))
        priority = from_union([from_float, from_none], obj.get("priority"))
        return AudiocontentAnnotations(audience, last_modified, priority)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.audience is not None:
            result["audience"] = from_union(
                [lambda x: from_list(lambda x: to_enum(RoleElement, x), x), from_none],
                self.audience,
            )
        if self.last_modified is not None:
            result["lastModified"] = from_union([from_str, from_none], self.last_modified)
        if self.priority is not None:
            result["priority"] = from_union([to_float, from_none], self.priority)
        return result


class AudiocontentType(Enum):
    AUDIO = "audio"


@dataclass
class Audiocontent(DataModelHelper):
    """Audio provided to or from an LLM."""

    data: str
    """The base64-encoded audio data."""

    mime_type: str
    """The MIME type of the audio. Different providers may support different audio types."""

    type: AudiocontentType
    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    annotations: Optional[AudiocontentAnnotations] = None
    """Optional annotations for the client."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Audiocontent":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        data = from_str(obj.get("data"))
        mime_type = from_str(obj.get("mimeType"))
        type = AudiocontentType(obj.get("type"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        annotations = from_union(
            [AudiocontentAnnotations.from_dict, from_none], obj.get("annotations")
        )
        return Audiocontent(data, mime_type, type, meta, annotations)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["data"] = from_str(self.data)
        result["mimeType"] = from_str(self.mime_type)
        result["type"] = to_enum(AudiocontentType, self.type)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.annotations is not None:
            result["annotations"] = from_union(
                [lambda x: to_class(AudiocontentAnnotations, x), from_none], self.annotations
            )
        return result


@dataclass
class Basemetadata(DataModelHelper):
    """Base interface for metadata with name (identifier) and title (display name) properties."""

    name: str
    """Intended for programmatic or logical use, but used as a display name in past specs or
    fallback (if title isn't present).
    """
    title: Optional[str] = None
    """Intended for UI and end-user contexts — optimized to be human-readable and easily
    understood,
    even by those unfamiliar with domain-specific terminology.
    
    If not provided, the name should be used for display (except for Tool,
    where `annotations.title` should be given precedence over using `name`,
    if present).
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "Basemetadata":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        name = from_str(obj.get("name"))
        title = from_union([from_str, from_none], obj.get("title"))
        return Basemetadata(name, title)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["name"] = from_str(self.name)
        if self.title is not None:
            result["title"] = from_union([from_str, from_none], self.title)
        return result


@dataclass
class Blobresourcecontents(DataModelHelper):
    blob: str
    """A base64-encoded string representing the binary data of the item."""

    uri: str
    """The URI of this resource."""

    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    mime_type: Optional[str] = None
    """The MIME type of this resource, if known."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Blobresourcecontents":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        blob = from_str(obj.get("blob"))
        uri = from_str(obj.get("uri"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        mime_type = from_union([from_str, from_none], obj.get("mimeType"))
        return Blobresourcecontents(blob, uri, meta, mime_type)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["blob"] = from_str(self.blob)
        result["uri"] = from_str(self.uri)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.mime_type is not None:
            result["mimeType"] = from_union([from_str, from_none], self.mime_type)
        return result


class BooleanschemaType(Enum):
    BOOLEAN = "boolean"


@dataclass
class BooleanschemaClass(DataModelHelper):
    type: BooleanschemaType
    default: Optional[bool] = None
    description: Optional[str] = None
    title: Optional[str] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "BooleanschemaClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        type = BooleanschemaType(obj.get("type"))
        default = from_union([from_bool, from_none], obj.get("default"))
        description = from_union([from_str, from_none], obj.get("description"))
        title = from_union([from_str, from_none], obj.get("title"))
        return BooleanschemaClass(type, default, description, title)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["type"] = to_enum(BooleanschemaType, self.type)
        if self.default is not None:
            result["default"] = from_union([from_bool, from_none], self.default)
        if self.description is not None:
            result["description"] = from_union([from_str, from_none], self.description)
        if self.title is not None:
            result["title"] = from_union([from_str, from_none], self.title)
        return result


class Jsonrpc(Enum):
    THE_20 = "2.0"


class CalltoolrequestMethod(Enum):
    TOOLS_CALL = "tools/call"


@dataclass
class PurpleMeta(DataModelHelper):
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """

    progress_token: Optional[Union[int, str]] = None
    """If specified, the caller is requesting out-of-band progress notifications for this
    request (as represented by notifications/progress). The value of this parameter is an
    opaque token that will be attached to any subsequent notifications. The receiver is not
    obligated to provide these notifications.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "PurpleMeta":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        progress_token = from_union([from_int, from_str, from_none], obj.get("progressToken"))
        return PurpleMeta(progress_token)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.progress_token is not None:
            result["progressToken"] = from_union(
                [from_int, from_str, from_none], self.progress_token
            )
        return result


@dataclass
class Task(DataModelHelper):
    """If specified, the caller is requesting task-augmented execution for this request.
    The request will return a CreateTaskResult immediately, and the actual result can be
    retrieved later via tasks/result.

    Task augmentation is subject to capability negotiation - receivers MUST declare support
    for task augmentation of specific request types in their capabilities.

    Metadata for augmenting a request with task execution.
    Include this in the `task` field of the request parameters.
    """

    ttl: Optional[int] = None
    """Requested duration in milliseconds to retain task from creation."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Task":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        ttl = from_union([from_int, from_none], obj.get("ttl"))
        return Task(ttl)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.ttl is not None:
            result["ttl"] = from_union([from_int, from_none], self.ttl)
        return result


@dataclass
class CalltoolrequestParams(DataModelHelper):
    """Parameters for a `tools/call` request."""

    name: str
    """The name of the tool."""

    meta: Optional[PurpleMeta] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    arguments: Optional[Dict[str, Any]] = None
    """Arguments to use for the tool call."""

    task: Optional[Task] = None
    """If specified, the caller is requesting task-augmented execution for this request.
    The request will return a CreateTaskResult immediately, and the actual result can be
    retrieved later via tasks/result.
    
    Task augmentation is subject to capability negotiation - receivers MUST declare support
    for task augmentation of specific request types in their capabilities.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "CalltoolrequestParams":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        name = from_str(obj.get("name"))
        meta = from_union([PurpleMeta.from_dict, from_none], obj.get("_meta"))
        arguments = from_union(
            [lambda x: from_dict(lambda x: x, x), from_none], obj.get("arguments")
        )
        task = from_union([Task.from_dict, from_none], obj.get("task"))
        return CalltoolrequestParams(name, meta, arguments, task)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["name"] = from_str(self.name)
        if self.meta is not None:
            result["_meta"] = from_union([lambda x: to_class(PurpleMeta, x), from_none], self.meta)
        if self.arguments is not None:
            result["arguments"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.arguments
            )
        if self.task is not None:
            result["task"] = from_union([lambda x: to_class(Task, x), from_none], self.task)
        return result


@dataclass
class Calltoolrequest(DataModelHelper):
    """Used by the client to invoke a tool provided by the server."""

    id: Union[int, str]
    jsonrpc: Jsonrpc
    method: CalltoolrequestMethod
    params: CalltoolrequestParams

    @classmethod
    def from_dict(cls, obj: Any) -> "Calltoolrequest":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        id = from_union([from_int, from_str], obj.get("id"))
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        method = CalltoolrequestMethod(obj.get("method"))
        params = CalltoolrequestParams.from_dict(obj.get("params"))
        return Calltoolrequest(id, jsonrpc, method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["id"] = from_union([from_int, from_str], self.id)
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        result["method"] = to_enum(CalltoolrequestMethod, self.method)
        result["params"] = to_class(CalltoolrequestParams, self.params)
        return result


class Theme(Enum):
    """Optional specifier for the theme this icon is designed for. `light` indicates
    the icon is designed to be used with a light background, and `dark` indicates
    the icon is designed to be used with a dark background.

    If not provided, the client should assume the icon can be used with any theme.
    """

    DARK = "dark"
    LIGHT = "light"


@dataclass
class IconElement(DataModelHelper):
    """An optionally-sized icon that can be displayed in a user interface."""

    src: str
    """A standard URI pointing to an icon resource. May be an HTTP/HTTPS URL or a
    `data:` URI with Base64-encoded image data.
    
    Consumers SHOULD takes steps to ensure URLs serving icons are from the
    same domain as the client/server or a trusted domain.
    
    Consumers SHOULD take appropriate precautions when consuming SVGs as they can contain
    executable JavaScript.
    """
    mime_type: Optional[str] = None
    """Optional MIME type override if the source MIME type is missing or generic.
    For example: `"image/png"`, `"image/jpeg"`, or `"image/svg+xml"`.
    """
    sizes: Optional[List[str]] = None
    """Optional array of strings that specify sizes at which the icon can be used.
    Each string should be in WxH format (e.g., `"48x48"`, `"96x96"`) or `"any"` for scalable
    formats like SVG.
    
    If not provided, the client should assume that the icon can be used at any size.
    """
    theme: Optional[Theme] = None
    """Optional specifier for the theme this icon is designed for. `light` indicates
    the icon is designed to be used with a light background, and `dark` indicates
    the icon is designed to be used with a dark background.
    
    If not provided, the client should assume the icon can be used with any theme.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "IconElement":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        src = from_str(obj.get("src"))
        mime_type = from_union([from_str, from_none], obj.get("mimeType"))
        sizes = from_union([lambda x: from_list(from_str, x), from_none], obj.get("sizes"))
        theme = from_union([Theme, from_none], obj.get("theme"))
        return IconElement(src, mime_type, sizes, theme)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["src"] = from_str(self.src)
        if self.mime_type is not None:
            result["mimeType"] = from_union([from_str, from_none], self.mime_type)
        if self.sizes is not None:
            result["sizes"] = from_union([lambda x: from_list(from_str, x), from_none], self.sizes)
        if self.theme is not None:
            result["theme"] = from_union([lambda x: to_enum(Theme, x), from_none], self.theme)
        return result


@dataclass
class Resource(DataModelHelper):
    uri: str
    """The URI of this resource."""

    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    mime_type: Optional[str] = None
    """The MIME type of this resource, if known."""

    text: Optional[str] = None
    """The text of the item. This must only be set if the item can actually be represented as
    text (not binary data).
    """
    blob: Optional[str] = None
    """A base64-encoded string representing the binary data of the item."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Resource":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        uri = from_str(obj.get("uri"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        mime_type = from_union([from_str, from_none], obj.get("mimeType"))
        text = from_union([from_str, from_none], obj.get("text"))
        blob = from_union([from_str, from_none], obj.get("blob"))
        return Resource(uri, meta, mime_type, text, blob)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["uri"] = from_str(self.uri)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.mime_type is not None:
            result["mimeType"] = from_union([from_str, from_none], self.mime_type)
        if self.text is not None:
            result["text"] = from_union([from_str, from_none], self.text)
        if self.blob is not None:
            result["blob"] = from_union([from_str, from_none], self.blob)
        return result


class ContentblockType(Enum):
    AUDIO = "audio"
    IMAGE = "image"
    RESOURCE = "resource"
    RESOURCE_LINK = "resource_link"
    TEXT = "text"


@dataclass
class ContentblockElement(DataModelHelper):
    """Text provided to or from an LLM.

    An image provided to or from an LLM.

    Audio provided to or from an LLM.

    A resource that the server is capable of reading, included in a prompt or tool call
    result.

    Note: resource links returned by tools are not guaranteed to appear in the results of
    `resources/list` requests.

    The contents of a resource, embedded into a prompt or tool call result.

    It is up to the client how best to render embedded resources for the benefit
    of the LLM and/or the user.
    """

    type: ContentblockType
    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    annotations: Optional[AudiocontentAnnotations] = None
    """Optional annotations for the client."""

    text: Optional[str] = None
    """The text content of the message."""

    data: Optional[str] = None
    """The base64-encoded image data.
    
    The base64-encoded audio data.
    """
    mime_type: Optional[str] = None
    """The MIME type of the image. Different providers may support different image types.
    
    The MIME type of the audio. Different providers may support different audio types.
    
    The MIME type of this resource, if known.
    """
    description: Optional[str] = None
    """A description of what this resource represents.
    
    This can be used by clients to improve the LLM's understanding of available resources. It
    can be thought of like a "hint" to the model.
    """
    icons: Optional[List[IconElement]] = None
    """Optional set of sized icons that the client can display in a user interface.
    
    Clients that support rendering icons MUST support at least the following MIME types:
    - `image/png` - PNG images (safe, universal compatibility)
    - `image/jpeg` (and `image/jpg`) - JPEG images (safe, universal compatibility)
    
    Clients that support rendering icons SHOULD also support:
    - `image/svg+xml` - SVG images (scalable but requires security precautions)
    - `image/webp` - WebP images (modern, efficient format)
    """
    name: Optional[str] = None
    """Intended for programmatic or logical use, but used as a display name in past specs or
    fallback (if title isn't present).
    """
    size: Optional[int] = None
    """The size of the raw resource content, in bytes (i.e., before base64 encoding or any
    tokenization), if known.
    
    This can be used by Hosts to display file sizes and estimate context window usage.
    """
    title: Optional[str] = None
    """Intended for UI and end-user contexts — optimized to be human-readable and easily
    understood,
    even by those unfamiliar with domain-specific terminology.
    
    If not provided, the name should be used for display (except for Tool,
    where `annotations.title` should be given precedence over using `name`,
    if present).
    """
    uri: Optional[str] = None
    """The URI of this resource."""

    resource: Optional[Resource] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "ContentblockElement":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        type = ContentblockType(obj.get("type"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        annotations = from_union(
            [AudiocontentAnnotations.from_dict, from_none], obj.get("annotations")
        )
        text = from_union([from_str, from_none], obj.get("text"))
        data = from_union([from_str, from_none], obj.get("data"))
        mime_type = from_union([from_str, from_none], obj.get("mimeType"))
        description = from_union([from_str, from_none], obj.get("description"))
        icons = from_union(
            [lambda x: from_list(IconElement.from_dict, x), from_none], obj.get("icons")
        )
        name = from_union([from_str, from_none], obj.get("name"))
        size = from_union([from_int, from_none], obj.get("size"))
        title = from_union([from_str, from_none], obj.get("title"))
        uri = from_union([from_str, from_none], obj.get("uri"))
        resource = from_union([Resource.from_dict, from_none], obj.get("resource"))
        return ContentblockElement(
            type,
            meta,
            annotations,
            text,
            data,
            mime_type,
            description,
            icons,
            name,
            size,
            title,
            uri,
            resource,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["type"] = to_enum(ContentblockType, self.type)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.annotations is not None:
            result["annotations"] = from_union(
                [lambda x: to_class(AudiocontentAnnotations, x), from_none], self.annotations
            )
        if self.text is not None:
            result["text"] = from_union([from_str, from_none], self.text)
        if self.data is not None:
            result["data"] = from_union([from_str, from_none], self.data)
        if self.mime_type is not None:
            result["mimeType"] = from_union([from_str, from_none], self.mime_type)
        if self.description is not None:
            result["description"] = from_union([from_str, from_none], self.description)
        if self.icons is not None:
            result["icons"] = from_union(
                [lambda x: from_list(lambda x: to_class(IconElement, x), x), from_none], self.icons
            )
        if self.name is not None:
            result["name"] = from_union([from_str, from_none], self.name)
        if self.size is not None:
            result["size"] = from_union([from_int, from_none], self.size)
        if self.title is not None:
            result["title"] = from_union([from_str, from_none], self.title)
        if self.uri is not None:
            result["uri"] = from_union([from_str, from_none], self.uri)
        if self.resource is not None:
            result["resource"] = from_union(
                [lambda x: to_class(Resource, x), from_none], self.resource
            )
        return result


@dataclass
class Calltoolresult(DataModelHelper):
    """The server's response to a tool call."""

    content: List[ContentblockElement]
    """A list of content objects that represent the unstructured result of the tool call."""

    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    is_error: Optional[bool] = None
    """Whether the tool call ended in an error.
    
    If not set, this is assumed to be false (the call was successful).
    
    Any errors that originate from the tool SHOULD be reported inside the result
    object, with `isError` set to true, _not_ as an MCP protocol-level error
    response. Otherwise, the LLM would not be able to see that an error occurred
    and self-correct.
    
    However, any errors in _finding_ the tool, an error indicating that the
    server does not support tool calls, or any other exceptional conditions,
    should be reported as an MCP error response.
    """
    structured_content: Optional[Dict[str, Any]] = None
    """An optional JSON object that represents the structured result of the tool call."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Calltoolresult":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        content = from_list(ContentblockElement.from_dict, obj.get("content"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        is_error = from_union([from_bool, from_none], obj.get("isError"))
        structured_content = from_union(
            [lambda x: from_dict(lambda x: x, x), from_none], obj.get("structuredContent")
        )
        return Calltoolresult(content, meta, is_error, structured_content)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["content"] = from_list(lambda x: to_class(ContentblockElement, x), self.content)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.is_error is not None:
            result["isError"] = from_union([from_bool, from_none], self.is_error)
        if self.structured_content is not None:
            result["structuredContent"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.structured_content
            )
        return result


class CancellednotificationMethod(Enum):
    NOTIFICATIONS_CANCELLED = "notifications/cancelled"


@dataclass
class CancellednotificationParams(DataModelHelper):
    """Parameters for a `notifications/cancelled` notification."""

    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    reason: Optional[str] = None
    """An optional string describing the reason for the cancellation. This MAY be logged or
    presented to the user.
    """
    request_id: Optional[Union[int, str]] = None
    """The ID of the request to cancel.
    
    This MUST correspond to the ID of a request previously issued in the same direction.
    This MUST be provided for cancelling non-task requests.
    This MUST NOT be used for cancelling tasks (use the `tasks/cancel` request instead).
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "CancellednotificationParams":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        reason = from_union([from_str, from_none], obj.get("reason"))
        request_id = from_union([from_int, from_str, from_none], obj.get("requestId"))
        return CancellednotificationParams(meta, reason, request_id)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.reason is not None:
            result["reason"] = from_union([from_str, from_none], self.reason)
        if self.request_id is not None:
            result["requestId"] = from_union([from_int, from_str, from_none], self.request_id)
        return result


@dataclass
class Cancellednotification(DataModelHelper):
    """This notification can be sent by either side to indicate that it is cancelling a
    previously-issued request.

    The request SHOULD still be in-flight, but due to communication latency, it is always
    possible that this notification MAY arrive after the request has already finished.

    This notification indicates that the result will be unused, so any associated processing
    SHOULD cease.

    A client MUST NOT attempt to cancel its `initialize` request.

    For task cancellation, use the `tasks/cancel` request instead of this notification.
    """

    jsonrpc: Jsonrpc
    method: CancellednotificationMethod
    params: CancellednotificationParams

    @classmethod
    def from_dict(cls, obj: Any) -> "Cancellednotification":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        method = CancellednotificationMethod(obj.get("method"))
        params = CancellednotificationParams.from_dict(obj.get("params"))
        return Cancellednotification(jsonrpc, method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        result["method"] = to_enum(CancellednotificationMethod, self.method)
        result["params"] = to_class(CancellednotificationParams, self.params)
        return result


@dataclass
class ClientcapabilitiesElicitation(DataModelHelper):
    """Present if the client supports elicitation from the server."""

    form: Optional[Dict[str, Any]] = None
    url: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "ClientcapabilitiesElicitation":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        form = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("form"))
        url = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("url"))
        return ClientcapabilitiesElicitation(form, url)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.form is not None:
            result["form"] = from_union([lambda x: from_dict(lambda x: x, x), from_none], self.form)
        if self.url is not None:
            result["url"] = from_union([lambda x: from_dict(lambda x: x, x), from_none], self.url)
        return result


@dataclass
class Roots(DataModelHelper):
    """Present if the client supports listing roots."""

    list_changed: Optional[bool] = None
    """Whether the client supports notifications for changes to the roots list."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Roots":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        list_changed = from_union([from_bool, from_none], obj.get("listChanged"))
        return Roots(list_changed)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.list_changed is not None:
            result["listChanged"] = from_union([from_bool, from_none], self.list_changed)
        return result


@dataclass
class ClientcapabilitiesSampling(DataModelHelper):
    """Present if the client supports sampling from an LLM."""

    context: Optional[Dict[str, Any]] = None
    """Whether the client supports context inclusion via includeContext parameter.
    If not declared, servers SHOULD only use `includeContext: "none"` (or omit it).
    """
    tools: Optional[Dict[str, Any]] = None
    """Whether the client supports tool use via tools and toolChoice parameters."""

    @classmethod
    def from_dict(cls, obj: Any) -> "ClientcapabilitiesSampling":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        context = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("context"))
        tools = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("tools"))
        return ClientcapabilitiesSampling(context, tools)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.context is not None:
            result["context"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.context
            )
        if self.tools is not None:
            result["tools"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.tools
            )
        return result


@dataclass
class RequestsElicitation(DataModelHelper):
    """Task support for elicitation-related requests."""

    create: Optional[Dict[str, Any]] = None
    """Whether the client supports task-augmented elicitation/create requests."""

    @classmethod
    def from_dict(cls, obj: Any) -> "RequestsElicitation":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        create = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("create"))
        return RequestsElicitation(create)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.create is not None:
            result["create"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.create
            )
        return result


@dataclass
class RequestsSampling(DataModelHelper):
    """Task support for sampling-related requests."""

    create_message: Optional[Dict[str, Any]] = None
    """Whether the client supports task-augmented sampling/createMessage requests."""

    @classmethod
    def from_dict(cls, obj: Any) -> "RequestsSampling":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        create_message = from_union(
            [lambda x: from_dict(lambda x: x, x), from_none], obj.get("createMessage")
        )
        return RequestsSampling(create_message)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.create_message is not None:
            result["createMessage"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.create_message
            )
        return result


@dataclass
class PurpleRequests(DataModelHelper):
    """Specifies which request types can be augmented with tasks."""

    elicitation: Optional[RequestsElicitation] = None
    """Task support for elicitation-related requests."""

    sampling: Optional[RequestsSampling] = None
    """Task support for sampling-related requests."""

    @classmethod
    def from_dict(cls, obj: Any) -> "PurpleRequests":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        elicitation = from_union([RequestsElicitation.from_dict, from_none], obj.get("elicitation"))
        sampling = from_union([RequestsSampling.from_dict, from_none], obj.get("sampling"))
        return PurpleRequests(elicitation, sampling)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.elicitation is not None:
            result["elicitation"] = from_union(
                [lambda x: to_class(RequestsElicitation, x), from_none], self.elicitation
            )
        if self.sampling is not None:
            result["sampling"] = from_union(
                [lambda x: to_class(RequestsSampling, x), from_none], self.sampling
            )
        return result


@dataclass
class ClientcapabilitiesTasks(DataModelHelper):
    """Present if the client supports task-augmented requests."""

    cancel: Optional[Dict[str, Any]] = None
    """Whether this client supports tasks/cancel."""

    list: Optional[Dict[str, Any]] = None
    """Whether this client supports tasks/list."""

    requests: Optional[PurpleRequests] = None
    """Specifies which request types can be augmented with tasks."""

    @classmethod
    def from_dict(cls, obj: Any) -> "ClientcapabilitiesTasks":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        cancel = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("cancel"))
        list = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("list"))
        requests = from_union([PurpleRequests.from_dict, from_none], obj.get("requests"))
        return ClientcapabilitiesTasks(cancel, list, requests)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.cancel is not None:
            result["cancel"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.cancel
            )
        if self.list is not None:
            result["list"] = from_union([lambda x: from_dict(lambda x: x, x), from_none], self.list)
        if self.requests is not None:
            result["requests"] = from_union(
                [lambda x: to_class(PurpleRequests, x), from_none], self.requests
            )
        return result


@dataclass
class Clientcapabilities(DataModelHelper):
    """Capabilities a client may support. Known capabilities are defined here, in this schema,
    but this is not a closed set: any client can define its own, additional capabilities.
    """

    elicitation: Optional[ClientcapabilitiesElicitation] = None
    """Present if the client supports elicitation from the server."""

    experimental: Optional[Dict[str, Dict[str, Any]]] = None
    """Experimental, non-standard capabilities that the client supports."""

    roots: Optional[Roots] = None
    """Present if the client supports listing roots."""

    sampling: Optional[ClientcapabilitiesSampling] = None
    """Present if the client supports sampling from an LLM."""

    tasks: Optional[ClientcapabilitiesTasks] = None
    """Present if the client supports task-augmented requests."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Clientcapabilities":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        elicitation = from_union(
            [ClientcapabilitiesElicitation.from_dict, from_none], obj.get("elicitation")
        )
        experimental = from_union(
            [lambda x: from_dict(lambda x: from_dict(lambda x: x, x), x), from_none],
            obj.get("experimental"),
        )
        roots = from_union([Roots.from_dict, from_none], obj.get("roots"))
        sampling = from_union(
            [ClientcapabilitiesSampling.from_dict, from_none], obj.get("sampling")
        )
        tasks = from_union([ClientcapabilitiesTasks.from_dict, from_none], obj.get("tasks"))
        return Clientcapabilities(elicitation, experimental, roots, sampling, tasks)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.elicitation is not None:
            result["elicitation"] = from_union(
                [lambda x: to_class(ClientcapabilitiesElicitation, x), from_none], self.elicitation
            )
        if self.experimental is not None:
            result["experimental"] = from_union(
                [lambda x: from_dict(lambda x: from_dict(lambda x: x, x), x), from_none],
                self.experimental,
            )
        if self.roots is not None:
            result["roots"] = from_union([lambda x: to_class(Roots, x), from_none], self.roots)
        if self.sampling is not None:
            result["sampling"] = from_union(
                [lambda x: to_class(ClientcapabilitiesSampling, x), from_none], self.sampling
            )
        if self.tasks is not None:
            result["tasks"] = from_union(
                [lambda x: to_class(ClientcapabilitiesTasks, x), from_none], self.tasks
            )
        return result


class ClientnotificationMethod(Enum):
    NOTIFICATIONS_CANCELLED = "notifications/cancelled"
    NOTIFICATIONS_INITIALIZED = "notifications/initialized"
    NOTIFICATIONS_PROGRESS = "notifications/progress"
    NOTIFICATIONS_ROOTS_LIST_CHANGED = "notifications/roots/list_changed"
    NOTIFICATIONS_TASKS_STATUS = "notifications/tasks/status"


class Status(Enum):
    """Current task state.

    The status of a task.
    """

    CANCELLED = "cancelled"
    COMPLETED = "completed"
    FAILED = "failed"
    INPUT_REQUIRED = "input_required"
    WORKING = "working"


@dataclass
class ClientnotificationParams(DataModelHelper):
    """Parameters for a `notifications/cancelled` notification.

    Parameters for a `notifications/progress` notification.

    Parameters for a `notifications/tasks/status` notification.

    Data associated with a task.
    """

    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    reason: Optional[str] = None
    """An optional string describing the reason for the cancellation. This MAY be logged or
    presented to the user.
    """
    request_id: Optional[Union[int, str]] = None
    """The ID of the request to cancel.
    
    This MUST correspond to the ID of a request previously issued in the same direction.
    This MUST be provided for cancelling non-task requests.
    This MUST NOT be used for cancelling tasks (use the `tasks/cancel` request instead).
    """
    message: Optional[str] = None
    """An optional message describing the current progress."""

    progress: Optional[float] = None
    """The progress thus far. This should increase every time progress is made, even if the
    total is unknown.
    """
    progress_token: Optional[Union[int, str]] = None
    """The progress token which was given in the initial request, used to associate this
    notification with the request that is proceeding.
    """
    total: Optional[float] = None
    """Total number of items to process (or total progress required), if known."""

    created_at: Optional[str] = None
    """ISO 8601 timestamp when the task was created."""

    last_updated_at: Optional[str] = None
    """ISO 8601 timestamp when the task was last updated."""

    poll_interval: Optional[int] = None
    """Suggested polling interval in milliseconds."""

    status: Optional[Status] = None
    """Current task state."""

    status_message: Optional[str] = None
    """Optional human-readable message describing the current task state.
    This can provide context for any status, including:
    - Reasons for "cancelled" status
    - Summaries for "completed" status
    - Diagnostic information for "failed" status (e.g., error details, what went wrong)
    """
    task_id: Optional[str] = None
    """The task identifier."""

    ttl: Optional[int] = None
    """Actual retention duration from creation in milliseconds, null for unlimited."""

    @classmethod
    def from_dict(cls, obj: Any) -> "ClientnotificationParams":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        reason = from_union([from_str, from_none], obj.get("reason"))
        request_id = from_union([from_int, from_str, from_none], obj.get("requestId"))
        message = from_union([from_str, from_none], obj.get("message"))
        progress = from_union([from_float, from_none], obj.get("progress"))
        progress_token = from_union([from_int, from_str, from_none], obj.get("progressToken"))
        total = from_union([from_float, from_none], obj.get("total"))
        created_at = from_union([from_str, from_none], obj.get("createdAt"))
        last_updated_at = from_union([from_str, from_none], obj.get("lastUpdatedAt"))
        poll_interval = from_union([from_int, from_none], obj.get("pollInterval"))
        status = from_union([Status, from_none], obj.get("status"))
        status_message = from_union([from_str, from_none], obj.get("statusMessage"))
        task_id = from_union([from_str, from_none], obj.get("taskId"))
        ttl = from_union([from_int, from_none], obj.get("ttl"))
        return ClientnotificationParams(
            meta,
            reason,
            request_id,
            message,
            progress,
            progress_token,
            total,
            created_at,
            last_updated_at,
            poll_interval,
            status,
            status_message,
            task_id,
            ttl,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.reason is not None:
            result["reason"] = from_union([from_str, from_none], self.reason)
        if self.request_id is not None:
            result["requestId"] = from_union([from_int, from_str, from_none], self.request_id)
        if self.message is not None:
            result["message"] = from_union([from_str, from_none], self.message)
        if self.progress is not None:
            result["progress"] = from_union([to_float, from_none], self.progress)
        if self.progress_token is not None:
            result["progressToken"] = from_union(
                [from_int, from_str, from_none], self.progress_token
            )
        if self.total is not None:
            result["total"] = from_union([to_float, from_none], self.total)
        if self.created_at is not None:
            result["createdAt"] = from_union([from_str, from_none], self.created_at)
        if self.last_updated_at is not None:
            result["lastUpdatedAt"] = from_union([from_str, from_none], self.last_updated_at)
        if self.poll_interval is not None:
            result["pollInterval"] = from_union([from_int, from_none], self.poll_interval)
        if self.status is not None:
            result["status"] = from_union([lambda x: to_enum(Status, x), from_none], self.status)
        if self.status_message is not None:
            result["statusMessage"] = from_union([from_str, from_none], self.status_message)
        if self.task_id is not None:
            result["taskId"] = from_union([from_str, from_none], self.task_id)
        if self.ttl is not None:
            result["ttl"] = from_union([from_int, from_none], self.ttl)
        return result


@dataclass
class Clientnotification(DataModelHelper):
    """This notification can be sent by either side to indicate that it is cancelling a
    previously-issued request.

    The request SHOULD still be in-flight, but due to communication latency, it is always
    possible that this notification MAY arrive after the request has already finished.

    This notification indicates that the result will be unused, so any associated processing
    SHOULD cease.

    A client MUST NOT attempt to cancel its `initialize` request.

    For task cancellation, use the `tasks/cancel` request instead of this notification.

    This notification is sent from the client to the server after initialization has
    finished.

    An out-of-band notification used to inform the receiver of a progress update for a
    long-running request.

    An optional notification from the receiver to the requestor, informing them that a task's
    status has changed. Receivers are not required to send these notifications.

    A notification from the client to the server, informing it that the list of roots has
    changed.
    This notification should be sent whenever the client adds, removes, or modifies any root.
    The server should then request an updated list of roots using the ListRootsRequest.
    """

    jsonrpc: Jsonrpc
    method: ClientnotificationMethod
    params: Optional[ClientnotificationParams] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "Clientnotification":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        method = ClientnotificationMethod(obj.get("method"))
        params = from_union([ClientnotificationParams.from_dict, from_none], obj.get("params"))
        return Clientnotification(jsonrpc, method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        result["method"] = to_enum(ClientnotificationMethod, self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(ClientnotificationParams, x), from_none], self.params
            )
        return result


class ClientrequestMethod(Enum):
    COMPLETION_COMPLETE = "completion/complete"
    INITIALIZE = "initialize"
    LOGGING_SET_LEVEL = "logging/setLevel"
    PING = "ping"
    PROMPTS_GET = "prompts/get"
    PROMPTS_LIST = "prompts/list"
    RESOURCES_LIST = "resources/list"
    RESOURCES_READ = "resources/read"
    RESOURCES_SUBSCRIBE = "resources/subscribe"
    RESOURCES_TEMPLATES_LIST = "resources/templates/list"
    RESOURCES_UNSUBSCRIBE = "resources/unsubscribe"
    TASKS_CANCEL = "tasks/cancel"
    TASKS_GET = "tasks/get"
    TASKS_LIST = "tasks/list"
    TASKS_RESULT = "tasks/result"
    TOOLS_CALL = "tools/call"
    TOOLS_LIST = "tools/list"


@dataclass
class Argument(DataModelHelper):
    """The argument's information"""

    name: str
    """The name of the argument"""

    value: str
    """The value of the argument to use for completion matching."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Argument":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        name = from_str(obj.get("name"))
        value = from_str(obj.get("value"))
        return Argument(name, value)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["name"] = from_str(self.name)
        result["value"] = from_str(self.value)
        return result


@dataclass
class ClientInfo(DataModelHelper):
    """Describes the MCP implementation."""

    name: str
    """Intended for programmatic or logical use, but used as a display name in past specs or
    fallback (if title isn't present).
    """
    version: str
    description: Optional[str] = None
    """An optional human-readable description of what this implementation does.
    
    This can be used by clients or servers to provide context about their purpose
    and capabilities. For example, a server might describe the types of resources
    or tools it provides, while a client might describe its intended use case.
    """
    icons: Optional[List[IconElement]] = None
    """Optional set of sized icons that the client can display in a user interface.
    
    Clients that support rendering icons MUST support at least the following MIME types:
    - `image/png` - PNG images (safe, universal compatibility)
    - `image/jpeg` (and `image/jpg`) - JPEG images (safe, universal compatibility)
    
    Clients that support rendering icons SHOULD also support:
    - `image/svg+xml` - SVG images (scalable but requires security precautions)
    - `image/webp` - WebP images (modern, efficient format)
    """
    title: Optional[str] = None
    """Intended for UI and end-user contexts — optimized to be human-readable and easily
    understood,
    even by those unfamiliar with domain-specific terminology.
    
    If not provided, the name should be used for display (except for Tool,
    where `annotations.title` should be given precedence over using `name`,
    if present).
    """
    website_url: Optional[str] = None
    """An optional URL of the website for this implementation."""

    @classmethod
    def from_dict(cls, obj: Any) -> "ClientInfo":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        name = from_str(obj.get("name"))
        version = from_str(obj.get("version"))
        description = from_union([from_str, from_none], obj.get("description"))
        icons = from_union(
            [lambda x: from_list(IconElement.from_dict, x), from_none], obj.get("icons")
        )
        title = from_union([from_str, from_none], obj.get("title"))
        website_url = from_union([from_str, from_none], obj.get("websiteUrl"))
        return ClientInfo(name, version, description, icons, title, website_url)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["name"] = from_str(self.name)
        result["version"] = from_str(self.version)
        if self.description is not None:
            result["description"] = from_union([from_str, from_none], self.description)
        if self.icons is not None:
            result["icons"] = from_union(
                [lambda x: from_list(lambda x: to_class(IconElement, x), x), from_none], self.icons
            )
        if self.title is not None:
            result["title"] = from_union([from_str, from_none], self.title)
        if self.website_url is not None:
            result["websiteUrl"] = from_union([from_str, from_none], self.website_url)
        return result


@dataclass
class Context(DataModelHelper):
    """Additional, optional context for completions"""

    arguments: Optional[Dict[str, str]] = None
    """Previously-resolved variables in a URI template or prompt."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Context":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        arguments = from_union([lambda x: from_dict(from_str, x), from_none], obj.get("arguments"))
        return Context(arguments)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.arguments is not None:
            result["arguments"] = from_union(
                [lambda x: from_dict(from_str, x), from_none], self.arguments
            )
        return result


class Level(Enum):
    """The level of logging that the client wants to receive from the server. The server should
    send all logs at this level and higher (i.e., more severe) to the client as
    notifications/message.

    The severity of a log message.

    These map to syslog message severities, as specified in RFC-5424:
    https://datatracker.ietf.org/doc/html/rfc5424#section-6.2.1

    The severity of this log message.
    """

    ALERT = "alert"
    CRITICAL = "critical"
    DEBUG = "debug"
    EMERGENCY = "emergency"
    ERROR = "error"
    INFO = "info"
    NOTICE = "notice"
    WARNING = "warning"


@dataclass
class FluffyMeta(DataModelHelper):
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """

    progress_token: Optional[Union[int, str]] = None
    """If specified, the caller is requesting out-of-band progress notifications for this
    request (as represented by notifications/progress). The value of this parameter is an
    opaque token that will be attached to any subsequent notifications. The receiver is not
    obligated to provide these notifications.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "FluffyMeta":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        progress_token = from_union([from_int, from_str, from_none], obj.get("progressToken"))
        return FluffyMeta(progress_token)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.progress_token is not None:
            result["progressToken"] = from_union(
                [from_int, from_str, from_none], self.progress_token
            )
        return result


class RefType(Enum):
    REF_PROMPT = "ref/prompt"
    REF_RESOURCE = "ref/resource"


@dataclass
class Ref(DataModelHelper):
    """Identifies a prompt.

    A reference to a resource or resource template definition.
    """

    type: RefType
    name: Optional[str] = None
    """Intended for programmatic or logical use, but used as a display name in past specs or
    fallback (if title isn't present).
    """
    title: Optional[str] = None
    """Intended for UI and end-user contexts — optimized to be human-readable and easily
    understood,
    even by those unfamiliar with domain-specific terminology.
    
    If not provided, the name should be used for display (except for Tool,
    where `annotations.title` should be given precedence over using `name`,
    if present).
    """
    uri: Optional[str] = None
    """The URI or URI template of the resource."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Ref":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        type = RefType(obj.get("type"))
        name = from_union([from_str, from_none], obj.get("name"))
        title = from_union([from_str, from_none], obj.get("title"))
        uri = from_union([from_str, from_none], obj.get("uri"))
        return Ref(type, name, title, uri)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["type"] = to_enum(RefType, self.type)
        if self.name is not None:
            result["name"] = from_union([from_str, from_none], self.name)
        if self.title is not None:
            result["title"] = from_union([from_str, from_none], self.title)
        if self.uri is not None:
            result["uri"] = from_union([from_str, from_none], self.uri)
        return result


@dataclass
class ClientrequestParams(DataModelHelper):
    """Parameters for an `initialize` request.

    Common params for any request.

    Common parameters for paginated requests.

    Parameters for a `resources/read` request.

    Parameters for a `resources/subscribe` request.

    Parameters for a `resources/unsubscribe` request.

    Parameters for a `prompts/get` request.

    Parameters for a `tools/call` request.

    Parameters for a `logging/setLevel` request.

    Parameters for a `completion/complete` request.
    """

    meta: Optional[FluffyMeta] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    capabilities: Optional[Clientcapabilities] = None
    client_info: Optional[ClientInfo] = None
    protocol_version: Optional[str] = None
    """The latest version of the Model Context Protocol that the client supports. The client MAY
    decide to support older versions as well.
    """
    cursor: Optional[str] = None
    """An opaque token representing the current pagination position.
    If provided, the server should return results starting after this cursor.
    """
    uri: Optional[str] = None
    """The URI of the resource. The URI can use any protocol; it is up to the server how to
    interpret it.
    """
    arguments: Optional[Dict[str, Any]] = None
    """Arguments to use for templating the prompt.
    
    Arguments to use for the tool call.
    """
    name: Optional[str] = None
    """The name of the prompt or prompt template.
    
    The name of the tool.
    """
    task: Optional[Task] = None
    """If specified, the caller is requesting task-augmented execution for this request.
    The request will return a CreateTaskResult immediately, and the actual result can be
    retrieved later via tasks/result.
    
    Task augmentation is subject to capability negotiation - receivers MUST declare support
    for task augmentation of specific request types in their capabilities.
    """
    task_id: Optional[str] = None
    """The task identifier to query.
    
    The task identifier to retrieve results for.
    
    The task identifier to cancel.
    """
    level: Optional[Level] = None
    """The level of logging that the client wants to receive from the server. The server should
    send all logs at this level and higher (i.e., more severe) to the client as
    notifications/message.
    """
    argument: Optional[Argument] = None
    """The argument's information"""

    context: Optional[Context] = None
    """Additional, optional context for completions"""

    ref: Optional[Ref] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "ClientrequestParams":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        meta = from_union([FluffyMeta.from_dict, from_none], obj.get("_meta"))
        capabilities = from_union(
            [Clientcapabilities.from_dict, from_none], obj.get("capabilities")
        )
        client_info = from_union([ClientInfo.from_dict, from_none], obj.get("clientInfo"))
        protocol_version = from_union([from_str, from_none], obj.get("protocolVersion"))
        cursor = from_union([from_str, from_none], obj.get("cursor"))
        uri = from_union([from_str, from_none], obj.get("uri"))
        arguments = from_union(
            [lambda x: from_dict(lambda x: x, x), from_none], obj.get("arguments")
        )
        name = from_union([from_str, from_none], obj.get("name"))
        task = from_union([Task.from_dict, from_none], obj.get("task"))
        task_id = from_union([from_str, from_none], obj.get("taskId"))
        level = from_union([Level, from_none], obj.get("level"))
        argument = from_union([Argument.from_dict, from_none], obj.get("argument"))
        context = from_union([Context.from_dict, from_none], obj.get("context"))
        ref = from_union([Ref.from_dict, from_none], obj.get("ref"))
        return ClientrequestParams(
            meta,
            capabilities,
            client_info,
            protocol_version,
            cursor,
            uri,
            arguments,
            name,
            task,
            task_id,
            level,
            argument,
            context,
            ref,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.meta is not None:
            result["_meta"] = from_union([lambda x: to_class(FluffyMeta, x), from_none], self.meta)
        if self.capabilities is not None:
            result["capabilities"] = from_union(
                [lambda x: to_class(Clientcapabilities, x), from_none], self.capabilities
            )
        if self.client_info is not None:
            result["clientInfo"] = from_union(
                [lambda x: to_class(ClientInfo, x), from_none], self.client_info
            )
        if self.protocol_version is not None:
            result["protocolVersion"] = from_union([from_str, from_none], self.protocol_version)
        if self.cursor is not None:
            result["cursor"] = from_union([from_str, from_none], self.cursor)
        if self.uri is not None:
            result["uri"] = from_union([from_str, from_none], self.uri)
        if self.arguments is not None:
            result["arguments"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.arguments
            )
        if self.name is not None:
            result["name"] = from_union([from_str, from_none], self.name)
        if self.task is not None:
            result["task"] = from_union([lambda x: to_class(Task, x), from_none], self.task)
        if self.task_id is not None:
            result["taskId"] = from_union([from_str, from_none], self.task_id)
        if self.level is not None:
            result["level"] = from_union([lambda x: to_enum(Level, x), from_none], self.level)
        if self.argument is not None:
            result["argument"] = from_union(
                [lambda x: to_class(Argument, x), from_none], self.argument
            )
        if self.context is not None:
            result["context"] = from_union(
                [lambda x: to_class(Context, x), from_none], self.context
            )
        if self.ref is not None:
            result["ref"] = from_union([lambda x: to_class(Ref, x), from_none], self.ref)
        return result


@dataclass
class Clientrequest(DataModelHelper):
    """This request is sent from the client to the server when it first connects, asking it to
    begin initialization.

    A ping, issued by either the server or the client, to check that the other party is still
    alive. The receiver must promptly respond, or else may be disconnected.

    Sent from the client to request a list of resources the server has.

    Sent from the client to request a list of resource templates the server has.

    Sent from the client to the server, to read a specific resource URI.

    Sent from the client to request resources/updated notifications from the server whenever
    a particular resource changes.

    Sent from the client to request cancellation of resources/updated notifications from the
    server. This should follow a previous resources/subscribe request.

    Sent from the client to request a list of prompts and prompt templates the server has.

    Used by the client to get a prompt provided by the server.

    Sent from the client to request a list of tools the server has.

    Used by the client to invoke a tool provided by the server.

    A request to retrieve the state of a task.

    A request to retrieve the result of a completed task.

    A request to cancel a task.

    A request to retrieve a list of tasks.

    A request from the client to the server, to enable or adjust logging.

    A request from the client to the server, to ask for completion options.
    """

    id: Union[int, str]
    jsonrpc: Jsonrpc
    method: ClientrequestMethod
    params: Optional[ClientrequestParams] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "Clientrequest":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        id = from_union([from_int, from_str], obj.get("id"))
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        method = ClientrequestMethod(obj.get("method"))
        params = from_union([ClientrequestParams.from_dict, from_none], obj.get("params"))
        return Clientrequest(id, jsonrpc, method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["id"] = from_union([from_int, from_str], self.id)
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        result["method"] = to_enum(ClientrequestMethod, self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(ClientrequestParams, x), from_none], self.params
            )
        return result


class Action(Enum):
    """The user action in response to the elicitation.
    - "accept": User submitted the form/confirmed the action
    - "decline": User explicitly decline the action
    - "cancel": User dismissed without making an explicit choice
    """

    ACCEPT = "accept"
    CANCEL = "cancel"
    DECLINE = "decline"


class PurpleType(Enum):
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    TOOL_RESULT = "tool_result"
    TOOL_USE = "tool_use"


@dataclass
class ContentElement(DataModelHelper):
    """Text provided to or from an LLM.

    An image provided to or from an LLM.

    Audio provided to or from an LLM.

    A request from the assistant to call a tool.

    The result of a tool use, provided by the user back to the assistant.
    """

    type: PurpleType
    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    
    Optional metadata about the tool use. Clients SHOULD preserve this field when
    including tool uses in subsequent sampling requests to enable caching optimizations.
    
    See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    
    Optional metadata about the tool result. Clients SHOULD preserve this field when
    including tool results in subsequent sampling requests to enable caching optimizations.
    
    See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    annotations: Optional[AudiocontentAnnotations] = None
    """Optional annotations for the client."""

    text: Optional[str] = None
    """The text content of the message."""

    data: Optional[str] = None
    """The base64-encoded image data.
    
    The base64-encoded audio data.
    """
    mime_type: Optional[str] = None
    """The MIME type of the image. Different providers may support different image types.
    
    The MIME type of the audio. Different providers may support different audio types.
    """
    id: Optional[str] = None
    """A unique identifier for this tool use.
    
    This ID is used to match tool results to their corresponding tool uses.
    """
    input: Optional[Dict[str, Any]] = None
    """The arguments to pass to the tool, conforming to the tool's input schema."""

    name: Optional[str] = None
    """The name of the tool to call."""

    content: Optional[List[ContentblockElement]] = None
    """The unstructured result content of the tool use.
    
    This has the same format as CallToolResult.content and can include text, images,
    audio, resource links, and embedded resources.
    """
    is_error: Optional[bool] = None
    """Whether the tool use resulted in an error.
    
    If true, the content typically describes the error that occurred.
    Default: false
    """
    structured_content: Optional[Dict[str, Any]] = None
    """An optional structured result object.
    
    If the tool defined an outputSchema, this SHOULD conform to that schema.
    """
    tool_use_id: Optional[str] = None
    """The ID of the tool use this result corresponds to.
    
    This MUST match the ID from a previous ToolUseContent.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ContentElement":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        type = PurpleType(obj.get("type"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        annotations = from_union(
            [AudiocontentAnnotations.from_dict, from_none], obj.get("annotations")
        )
        text = from_union([from_str, from_none], obj.get("text"))
        data = from_union([from_str, from_none], obj.get("data"))
        mime_type = from_union([from_str, from_none], obj.get("mimeType"))
        id = from_union([from_str, from_none], obj.get("id"))
        input = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("input"))
        name = from_union([from_str, from_none], obj.get("name"))
        content = from_union(
            [lambda x: from_list(ContentblockElement.from_dict, x), from_none], obj.get("content")
        )
        is_error = from_union([from_bool, from_none], obj.get("isError"))
        structured_content = from_union(
            [lambda x: from_dict(lambda x: x, x), from_none], obj.get("structuredContent")
        )
        tool_use_id = from_union([from_str, from_none], obj.get("toolUseId"))
        return ContentElement(
            type,
            meta,
            annotations,
            text,
            data,
            mime_type,
            id,
            input,
            name,
            content,
            is_error,
            structured_content,
            tool_use_id,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["type"] = to_enum(PurpleType, self.type)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.annotations is not None:
            result["annotations"] = from_union(
                [lambda x: to_class(AudiocontentAnnotations, x), from_none], self.annotations
            )
        if self.text is not None:
            result["text"] = from_union([from_str, from_none], self.text)
        if self.data is not None:
            result["data"] = from_union([from_str, from_none], self.data)
        if self.mime_type is not None:
            result["mimeType"] = from_union([from_str, from_none], self.mime_type)
        if self.id is not None:
            result["id"] = from_union([from_str, from_none], self.id)
        if self.input is not None:
            result["input"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.input
            )
        if self.name is not None:
            result["name"] = from_union([from_str, from_none], self.name)
        if self.content is not None:
            result["content"] = from_union(
                [lambda x: from_list(lambda x: to_class(ContentblockElement, x), x), from_none],
                self.content,
            )
        if self.is_error is not None:
            result["isError"] = from_union([from_bool, from_none], self.is_error)
        if self.structured_content is not None:
            result["structuredContent"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.structured_content
            )
        if self.tool_use_id is not None:
            result["toolUseId"] = from_union([from_str, from_none], self.tool_use_id)
        return result


@dataclass
class PurpleModelContextProtocol20250618_Schema(DataModelHelper):
    """Text provided to or from an LLM.

    An image provided to or from an LLM.

    Audio provided to or from an LLM.

    A request from the assistant to call a tool.

    The result of a tool use, provided by the user back to the assistant.

    The submitted form data, only present when action is "accept" and mode was "form".
    Contains values matching the requested schema.
    Omitted for out-of-band mode responses.
    """

    meta: Optional[Union[Dict[str, Any], List[str], int, bool, str]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    
    Optional metadata about the tool use. Clients SHOULD preserve this field when
    including tool uses in subsequent sampling requests to enable caching optimizations.
    
    See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    
    Optional metadata about the tool result. Clients SHOULD preserve this field when
    including tool results in subsequent sampling requests to enable caching optimizations.
    
    See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    annotations: Optional[Union[AudiocontentAnnotations, List[str], int, bool, str]] = None
    """Optional annotations for the client."""

    text: Optional[Union[List[str], int, bool, str]] = None
    """The text content of the message."""

    type: Optional[Union[List[str], int, bool, str]] = None
    data: Optional[Union[List[str], int, bool, str]] = None
    """The base64-encoded image data.
    
    The base64-encoded audio data.
    """
    mime_type: Optional[Union[List[str], int, bool, str]] = None
    """The MIME type of the image. Different providers may support different image types.
    
    The MIME type of the audio. Different providers may support different audio types.
    """
    id: Optional[Union[List[str], int, bool, str]] = None
    """A unique identifier for this tool use.
    
    This ID is used to match tool results to their corresponding tool uses.
    """
    input: Optional[Union[Dict[str, Any], List[str], int, bool, str]] = None
    """The arguments to pass to the tool, conforming to the tool's input schema."""

    name: Optional[Union[List[str], int, bool, str]] = None
    """The name of the tool to call."""

    content: Optional[Union[List[Union[ContentblockElement, str]], int, bool, str]] = None
    """The unstructured result content of the tool use.
    
    This has the same format as CallToolResult.content and can include text, images,
    audio, resource links, and embedded resources.
    """
    is_error: Optional[Union[List[str], int, bool, str]] = None
    """Whether the tool use resulted in an error.
    
    If true, the content typically describes the error that occurred.
    Default: false
    """
    structured_content: Optional[Union[Dict[str, Any], List[str], int, bool, str]] = None
    """An optional structured result object.
    
    If the tool defined an outputSchema, this SHOULD conform to that schema.
    """
    tool_use_id: Optional[Union[List[str], int, bool, str]] = None
    """The ID of the tool use this result corresponds to.
    
    This MUST match the ID from a previous ToolUseContent.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "PurpleModelContextProtocol20250618_Schema":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        meta = from_union(
            [
                lambda x: from_dict(lambda x: x, x),
                lambda x: from_list(from_str, x),
                from_int,
                from_bool,
                from_str,
                from_none,
            ],
            obj.get("_meta"),
        )
        annotations = from_union(
            [
                AudiocontentAnnotations.from_dict,
                lambda x: from_list(from_str, x),
                from_int,
                from_bool,
                from_str,
                from_none,
            ],
            obj.get("annotations"),
        )
        text = from_union(
            [lambda x: from_list(from_str, x), from_int, from_bool, from_str, from_none],
            obj.get("text"),
        )
        type = from_union(
            [lambda x: from_list(from_str, x), from_int, from_bool, from_str, from_none],
            obj.get("type"),
        )
        data = from_union(
            [lambda x: from_list(from_str, x), from_int, from_bool, from_str, from_none],
            obj.get("data"),
        )
        mime_type = from_union(
            [lambda x: from_list(from_str, x), from_int, from_bool, from_str, from_none],
            obj.get("mimeType"),
        )
        id = from_union(
            [lambda x: from_list(from_str, x), from_int, from_bool, from_str, from_none],
            obj.get("id"),
        )
        input = from_union(
            [
                lambda x: from_dict(lambda x: x, x),
                lambda x: from_list(from_str, x),
                from_int,
                from_bool,
                from_str,
                from_none,
            ],
            obj.get("input"),
        )
        name = from_union(
            [lambda x: from_list(from_str, x), from_int, from_bool, from_str, from_none],
            obj.get("name"),
        )
        content = from_union(
            [
                lambda x: from_list(
                    lambda x: from_union([ContentblockElement.from_dict, from_str], x), x
                ),
                from_int,
                from_bool,
                from_str,
                from_none,
            ],
            obj.get("content"),
        )
        is_error = from_union(
            [lambda x: from_list(from_str, x), from_int, from_bool, from_str, from_none],
            obj.get("isError"),
        )
        structured_content = from_union(
            [
                lambda x: from_dict(lambda x: x, x),
                lambda x: from_list(from_str, x),
                from_int,
                from_bool,
                from_str,
                from_none,
            ],
            obj.get("structuredContent"),
        )
        tool_use_id = from_union(
            [lambda x: from_list(from_str, x), from_int, from_bool, from_str, from_none],
            obj.get("toolUseId"),
        )
        return PurpleModelContextProtocol20250618_Schema(
            meta,
            annotations,
            text,
            type,
            data,
            mime_type,
            id,
            input,
            name,
            content,
            is_error,
            structured_content,
            tool_use_id,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.meta is not None:
            result["_meta"] = from_union(
                [
                    lambda x: from_dict(lambda x: x, x),
                    lambda x: from_list(from_str, x),
                    from_int,
                    from_bool,
                    from_str,
                    from_none,
                ],
                self.meta,
            )
        if self.annotations is not None:
            result["annotations"] = from_union(
                [
                    lambda x: to_class(AudiocontentAnnotations, x),
                    lambda x: from_list(from_str, x),
                    from_int,
                    from_bool,
                    from_str,
                    from_none,
                ],
                self.annotations,
            )
        if self.text is not None:
            result["text"] = from_union(
                [lambda x: from_list(from_str, x), from_int, from_bool, from_str, from_none],
                self.text,
            )
        if self.type is not None:
            result["type"] = from_union(
                [lambda x: from_list(from_str, x), from_int, from_bool, from_str, from_none],
                self.type,
            )
        if self.data is not None:
            result["data"] = from_union(
                [lambda x: from_list(from_str, x), from_int, from_bool, from_str, from_none],
                self.data,
            )
        if self.mime_type is not None:
            result["mimeType"] = from_union(
                [lambda x: from_list(from_str, x), from_int, from_bool, from_str, from_none],
                self.mime_type,
            )
        if self.id is not None:
            result["id"] = from_union(
                [lambda x: from_list(from_str, x), from_int, from_bool, from_str, from_none],
                self.id,
            )
        if self.input is not None:
            result["input"] = from_union(
                [
                    lambda x: from_dict(lambda x: x, x),
                    lambda x: from_list(from_str, x),
                    from_int,
                    from_bool,
                    from_str,
                    from_none,
                ],
                self.input,
            )
        if self.name is not None:
            result["name"] = from_union(
                [lambda x: from_list(from_str, x), from_int, from_bool, from_str, from_none],
                self.name,
            )
        if self.content is not None:
            result["content"] = from_union(
                [
                    lambda x: from_list(
                        lambda x: from_union(
                            [lambda x: to_class(ContentblockElement, x), from_str], x
                        ),
                        x,
                    ),
                    from_int,
                    from_bool,
                    from_str,
                    from_none,
                ],
                self.content,
            )
        if self.is_error is not None:
            result["isError"] = from_union(
                [lambda x: from_list(from_str, x), from_int, from_bool, from_str, from_none],
                self.is_error,
            )
        if self.structured_content is not None:
            result["structuredContent"] = from_union(
                [
                    lambda x: from_dict(lambda x: x, x),
                    lambda x: from_list(from_str, x),
                    from_int,
                    from_bool,
                    from_str,
                    from_none,
                ],
                self.structured_content,
            )
        if self.tool_use_id is not None:
            result["toolUseId"] = from_union(
                [lambda x: from_list(from_str, x), from_int, from_bool, from_str, from_none],
                self.tool_use_id,
            )
        return result


@dataclass
class RootElement(DataModelHelper):
    """Represents a root directory or file that the server can operate on."""

    uri: str
    """The URI identifying the root. This *must* start with file:// for now.
    This restriction may be relaxed in future versions of the protocol to allow
    other URI schemes.
    """
    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    name: Optional[str] = None
    """An optional name for the root. This can be used to provide a human-readable
    identifier for the root, which may be useful for display purposes or for
    referencing the root in other parts of the application.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "RootElement":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        uri = from_str(obj.get("uri"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        name = from_union([from_str, from_none], obj.get("name"))
        return RootElement(uri, meta, name)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["uri"] = from_str(self.uri)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.name is not None:
            result["name"] = from_union([from_str, from_none], self.name)
        return result


@dataclass
class TaskElement(DataModelHelper):
    """Data associated with a task."""

    created_at: str
    """ISO 8601 timestamp when the task was created."""

    last_updated_at: str
    """ISO 8601 timestamp when the task was last updated."""

    status: Status
    """Current task state."""

    task_id: str
    """The task identifier."""

    poll_interval: Optional[int] = None
    """Suggested polling interval in milliseconds."""

    status_message: Optional[str] = None
    """Optional human-readable message describing the current task state.
    This can provide context for any status, including:
    - Reasons for "cancelled" status
    - Summaries for "completed" status
    - Diagnostic information for "failed" status (e.g., error details, what went wrong)
    """
    ttl: Optional[int] = None
    """Actual retention duration from creation in milliseconds, null for unlimited."""

    @classmethod
    def from_dict(cls, obj: Any) -> "TaskElement":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        created_at = from_str(obj.get("createdAt"))
        last_updated_at = from_str(obj.get("lastUpdatedAt"))
        status = Status(obj.get("status"))
        task_id = from_str(obj.get("taskId"))
        poll_interval = from_union([from_int, from_none], obj.get("pollInterval"))
        status_message = from_union([from_str, from_none], obj.get("statusMessage"))
        ttl = from_union([from_int, from_none], obj.get("ttl"))
        return TaskElement(
            created_at, last_updated_at, status, task_id, poll_interval, status_message, ttl
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["createdAt"] = from_str(self.created_at)
        result["lastUpdatedAt"] = from_str(self.last_updated_at)
        result["status"] = to_enum(Status, self.status)
        result["taskId"] = from_str(self.task_id)
        if self.poll_interval is not None:
            result["pollInterval"] = from_union([from_int, from_none], self.poll_interval)
        if self.status_message is not None:
            result["statusMessage"] = from_union([from_str, from_none], self.status_message)
        result["ttl"] = from_union([from_int, from_none], self.ttl)
        return result


@dataclass
class Clientresult(DataModelHelper):
    """The response to a tasks/get request.

    The response to a tasks/cancel request.

    Data associated with a task.

    The response to a tasks/result request.
    The structure matches the result type of the original request.
    For example, a tools/call task would return the CallToolResult structure.

    The response to a tasks/list request.

    The client's response to a sampling/createMessage request from the server.
    The client should inform the user before returning the sampled message, to allow them
    to inspect the response (human in the loop) and decide whether to allow the server to see
    it.

    The client's response to a roots/list request from the server.
    This result contains an array of Root objects, each representing a root directory
    or file that the server can operate on.

    The client's response to an elicitation request.
    """

    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    created_at: Optional[str] = None
    """ISO 8601 timestamp when the task was created."""

    last_updated_at: Optional[str] = None
    """ISO 8601 timestamp when the task was last updated."""

    poll_interval: Optional[int] = None
    """Suggested polling interval in milliseconds."""

    status: Optional[Status] = None
    """Current task state."""

    status_message: Optional[str] = None
    """Optional human-readable message describing the current task state.
    This can provide context for any status, including:
    - Reasons for "cancelled" status
    - Summaries for "completed" status
    - Diagnostic information for "failed" status (e.g., error details, what went wrong)
    """
    task_id: Optional[str] = None
    """The task identifier."""

    ttl: Optional[int] = None
    """Actual retention duration from creation in milliseconds, null for unlimited."""

    next_cursor: Optional[str] = None
    """An opaque token representing the pagination position after the last returned result.
    If present, there may be more results available.
    """
    tasks: Optional[List[TaskElement]] = None
    content: Optional[Union[PurpleModelContextProtocol20250618_Schema, List[ContentElement]]] = None
    """The submitted form data, only present when action is "accept" and mode was "form".
    Contains values matching the requested schema.
    Omitted for out-of-band mode responses.
    """
    model: Optional[str] = None
    """The name of the model that generated the message."""

    role: Optional[RoleElement] = None
    stop_reason: Optional[str] = None
    """The reason why sampling stopped, if known.
    
    Standard values:
    - "endTurn": Natural end of the assistant's turn
    - "stopSequence": A stop sequence was encountered
    - "maxTokens": Maximum token limit was reached
    - "toolUse": The model wants to use one or more tools
    
    This field is an open string to allow for provider-specific stop reasons.
    """
    roots: Optional[List[RootElement]] = None
    action: Optional[Action] = None
    """The user action in response to the elicitation.
    - "accept": User submitted the form/confirmed the action
    - "decline": User explicitly decline the action
    - "cancel": User dismissed without making an explicit choice
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "Clientresult":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        created_at = from_union([from_str, from_none], obj.get("createdAt"))
        last_updated_at = from_union([from_str, from_none], obj.get("lastUpdatedAt"))
        poll_interval = from_union([from_int, from_none], obj.get("pollInterval"))
        status = from_union([Status, from_none], obj.get("status"))
        status_message = from_union([from_str, from_none], obj.get("statusMessage"))
        task_id = from_union([from_str, from_none], obj.get("taskId"))
        ttl = from_union([from_int, from_none], obj.get("ttl"))
        next_cursor = from_union([from_str, from_none], obj.get("nextCursor"))
        tasks = from_union(
            [lambda x: from_list(TaskElement.from_dict, x), from_none], obj.get("tasks")
        )
        content = from_union(
            [
                PurpleModelContextProtocol20250618_Schema.from_dict,
                lambda x: from_list(ContentElement.from_dict, x),
                from_none,
            ],
            obj.get("content"),
        )
        model = from_union([from_str, from_none], obj.get("model"))
        role = from_union([RoleElement, from_none], obj.get("role"))
        stop_reason = from_union([from_str, from_none], obj.get("stopReason"))
        roots = from_union(
            [lambda x: from_list(RootElement.from_dict, x), from_none], obj.get("roots")
        )
        action = from_union([Action, from_none], obj.get("action"))
        return Clientresult(
            meta,
            created_at,
            last_updated_at,
            poll_interval,
            status,
            status_message,
            task_id,
            ttl,
            next_cursor,
            tasks,
            content,
            model,
            role,
            stop_reason,
            roots,
            action,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.created_at is not None:
            result["createdAt"] = from_union([from_str, from_none], self.created_at)
        if self.last_updated_at is not None:
            result["lastUpdatedAt"] = from_union([from_str, from_none], self.last_updated_at)
        if self.poll_interval is not None:
            result["pollInterval"] = from_union([from_int, from_none], self.poll_interval)
        if self.status is not None:
            result["status"] = from_union([lambda x: to_enum(Status, x), from_none], self.status)
        if self.status_message is not None:
            result["statusMessage"] = from_union([from_str, from_none], self.status_message)
        if self.task_id is not None:
            result["taskId"] = from_union([from_str, from_none], self.task_id)
        if self.ttl is not None:
            result["ttl"] = from_union([from_int, from_none], self.ttl)
        if self.next_cursor is not None:
            result["nextCursor"] = from_union([from_str, from_none], self.next_cursor)
        if self.tasks is not None:
            result["tasks"] = from_union(
                [lambda x: from_list(lambda x: to_class(TaskElement, x), x), from_none], self.tasks
            )
        if self.content is not None:
            result["content"] = from_union(
                [
                    lambda x: to_class(PurpleModelContextProtocol20250618_Schema, x),
                    lambda x: from_list(lambda x: to_class(ContentElement, x), x),
                    from_none,
                ],
                self.content,
            )
        if self.model is not None:
            result["model"] = from_union([from_str, from_none], self.model)
        if self.role is not None:
            result["role"] = from_union([lambda x: to_enum(RoleElement, x), from_none], self.role)
        if self.stop_reason is not None:
            result["stopReason"] = from_union([from_str, from_none], self.stop_reason)
        if self.roots is not None:
            result["roots"] = from_union(
                [lambda x: from_list(lambda x: to_class(RootElement, x), x), from_none], self.roots
            )
        if self.action is not None:
            result["action"] = from_union([lambda x: to_enum(Action, x), from_none], self.action)
        return result


class CompleterequestMethod(Enum):
    COMPLETION_COMPLETE = "completion/complete"


@dataclass
class TentacledMeta(DataModelHelper):
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """

    progress_token: Optional[Union[int, str]] = None
    """If specified, the caller is requesting out-of-band progress notifications for this
    request (as represented by notifications/progress). The value of this parameter is an
    opaque token that will be attached to any subsequent notifications. The receiver is not
    obligated to provide these notifications.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "TentacledMeta":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        progress_token = from_union([from_int, from_str, from_none], obj.get("progressToken"))
        return TentacledMeta(progress_token)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.progress_token is not None:
            result["progressToken"] = from_union(
                [from_int, from_str, from_none], self.progress_token
            )
        return result


@dataclass
class CompleterequestParams(DataModelHelper):
    """Parameters for a `completion/complete` request."""

    argument: Argument
    """The argument's information"""

    ref: Ref
    meta: Optional[TentacledMeta] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    context: Optional[Context] = None
    """Additional, optional context for completions"""

    @classmethod
    def from_dict(cls, obj: Any) -> "CompleterequestParams":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        argument = Argument.from_dict(obj.get("argument"))
        ref = Ref.from_dict(obj.get("ref"))
        meta = from_union([TentacledMeta.from_dict, from_none], obj.get("_meta"))
        context = from_union([Context.from_dict, from_none], obj.get("context"))
        return CompleterequestParams(argument, ref, meta, context)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["argument"] = to_class(Argument, self.argument)
        result["ref"] = to_class(Ref, self.ref)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: to_class(TentacledMeta, x), from_none], self.meta
            )
        if self.context is not None:
            result["context"] = from_union(
                [lambda x: to_class(Context, x), from_none], self.context
            )
        return result


@dataclass
class CompleterequestClass(DataModelHelper):
    """A request from the client to the server, to ask for completion options."""

    id: Union[int, str]
    jsonrpc: Jsonrpc
    method: CompleterequestMethod
    params: CompleterequestParams

    @classmethod
    def from_dict(cls, obj: Any) -> "CompleterequestClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        id = from_union([from_int, from_str], obj.get("id"))
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        method = CompleterequestMethod(obj.get("method"))
        params = CompleterequestParams.from_dict(obj.get("params"))
        return CompleterequestClass(id, jsonrpc, method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["id"] = from_union([from_int, from_str], self.id)
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        result["method"] = to_enum(CompleterequestMethod, self.method)
        result["params"] = to_class(CompleterequestParams, self.params)
        return result


@dataclass
class Completion(DataModelHelper):
    values: List[str]
    """An array of completion values. Must not exceed 100 items."""

    has_more: Optional[bool] = None
    """Indicates whether there are additional completion options beyond those provided in the
    current response, even if the exact total is unknown.
    """
    total: Optional[int] = None
    """The total number of completion options available. This can exceed the number of values
    actually sent in the response.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "Completion":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        values = from_list(from_str, obj.get("values"))
        has_more = from_union([from_bool, from_none], obj.get("hasMore"))
        total = from_union([from_int, from_none], obj.get("total"))
        return Completion(values, has_more, total)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["values"] = from_list(from_str, self.values)
        if self.has_more is not None:
            result["hasMore"] = from_union([from_bool, from_none], self.has_more)
        if self.total is not None:
            result["total"] = from_union([from_int, from_none], self.total)
        return result


@dataclass
class Completeresult(DataModelHelper):
    """The server's response to a completion/complete request"""

    completion: Completion
    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "Completeresult":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        completion = Completion.from_dict(obj.get("completion"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        return Completeresult(completion, meta)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["completion"] = to_class(Completion, self.completion)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        return result


class CreatemessagerequestMethod(Enum):
    SAMPLING_CREATE_MESSAGE = "sampling/createMessage"


class IncludeContext(Enum):
    """A request to include context from one or more MCP servers (including the caller), to be
    attached to the prompt.
    The client MAY ignore this request.

    Default is "none". Values "thisServer" and "allServers" are soft-deprecated. Servers
    SHOULD only use these values if the client
    declares ClientCapabilities.sampling.context. These values may be removed in future spec
    releases.
    """

    ALL_SERVERS = "allServers"
    NONE = "none"
    THIS_SERVER = "thisServer"


@dataclass
class FluffyModelContextProtocol20250618_Schema(DataModelHelper):
    """Text provided to or from an LLM.

    An image provided to or from an LLM.

    Audio provided to or from an LLM.

    A request from the assistant to call a tool.

    The result of a tool use, provided by the user back to the assistant.
    """

    type: PurpleType
    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    
    Optional metadata about the tool use. Clients SHOULD preserve this field when
    including tool uses in subsequent sampling requests to enable caching optimizations.
    
    See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    
    Optional metadata about the tool result. Clients SHOULD preserve this field when
    including tool results in subsequent sampling requests to enable caching optimizations.
    
    See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    annotations: Optional[AudiocontentAnnotations] = None
    """Optional annotations for the client."""

    text: Optional[str] = None
    """The text content of the message."""

    data: Optional[str] = None
    """The base64-encoded image data.
    
    The base64-encoded audio data.
    """
    mime_type: Optional[str] = None
    """The MIME type of the image. Different providers may support different image types.
    
    The MIME type of the audio. Different providers may support different audio types.
    """
    id: Optional[str] = None
    """A unique identifier for this tool use.
    
    This ID is used to match tool results to their corresponding tool uses.
    """
    input: Optional[Dict[str, Any]] = None
    """The arguments to pass to the tool, conforming to the tool's input schema."""

    name: Optional[str] = None
    """The name of the tool to call."""

    content: Optional[List[ContentblockElement]] = None
    """The unstructured result content of the tool use.
    
    This has the same format as CallToolResult.content and can include text, images,
    audio, resource links, and embedded resources.
    """
    is_error: Optional[bool] = None
    """Whether the tool use resulted in an error.
    
    If true, the content typically describes the error that occurred.
    Default: false
    """
    structured_content: Optional[Dict[str, Any]] = None
    """An optional structured result object.
    
    If the tool defined an outputSchema, this SHOULD conform to that schema.
    """
    tool_use_id: Optional[str] = None
    """The ID of the tool use this result corresponds to.
    
    This MUST match the ID from a previous ToolUseContent.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "FluffyModelContextProtocol20250618_Schema":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        type = PurpleType(obj.get("type"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        annotations = from_union(
            [AudiocontentAnnotations.from_dict, from_none], obj.get("annotations")
        )
        text = from_union([from_str, from_none], obj.get("text"))
        data = from_union([from_str, from_none], obj.get("data"))
        mime_type = from_union([from_str, from_none], obj.get("mimeType"))
        id = from_union([from_str, from_none], obj.get("id"))
        input = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("input"))
        name = from_union([from_str, from_none], obj.get("name"))
        content = from_union(
            [lambda x: from_list(ContentblockElement.from_dict, x), from_none], obj.get("content")
        )
        is_error = from_union([from_bool, from_none], obj.get("isError"))
        structured_content = from_union(
            [lambda x: from_dict(lambda x: x, x), from_none], obj.get("structuredContent")
        )
        tool_use_id = from_union([from_str, from_none], obj.get("toolUseId"))
        return FluffyModelContextProtocol20250618_Schema(
            type,
            meta,
            annotations,
            text,
            data,
            mime_type,
            id,
            input,
            name,
            content,
            is_error,
            structured_content,
            tool_use_id,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["type"] = to_enum(PurpleType, self.type)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.annotations is not None:
            result["annotations"] = from_union(
                [lambda x: to_class(AudiocontentAnnotations, x), from_none], self.annotations
            )
        if self.text is not None:
            result["text"] = from_union([from_str, from_none], self.text)
        if self.data is not None:
            result["data"] = from_union([from_str, from_none], self.data)
        if self.mime_type is not None:
            result["mimeType"] = from_union([from_str, from_none], self.mime_type)
        if self.id is not None:
            result["id"] = from_union([from_str, from_none], self.id)
        if self.input is not None:
            result["input"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.input
            )
        if self.name is not None:
            result["name"] = from_union([from_str, from_none], self.name)
        if self.content is not None:
            result["content"] = from_union(
                [lambda x: from_list(lambda x: to_class(ContentblockElement, x), x), from_none],
                self.content,
            )
        if self.is_error is not None:
            result["isError"] = from_union([from_bool, from_none], self.is_error)
        if self.structured_content is not None:
            result["structuredContent"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.structured_content
            )
        if self.tool_use_id is not None:
            result["toolUseId"] = from_union([from_str, from_none], self.tool_use_id)
        return result


@dataclass
class SamplingmessageElement(DataModelHelper):
    """Describes a message issued to or received from an LLM API."""

    content: Union[FluffyModelContextProtocol20250618_Schema, List[ContentElement]]
    role: RoleElement
    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "SamplingmessageElement":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        content = from_union(
            [
                FluffyModelContextProtocol20250618_Schema.from_dict,
                lambda x: from_list(ContentElement.from_dict, x),
            ],
            obj.get("content"),
        )
        role = RoleElement(obj.get("role"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        return SamplingmessageElement(content, role, meta)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["content"] = from_union(
            [
                lambda x: to_class(FluffyModelContextProtocol20250618_Schema, x),
                lambda x: from_list(lambda x: to_class(ContentElement, x), x),
            ],
            self.content,
        )
        result["role"] = to_enum(RoleElement, self.role)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        return result


@dataclass
class StickyMeta(DataModelHelper):
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """

    progress_token: Optional[Union[int, str]] = None
    """If specified, the caller is requesting out-of-band progress notifications for this
    request (as represented by notifications/progress). The value of this parameter is an
    opaque token that will be attached to any subsequent notifications. The receiver is not
    obligated to provide these notifications.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "StickyMeta":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        progress_token = from_union([from_int, from_str, from_none], obj.get("progressToken"))
        return StickyMeta(progress_token)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.progress_token is not None:
            result["progressToken"] = from_union(
                [from_int, from_str, from_none], self.progress_token
            )
        return result


@dataclass
class ModelhintElement(DataModelHelper):
    """Hints to use for model selection.

    Keys not declared here are currently left unspecified by the spec and are up
    to the client to interpret.
    """

    name: Optional[str] = None
    """A hint for a model name.
    
    The client SHOULD treat this as a substring of a model name; for example:
    - `claude-3-5-sonnet` should match `claude-3-5-sonnet-20241022`
    - `sonnet` should match `claude-3-5-sonnet-20241022`, `claude-3-sonnet-20240229`, etc.
    - `claude` should match any Claude model
    
    The client MAY also map the string to a different provider's model name or a different
    model family, as long as it fills a similar niche; for example:
    - `gemini-1.5-flash` could match `claude-3-haiku-20240307`
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ModelhintElement":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        name = from_union([from_str, from_none], obj.get("name"))
        return ModelhintElement(name)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.name is not None:
            result["name"] = from_union([from_str, from_none], self.name)
        return result


@dataclass
class ModelpreferencesClass(DataModelHelper):
    """The server's preferences for which model to select. The client MAY ignore these
    preferences.

    The server's preferences for model selection, requested of the client during sampling.

    Because LLMs can vary along multiple dimensions, choosing the "best" model is
    rarely straightforward.  Different models excel in different areas—some are
    faster but less capable, others are more capable but more expensive, and so
    on. This interface allows servers to express their priorities across multiple
    dimensions to help clients make an appropriate selection for their use case.

    These preferences are always advisory. The client MAY ignore them. It is also
    up to the client to decide how to interpret these preferences and how to
    balance them against other considerations.
    """

    cost_priority: Optional[float] = None
    """How much to prioritize cost when selecting a model. A value of 0 means cost
    is not important, while a value of 1 means cost is the most important
    factor.
    """
    hints: Optional[List[ModelhintElement]] = None
    """Optional hints to use for model selection.
    
    If multiple hints are specified, the client MUST evaluate them in order
    (such that the first match is taken).
    
    The client SHOULD prioritize these hints over the numeric priorities, but
    MAY still use the priorities to select from ambiguous matches.
    """
    intelligence_priority: Optional[float] = None
    """How much to prioritize intelligence and capabilities when selecting a
    model. A value of 0 means intelligence is not important, while a value of 1
    means intelligence is the most important factor.
    """
    speed_priority: Optional[float] = None
    """How much to prioritize sampling speed (latency) when selecting a model. A
    value of 0 means speed is not important, while a value of 1 means speed is
    the most important factor.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ModelpreferencesClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        cost_priority = from_union([from_float, from_none], obj.get("costPriority"))
        hints = from_union(
            [lambda x: from_list(ModelhintElement.from_dict, x), from_none], obj.get("hints")
        )
        intelligence_priority = from_union([from_float, from_none], obj.get("intelligencePriority"))
        speed_priority = from_union([from_float, from_none], obj.get("speedPriority"))
        return ModelpreferencesClass(cost_priority, hints, intelligence_priority, speed_priority)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.cost_priority is not None:
            result["costPriority"] = from_union([to_float, from_none], self.cost_priority)
        if self.hints is not None:
            result["hints"] = from_union(
                [lambda x: from_list(lambda x: to_class(ModelhintElement, x), x), from_none],
                self.hints,
            )
        if self.intelligence_priority is not None:
            result["intelligencePriority"] = from_union(
                [to_float, from_none], self.intelligence_priority
            )
        if self.speed_priority is not None:
            result["speedPriority"] = from_union([to_float, from_none], self.speed_priority)
        return result


class ToolChoiceMode(Enum):
    """Controls the tool use ability of the model:
    - "auto": Model decides whether to use tools (default)
    - "required": Model MUST use at least one tool before completing
    - "none": Model MUST NOT use any tools
    """

    AUTO = "auto"
    NONE = "none"
    REQUIRED = "required"


@dataclass
class ToolChoice(DataModelHelper):
    """Controls how the model uses tools.
    The client MUST return an error if this field is provided but
    ClientCapabilities.sampling.tools is not declared.
    Default is `{ mode: "auto" }`.

    Controls tool selection behavior for sampling requests.
    """

    mode: Optional[ToolChoiceMode] = None
    """Controls the tool use ability of the model:
    - "auto": Model decides whether to use tools (default)
    - "required": Model MUST use at least one tool before completing
    - "none": Model MUST NOT use any tools
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ToolChoice":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        mode = from_union([ToolChoiceMode, from_none], obj.get("mode"))
        return ToolChoice(mode)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.mode is not None:
            result["mode"] = from_union(
                [lambda x: to_enum(ToolChoiceMode, x), from_none], self.mode
            )
        return result


@dataclass
class ToolannotationsClass(DataModelHelper):
    """Optional additional tool information.

    Display name precedence order is: title, annotations.title, then name.

    Additional properties describing a Tool to clients.

    NOTE: all properties in ToolAnnotations are **hints**.
    They are not guaranteed to provide a faithful description of
    tool behavior (including descriptive properties like `title`).

    Clients should never make tool use decisions based on ToolAnnotations
    received from untrusted servers.
    """

    destructive_hint: Optional[bool] = None
    """If true, the tool may perform destructive updates to its environment.
    If false, the tool performs only additive updates.
    
    (This property is meaningful only when `readOnlyHint == false`)
    
    Default: true
    """
    idempotent_hint: Optional[bool] = None
    """If true, calling the tool repeatedly with the same arguments
    will have no additional effect on its environment.
    
    (This property is meaningful only when `readOnlyHint == false`)
    
    Default: false
    """
    open_world_hint: Optional[bool] = None
    """If true, this tool may interact with an "open world" of external
    entities. If false, the tool's domain of interaction is closed.
    For example, the world of a web search tool is open, whereas that
    of a memory tool is not.
    
    Default: true
    """
    read_only_hint: Optional[bool] = None
    """If true, the tool does not modify its environment.
    
    Default: false
    """
    title: Optional[str] = None
    """A human-readable title for the tool."""

    @classmethod
    def from_dict(cls, obj: Any) -> "ToolannotationsClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        destructive_hint = from_union([from_bool, from_none], obj.get("destructiveHint"))
        idempotent_hint = from_union([from_bool, from_none], obj.get("idempotentHint"))
        open_world_hint = from_union([from_bool, from_none], obj.get("openWorldHint"))
        read_only_hint = from_union([from_bool, from_none], obj.get("readOnlyHint"))
        title = from_union([from_str, from_none], obj.get("title"))
        return ToolannotationsClass(
            destructive_hint, idempotent_hint, open_world_hint, read_only_hint, title
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.destructive_hint is not None:
            result["destructiveHint"] = from_union([from_bool, from_none], self.destructive_hint)
        if self.idempotent_hint is not None:
            result["idempotentHint"] = from_union([from_bool, from_none], self.idempotent_hint)
        if self.open_world_hint is not None:
            result["openWorldHint"] = from_union([from_bool, from_none], self.open_world_hint)
        if self.read_only_hint is not None:
            result["readOnlyHint"] = from_union([from_bool, from_none], self.read_only_hint)
        if self.title is not None:
            result["title"] = from_union([from_str, from_none], self.title)
        return result


class TaskSupport(Enum):
    """Indicates whether this tool supports task-augmented execution.
    This allows clients to handle long-running operations through polling
    the task system.

    - "forbidden": Tool does not support task-augmented execution (default when absent)
    - "optional": Tool may support task-augmented execution
    - "required": Tool requires task-augmented execution

    Default: "forbidden"
    """

    FORBIDDEN = "forbidden"
    OPTIONAL = "optional"
    REQUIRED = "required"


@dataclass
class Execution(DataModelHelper):
    """Execution-related properties for this tool.

    Execution-related properties for a tool.
    """

    task_support: Optional[TaskSupport] = None
    """Indicates whether this tool supports task-augmented execution.
    This allows clients to handle long-running operations through polling
    the task system.
    
    - "forbidden": Tool does not support task-augmented execution (default when absent)
    - "optional": Tool may support task-augmented execution
    - "required": Tool requires task-augmented execution
    
    Default: "forbidden"
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "Execution":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        task_support = from_union([TaskSupport, from_none], obj.get("taskSupport"))
        return Execution(task_support)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.task_support is not None:
            result["taskSupport"] = from_union(
                [lambda x: to_enum(TaskSupport, x), from_none], self.task_support
            )
        return result


class InputSchemaType(Enum):
    OBJECT = "object"


@dataclass
class InputSchema(DataModelHelper):
    """A JSON Schema object defining the expected parameters for the tool."""

    type: InputSchemaType
    schema: Optional[str] = None
    properties: Optional[Dict[str, Dict[str, Any]]] = None
    required: Optional[List[str]] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "InputSchema":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        type = InputSchemaType(obj.get("type"))
        schema = from_union([from_str, from_none], obj.get("$schema"))
        properties = from_union(
            [lambda x: from_dict(lambda x: from_dict(lambda x: x, x), x), from_none],
            obj.get("properties"),
        )
        required = from_union([lambda x: from_list(from_str, x), from_none], obj.get("required"))
        return InputSchema(type, schema, properties, required)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["type"] = to_enum(InputSchemaType, self.type)
        if self.schema is not None:
            result["$schema"] = from_union([from_str, from_none], self.schema)
        if self.properties is not None:
            result["properties"] = from_union(
                [lambda x: from_dict(lambda x: from_dict(lambda x: x, x), x), from_none],
                self.properties,
            )
        if self.required is not None:
            result["required"] = from_union(
                [lambda x: from_list(from_str, x), from_none], self.required
            )
        return result


@dataclass
class OutputSchema(DataModelHelper):
    """An optional JSON Schema object defining the structure of the tool's output returned in
    the structuredContent field of a CallToolResult.

    Defaults to JSON Schema 2020-12 when no explicit $schema is provided.
    Currently restricted to type: "object" at the root level.
    """

    type: InputSchemaType
    schema: Optional[str] = None
    properties: Optional[Dict[str, Dict[str, Any]]] = None
    required: Optional[List[str]] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "OutputSchema":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        type = InputSchemaType(obj.get("type"))
        schema = from_union([from_str, from_none], obj.get("$schema"))
        properties = from_union(
            [lambda x: from_dict(lambda x: from_dict(lambda x: x, x), x), from_none],
            obj.get("properties"),
        )
        required = from_union([lambda x: from_list(from_str, x), from_none], obj.get("required"))
        return OutputSchema(type, schema, properties, required)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["type"] = to_enum(InputSchemaType, self.type)
        if self.schema is not None:
            result["$schema"] = from_union([from_str, from_none], self.schema)
        if self.properties is not None:
            result["properties"] = from_union(
                [lambda x: from_dict(lambda x: from_dict(lambda x: x, x), x), from_none],
                self.properties,
            )
        if self.required is not None:
            result["required"] = from_union(
                [lambda x: from_list(from_str, x), from_none], self.required
            )
        return result


@dataclass
class ToolElement(DataModelHelper):
    """Definition for a tool the client can call."""

    input_schema: InputSchema
    """A JSON Schema object defining the expected parameters for the tool."""

    name: str
    """Intended for programmatic or logical use, but used as a display name in past specs or
    fallback (if title isn't present).
    """
    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    annotations: Optional[ToolannotationsClass] = None
    """Optional additional tool information.
    
    Display name precedence order is: title, annotations.title, then name.
    """
    description: Optional[str] = None
    """A human-readable description of the tool.
    
    This can be used by clients to improve the LLM's understanding of available tools. It can
    be thought of like a "hint" to the model.
    """
    execution: Optional[Execution] = None
    """Execution-related properties for this tool."""

    icons: Optional[List[IconElement]] = None
    """Optional set of sized icons that the client can display in a user interface.
    
    Clients that support rendering icons MUST support at least the following MIME types:
    - `image/png` - PNG images (safe, universal compatibility)
    - `image/jpeg` (and `image/jpg`) - JPEG images (safe, universal compatibility)
    
    Clients that support rendering icons SHOULD also support:
    - `image/svg+xml` - SVG images (scalable but requires security precautions)
    - `image/webp` - WebP images (modern, efficient format)
    """
    output_schema: Optional[OutputSchema] = None
    """An optional JSON Schema object defining the structure of the tool's output returned in
    the structuredContent field of a CallToolResult.
    
    Defaults to JSON Schema 2020-12 when no explicit $schema is provided.
    Currently restricted to type: "object" at the root level.
    """
    title: Optional[str] = None
    """Intended for UI and end-user contexts — optimized to be human-readable and easily
    understood,
    even by those unfamiliar with domain-specific terminology.
    
    If not provided, the name should be used for display (except for Tool,
    where `annotations.title` should be given precedence over using `name`,
    if present).
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ToolElement":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        input_schema = InputSchema.from_dict(obj.get("inputSchema"))
        name = from_str(obj.get("name"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        annotations = from_union(
            [ToolannotationsClass.from_dict, from_none], obj.get("annotations")
        )
        description = from_union([from_str, from_none], obj.get("description"))
        execution = from_union([Execution.from_dict, from_none], obj.get("execution"))
        icons = from_union(
            [lambda x: from_list(IconElement.from_dict, x), from_none], obj.get("icons")
        )
        output_schema = from_union([OutputSchema.from_dict, from_none], obj.get("outputSchema"))
        title = from_union([from_str, from_none], obj.get("title"))
        return ToolElement(
            input_schema,
            name,
            meta,
            annotations,
            description,
            execution,
            icons,
            output_schema,
            title,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["inputSchema"] = to_class(InputSchema, self.input_schema)
        result["name"] = from_str(self.name)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.annotations is not None:
            result["annotations"] = from_union(
                [lambda x: to_class(ToolannotationsClass, x), from_none], self.annotations
            )
        if self.description is not None:
            result["description"] = from_union([from_str, from_none], self.description)
        if self.execution is not None:
            result["execution"] = from_union(
                [lambda x: to_class(Execution, x), from_none], self.execution
            )
        if self.icons is not None:
            result["icons"] = from_union(
                [lambda x: from_list(lambda x: to_class(IconElement, x), x), from_none], self.icons
            )
        if self.output_schema is not None:
            result["outputSchema"] = from_union(
                [lambda x: to_class(OutputSchema, x), from_none], self.output_schema
            )
        if self.title is not None:
            result["title"] = from_union([from_str, from_none], self.title)
        return result


@dataclass
class CreatemessagerequestParams(DataModelHelper):
    """Parameters for a `sampling/createMessage` request."""

    max_tokens: int
    """The requested maximum number of tokens to sample (to prevent runaway completions).
    
    The client MAY choose to sample fewer tokens than the requested maximum.
    """
    messages: List[SamplingmessageElement]
    meta: Optional[StickyMeta] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    include_context: Optional[IncludeContext] = None
    """A request to include context from one or more MCP servers (including the caller), to be
    attached to the prompt.
    The client MAY ignore this request.
    
    Default is "none". Values "thisServer" and "allServers" are soft-deprecated. Servers
    SHOULD only use these values if the client
    declares ClientCapabilities.sampling.context. These values may be removed in future spec
    releases.
    """
    metadata: Optional[Dict[str, Any]] = None
    """Optional metadata to pass through to the LLM provider. The format of this metadata is
    provider-specific.
    """
    model_preferences: Optional[ModelpreferencesClass] = None
    """The server's preferences for which model to select. The client MAY ignore these
    preferences.
    """
    stop_sequences: Optional[List[str]] = None
    system_prompt: Optional[str] = None
    """An optional system prompt the server wants to use for sampling. The client MAY modify or
    omit this prompt.
    """
    task: Optional[Task] = None
    """If specified, the caller is requesting task-augmented execution for this request.
    The request will return a CreateTaskResult immediately, and the actual result can be
    retrieved later via tasks/result.
    
    Task augmentation is subject to capability negotiation - receivers MUST declare support
    for task augmentation of specific request types in their capabilities.
    """
    temperature: Optional[float] = None
    tool_choice: Optional[ToolChoice] = None
    """Controls how the model uses tools.
    The client MUST return an error if this field is provided but
    ClientCapabilities.sampling.tools is not declared.
    Default is `{ mode: "auto" }`.
    """
    tools: Optional[List[ToolElement]] = None
    """Tools that the model may use during generation.
    The client MUST return an error if this field is provided but
    ClientCapabilities.sampling.tools is not declared.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "CreatemessagerequestParams":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        max_tokens = from_int(obj.get("maxTokens"))
        messages = from_list(SamplingmessageElement.from_dict, obj.get("messages"))
        meta = from_union([StickyMeta.from_dict, from_none], obj.get("_meta"))
        include_context = from_union([IncludeContext, from_none], obj.get("includeContext"))
        metadata = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("metadata"))
        model_preferences = from_union(
            [ModelpreferencesClass.from_dict, from_none], obj.get("modelPreferences")
        )
        stop_sequences = from_union(
            [lambda x: from_list(from_str, x), from_none], obj.get("stopSequences")
        )
        system_prompt = from_union([from_str, from_none], obj.get("systemPrompt"))
        task = from_union([Task.from_dict, from_none], obj.get("task"))
        temperature = from_union([from_float, from_none], obj.get("temperature"))
        tool_choice = from_union([ToolChoice.from_dict, from_none], obj.get("toolChoice"))
        tools = from_union(
            [lambda x: from_list(ToolElement.from_dict, x), from_none], obj.get("tools")
        )
        return CreatemessagerequestParams(
            max_tokens,
            messages,
            meta,
            include_context,
            metadata,
            model_preferences,
            stop_sequences,
            system_prompt,
            task,
            temperature,
            tool_choice,
            tools,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["maxTokens"] = from_int(self.max_tokens)
        result["messages"] = from_list(lambda x: to_class(SamplingmessageElement, x), self.messages)
        if self.meta is not None:
            result["_meta"] = from_union([lambda x: to_class(StickyMeta, x), from_none], self.meta)
        if self.include_context is not None:
            result["includeContext"] = from_union(
                [lambda x: to_enum(IncludeContext, x), from_none], self.include_context
            )
        if self.metadata is not None:
            result["metadata"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.metadata
            )
        if self.model_preferences is not None:
            result["modelPreferences"] = from_union(
                [lambda x: to_class(ModelpreferencesClass, x), from_none], self.model_preferences
            )
        if self.stop_sequences is not None:
            result["stopSequences"] = from_union(
                [lambda x: from_list(from_str, x), from_none], self.stop_sequences
            )
        if self.system_prompt is not None:
            result["systemPrompt"] = from_union([from_str, from_none], self.system_prompt)
        if self.task is not None:
            result["task"] = from_union([lambda x: to_class(Task, x), from_none], self.task)
        if self.temperature is not None:
            result["temperature"] = from_union([to_float, from_none], self.temperature)
        if self.tool_choice is not None:
            result["toolChoice"] = from_union(
                [lambda x: to_class(ToolChoice, x), from_none], self.tool_choice
            )
        if self.tools is not None:
            result["tools"] = from_union(
                [lambda x: from_list(lambda x: to_class(ToolElement, x), x), from_none], self.tools
            )
        return result


@dataclass
class Createmessagerequest(DataModelHelper):
    """A request from the server to sample an LLM via the client. The client has full discretion
    over which model to select. The client should also inform the user before beginning
    sampling, to allow them to inspect the request (human in the loop) and decide whether to
    approve it.
    """

    id: Union[int, str]
    jsonrpc: Jsonrpc
    method: CreatemessagerequestMethod
    params: CreatemessagerequestParams

    @classmethod
    def from_dict(cls, obj: Any) -> "Createmessagerequest":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        id = from_union([from_int, from_str], obj.get("id"))
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        method = CreatemessagerequestMethod(obj.get("method"))
        params = CreatemessagerequestParams.from_dict(obj.get("params"))
        return Createmessagerequest(id, jsonrpc, method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["id"] = from_union([from_int, from_str], self.id)
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        result["method"] = to_enum(CreatemessagerequestMethod, self.method)
        result["params"] = to_class(CreatemessagerequestParams, self.params)
        return result


@dataclass
class CreatemessageresultClass(DataModelHelper):
    """The client's response to a sampling/createMessage request from the server.
    The client should inform the user before returning the sampled message, to allow them
    to inspect the response (human in the loop) and decide whether to allow the server to see
    it.
    """

    content: Union[FluffyModelContextProtocol20250618_Schema, List[ContentElement]]
    model: str
    """The name of the model that generated the message."""

    role: RoleElement
    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    stop_reason: Optional[str] = None
    """The reason why sampling stopped, if known.
    
    Standard values:
    - "endTurn": Natural end of the assistant's turn
    - "stopSequence": A stop sequence was encountered
    - "maxTokens": Maximum token limit was reached
    - "toolUse": The model wants to use one or more tools
    
    This field is an open string to allow for provider-specific stop reasons.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "CreatemessageresultClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        content = from_union(
            [
                FluffyModelContextProtocol20250618_Schema.from_dict,
                lambda x: from_list(ContentElement.from_dict, x),
            ],
            obj.get("content"),
        )
        model = from_str(obj.get("model"))
        role = RoleElement(obj.get("role"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        stop_reason = from_union([from_str, from_none], obj.get("stopReason"))
        return CreatemessageresultClass(content, model, role, meta, stop_reason)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["content"] = from_union(
            [
                lambda x: to_class(FluffyModelContextProtocol20250618_Schema, x),
                lambda x: from_list(lambda x: to_class(ContentElement, x), x),
            ],
            self.content,
        )
        result["model"] = from_str(self.model)
        result["role"] = to_enum(RoleElement, self.role)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.stop_reason is not None:
            result["stopReason"] = from_union([from_str, from_none], self.stop_reason)
        return result


class ElicitrequestMethod(Enum):
    ELICITATION_CREATE = "elicitation/create"


@dataclass
class IndigoMeta(DataModelHelper):
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """

    progress_token: Optional[Union[int, str]] = None
    """If specified, the caller is requesting out-of-band progress notifications for this
    request (as represented by notifications/progress). The value of this parameter is an
    opaque token that will be attached to any subsequent notifications. The receiver is not
    obligated to provide these notifications.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "IndigoMeta":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        progress_token = from_union([from_int, from_str, from_none], obj.get("progressToken"))
        return IndigoMeta(progress_token)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.progress_token is not None:
            result["progressToken"] = from_union(
                [from_int, from_str, from_none], self.progress_token
            )
        return result


class ParamsMode(Enum):
    FORM = "form"
    URL = "url"


class Format(Enum):
    DATE = "date"
    DATE_TIME = "date-time"
    EMAIL = "email"
    URI = "uri"


@dataclass
class AnyOf(DataModelHelper):
    const: str
    """The constant enum value."""

    title: str
    """Display title for this option."""

    @classmethod
    def from_dict(cls, obj: Any) -> "AnyOf":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        const = from_str(obj.get("const"))
        title = from_str(obj.get("title"))
        return AnyOf(const, title)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["const"] = from_str(self.const)
        result["title"] = from_str(self.title)
        return result


class ItemsType(Enum):
    STRING = "string"


@dataclass
class Items(DataModelHelper):
    """Schema for the array items.

    Schema for array items with enum options and display labels.
    """

    enum: Optional[List[str]] = None
    """Array of enum values to choose from."""

    type: Optional[ItemsType] = None
    any_of: Optional[List[AnyOf]] = None
    """Array of enum options with values and display labels."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Items":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        enum = from_union([lambda x: from_list(from_str, x), from_none], obj.get("enum"))
        type = from_union([ItemsType, from_none], obj.get("type"))
        any_of = from_union([lambda x: from_list(AnyOf.from_dict, x), from_none], obj.get("anyOf"))
        return Items(enum, type, any_of)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.enum is not None:
            result["enum"] = from_union([lambda x: from_list(from_str, x), from_none], self.enum)
        if self.type is not None:
            result["type"] = from_union([lambda x: to_enum(ItemsType, x), from_none], self.type)
        if self.any_of is not None:
            result["anyOf"] = from_union(
                [lambda x: from_list(lambda x: to_class(AnyOf, x), x), from_none], self.any_of
            )
        return result


@dataclass
class OneOf(DataModelHelper):
    const: str
    """The enum value."""

    title: str
    """Display label for this option."""

    @classmethod
    def from_dict(cls, obj: Any) -> "OneOf":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        const = from_str(obj.get("const"))
        title = from_str(obj.get("title"))
        return OneOf(const, title)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["const"] = from_str(self.const)
        result["title"] = from_str(self.title)
        return result


class PrimitiveschemadefinitionType(Enum):
    ARRAY = "array"
    BOOLEAN = "boolean"
    INTEGER = "integer"
    NUMBER = "number"
    STRING = "string"


@dataclass
class PrimitiveschemadefinitionValue(DataModelHelper):
    """Restricted schema definitions that only allow primitive types
    without nested objects or arrays.

    Schema for single-selection enumeration without display titles for options.

    Schema for single-selection enumeration with display titles for each option.

    Schema for multiple-selection enumeration without display titles for options.

    Schema for multiple-selection enumeration with display titles for each option.

    Use TitledSingleSelectEnumSchema instead.
    This interface will be removed in a future version.
    """

    type: PrimitiveschemadefinitionType
    default: Optional[Union[List[str], int, bool, str]] = None
    """Optional default value."""

    description: Optional[str] = None
    """Optional description for the enum field."""

    format: Optional[Format] = None
    max_length: Optional[int] = None
    min_length: Optional[int] = None
    title: Optional[str] = None
    """Optional title for the enum field."""

    maximum: Optional[int] = None
    minimum: Optional[int] = None
    enum: Optional[List[str]] = None
    """Array of enum values to choose from."""

    one_of: Optional[List[OneOf]] = None
    """Array of enum options with values and display labels."""

    items: Optional[Items] = None
    """Schema for the array items.
    
    Schema for array items with enum options and display labels.
    """
    max_items: Optional[int] = None
    """Maximum number of items to select."""

    min_items: Optional[int] = None
    """Minimum number of items to select."""

    enum_names: Optional[List[str]] = None
    """(Legacy) Display names for enum values.
    Non-standard according to JSON schema 2020-12.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "PrimitiveschemadefinitionValue":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        type = PrimitiveschemadefinitionType(obj.get("type"))
        default = from_union(
            [lambda x: from_list(from_str, x), from_int, from_bool, from_str, from_none],
            obj.get("default"),
        )
        description = from_union([from_str, from_none], obj.get("description"))
        format = from_union([Format, from_none], obj.get("format"))
        max_length = from_union([from_int, from_none], obj.get("maxLength"))
        min_length = from_union([from_int, from_none], obj.get("minLength"))
        title = from_union([from_str, from_none], obj.get("title"))
        maximum = from_union([from_int, from_none], obj.get("maximum"))
        minimum = from_union([from_int, from_none], obj.get("minimum"))
        enum = from_union([lambda x: from_list(from_str, x), from_none], obj.get("enum"))
        one_of = from_union([lambda x: from_list(OneOf.from_dict, x), from_none], obj.get("oneOf"))
        items = from_union([Items.from_dict, from_none], obj.get("items"))
        max_items = from_union([from_int, from_none], obj.get("maxItems"))
        min_items = from_union([from_int, from_none], obj.get("minItems"))
        enum_names = from_union([lambda x: from_list(from_str, x), from_none], obj.get("enumNames"))
        return PrimitiveschemadefinitionValue(
            type,
            default,
            description,
            format,
            max_length,
            min_length,
            title,
            maximum,
            minimum,
            enum,
            one_of,
            items,
            max_items,
            min_items,
            enum_names,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["type"] = to_enum(PrimitiveschemadefinitionType, self.type)
        if self.default is not None:
            result["default"] = from_union(
                [lambda x: from_list(from_str, x), from_int, from_bool, from_str, from_none],
                self.default,
            )
        if self.description is not None:
            result["description"] = from_union([from_str, from_none], self.description)
        if self.format is not None:
            result["format"] = from_union([lambda x: to_enum(Format, x), from_none], self.format)
        if self.max_length is not None:
            result["maxLength"] = from_union([from_int, from_none], self.max_length)
        if self.min_length is not None:
            result["minLength"] = from_union([from_int, from_none], self.min_length)
        if self.title is not None:
            result["title"] = from_union([from_str, from_none], self.title)
        if self.maximum is not None:
            result["maximum"] = from_union([from_int, from_none], self.maximum)
        if self.minimum is not None:
            result["minimum"] = from_union([from_int, from_none], self.minimum)
        if self.enum is not None:
            result["enum"] = from_union([lambda x: from_list(from_str, x), from_none], self.enum)
        if self.one_of is not None:
            result["oneOf"] = from_union(
                [lambda x: from_list(lambda x: to_class(OneOf, x), x), from_none], self.one_of
            )
        if self.items is not None:
            result["items"] = from_union([lambda x: to_class(Items, x), from_none], self.items)
        if self.max_items is not None:
            result["maxItems"] = from_union([from_int, from_none], self.max_items)
        if self.min_items is not None:
            result["minItems"] = from_union([from_int, from_none], self.min_items)
        if self.enum_names is not None:
            result["enumNames"] = from_union(
                [lambda x: from_list(from_str, x), from_none], self.enum_names
            )
        return result


@dataclass
class RequestedSchema(DataModelHelper):
    """A restricted subset of JSON Schema.
    Only top-level properties are allowed, without nesting.
    """

    properties: Dict[str, PrimitiveschemadefinitionValue]
    type: InputSchemaType
    schema: Optional[str] = None
    required: Optional[List[str]] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "RequestedSchema":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        properties = from_dict(PrimitiveschemadefinitionValue.from_dict, obj.get("properties"))
        type = InputSchemaType(obj.get("type"))
        schema = from_union([from_str, from_none], obj.get("$schema"))
        required = from_union([lambda x: from_list(from_str, x), from_none], obj.get("required"))
        return RequestedSchema(properties, type, schema, required)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["properties"] = from_dict(
            lambda x: to_class(PrimitiveschemadefinitionValue, x), self.properties
        )
        result["type"] = to_enum(InputSchemaType, self.type)
        if self.schema is not None:
            result["$schema"] = from_union([from_str, from_none], self.schema)
        if self.required is not None:
            result["required"] = from_union(
                [lambda x: from_list(from_str, x), from_none], self.required
            )
        return result


@dataclass
class ElicitrequestParams(DataModelHelper):
    """The parameters for a request to elicit additional information from the user via the
    client.

    The parameters for a request to elicit information from the user via a URL in the
    client.

    The parameters for a request to elicit non-sensitive information from the user via a form
    in the client.
    """

    message: str
    """The message to present to the user explaining why the interaction is needed.
    
    The message to present to the user describing what information is being requested.
    """
    meta: Optional[IndigoMeta] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    elicitation_id: Optional[str] = None
    """The ID of the elicitation, which must be unique within the context of the server.
    The client MUST treat this ID as an opaque value.
    """
    mode: Optional[ParamsMode] = None
    """The elicitation mode."""

    task: Optional[Task] = None
    """If specified, the caller is requesting task-augmented execution for this request.
    The request will return a CreateTaskResult immediately, and the actual result can be
    retrieved later via tasks/result.
    
    Task augmentation is subject to capability negotiation - receivers MUST declare support
    for task augmentation of specific request types in their capabilities.
    """
    url: Optional[str] = None
    """The URL that the user should navigate to."""

    requested_schema: Optional[RequestedSchema] = None
    """A restricted subset of JSON Schema.
    Only top-level properties are allowed, without nesting.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ElicitrequestParams":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        message = from_str(obj.get("message"))
        meta = from_union([IndigoMeta.from_dict, from_none], obj.get("_meta"))
        elicitation_id = from_union([from_str, from_none], obj.get("elicitationId"))
        mode = from_union([ParamsMode, from_none], obj.get("mode"))
        task = from_union([Task.from_dict, from_none], obj.get("task"))
        url = from_union([from_str, from_none], obj.get("url"))
        requested_schema = from_union(
            [RequestedSchema.from_dict, from_none], obj.get("requestedSchema")
        )
        return ElicitrequestParams(message, meta, elicitation_id, mode, task, url, requested_schema)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["message"] = from_str(self.message)
        if self.meta is not None:
            result["_meta"] = from_union([lambda x: to_class(IndigoMeta, x), from_none], self.meta)
        if self.elicitation_id is not None:
            result["elicitationId"] = from_union([from_str, from_none], self.elicitation_id)
        if self.mode is not None:
            result["mode"] = from_union([lambda x: to_enum(ParamsMode, x), from_none], self.mode)
        if self.task is not None:
            result["task"] = from_union([lambda x: to_class(Task, x), from_none], self.task)
        if self.url is not None:
            result["url"] = from_union([from_str, from_none], self.url)
        if self.requested_schema is not None:
            result["requestedSchema"] = from_union(
                [lambda x: to_class(RequestedSchema, x), from_none], self.requested_schema
            )
        return result


@dataclass
class Elicitrequest(DataModelHelper):
    """A request from the server to elicit additional information from the user via the client."""

    id: Union[int, str]
    jsonrpc: Jsonrpc
    method: ElicitrequestMethod
    params: ElicitrequestParams

    @classmethod
    def from_dict(cls, obj: Any) -> "Elicitrequest":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        id = from_union([from_int, from_str], obj.get("id"))
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        method = ElicitrequestMethod(obj.get("method"))
        params = ElicitrequestParams.from_dict(obj.get("params"))
        return Elicitrequest(id, jsonrpc, method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["id"] = from_union([from_int, from_str], self.id)
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        result["method"] = to_enum(ElicitrequestMethod, self.method)
        result["params"] = to_class(ElicitrequestParams, self.params)
        return result


@dataclass
class ElicitresultClass(DataModelHelper):
    """The client's response to an elicitation request."""

    action: Action
    """The user action in response to the elicitation.
    - "accept": User submitted the form/confirmed the action
    - "decline": User explicitly decline the action
    - "cancel": User dismissed without making an explicit choice
    """
    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    content: Optional[Dict[str, Union[List[str], int, bool, str]]] = None
    """The submitted form data, only present when action is "accept" and mode was "form".
    Contains values matching the requested schema.
    Omitted for out-of-band mode responses.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ElicitresultClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        action = Action(obj.get("action"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        content = from_union(
            [
                lambda x: from_dict(
                    lambda x: from_union(
                        [lambda x: from_list(from_str, x), from_int, from_bool, from_str], x
                    ),
                    x,
                ),
                from_none,
            ],
            obj.get("content"),
        )
        return ElicitresultClass(action, meta, content)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["action"] = to_enum(Action, self.action)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.content is not None:
            result["content"] = from_union(
                [
                    lambda x: from_dict(
                        lambda x: from_union(
                            [lambda x: from_list(from_str, x), from_int, from_bool, from_str], x
                        ),
                        x,
                    ),
                    from_none,
                ],
                self.content,
            )
        return result


class EmbeddedresourceType(Enum):
    RESOURCE = "resource"


@dataclass
class EmbeddedresourceClass(DataModelHelper):
    """The contents of a resource, embedded into a prompt or tool call result.

    It is up to the client how best to render embedded resources for the benefit
    of the LLM and/or the user.
    """

    resource: Resource
    type: EmbeddedresourceType
    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    annotations: Optional[AudiocontentAnnotations] = None
    """Optional annotations for the client."""

    @classmethod
    def from_dict(cls, obj: Any) -> "EmbeddedresourceClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        resource = Resource.from_dict(obj.get("resource"))
        type = EmbeddedresourceType(obj.get("type"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        annotations = from_union(
            [AudiocontentAnnotations.from_dict, from_none], obj.get("annotations")
        )
        return EmbeddedresourceClass(resource, type, meta, annotations)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["resource"] = to_class(Resource, self.resource)
        result["type"] = to_enum(EmbeddedresourceType, self.type)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.annotations is not None:
            result["annotations"] = from_union(
                [lambda x: to_class(AudiocontentAnnotations, x), from_none], self.annotations
            )
        return result


@dataclass
class EmptyresultClass(DataModelHelper):
    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "EmptyresultClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        return EmptyresultClass(meta)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        return result


class EnumschemaType(Enum):
    ARRAY = "array"
    STRING = "string"


@dataclass
class EnumschemaClass(DataModelHelper):
    """Schema for single-selection enumeration without display titles for options.

    Schema for single-selection enumeration with display titles for each option.

    Schema for multiple-selection enumeration without display titles for options.

    Schema for multiple-selection enumeration with display titles for each option.

    Use TitledSingleSelectEnumSchema instead.
    This interface will be removed in a future version.
    """

    type: EnumschemaType
    default: Optional[Union[str, List[str]]] = None
    """Optional default value."""

    description: Optional[str] = None
    """Optional description for the enum field."""

    enum: Optional[List[str]] = None
    """Array of enum values to choose from."""

    title: Optional[str] = None
    """Optional title for the enum field."""

    one_of: Optional[List[OneOf]] = None
    """Array of enum options with values and display labels."""

    items: Optional[Items] = None
    """Schema for the array items.
    
    Schema for array items with enum options and display labels.
    """
    max_items: Optional[int] = None
    """Maximum number of items to select."""

    min_items: Optional[int] = None
    """Minimum number of items to select."""

    enum_names: Optional[List[str]] = None
    """(Legacy) Display names for enum values.
    Non-standard according to JSON schema 2020-12.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "EnumschemaClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        type = EnumschemaType(obj.get("type"))
        default = from_union(
            [from_str, lambda x: from_list(from_str, x), from_none], obj.get("default")
        )
        description = from_union([from_str, from_none], obj.get("description"))
        enum = from_union([lambda x: from_list(from_str, x), from_none], obj.get("enum"))
        title = from_union([from_str, from_none], obj.get("title"))
        one_of = from_union([lambda x: from_list(OneOf.from_dict, x), from_none], obj.get("oneOf"))
        items = from_union([Items.from_dict, from_none], obj.get("items"))
        max_items = from_union([from_int, from_none], obj.get("maxItems"))
        min_items = from_union([from_int, from_none], obj.get("minItems"))
        enum_names = from_union([lambda x: from_list(from_str, x), from_none], obj.get("enumNames"))
        return EnumschemaClass(
            type, default, description, enum, title, one_of, items, max_items, min_items, enum_names
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["type"] = to_enum(EnumschemaType, self.type)
        if self.default is not None:
            result["default"] = from_union(
                [from_str, lambda x: from_list(from_str, x), from_none], self.default
            )
        if self.description is not None:
            result["description"] = from_union([from_str, from_none], self.description)
        if self.enum is not None:
            result["enum"] = from_union([lambda x: from_list(from_str, x), from_none], self.enum)
        if self.title is not None:
            result["title"] = from_union([from_str, from_none], self.title)
        if self.one_of is not None:
            result["oneOf"] = from_union(
                [lambda x: from_list(lambda x: to_class(OneOf, x), x), from_none], self.one_of
            )
        if self.items is not None:
            result["items"] = from_union([lambda x: to_class(Items, x), from_none], self.items)
        if self.max_items is not None:
            result["maxItems"] = from_union([from_int, from_none], self.max_items)
        if self.min_items is not None:
            result["minItems"] = from_union([from_int, from_none], self.min_items)
        if self.enum_names is not None:
            result["enumNames"] = from_union(
                [lambda x: from_list(from_str, x), from_none], self.enum_names
            )
        return result


class GetpromptrequestMethod(Enum):
    PROMPTS_GET = "prompts/get"


@dataclass
class IndecentMeta(DataModelHelper):
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """

    progress_token: Optional[Union[int, str]] = None
    """If specified, the caller is requesting out-of-band progress notifications for this
    request (as represented by notifications/progress). The value of this parameter is an
    opaque token that will be attached to any subsequent notifications. The receiver is not
    obligated to provide these notifications.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "IndecentMeta":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        progress_token = from_union([from_int, from_str, from_none], obj.get("progressToken"))
        return IndecentMeta(progress_token)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.progress_token is not None:
            result["progressToken"] = from_union(
                [from_int, from_str, from_none], self.progress_token
            )
        return result


@dataclass
class GetpromptrequestParams(DataModelHelper):
    """Parameters for a `prompts/get` request."""

    name: str
    """The name of the prompt or prompt template."""

    meta: Optional[IndecentMeta] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    arguments: Optional[Dict[str, str]] = None
    """Arguments to use for templating the prompt."""

    @classmethod
    def from_dict(cls, obj: Any) -> "GetpromptrequestParams":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        name = from_str(obj.get("name"))
        meta = from_union([IndecentMeta.from_dict, from_none], obj.get("_meta"))
        arguments = from_union([lambda x: from_dict(from_str, x), from_none], obj.get("arguments"))
        return GetpromptrequestParams(name, meta, arguments)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["name"] = from_str(self.name)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: to_class(IndecentMeta, x), from_none], self.meta
            )
        if self.arguments is not None:
            result["arguments"] = from_union(
                [lambda x: from_dict(from_str, x), from_none], self.arguments
            )
        return result


@dataclass
class GetpromptrequestClass(DataModelHelper):
    """Used by the client to get a prompt provided by the server."""

    id: Union[int, str]
    jsonrpc: Jsonrpc
    method: GetpromptrequestMethod
    params: GetpromptrequestParams

    @classmethod
    def from_dict(cls, obj: Any) -> "GetpromptrequestClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        id = from_union([from_int, from_str], obj.get("id"))
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        method = GetpromptrequestMethod(obj.get("method"))
        params = GetpromptrequestParams.from_dict(obj.get("params"))
        return GetpromptrequestClass(id, jsonrpc, method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["id"] = from_union([from_int, from_str], self.id)
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        result["method"] = to_enum(GetpromptrequestMethod, self.method)
        result["params"] = to_class(GetpromptrequestParams, self.params)
        return result


@dataclass
class PromptmessageElement(DataModelHelper):
    """Describes a message returned as part of a prompt.

    This is similar to `SamplingMessage`, but also supports the embedding of
    resources from the MCP server.
    """

    content: ContentblockElement
    role: RoleElement

    @classmethod
    def from_dict(cls, obj: Any) -> "PromptmessageElement":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        content = ContentblockElement.from_dict(obj.get("content"))
        role = RoleElement(obj.get("role"))
        return PromptmessageElement(content, role)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["content"] = to_class(ContentblockElement, self.content)
        result["role"] = to_enum(RoleElement, self.role)
        return result


@dataclass
class Getpromptresult(DataModelHelper):
    """The server's response to a prompts/get request from the client."""

    messages: List[PromptmessageElement]
    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    description: Optional[str] = None
    """An optional description for the prompt."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Getpromptresult":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        messages = from_list(PromptmessageElement.from_dict, obj.get("messages"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        description = from_union([from_str, from_none], obj.get("description"))
        return Getpromptresult(messages, meta, description)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["messages"] = from_list(lambda x: to_class(PromptmessageElement, x), self.messages)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.description is not None:
            result["description"] = from_union([from_str, from_none], self.description)
        return result


class ImagecontentType(Enum):
    IMAGE = "image"


@dataclass
class ImagecontentClass(DataModelHelper):
    """An image provided to or from an LLM."""

    data: str
    """The base64-encoded image data."""

    mime_type: str
    """The MIME type of the image. Different providers may support different image types."""

    type: ImagecontentType
    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    annotations: Optional[AudiocontentAnnotations] = None
    """Optional annotations for the client."""

    @classmethod
    def from_dict(cls, obj: Any) -> "ImagecontentClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        data = from_str(obj.get("data"))
        mime_type = from_str(obj.get("mimeType"))
        type = ImagecontentType(obj.get("type"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        annotations = from_union(
            [AudiocontentAnnotations.from_dict, from_none], obj.get("annotations")
        )
        return ImagecontentClass(data, mime_type, type, meta, annotations)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["data"] = from_str(self.data)
        result["mimeType"] = from_str(self.mime_type)
        result["type"] = to_enum(ImagecontentType, self.type)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.annotations is not None:
            result["annotations"] = from_union(
                [lambda x: to_class(AudiocontentAnnotations, x), from_none], self.annotations
            )
        return result


class InitializednotificationMethod(Enum):
    NOTIFICATIONS_INITIALIZED = "notifications/initialized"


@dataclass
class InitializednotificationParams(DataModelHelper):
    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "InitializednotificationParams":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        return InitializednotificationParams(meta)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        return result


@dataclass
class InitializednotificationClass(DataModelHelper):
    """This notification is sent from the client to the server after initialization has finished."""

    jsonrpc: Jsonrpc
    method: InitializednotificationMethod
    params: Optional[InitializednotificationParams] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "InitializednotificationClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        method = InitializednotificationMethod(obj.get("method"))
        params = from_union([InitializednotificationParams.from_dict, from_none], obj.get("params"))
        return InitializednotificationClass(jsonrpc, method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        result["method"] = to_enum(InitializednotificationMethod, self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(InitializednotificationParams, x), from_none], self.params
            )
        return result


class InitializerequestMethod(Enum):
    INITIALIZE = "initialize"


@dataclass
class HilariousMeta(DataModelHelper):
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """

    progress_token: Optional[Union[int, str]] = None
    """If specified, the caller is requesting out-of-band progress notifications for this
    request (as represented by notifications/progress). The value of this parameter is an
    opaque token that will be attached to any subsequent notifications. The receiver is not
    obligated to provide these notifications.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "HilariousMeta":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        progress_token = from_union([from_int, from_str, from_none], obj.get("progressToken"))
        return HilariousMeta(progress_token)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.progress_token is not None:
            result["progressToken"] = from_union(
                [from_int, from_str, from_none], self.progress_token
            )
        return result


@dataclass
class InitializerequestParams(DataModelHelper):
    """Parameters for an `initialize` request."""

    capabilities: Clientcapabilities
    client_info: ClientInfo
    protocol_version: str
    """The latest version of the Model Context Protocol that the client supports. The client MAY
    decide to support older versions as well.
    """
    meta: Optional[HilariousMeta] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "InitializerequestParams":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        capabilities = Clientcapabilities.from_dict(obj.get("capabilities"))
        client_info = ClientInfo.from_dict(obj.get("clientInfo"))
        protocol_version = from_str(obj.get("protocolVersion"))
        meta = from_union([HilariousMeta.from_dict, from_none], obj.get("_meta"))
        return InitializerequestParams(capabilities, client_info, protocol_version, meta)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["capabilities"] = to_class(Clientcapabilities, self.capabilities)
        result["clientInfo"] = to_class(ClientInfo, self.client_info)
        result["protocolVersion"] = from_str(self.protocol_version)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: to_class(HilariousMeta, x), from_none], self.meta
            )
        return result


@dataclass
class InitializerequestClass(DataModelHelper):
    """This request is sent from the client to the server when it first connects, asking it to
    begin initialization.
    """

    id: Union[int, str]
    jsonrpc: Jsonrpc
    method: InitializerequestMethod
    params: InitializerequestParams

    @classmethod
    def from_dict(cls, obj: Any) -> "InitializerequestClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        id = from_union([from_int, from_str], obj.get("id"))
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        method = InitializerequestMethod(obj.get("method"))
        params = InitializerequestParams.from_dict(obj.get("params"))
        return InitializerequestClass(id, jsonrpc, method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["id"] = from_union([from_int, from_str], self.id)
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        result["method"] = to_enum(InitializerequestMethod, self.method)
        result["params"] = to_class(InitializerequestParams, self.params)
        return result


@dataclass
class Prompts(DataModelHelper):
    """Present if the server offers any prompt templates."""

    list_changed: Optional[bool] = None
    """Whether this server supports notifications for changes to the prompt list."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Prompts":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        list_changed = from_union([from_bool, from_none], obj.get("listChanged"))
        return Prompts(list_changed)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.list_changed is not None:
            result["listChanged"] = from_union([from_bool, from_none], self.list_changed)
        return result


@dataclass
class Resources(DataModelHelper):
    """Present if the server offers any resources to read."""

    list_changed: Optional[bool] = None
    """Whether this server supports notifications for changes to the resource list."""

    subscribe: Optional[bool] = None
    """Whether this server supports subscribing to resource updates."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Resources":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        list_changed = from_union([from_bool, from_none], obj.get("listChanged"))
        subscribe = from_union([from_bool, from_none], obj.get("subscribe"))
        return Resources(list_changed, subscribe)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.list_changed is not None:
            result["listChanged"] = from_union([from_bool, from_none], self.list_changed)
        if self.subscribe is not None:
            result["subscribe"] = from_union([from_bool, from_none], self.subscribe)
        return result


@dataclass
class RequestsTools(DataModelHelper):
    """Task support for tool-related requests."""

    call: Optional[Dict[str, Any]] = None
    """Whether the server supports task-augmented tools/call requests."""

    @classmethod
    def from_dict(cls, obj: Any) -> "RequestsTools":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        call = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("call"))
        return RequestsTools(call)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.call is not None:
            result["call"] = from_union([lambda x: from_dict(lambda x: x, x), from_none], self.call)
        return result


@dataclass
class FluffyRequests(DataModelHelper):
    """Specifies which request types can be augmented with tasks."""

    tools: Optional[RequestsTools] = None
    """Task support for tool-related requests."""

    @classmethod
    def from_dict(cls, obj: Any) -> "FluffyRequests":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        tools = from_union([RequestsTools.from_dict, from_none], obj.get("tools"))
        return FluffyRequests(tools)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.tools is not None:
            result["tools"] = from_union(
                [lambda x: to_class(RequestsTools, x), from_none], self.tools
            )
        return result


@dataclass
class ServercapabilitiesTasks(DataModelHelper):
    """Present if the server supports task-augmented requests."""

    cancel: Optional[Dict[str, Any]] = None
    """Whether this server supports tasks/cancel."""

    list: Optional[Dict[str, Any]] = None
    """Whether this server supports tasks/list."""

    requests: Optional[FluffyRequests] = None
    """Specifies which request types can be augmented with tasks."""

    @classmethod
    def from_dict(cls, obj: Any) -> "ServercapabilitiesTasks":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        cancel = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("cancel"))
        list = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("list"))
        requests = from_union([FluffyRequests.from_dict, from_none], obj.get("requests"))
        return ServercapabilitiesTasks(cancel, list, requests)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.cancel is not None:
            result["cancel"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.cancel
            )
        if self.list is not None:
            result["list"] = from_union([lambda x: from_dict(lambda x: x, x), from_none], self.list)
        if self.requests is not None:
            result["requests"] = from_union(
                [lambda x: to_class(FluffyRequests, x), from_none], self.requests
            )
        return result


@dataclass
class ServercapabilitiesTools(DataModelHelper):
    """Present if the server offers any tools to call."""

    list_changed: Optional[bool] = None
    """Whether this server supports notifications for changes to the tool list."""

    @classmethod
    def from_dict(cls, obj: Any) -> "ServercapabilitiesTools":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        list_changed = from_union([from_bool, from_none], obj.get("listChanged"))
        return ServercapabilitiesTools(list_changed)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.list_changed is not None:
            result["listChanged"] = from_union([from_bool, from_none], self.list_changed)
        return result


@dataclass
class Capabilities(DataModelHelper):
    """Capabilities that a server may support. Known capabilities are defined here, in this
    schema, but this is not a closed set: any server can define its own, additional
    capabilities.
    """

    completions: Optional[Dict[str, Any]] = None
    """Present if the server supports argument autocompletion suggestions."""

    experimental: Optional[Dict[str, Dict[str, Any]]] = None
    """Experimental, non-standard capabilities that the server supports."""

    logging: Optional[Dict[str, Any]] = None
    """Present if the server supports sending log messages to the client."""

    prompts: Optional[Prompts] = None
    """Present if the server offers any prompt templates."""

    resources: Optional[Resources] = None
    """Present if the server offers any resources to read."""

    tasks: Optional[ServercapabilitiesTasks] = None
    """Present if the server supports task-augmented requests."""

    tools: Optional[ServercapabilitiesTools] = None
    """Present if the server offers any tools to call."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Capabilities":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        completions = from_union(
            [lambda x: from_dict(lambda x: x, x), from_none], obj.get("completions")
        )
        experimental = from_union(
            [lambda x: from_dict(lambda x: from_dict(lambda x: x, x), x), from_none],
            obj.get("experimental"),
        )
        logging = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("logging"))
        prompts = from_union([Prompts.from_dict, from_none], obj.get("prompts"))
        resources = from_union([Resources.from_dict, from_none], obj.get("resources"))
        tasks = from_union([ServercapabilitiesTasks.from_dict, from_none], obj.get("tasks"))
        tools = from_union([ServercapabilitiesTools.from_dict, from_none], obj.get("tools"))
        return Capabilities(completions, experimental, logging, prompts, resources, tasks, tools)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.completions is not None:
            result["completions"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.completions
            )
        if self.experimental is not None:
            result["experimental"] = from_union(
                [lambda x: from_dict(lambda x: from_dict(lambda x: x, x), x), from_none],
                self.experimental,
            )
        if self.logging is not None:
            result["logging"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.logging
            )
        if self.prompts is not None:
            result["prompts"] = from_union(
                [lambda x: to_class(Prompts, x), from_none], self.prompts
            )
        if self.resources is not None:
            result["resources"] = from_union(
                [lambda x: to_class(Resources, x), from_none], self.resources
            )
        if self.tasks is not None:
            result["tasks"] = from_union(
                [lambda x: to_class(ServercapabilitiesTasks, x), from_none], self.tasks
            )
        if self.tools is not None:
            result["tools"] = from_union(
                [lambda x: to_class(ServercapabilitiesTools, x), from_none], self.tools
            )
        return result


@dataclass
class Initializeresult(DataModelHelper):
    """After receiving an initialize request from the client, the server sends this response."""

    capabilities: Capabilities
    protocol_version: str
    """The version of the Model Context Protocol that the server wants to use. This may not
    match the version that the client requested. If the client cannot support this version,
    it MUST disconnect.
    """
    server_info: ClientInfo
    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    instructions: Optional[str] = None
    """Instructions describing how to use the server and its features.
    
    This can be used by clients to improve the LLM's understanding of available tools,
    resources, etc. It can be thought of like a "hint" to the model. For example, this
    information MAY be added to the system prompt.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "Initializeresult":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        capabilities = Capabilities.from_dict(obj.get("capabilities"))
        protocol_version = from_str(obj.get("protocolVersion"))
        server_info = ClientInfo.from_dict(obj.get("serverInfo"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        instructions = from_union([from_str, from_none], obj.get("instructions"))
        return Initializeresult(capabilities, protocol_version, server_info, meta, instructions)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["capabilities"] = to_class(Capabilities, self.capabilities)
        result["protocolVersion"] = from_str(self.protocol_version)
        result["serverInfo"] = to_class(ClientInfo, self.server_info)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.instructions is not None:
            result["instructions"] = from_union([from_str, from_none], self.instructions)
        return result


@dataclass
class Error(DataModelHelper):
    code: int
    """The error type that occurred."""

    message: str
    """A short description of the error. The message SHOULD be limited to a concise single
    sentence.
    """
    data: Any
    """Additional information about the error. The value of this member is defined by the sender
    (e.g. detailed error information, nested errors etc.).
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "Error":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        code = from_int(obj.get("code"))
        message = from_str(obj.get("message"))
        data = obj.get("data")
        return Error(code, message, data)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["code"] = from_int(self.code)
        result["message"] = from_str(self.message)
        if self.data is not None:
            result["data"] = self.data
        return result


@dataclass
class Jsonrpcerror(DataModelHelper):
    """A response to a request that indicates an error occurred."""

    error: Error
    jsonrpc: Jsonrpc
    id: Optional[Union[int, str]] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "Jsonrpcerror":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        error = Error.from_dict(obj.get("error"))
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        id = from_union([from_int, from_str, from_none], obj.get("id"))
        return Jsonrpcerror(error, jsonrpc, id)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["error"] = to_class(Error, self.error)
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        if self.id is not None:
            result["id"] = from_union([from_int, from_str, from_none], self.id)
        return result


@dataclass
class Jsonrpcmessage(DataModelHelper):
    """Refers to any valid JSON-RPC object that can be decoded off the wire, or encoded to be
    sent.

    A request that expects a response.

    A notification which does not expect a response.

    A successful (non-error) response to a request.

    A response to a request that indicates an error occurred.
    """

    jsonrpc: Jsonrpc
    id: Optional[Union[int, str]] = None
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[EmptyresultClass] = None
    error: Optional[Error] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "Jsonrpcmessage":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        id = from_union([from_int, from_str, from_none], obj.get("id"))
        method = from_union([from_str, from_none], obj.get("method"))
        params = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("params"))
        result = from_union([EmptyresultClass.from_dict, from_none], obj.get("result"))
        error = from_union([Error.from_dict, from_none], obj.get("error"))
        return Jsonrpcmessage(jsonrpc, id, method, params, result, error)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        if self.id is not None:
            result["id"] = from_union([from_int, from_str, from_none], self.id)
        if self.method is not None:
            result["method"] = from_union([from_str, from_none], self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.params
            )
        if self.result is not None:
            result["result"] = from_union(
                [lambda x: to_class(EmptyresultClass, x), from_none], self.result
            )
        if self.error is not None:
            result["error"] = from_union([lambda x: to_class(Error, x), from_none], self.error)
        return result


@dataclass
class JsonrpcnotificationClass(DataModelHelper):
    """A notification which does not expect a response."""

    jsonrpc: Jsonrpc
    method: str
    params: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "JsonrpcnotificationClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        method = from_str(obj.get("method"))
        params = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("params"))
        return JsonrpcnotificationClass(jsonrpc, method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        result["method"] = from_str(self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.params
            )
        return result


@dataclass
class JsonrpcrequestClass(DataModelHelper):
    """A request that expects a response."""

    id: Union[int, str]
    jsonrpc: Jsonrpc
    method: str
    params: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "JsonrpcrequestClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        id = from_union([from_int, from_str], obj.get("id"))
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        method = from_str(obj.get("method"))
        params = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("params"))
        return JsonrpcrequestClass(id, jsonrpc, method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["id"] = from_union([from_int, from_str], self.id)
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        result["method"] = from_str(self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.params
            )
        return result


@dataclass
class Jsonrpcresponse(DataModelHelper):
    """A response to a request, containing either the result or error.

    A successful (non-error) response to a request.

    A response to a request that indicates an error occurred.
    """

    jsonrpc: Jsonrpc
    id: Optional[Union[int, str]] = None
    result: Optional[EmptyresultClass] = None
    error: Optional[Error] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "Jsonrpcresponse":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        id = from_union([from_int, from_str, from_none], obj.get("id"))
        result = from_union([EmptyresultClass.from_dict, from_none], obj.get("result"))
        error = from_union([Error.from_dict, from_none], obj.get("error"))
        return Jsonrpcresponse(jsonrpc, id, result, error)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        if self.id is not None:
            result["id"] = from_union([from_int, from_str, from_none], self.id)
        if self.result is not None:
            result["result"] = from_union(
                [lambda x: to_class(EmptyresultClass, x), from_none], self.result
            )
        if self.error is not None:
            result["error"] = from_union([lambda x: to_class(Error, x), from_none], self.error)
        return result


class ListpromptsrequestMethod(Enum):
    PROMPTS_LIST = "prompts/list"


@dataclass
class AmbitiousMeta(DataModelHelper):
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """

    progress_token: Optional[Union[int, str]] = None
    """If specified, the caller is requesting out-of-band progress notifications for this
    request (as represented by notifications/progress). The value of this parameter is an
    opaque token that will be attached to any subsequent notifications. The receiver is not
    obligated to provide these notifications.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "AmbitiousMeta":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        progress_token = from_union([from_int, from_str, from_none], obj.get("progressToken"))
        return AmbitiousMeta(progress_token)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.progress_token is not None:
            result["progressToken"] = from_union(
                [from_int, from_str, from_none], self.progress_token
            )
        return result


@dataclass
class ListpromptsrequestParams(DataModelHelper):
    """Common parameters for paginated requests."""

    meta: Optional[AmbitiousMeta] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    cursor: Optional[str] = None
    """An opaque token representing the current pagination position.
    If provided, the server should return results starting after this cursor.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ListpromptsrequestParams":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        meta = from_union([AmbitiousMeta.from_dict, from_none], obj.get("_meta"))
        cursor = from_union([from_str, from_none], obj.get("cursor"))
        return ListpromptsrequestParams(meta, cursor)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: to_class(AmbitiousMeta, x), from_none], self.meta
            )
        if self.cursor is not None:
            result["cursor"] = from_union([from_str, from_none], self.cursor)
        return result


@dataclass
class ListpromptsrequestClass(DataModelHelper):
    """Sent from the client to request a list of prompts and prompt templates the server has."""

    id: Union[int, str]
    jsonrpc: Jsonrpc
    method: ListpromptsrequestMethod
    params: Optional[ListpromptsrequestParams] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "ListpromptsrequestClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        id = from_union([from_int, from_str], obj.get("id"))
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        method = ListpromptsrequestMethod(obj.get("method"))
        params = from_union([ListpromptsrequestParams.from_dict, from_none], obj.get("params"))
        return ListpromptsrequestClass(id, jsonrpc, method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["id"] = from_union([from_int, from_str], self.id)
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        result["method"] = to_enum(ListpromptsrequestMethod, self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(ListpromptsrequestParams, x), from_none], self.params
            )
        return result


@dataclass
class PromptargumentElement(DataModelHelper):
    """Describes an argument that a prompt can accept."""

    name: str
    """Intended for programmatic or logical use, but used as a display name in past specs or
    fallback (if title isn't present).
    """
    description: Optional[str] = None
    """A human-readable description of the argument."""

    required: Optional[bool] = None
    """Whether this argument must be provided."""

    title: Optional[str] = None
    """Intended for UI and end-user contexts — optimized to be human-readable and easily
    understood,
    even by those unfamiliar with domain-specific terminology.
    
    If not provided, the name should be used for display (except for Tool,
    where `annotations.title` should be given precedence over using `name`,
    if present).
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "PromptargumentElement":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        name = from_str(obj.get("name"))
        description = from_union([from_str, from_none], obj.get("description"))
        required = from_union([from_bool, from_none], obj.get("required"))
        title = from_union([from_str, from_none], obj.get("title"))
        return PromptargumentElement(name, description, required, title)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["name"] = from_str(self.name)
        if self.description is not None:
            result["description"] = from_union([from_str, from_none], self.description)
        if self.required is not None:
            result["required"] = from_union([from_bool, from_none], self.required)
        if self.title is not None:
            result["title"] = from_union([from_str, from_none], self.title)
        return result


@dataclass
class PromptElement(DataModelHelper):
    """A prompt or prompt template that the server offers."""

    name: str
    """Intended for programmatic or logical use, but used as a display name in past specs or
    fallback (if title isn't present).
    """
    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    arguments: Optional[List[PromptargumentElement]] = None
    """A list of arguments to use for templating the prompt."""

    description: Optional[str] = None
    """An optional description of what this prompt provides"""

    icons: Optional[List[IconElement]] = None
    """Optional set of sized icons that the client can display in a user interface.
    
    Clients that support rendering icons MUST support at least the following MIME types:
    - `image/png` - PNG images (safe, universal compatibility)
    - `image/jpeg` (and `image/jpg`) - JPEG images (safe, universal compatibility)
    
    Clients that support rendering icons SHOULD also support:
    - `image/svg+xml` - SVG images (scalable but requires security precautions)
    - `image/webp` - WebP images (modern, efficient format)
    """
    title: Optional[str] = None
    """Intended for UI and end-user contexts — optimized to be human-readable and easily
    understood,
    even by those unfamiliar with domain-specific terminology.
    
    If not provided, the name should be used for display (except for Tool,
    where `annotations.title` should be given precedence over using `name`,
    if present).
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "PromptElement":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        name = from_str(obj.get("name"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        arguments = from_union(
            [lambda x: from_list(PromptargumentElement.from_dict, x), from_none],
            obj.get("arguments"),
        )
        description = from_union([from_str, from_none], obj.get("description"))
        icons = from_union(
            [lambda x: from_list(IconElement.from_dict, x), from_none], obj.get("icons")
        )
        title = from_union([from_str, from_none], obj.get("title"))
        return PromptElement(name, meta, arguments, description, icons, title)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["name"] = from_str(self.name)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.arguments is not None:
            result["arguments"] = from_union(
                [lambda x: from_list(lambda x: to_class(PromptargumentElement, x), x), from_none],
                self.arguments,
            )
        if self.description is not None:
            result["description"] = from_union([from_str, from_none], self.description)
        if self.icons is not None:
            result["icons"] = from_union(
                [lambda x: from_list(lambda x: to_class(IconElement, x), x), from_none], self.icons
            )
        if self.title is not None:
            result["title"] = from_union([from_str, from_none], self.title)
        return result


@dataclass
class Listpromptsresult(DataModelHelper):
    """The server's response to a prompts/list request from the client."""

    prompts: List[PromptElement]
    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    next_cursor: Optional[str] = None
    """An opaque token representing the pagination position after the last returned result.
    If present, there may be more results available.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "Listpromptsresult":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        prompts = from_list(PromptElement.from_dict, obj.get("prompts"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        next_cursor = from_union([from_str, from_none], obj.get("nextCursor"))
        return Listpromptsresult(prompts, meta, next_cursor)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["prompts"] = from_list(lambda x: to_class(PromptElement, x), self.prompts)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.next_cursor is not None:
            result["nextCursor"] = from_union([from_str, from_none], self.next_cursor)
        return result


class ListresourcesrequestMethod(Enum):
    RESOURCES_LIST = "resources/list"


@dataclass
class ListresourcesrequestClass(DataModelHelper):
    """Sent from the client to request a list of resources the server has."""

    id: Union[int, str]
    jsonrpc: Jsonrpc
    method: ListresourcesrequestMethod
    params: Optional[ListpromptsrequestParams] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "ListresourcesrequestClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        id = from_union([from_int, from_str], obj.get("id"))
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        method = ListresourcesrequestMethod(obj.get("method"))
        params = from_union([ListpromptsrequestParams.from_dict, from_none], obj.get("params"))
        return ListresourcesrequestClass(id, jsonrpc, method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["id"] = from_union([from_int, from_str], self.id)
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        result["method"] = to_enum(ListresourcesrequestMethod, self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(ListpromptsrequestParams, x), from_none], self.params
            )
        return result


@dataclass
class ResourceElement(DataModelHelper):
    """A known resource that the server is capable of reading."""

    name: str
    """Intended for programmatic or logical use, but used as a display name in past specs or
    fallback (if title isn't present).
    """
    uri: str
    """The URI of this resource."""

    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    annotations: Optional[AudiocontentAnnotations] = None
    """Optional annotations for the client."""

    description: Optional[str] = None
    """A description of what this resource represents.
    
    This can be used by clients to improve the LLM's understanding of available resources. It
    can be thought of like a "hint" to the model.
    """
    icons: Optional[List[IconElement]] = None
    """Optional set of sized icons that the client can display in a user interface.
    
    Clients that support rendering icons MUST support at least the following MIME types:
    - `image/png` - PNG images (safe, universal compatibility)
    - `image/jpeg` (and `image/jpg`) - JPEG images (safe, universal compatibility)
    
    Clients that support rendering icons SHOULD also support:
    - `image/svg+xml` - SVG images (scalable but requires security precautions)
    - `image/webp` - WebP images (modern, efficient format)
    """
    mime_type: Optional[str] = None
    """The MIME type of this resource, if known."""

    size: Optional[int] = None
    """The size of the raw resource content, in bytes (i.e., before base64 encoding or any
    tokenization), if known.
    
    This can be used by Hosts to display file sizes and estimate context window usage.
    """
    title: Optional[str] = None
    """Intended for UI and end-user contexts — optimized to be human-readable and easily
    understood,
    even by those unfamiliar with domain-specific terminology.
    
    If not provided, the name should be used for display (except for Tool,
    where `annotations.title` should be given precedence over using `name`,
    if present).
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ResourceElement":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        name = from_str(obj.get("name"))
        uri = from_str(obj.get("uri"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        annotations = from_union(
            [AudiocontentAnnotations.from_dict, from_none], obj.get("annotations")
        )
        description = from_union([from_str, from_none], obj.get("description"))
        icons = from_union(
            [lambda x: from_list(IconElement.from_dict, x), from_none], obj.get("icons")
        )
        mime_type = from_union([from_str, from_none], obj.get("mimeType"))
        size = from_union([from_int, from_none], obj.get("size"))
        title = from_union([from_str, from_none], obj.get("title"))
        return ResourceElement(
            name, uri, meta, annotations, description, icons, mime_type, size, title
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["name"] = from_str(self.name)
        result["uri"] = from_str(self.uri)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.annotations is not None:
            result["annotations"] = from_union(
                [lambda x: to_class(AudiocontentAnnotations, x), from_none], self.annotations
            )
        if self.description is not None:
            result["description"] = from_union([from_str, from_none], self.description)
        if self.icons is not None:
            result["icons"] = from_union(
                [lambda x: from_list(lambda x: to_class(IconElement, x), x), from_none], self.icons
            )
        if self.mime_type is not None:
            result["mimeType"] = from_union([from_str, from_none], self.mime_type)
        if self.size is not None:
            result["size"] = from_union([from_int, from_none], self.size)
        if self.title is not None:
            result["title"] = from_union([from_str, from_none], self.title)
        return result


@dataclass
class Listresourcesresult(DataModelHelper):
    """The server's response to a resources/list request from the client."""

    resources: List[ResourceElement]
    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    next_cursor: Optional[str] = None
    """An opaque token representing the pagination position after the last returned result.
    If present, there may be more results available.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "Listresourcesresult":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        resources = from_list(ResourceElement.from_dict, obj.get("resources"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        next_cursor = from_union([from_str, from_none], obj.get("nextCursor"))
        return Listresourcesresult(resources, meta, next_cursor)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["resources"] = from_list(lambda x: to_class(ResourceElement, x), self.resources)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.next_cursor is not None:
            result["nextCursor"] = from_union([from_str, from_none], self.next_cursor)
        return result


class ListresourcetemplatesrequestMethod(Enum):
    RESOURCES_TEMPLATES_LIST = "resources/templates/list"


@dataclass
class ListresourcetemplatesrequestClass(DataModelHelper):
    """Sent from the client to request a list of resource templates the server has."""

    id: Union[int, str]
    jsonrpc: Jsonrpc
    method: ListresourcetemplatesrequestMethod
    params: Optional[ListpromptsrequestParams] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "ListresourcetemplatesrequestClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        id = from_union([from_int, from_str], obj.get("id"))
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        method = ListresourcetemplatesrequestMethod(obj.get("method"))
        params = from_union([ListpromptsrequestParams.from_dict, from_none], obj.get("params"))
        return ListresourcetemplatesrequestClass(id, jsonrpc, method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["id"] = from_union([from_int, from_str], self.id)
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        result["method"] = to_enum(ListresourcetemplatesrequestMethod, self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(ListpromptsrequestParams, x), from_none], self.params
            )
        return result


@dataclass
class ResourcetemplateElement(DataModelHelper):
    """A template description for resources available on the server."""

    name: str
    """Intended for programmatic or logical use, but used as a display name in past specs or
    fallback (if title isn't present).
    """
    uri_template: str
    """A URI template (according to RFC 6570) that can be used to construct resource URIs."""

    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    annotations: Optional[AudiocontentAnnotations] = None
    """Optional annotations for the client."""

    description: Optional[str] = None
    """A description of what this template is for.
    
    This can be used by clients to improve the LLM's understanding of available resources. It
    can be thought of like a "hint" to the model.
    """
    icons: Optional[List[IconElement]] = None
    """Optional set of sized icons that the client can display in a user interface.
    
    Clients that support rendering icons MUST support at least the following MIME types:
    - `image/png` - PNG images (safe, universal compatibility)
    - `image/jpeg` (and `image/jpg`) - JPEG images (safe, universal compatibility)
    
    Clients that support rendering icons SHOULD also support:
    - `image/svg+xml` - SVG images (scalable but requires security precautions)
    - `image/webp` - WebP images (modern, efficient format)
    """
    mime_type: Optional[str] = None
    """The MIME type for all resources that match this template. This should only be included if
    all resources matching this template have the same type.
    """
    title: Optional[str] = None
    """Intended for UI and end-user contexts — optimized to be human-readable and easily
    understood,
    even by those unfamiliar with domain-specific terminology.
    
    If not provided, the name should be used for display (except for Tool,
    where `annotations.title` should be given precedence over using `name`,
    if present).
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ResourcetemplateElement":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        name = from_str(obj.get("name"))
        uri_template = from_str(obj.get("uriTemplate"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        annotations = from_union(
            [AudiocontentAnnotations.from_dict, from_none], obj.get("annotations")
        )
        description = from_union([from_str, from_none], obj.get("description"))
        icons = from_union(
            [lambda x: from_list(IconElement.from_dict, x), from_none], obj.get("icons")
        )
        mime_type = from_union([from_str, from_none], obj.get("mimeType"))
        title = from_union([from_str, from_none], obj.get("title"))
        return ResourcetemplateElement(
            name, uri_template, meta, annotations, description, icons, mime_type, title
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["name"] = from_str(self.name)
        result["uriTemplate"] = from_str(self.uri_template)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.annotations is not None:
            result["annotations"] = from_union(
                [lambda x: to_class(AudiocontentAnnotations, x), from_none], self.annotations
            )
        if self.description is not None:
            result["description"] = from_union([from_str, from_none], self.description)
        if self.icons is not None:
            result["icons"] = from_union(
                [lambda x: from_list(lambda x: to_class(IconElement, x), x), from_none], self.icons
            )
        if self.mime_type is not None:
            result["mimeType"] = from_union([from_str, from_none], self.mime_type)
        if self.title is not None:
            result["title"] = from_union([from_str, from_none], self.title)
        return result


@dataclass
class Listresourcetemplatesresult(DataModelHelper):
    """The server's response to a resources/templates/list request from the client."""

    resource_templates: List[ResourcetemplateElement]
    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    next_cursor: Optional[str] = None
    """An opaque token representing the pagination position after the last returned result.
    If present, there may be more results available.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "Listresourcetemplatesresult":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        resource_templates = from_list(
            ResourcetemplateElement.from_dict, obj.get("resourceTemplates")
        )
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        next_cursor = from_union([from_str, from_none], obj.get("nextCursor"))
        return Listresourcetemplatesresult(resource_templates, meta, next_cursor)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["resourceTemplates"] = from_list(
            lambda x: to_class(ResourcetemplateElement, x), self.resource_templates
        )
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.next_cursor is not None:
            result["nextCursor"] = from_union([from_str, from_none], self.next_cursor)
        return result


class ListrootsrequestMethod(Enum):
    ROOTS_LIST = "roots/list"


@dataclass
class CunningMeta(DataModelHelper):
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """

    progress_token: Optional[Union[int, str]] = None
    """If specified, the caller is requesting out-of-band progress notifications for this
    request (as represented by notifications/progress). The value of this parameter is an
    opaque token that will be attached to any subsequent notifications. The receiver is not
    obligated to provide these notifications.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "CunningMeta":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        progress_token = from_union([from_int, from_str, from_none], obj.get("progressToken"))
        return CunningMeta(progress_token)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.progress_token is not None:
            result["progressToken"] = from_union(
                [from_int, from_str, from_none], self.progress_token
            )
        return result


@dataclass
class ListrootsrequestParams(DataModelHelper):
    """Common params for any request."""

    meta: Optional[CunningMeta] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ListrootsrequestParams":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        meta = from_union([CunningMeta.from_dict, from_none], obj.get("_meta"))
        return ListrootsrequestParams(meta)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.meta is not None:
            result["_meta"] = from_union([lambda x: to_class(CunningMeta, x), from_none], self.meta)
        return result


@dataclass
class Listrootsrequest(DataModelHelper):
    """Sent from the server to request a list of root URIs from the client. Roots allow
    servers to ask for specific directories or files to operate on. A common example
    for roots is providing a set of repositories or directories a server should operate
    on.

    This request is typically used when the server needs to understand the file system
    structure or access specific locations that the client has permission to read from.
    """

    id: Union[int, str]
    jsonrpc: Jsonrpc
    method: ListrootsrequestMethod
    params: Optional[ListrootsrequestParams] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "Listrootsrequest":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        id = from_union([from_int, from_str], obj.get("id"))
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        method = ListrootsrequestMethod(obj.get("method"))
        params = from_union([ListrootsrequestParams.from_dict, from_none], obj.get("params"))
        return Listrootsrequest(id, jsonrpc, method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["id"] = from_union([from_int, from_str], self.id)
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        result["method"] = to_enum(ListrootsrequestMethod, self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(ListrootsrequestParams, x), from_none], self.params
            )
        return result


@dataclass
class ListrootsresultClass(DataModelHelper):
    """The client's response to a roots/list request from the server.
    This result contains an array of Root objects, each representing a root directory
    or file that the server can operate on.
    """

    roots: List[RootElement]
    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ListrootsresultClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        roots = from_list(RootElement.from_dict, obj.get("roots"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        return ListrootsresultClass(roots, meta)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["roots"] = from_list(lambda x: to_class(RootElement, x), self.roots)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        return result


class ListtoolsrequestMethod(Enum):
    TOOLS_LIST = "tools/list"


@dataclass
class ListtoolsrequestClass(DataModelHelper):
    """Sent from the client to request a list of tools the server has."""

    id: Union[int, str]
    jsonrpc: Jsonrpc
    method: ListtoolsrequestMethod
    params: Optional[ListpromptsrequestParams] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "ListtoolsrequestClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        id = from_union([from_int, from_str], obj.get("id"))
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        method = ListtoolsrequestMethod(obj.get("method"))
        params = from_union([ListpromptsrequestParams.from_dict, from_none], obj.get("params"))
        return ListtoolsrequestClass(id, jsonrpc, method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["id"] = from_union([from_int, from_str], self.id)
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        result["method"] = to_enum(ListtoolsrequestMethod, self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(ListpromptsrequestParams, x), from_none], self.params
            )
        return result


@dataclass
class Listtoolsresult(DataModelHelper):
    """The server's response to a tools/list request from the client."""

    tools: List[ToolElement]
    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    next_cursor: Optional[str] = None
    """An opaque token representing the pagination position after the last returned result.
    If present, there may be more results available.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "Listtoolsresult":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        tools = from_list(ToolElement.from_dict, obj.get("tools"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        next_cursor = from_union([from_str, from_none], obj.get("nextCursor"))
        return Listtoolsresult(tools, meta, next_cursor)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["tools"] = from_list(lambda x: to_class(ToolElement, x), self.tools)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.next_cursor is not None:
            result["nextCursor"] = from_union([from_str, from_none], self.next_cursor)
        return result


class LoggingmessagenotificationMethod(Enum):
    NOTIFICATIONS_MESSAGE = "notifications/message"


@dataclass
class LoggingmessagenotificationParams(DataModelHelper):
    """Parameters for a `notifications/message` notification."""

    data: Any
    """The data to be logged, such as a string message or an object. Any JSON serializable type
    is allowed here.
    """
    level: Level
    """The severity of this log message."""

    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    logger: Optional[str] = None
    """An optional name of the logger issuing this message."""

    @classmethod
    def from_dict(cls, obj: Any) -> "LoggingmessagenotificationParams":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        data = obj.get("data")
        level = Level(obj.get("level"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        logger = from_union([from_str, from_none], obj.get("logger"))
        return LoggingmessagenotificationParams(data, level, meta, logger)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["data"] = self.data
        result["level"] = to_enum(Level, self.level)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.logger is not None:
            result["logger"] = from_union([from_str, from_none], self.logger)
        return result


@dataclass
class Loggingmessagenotification(DataModelHelper):
    """JSONRPCNotification of a log message passed from server to client. If no logging/setLevel
    request has been sent from the client, the server MAY decide which messages to send
    automatically.
    """

    jsonrpc: Jsonrpc
    method: LoggingmessagenotificationMethod
    params: LoggingmessagenotificationParams

    @classmethod
    def from_dict(cls, obj: Any) -> "Loggingmessagenotification":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        method = LoggingmessagenotificationMethod(obj.get("method"))
        params = LoggingmessagenotificationParams.from_dict(obj.get("params"))
        return Loggingmessagenotification(jsonrpc, method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        result["method"] = to_enum(LoggingmessagenotificationMethod, self.method)
        result["params"] = to_class(LoggingmessagenotificationParams, self.params)
        return result


@dataclass
class Notification(DataModelHelper):
    method: str
    params: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "Notification":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        method = from_str(obj.get("method"))
        params = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("params"))
        return Notification(method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["method"] = from_str(self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.params
            )
        return result


class NumberschemaType(Enum):
    INTEGER = "integer"
    NUMBER = "number"


@dataclass
class NumberschemaClass(DataModelHelper):
    type: NumberschemaType
    default: Optional[int] = None
    description: Optional[str] = None
    maximum: Optional[int] = None
    minimum: Optional[int] = None
    title: Optional[str] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "NumberschemaClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        type = NumberschemaType(obj.get("type"))
        default = from_union([from_int, from_none], obj.get("default"))
        description = from_union([from_str, from_none], obj.get("description"))
        maximum = from_union([from_int, from_none], obj.get("maximum"))
        minimum = from_union([from_int, from_none], obj.get("minimum"))
        title = from_union([from_str, from_none], obj.get("title"))
        return NumberschemaClass(type, default, description, maximum, minimum, title)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["type"] = to_enum(NumberschemaType, self.type)
        if self.default is not None:
            result["default"] = from_union([from_int, from_none], self.default)
        if self.description is not None:
            result["description"] = from_union([from_str, from_none], self.description)
        if self.maximum is not None:
            result["maximum"] = from_union([from_int, from_none], self.maximum)
        if self.minimum is not None:
            result["minimum"] = from_union([from_int, from_none], self.minimum)
        if self.title is not None:
            result["title"] = from_union([from_str, from_none], self.title)
        return result


@dataclass
class Paginatedrequest(DataModelHelper):
    id: Union[int, str]
    jsonrpc: Jsonrpc
    method: str
    params: Optional[ListpromptsrequestParams] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "Paginatedrequest":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        id = from_union([from_int, from_str], obj.get("id"))
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        method = from_str(obj.get("method"))
        params = from_union([ListpromptsrequestParams.from_dict, from_none], obj.get("params"))
        return Paginatedrequest(id, jsonrpc, method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["id"] = from_union([from_int, from_str], self.id)
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        result["method"] = from_str(self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(ListpromptsrequestParams, x), from_none], self.params
            )
        return result


@dataclass
class Paginatedresult(DataModelHelper):
    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    next_cursor: Optional[str] = None
    """An opaque token representing the pagination position after the last returned result.
    If present, there may be more results available.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "Paginatedresult":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        next_cursor = from_union([from_str, from_none], obj.get("nextCursor"))
        return Paginatedresult(meta, next_cursor)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.next_cursor is not None:
            result["nextCursor"] = from_union([from_str, from_none], self.next_cursor)
        return result


class PingrequestMethod(Enum):
    PING = "ping"


@dataclass
class PingrequestClass(DataModelHelper):
    """A ping, issued by either the server or the client, to check that the other party is still
    alive. The receiver must promptly respond, or else may be disconnected.
    """

    id: Union[int, str]
    jsonrpc: Jsonrpc
    method: PingrequestMethod
    params: Optional[ListrootsrequestParams] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "PingrequestClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        id = from_union([from_int, from_str], obj.get("id"))
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        method = PingrequestMethod(obj.get("method"))
        params = from_union([ListrootsrequestParams.from_dict, from_none], obj.get("params"))
        return PingrequestClass(id, jsonrpc, method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["id"] = from_union([from_int, from_str], self.id)
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        result["method"] = to_enum(PingrequestMethod, self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(ListrootsrequestParams, x), from_none], self.params
            )
        return result


class ProgressnotificationMethod(Enum):
    NOTIFICATIONS_PROGRESS = "notifications/progress"


@dataclass
class ProgressnotificationParams(DataModelHelper):
    """Parameters for a `notifications/progress` notification."""

    progress: float
    """The progress thus far. This should increase every time progress is made, even if the
    total is unknown.
    """
    progress_token: Union[int, str]
    """The progress token which was given in the initial request, used to associate this
    notification with the request that is proceeding.
    """
    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    message: Optional[str] = None
    """An optional message describing the current progress."""

    total: Optional[float] = None
    """Total number of items to process (or total progress required), if known."""

    @classmethod
    def from_dict(cls, obj: Any) -> "ProgressnotificationParams":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        progress = from_float(obj.get("progress"))
        progress_token = from_union([from_int, from_str], obj.get("progressToken"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        message = from_union([from_str, from_none], obj.get("message"))
        total = from_union([from_float, from_none], obj.get("total"))
        return ProgressnotificationParams(progress, progress_token, meta, message, total)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["progress"] = to_float(self.progress)
        result["progressToken"] = from_union([from_int, from_str], self.progress_token)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.message is not None:
            result["message"] = from_union([from_str, from_none], self.message)
        if self.total is not None:
            result["total"] = from_union([to_float, from_none], self.total)
        return result


@dataclass
class ProgressnotificationClass(DataModelHelper):
    """An out-of-band notification used to inform the receiver of a progress update for a
    long-running request.
    """

    jsonrpc: Jsonrpc
    method: ProgressnotificationMethod
    params: ProgressnotificationParams

    @classmethod
    def from_dict(cls, obj: Any) -> "ProgressnotificationClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        method = ProgressnotificationMethod(obj.get("method"))
        params = ProgressnotificationParams.from_dict(obj.get("params"))
        return ProgressnotificationClass(jsonrpc, method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        result["method"] = to_enum(ProgressnotificationMethod, self.method)
        result["params"] = to_class(ProgressnotificationParams, self.params)
        return result


class PromptlistchangednotificationMethod(Enum):
    NOTIFICATIONS_PROMPTS_LIST_CHANGED = "notifications/prompts/list_changed"


@dataclass
class Promptlistchangednotification(DataModelHelper):
    """An optional notification from the server to the client, informing it that the list of
    prompts it offers has changed. This may be issued by servers without any previous
    subscription from the client.
    """

    jsonrpc: Jsonrpc
    method: PromptlistchangednotificationMethod
    params: Optional[InitializednotificationParams] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "Promptlistchangednotification":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        method = PromptlistchangednotificationMethod(obj.get("method"))
        params = from_union([InitializednotificationParams.from_dict, from_none], obj.get("params"))
        return Promptlistchangednotification(jsonrpc, method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        result["method"] = to_enum(PromptlistchangednotificationMethod, self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(InitializednotificationParams, x), from_none], self.params
            )
        return result


class PromptreferenceType(Enum):
    REF_PROMPT = "ref/prompt"


@dataclass
class PromptreferenceClass(DataModelHelper):
    """Identifies a prompt."""

    name: str
    """Intended for programmatic or logical use, but used as a display name in past specs or
    fallback (if title isn't present).
    """
    type: PromptreferenceType
    title: Optional[str] = None
    """Intended for UI and end-user contexts — optimized to be human-readable and easily
    understood,
    even by those unfamiliar with domain-specific terminology.
    
    If not provided, the name should be used for display (except for Tool,
    where `annotations.title` should be given precedence over using `name`,
    if present).
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "PromptreferenceClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        name = from_str(obj.get("name"))
        type = PromptreferenceType(obj.get("type"))
        title = from_union([from_str, from_none], obj.get("title"))
        return PromptreferenceClass(name, type, title)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["name"] = from_str(self.name)
        result["type"] = to_enum(PromptreferenceType, self.type)
        if self.title is not None:
            result["title"] = from_union([from_str, from_none], self.title)
        return result


class ReadresourcerequestMethod(Enum):
    RESOURCES_READ = "resources/read"


@dataclass
class MagentaMeta(DataModelHelper):
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """

    progress_token: Optional[Union[int, str]] = None
    """If specified, the caller is requesting out-of-band progress notifications for this
    request (as represented by notifications/progress). The value of this parameter is an
    opaque token that will be attached to any subsequent notifications. The receiver is not
    obligated to provide these notifications.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "MagentaMeta":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        progress_token = from_union([from_int, from_str, from_none], obj.get("progressToken"))
        return MagentaMeta(progress_token)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.progress_token is not None:
            result["progressToken"] = from_union(
                [from_int, from_str, from_none], self.progress_token
            )
        return result


@dataclass
class ReadresourcerequestParams(DataModelHelper):
    """Parameters for a `resources/read` request."""

    uri: str
    """The URI of the resource. The URI can use any protocol; it is up to the server how to
    interpret it.
    """
    meta: Optional[MagentaMeta] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ReadresourcerequestParams":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        uri = from_str(obj.get("uri"))
        meta = from_union([MagentaMeta.from_dict, from_none], obj.get("_meta"))
        return ReadresourcerequestParams(uri, meta)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["uri"] = from_str(self.uri)
        if self.meta is not None:
            result["_meta"] = from_union([lambda x: to_class(MagentaMeta, x), from_none], self.meta)
        return result


@dataclass
class ReadresourcerequestClass(DataModelHelper):
    """Sent from the client to the server, to read a specific resource URI."""

    id: Union[int, str]
    jsonrpc: Jsonrpc
    method: ReadresourcerequestMethod
    params: ReadresourcerequestParams

    @classmethod
    def from_dict(cls, obj: Any) -> "ReadresourcerequestClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        id = from_union([from_int, from_str], obj.get("id"))
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        method = ReadresourcerequestMethod(obj.get("method"))
        params = ReadresourcerequestParams.from_dict(obj.get("params"))
        return ReadresourcerequestClass(id, jsonrpc, method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["id"] = from_union([from_int, from_str], self.id)
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        result["method"] = to_enum(ReadresourcerequestMethod, self.method)
        result["params"] = to_class(ReadresourcerequestParams, self.params)
        return result


@dataclass
class Readresourceresult(DataModelHelper):
    """The server's response to a resources/read request from the client."""

    contents: List[Resource]
    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "Readresourceresult":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        contents = from_list(Resource.from_dict, obj.get("contents"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        return Readresourceresult(contents, meta)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["contents"] = from_list(lambda x: to_class(Resource, x), self.contents)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        return result


@dataclass
class Request(DataModelHelper):
    method: str
    params: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "Request":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        method = from_str(obj.get("method"))
        params = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("params"))
        return Request(method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["method"] = from_str(self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.params
            )
        return result


@dataclass
class Resourcecontents(DataModelHelper):
    """The contents of a specific resource or sub-resource."""

    uri: str
    """The URI of this resource."""

    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    mime_type: Optional[str] = None
    """The MIME type of this resource, if known."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Resourcecontents":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        uri = from_str(obj.get("uri"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        mime_type = from_union([from_str, from_none], obj.get("mimeType"))
        return Resourcecontents(uri, meta, mime_type)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["uri"] = from_str(self.uri)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.mime_type is not None:
            result["mimeType"] = from_union([from_str, from_none], self.mime_type)
        return result


class ResourcelinkType(Enum):
    RESOURCE_LINK = "resource_link"


@dataclass
class ResourcelinkClass(DataModelHelper):
    """A resource that the server is capable of reading, included in a prompt or tool call
    result.

    Note: resource links returned by tools are not guaranteed to appear in the results of
    `resources/list` requests.
    """

    name: str
    """Intended for programmatic or logical use, but used as a display name in past specs or
    fallback (if title isn't present).
    """
    type: ResourcelinkType
    uri: str
    """The URI of this resource."""

    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    annotations: Optional[AudiocontentAnnotations] = None
    """Optional annotations for the client."""

    description: Optional[str] = None
    """A description of what this resource represents.
    
    This can be used by clients to improve the LLM's understanding of available resources. It
    can be thought of like a "hint" to the model.
    """
    icons: Optional[List[IconElement]] = None
    """Optional set of sized icons that the client can display in a user interface.
    
    Clients that support rendering icons MUST support at least the following MIME types:
    - `image/png` - PNG images (safe, universal compatibility)
    - `image/jpeg` (and `image/jpg`) - JPEG images (safe, universal compatibility)
    
    Clients that support rendering icons SHOULD also support:
    - `image/svg+xml` - SVG images (scalable but requires security precautions)
    - `image/webp` - WebP images (modern, efficient format)
    """
    mime_type: Optional[str] = None
    """The MIME type of this resource, if known."""

    size: Optional[int] = None
    """The size of the raw resource content, in bytes (i.e., before base64 encoding or any
    tokenization), if known.
    
    This can be used by Hosts to display file sizes and estimate context window usage.
    """
    title: Optional[str] = None
    """Intended for UI and end-user contexts — optimized to be human-readable and easily
    understood,
    even by those unfamiliar with domain-specific terminology.
    
    If not provided, the name should be used for display (except for Tool,
    where `annotations.title` should be given precedence over using `name`,
    if present).
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ResourcelinkClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        name = from_str(obj.get("name"))
        type = ResourcelinkType(obj.get("type"))
        uri = from_str(obj.get("uri"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        annotations = from_union(
            [AudiocontentAnnotations.from_dict, from_none], obj.get("annotations")
        )
        description = from_union([from_str, from_none], obj.get("description"))
        icons = from_union(
            [lambda x: from_list(IconElement.from_dict, x), from_none], obj.get("icons")
        )
        mime_type = from_union([from_str, from_none], obj.get("mimeType"))
        size = from_union([from_int, from_none], obj.get("size"))
        title = from_union([from_str, from_none], obj.get("title"))
        return ResourcelinkClass(
            name, type, uri, meta, annotations, description, icons, mime_type, size, title
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["name"] = from_str(self.name)
        result["type"] = to_enum(ResourcelinkType, self.type)
        result["uri"] = from_str(self.uri)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.annotations is not None:
            result["annotations"] = from_union(
                [lambda x: to_class(AudiocontentAnnotations, x), from_none], self.annotations
            )
        if self.description is not None:
            result["description"] = from_union([from_str, from_none], self.description)
        if self.icons is not None:
            result["icons"] = from_union(
                [lambda x: from_list(lambda x: to_class(IconElement, x), x), from_none], self.icons
            )
        if self.mime_type is not None:
            result["mimeType"] = from_union([from_str, from_none], self.mime_type)
        if self.size is not None:
            result["size"] = from_union([from_int, from_none], self.size)
        if self.title is not None:
            result["title"] = from_union([from_str, from_none], self.title)
        return result


class ResourcelistchangednotificationMethod(Enum):
    NOTIFICATIONS_RESOURCES_LIST_CHANGED = "notifications/resources/list_changed"


@dataclass
class Resourcelistchangednotification(DataModelHelper):
    """An optional notification from the server to the client, informing it that the list of
    resources it can read from has changed. This may be issued by servers without any
    previous subscription from the client.
    """

    jsonrpc: Jsonrpc
    method: ResourcelistchangednotificationMethod
    params: Optional[InitializednotificationParams] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "Resourcelistchangednotification":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        method = ResourcelistchangednotificationMethod(obj.get("method"))
        params = from_union([InitializednotificationParams.from_dict, from_none], obj.get("params"))
        return Resourcelistchangednotification(jsonrpc, method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        result["method"] = to_enum(ResourcelistchangednotificationMethod, self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(InitializednotificationParams, x), from_none], self.params
            )
        return result


class ResourcetemplatereferenceType(Enum):
    REF_RESOURCE = "ref/resource"


@dataclass
class ResourcetemplatereferenceClass(DataModelHelper):
    """A reference to a resource or resource template definition."""

    type: ResourcetemplatereferenceType
    uri: str
    """The URI or URI template of the resource."""

    @classmethod
    def from_dict(cls, obj: Any) -> "ResourcetemplatereferenceClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        type = ResourcetemplatereferenceType(obj.get("type"))
        uri = from_str(obj.get("uri"))
        return ResourcetemplatereferenceClass(type, uri)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["type"] = to_enum(ResourcetemplatereferenceType, self.type)
        result["uri"] = from_str(self.uri)
        return result


class ResourceupdatednotificationMethod(Enum):
    NOTIFICATIONS_RESOURCES_UPDATED = "notifications/resources/updated"


@dataclass
class ResourceupdatednotificationParams(DataModelHelper):
    """Parameters for a `notifications/resources/updated` notification."""

    uri: str
    """The URI of the resource that has been updated. This might be a sub-resource of the one
    that the client actually subscribed to.
    """
    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ResourceupdatednotificationParams":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        uri = from_str(obj.get("uri"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        return ResourceupdatednotificationParams(uri, meta)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["uri"] = from_str(self.uri)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        return result


@dataclass
class Resourceupdatednotification(DataModelHelper):
    """A notification from the server to the client, informing it that a resource has changed
    and may need to be read again. This should only be sent if the client previously sent a
    resources/subscribe request.
    """

    jsonrpc: Jsonrpc
    method: ResourceupdatednotificationMethod
    params: ResourceupdatednotificationParams

    @classmethod
    def from_dict(cls, obj: Any) -> "Resourceupdatednotification":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        method = ResourceupdatednotificationMethod(obj.get("method"))
        params = ResourceupdatednotificationParams.from_dict(obj.get("params"))
        return Resourceupdatednotification(jsonrpc, method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        result["method"] = to_enum(ResourceupdatednotificationMethod, self.method)
        result["params"] = to_class(ResourceupdatednotificationParams, self.params)
        return result


class RootslistchangednotificationMethod(Enum):
    NOTIFICATIONS_ROOTS_LIST_CHANGED = "notifications/roots/list_changed"


@dataclass
class RootslistchangednotificationClass(DataModelHelper):
    """A notification from the client to the server, informing it that the list of roots has
    changed.
    This notification should be sent whenever the client adds, removes, or modifies any root.
    The server should then request an updated list of roots using the ListRootsRequest.
    """

    jsonrpc: Jsonrpc
    method: RootslistchangednotificationMethod
    params: Optional[InitializednotificationParams] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "RootslistchangednotificationClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        method = RootslistchangednotificationMethod(obj.get("method"))
        params = from_union([InitializednotificationParams.from_dict, from_none], obj.get("params"))
        return RootslistchangednotificationClass(jsonrpc, method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        result["method"] = to_enum(RootslistchangednotificationMethod, self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(InitializednotificationParams, x), from_none], self.params
            )
        return result


class ServernotificationMethod(Enum):
    NOTIFICATIONS_CANCELLED = "notifications/cancelled"
    NOTIFICATIONS_ELICITATION_COMPLETE = "notifications/elicitation/complete"
    NOTIFICATIONS_MESSAGE = "notifications/message"
    NOTIFICATIONS_PROGRESS = "notifications/progress"
    NOTIFICATIONS_PROMPTS_LIST_CHANGED = "notifications/prompts/list_changed"
    NOTIFICATIONS_RESOURCES_LIST_CHANGED = "notifications/resources/list_changed"
    NOTIFICATIONS_RESOURCES_UPDATED = "notifications/resources/updated"
    NOTIFICATIONS_TASKS_STATUS = "notifications/tasks/status"
    NOTIFICATIONS_TOOLS_LIST_CHANGED = "notifications/tools/list_changed"


@dataclass
class ServernotificationParams(DataModelHelper):
    """Parameters for a `notifications/cancelled` notification.

    Parameters for a `notifications/progress` notification.

    Parameters for a `notifications/resources/updated` notification.

    Parameters for a `notifications/tasks/status` notification.

    Data associated with a task.

    Parameters for a `notifications/message` notification.
    """

    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    reason: Optional[str] = None
    """An optional string describing the reason for the cancellation. This MAY be logged or
    presented to the user.
    """
    request_id: Optional[Union[int, str]] = None
    """The ID of the request to cancel.
    
    This MUST correspond to the ID of a request previously issued in the same direction.
    This MUST be provided for cancelling non-task requests.
    This MUST NOT be used for cancelling tasks (use the `tasks/cancel` request instead).
    """
    message: Optional[str] = None
    """An optional message describing the current progress."""

    progress: Optional[float] = None
    """The progress thus far. This should increase every time progress is made, even if the
    total is unknown.
    """
    progress_token: Optional[Union[int, str]] = None
    """The progress token which was given in the initial request, used to associate this
    notification with the request that is proceeding.
    """
    total: Optional[float] = None
    """Total number of items to process (or total progress required), if known."""

    uri: Optional[str] = None
    """The URI of the resource that has been updated. This might be a sub-resource of the one
    that the client actually subscribed to.
    """
    created_at: Optional[str] = None
    """ISO 8601 timestamp when the task was created."""

    last_updated_at: Optional[str] = None
    """ISO 8601 timestamp when the task was last updated."""

    poll_interval: Optional[int] = None
    """Suggested polling interval in milliseconds."""

    status: Optional[Status] = None
    """Current task state."""

    status_message: Optional[str] = None
    """Optional human-readable message describing the current task state.
    This can provide context for any status, including:
    - Reasons for "cancelled" status
    - Summaries for "completed" status
    - Diagnostic information for "failed" status (e.g., error details, what went wrong)
    """
    task_id: Optional[str] = None
    """The task identifier."""

    ttl: Optional[int] = None
    """Actual retention duration from creation in milliseconds, null for unlimited."""

    data: Any = None
    """The data to be logged, such as a string message or an object. Any JSON serializable type
    is allowed here.
    """
    level: Optional[Level] = None
    """The severity of this log message."""

    logger: Optional[str] = None
    """An optional name of the logger issuing this message."""

    elicitation_id: Optional[str] = None
    """The ID of the elicitation that completed."""

    @classmethod
    def from_dict(cls, obj: Any) -> "ServernotificationParams":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        reason = from_union([from_str, from_none], obj.get("reason"))
        request_id = from_union([from_int, from_str, from_none], obj.get("requestId"))
        message = from_union([from_str, from_none], obj.get("message"))
        progress = from_union([from_float, from_none], obj.get("progress"))
        progress_token = from_union([from_int, from_str, from_none], obj.get("progressToken"))
        total = from_union([from_float, from_none], obj.get("total"))
        uri = from_union([from_str, from_none], obj.get("uri"))
        created_at = from_union([from_str, from_none], obj.get("createdAt"))
        last_updated_at = from_union([from_str, from_none], obj.get("lastUpdatedAt"))
        poll_interval = from_union([from_int, from_none], obj.get("pollInterval"))
        status = from_union([Status, from_none], obj.get("status"))
        status_message = from_union([from_str, from_none], obj.get("statusMessage"))
        task_id = from_union([from_str, from_none], obj.get("taskId"))
        ttl = from_union([from_int, from_none], obj.get("ttl"))
        data = obj.get("data")
        level = from_union([Level, from_none], obj.get("level"))
        logger = from_union([from_str, from_none], obj.get("logger"))
        elicitation_id = from_union([from_str, from_none], obj.get("elicitationId"))
        return ServernotificationParams(
            meta,
            reason,
            request_id,
            message,
            progress,
            progress_token,
            total,
            uri,
            created_at,
            last_updated_at,
            poll_interval,
            status,
            status_message,
            task_id,
            ttl,
            data,
            level,
            logger,
            elicitation_id,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.reason is not None:
            result["reason"] = from_union([from_str, from_none], self.reason)
        if self.request_id is not None:
            result["requestId"] = from_union([from_int, from_str, from_none], self.request_id)
        if self.message is not None:
            result["message"] = from_union([from_str, from_none], self.message)
        if self.progress is not None:
            result["progress"] = from_union([to_float, from_none], self.progress)
        if self.progress_token is not None:
            result["progressToken"] = from_union(
                [from_int, from_str, from_none], self.progress_token
            )
        if self.total is not None:
            result["total"] = from_union([to_float, from_none], self.total)
        if self.uri is not None:
            result["uri"] = from_union([from_str, from_none], self.uri)
        if self.created_at is not None:
            result["createdAt"] = from_union([from_str, from_none], self.created_at)
        if self.last_updated_at is not None:
            result["lastUpdatedAt"] = from_union([from_str, from_none], self.last_updated_at)
        if self.poll_interval is not None:
            result["pollInterval"] = from_union([from_int, from_none], self.poll_interval)
        if self.status is not None:
            result["status"] = from_union([lambda x: to_enum(Status, x), from_none], self.status)
        if self.status_message is not None:
            result["statusMessage"] = from_union([from_str, from_none], self.status_message)
        if self.task_id is not None:
            result["taskId"] = from_union([from_str, from_none], self.task_id)
        if self.ttl is not None:
            result["ttl"] = from_union([from_int, from_none], self.ttl)
        if self.data is not None:
            result["data"] = self.data
        if self.level is not None:
            result["level"] = from_union([lambda x: to_enum(Level, x), from_none], self.level)
        if self.logger is not None:
            result["logger"] = from_union([from_str, from_none], self.logger)
        if self.elicitation_id is not None:
            result["elicitationId"] = from_union([from_str, from_none], self.elicitation_id)
        return result


@dataclass
class Servernotification(DataModelHelper):
    """This notification can be sent by either side to indicate that it is cancelling a
    previously-issued request.

    The request SHOULD still be in-flight, but due to communication latency, it is always
    possible that this notification MAY arrive after the request has already finished.

    This notification indicates that the result will be unused, so any associated processing
    SHOULD cease.

    A client MUST NOT attempt to cancel its `initialize` request.

    For task cancellation, use the `tasks/cancel` request instead of this notification.

    An out-of-band notification used to inform the receiver of a progress update for a
    long-running request.

    An optional notification from the server to the client, informing it that the list of
    resources it can read from has changed. This may be issued by servers without any
    previous subscription from the client.

    A notification from the server to the client, informing it that a resource has changed
    and may need to be read again. This should only be sent if the client previously sent a
    resources/subscribe request.

    An optional notification from the server to the client, informing it that the list of
    prompts it offers has changed. This may be issued by servers without any previous
    subscription from the client.

    An optional notification from the server to the client, informing it that the list of
    tools it offers has changed. This may be issued by servers without any previous
    subscription from the client.

    An optional notification from the receiver to the requestor, informing them that a task's
    status has changed. Receivers are not required to send these notifications.

    JSONRPCNotification of a log message passed from server to client. If no logging/setLevel
    request has been sent from the client, the server MAY decide which messages to send
    automatically.

    An optional notification from the server to the client, informing it of a completion of a
    out-of-band elicitation request.
    """

    jsonrpc: Jsonrpc
    method: ServernotificationMethod
    params: Optional[ServernotificationParams] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "Servernotification":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        method = ServernotificationMethod(obj.get("method"))
        params = from_union([ServernotificationParams.from_dict, from_none], obj.get("params"))
        return Servernotification(jsonrpc, method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        result["method"] = to_enum(ServernotificationMethod, self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(ServernotificationParams, x), from_none], self.params
            )
        return result


class ServerrequestMethod(Enum):
    ELICITATION_CREATE = "elicitation/create"
    PING = "ping"
    ROOTS_LIST = "roots/list"
    SAMPLING_CREATE_MESSAGE = "sampling/createMessage"
    TASKS_CANCEL = "tasks/cancel"
    TASKS_GET = "tasks/get"
    TASKS_LIST = "tasks/list"
    TASKS_RESULT = "tasks/result"


@dataclass
class FriskyMeta(DataModelHelper):
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """

    progress_token: Optional[Union[int, str]] = None
    """If specified, the caller is requesting out-of-band progress notifications for this
    request (as represented by notifications/progress). The value of this parameter is an
    opaque token that will be attached to any subsequent notifications. The receiver is not
    obligated to provide these notifications.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "FriskyMeta":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        progress_token = from_union([from_int, from_str, from_none], obj.get("progressToken"))
        return FriskyMeta(progress_token)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.progress_token is not None:
            result["progressToken"] = from_union(
                [from_int, from_str, from_none], self.progress_token
            )
        return result


@dataclass
class ServerrequestParams(DataModelHelper):
    """Common params for any request.

    Common parameters for paginated requests.

    Parameters for a `sampling/createMessage` request.

    The parameters for a request to elicit additional information from the user via the
    client.

    The parameters for a request to elicit information from the user via a URL in the
    client.

    The parameters for a request to elicit non-sensitive information from the user via a form
    in the client.
    """

    meta: Optional[FriskyMeta] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    task_id: Optional[str] = None
    """The task identifier to query.
    
    The task identifier to retrieve results for.
    
    The task identifier to cancel.
    """
    cursor: Optional[str] = None
    """An opaque token representing the current pagination position.
    If provided, the server should return results starting after this cursor.
    """
    include_context: Optional[IncludeContext] = None
    """A request to include context from one or more MCP servers (including the caller), to be
    attached to the prompt.
    The client MAY ignore this request.
    
    Default is "none". Values "thisServer" and "allServers" are soft-deprecated. Servers
    SHOULD only use these values if the client
    declares ClientCapabilities.sampling.context. These values may be removed in future spec
    releases.
    """
    max_tokens: Optional[int] = None
    """The requested maximum number of tokens to sample (to prevent runaway completions).
    
    The client MAY choose to sample fewer tokens than the requested maximum.
    """
    messages: Optional[List[SamplingmessageElement]] = None
    metadata: Optional[Dict[str, Any]] = None
    """Optional metadata to pass through to the LLM provider. The format of this metadata is
    provider-specific.
    """
    model_preferences: Optional[ModelpreferencesClass] = None
    """The server's preferences for which model to select. The client MAY ignore these
    preferences.
    """
    stop_sequences: Optional[List[str]] = None
    system_prompt: Optional[str] = None
    """An optional system prompt the server wants to use for sampling. The client MAY modify or
    omit this prompt.
    """
    task: Optional[Task] = None
    """If specified, the caller is requesting task-augmented execution for this request.
    The request will return a CreateTaskResult immediately, and the actual result can be
    retrieved later via tasks/result.
    
    Task augmentation is subject to capability negotiation - receivers MUST declare support
    for task augmentation of specific request types in their capabilities.
    """
    temperature: Optional[float] = None
    tool_choice: Optional[ToolChoice] = None
    """Controls how the model uses tools.
    The client MUST return an error if this field is provided but
    ClientCapabilities.sampling.tools is not declared.
    Default is `{ mode: "auto" }`.
    """
    tools: Optional[List[ToolElement]] = None
    """Tools that the model may use during generation.
    The client MUST return an error if this field is provided but
    ClientCapabilities.sampling.tools is not declared.
    """
    elicitation_id: Optional[str] = None
    """The ID of the elicitation, which must be unique within the context of the server.
    The client MUST treat this ID as an opaque value.
    """
    message: Optional[str] = None
    """The message to present to the user explaining why the interaction is needed.
    
    The message to present to the user describing what information is being requested.
    """
    mode: Optional[ParamsMode] = None
    """The elicitation mode."""

    url: Optional[str] = None
    """The URL that the user should navigate to."""

    requested_schema: Optional[RequestedSchema] = None
    """A restricted subset of JSON Schema.
    Only top-level properties are allowed, without nesting.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ServerrequestParams":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        meta = from_union([FriskyMeta.from_dict, from_none], obj.get("_meta"))
        task_id = from_union([from_str, from_none], obj.get("taskId"))
        cursor = from_union([from_str, from_none], obj.get("cursor"))
        include_context = from_union([IncludeContext, from_none], obj.get("includeContext"))
        max_tokens = from_union([from_int, from_none], obj.get("maxTokens"))
        messages = from_union(
            [lambda x: from_list(SamplingmessageElement.from_dict, x), from_none],
            obj.get("messages"),
        )
        metadata = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("metadata"))
        model_preferences = from_union(
            [ModelpreferencesClass.from_dict, from_none], obj.get("modelPreferences")
        )
        stop_sequences = from_union(
            [lambda x: from_list(from_str, x), from_none], obj.get("stopSequences")
        )
        system_prompt = from_union([from_str, from_none], obj.get("systemPrompt"))
        task = from_union([Task.from_dict, from_none], obj.get("task"))
        temperature = from_union([from_float, from_none], obj.get("temperature"))
        tool_choice = from_union([ToolChoice.from_dict, from_none], obj.get("toolChoice"))
        tools = from_union(
            [lambda x: from_list(ToolElement.from_dict, x), from_none], obj.get("tools")
        )
        elicitation_id = from_union([from_str, from_none], obj.get("elicitationId"))
        message = from_union([from_str, from_none], obj.get("message"))
        mode = from_union([ParamsMode, from_none], obj.get("mode"))
        url = from_union([from_str, from_none], obj.get("url"))
        requested_schema = from_union(
            [RequestedSchema.from_dict, from_none], obj.get("requestedSchema")
        )
        return ServerrequestParams(
            meta,
            task_id,
            cursor,
            include_context,
            max_tokens,
            messages,
            metadata,
            model_preferences,
            stop_sequences,
            system_prompt,
            task,
            temperature,
            tool_choice,
            tools,
            elicitation_id,
            message,
            mode,
            url,
            requested_schema,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.meta is not None:
            result["_meta"] = from_union([lambda x: to_class(FriskyMeta, x), from_none], self.meta)
        if self.task_id is not None:
            result["taskId"] = from_union([from_str, from_none], self.task_id)
        if self.cursor is not None:
            result["cursor"] = from_union([from_str, from_none], self.cursor)
        if self.include_context is not None:
            result["includeContext"] = from_union(
                [lambda x: to_enum(IncludeContext, x), from_none], self.include_context
            )
        if self.max_tokens is not None:
            result["maxTokens"] = from_union([from_int, from_none], self.max_tokens)
        if self.messages is not None:
            result["messages"] = from_union(
                [lambda x: from_list(lambda x: to_class(SamplingmessageElement, x), x), from_none],
                self.messages,
            )
        if self.metadata is not None:
            result["metadata"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.metadata
            )
        if self.model_preferences is not None:
            result["modelPreferences"] = from_union(
                [lambda x: to_class(ModelpreferencesClass, x), from_none], self.model_preferences
            )
        if self.stop_sequences is not None:
            result["stopSequences"] = from_union(
                [lambda x: from_list(from_str, x), from_none], self.stop_sequences
            )
        if self.system_prompt is not None:
            result["systemPrompt"] = from_union([from_str, from_none], self.system_prompt)
        if self.task is not None:
            result["task"] = from_union([lambda x: to_class(Task, x), from_none], self.task)
        if self.temperature is not None:
            result["temperature"] = from_union([to_float, from_none], self.temperature)
        if self.tool_choice is not None:
            result["toolChoice"] = from_union(
                [lambda x: to_class(ToolChoice, x), from_none], self.tool_choice
            )
        if self.tools is not None:
            result["tools"] = from_union(
                [lambda x: from_list(lambda x: to_class(ToolElement, x), x), from_none], self.tools
            )
        if self.elicitation_id is not None:
            result["elicitationId"] = from_union([from_str, from_none], self.elicitation_id)
        if self.message is not None:
            result["message"] = from_union([from_str, from_none], self.message)
        if self.mode is not None:
            result["mode"] = from_union([lambda x: to_enum(ParamsMode, x), from_none], self.mode)
        if self.url is not None:
            result["url"] = from_union([from_str, from_none], self.url)
        if self.requested_schema is not None:
            result["requestedSchema"] = from_union(
                [lambda x: to_class(RequestedSchema, x), from_none], self.requested_schema
            )
        return result


@dataclass
class Serverrequest(DataModelHelper):
    """A ping, issued by either the server or the client, to check that the other party is still
    alive. The receiver must promptly respond, or else may be disconnected.

    A request to retrieve the state of a task.

    A request to retrieve the result of a completed task.

    A request to cancel a task.

    A request to retrieve a list of tasks.

    A request from the server to sample an LLM via the client. The client has full discretion
    over which model to select. The client should also inform the user before beginning
    sampling, to allow them to inspect the request (human in the loop) and decide whether to
    approve it.

    Sent from the server to request a list of root URIs from the client. Roots allow
    servers to ask for specific directories or files to operate on. A common example
    for roots is providing a set of repositories or directories a server should operate
    on.

    This request is typically used when the server needs to understand the file system
    structure or access specific locations that the client has permission to read from.

    A request from the server to elicit additional information from the user via the client.
    """

    id: Union[int, str]
    jsonrpc: Jsonrpc
    method: ServerrequestMethod
    params: Optional[ServerrequestParams] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "Serverrequest":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        id = from_union([from_int, from_str], obj.get("id"))
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        method = ServerrequestMethod(obj.get("method"))
        params = from_union([ServerrequestParams.from_dict, from_none], obj.get("params"))
        return Serverrequest(id, jsonrpc, method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["id"] = from_union([from_int, from_str], self.id)
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        result["method"] = to_enum(ServerrequestMethod, self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(ServerrequestParams, x), from_none], self.params
            )
        return result


@dataclass
class Serverresult(DataModelHelper):
    """After receiving an initialize request from the client, the server sends this response.

    The server's response to a resources/list request from the client.

    The server's response to a resources/templates/list request from the client.

    The server's response to a resources/read request from the client.

    The server's response to a prompts/list request from the client.

    The server's response to a prompts/get request from the client.

    The server's response to a tools/list request from the client.

    The server's response to a tool call.

    The response to a tasks/get request.

    The response to a tasks/cancel request.

    Data associated with a task.

    The response to a tasks/result request.
    The structure matches the result type of the original request.
    For example, a tools/call task would return the CallToolResult structure.

    The response to a tasks/list request.

    The server's response to a completion/complete request
    """

    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    capabilities: Optional[Capabilities] = None
    instructions: Optional[str] = None
    """Instructions describing how to use the server and its features.
    
    This can be used by clients to improve the LLM's understanding of available tools,
    resources, etc. It can be thought of like a "hint" to the model. For example, this
    information MAY be added to the system prompt.
    """
    protocol_version: Optional[str] = None
    """The version of the Model Context Protocol that the server wants to use. This may not
    match the version that the client requested. If the client cannot support this version,
    it MUST disconnect.
    """
    server_info: Optional[ClientInfo] = None
    next_cursor: Optional[str] = None
    """An opaque token representing the pagination position after the last returned result.
    If present, there may be more results available.
    """
    resources: Optional[List[ResourceElement]] = None
    resource_templates: Optional[List[ResourcetemplateElement]] = None
    contents: Optional[List[Resource]] = None
    prompts: Optional[List[PromptElement]] = None
    description: Optional[str] = None
    """An optional description for the prompt."""

    messages: Optional[List[PromptmessageElement]] = None
    tools: Optional[List[ToolElement]] = None
    content: Optional[List[ContentblockElement]] = None
    """A list of content objects that represent the unstructured result of the tool call."""

    is_error: Optional[bool] = None
    """Whether the tool call ended in an error.
    
    If not set, this is assumed to be false (the call was successful).
    
    Any errors that originate from the tool SHOULD be reported inside the result
    object, with `isError` set to true, _not_ as an MCP protocol-level error
    response. Otherwise, the LLM would not be able to see that an error occurred
    and self-correct.
    
    However, any errors in _finding_ the tool, an error indicating that the
    server does not support tool calls, or any other exceptional conditions,
    should be reported as an MCP error response.
    """
    structured_content: Optional[Dict[str, Any]] = None
    """An optional JSON object that represents the structured result of the tool call."""

    created_at: Optional[str] = None
    """ISO 8601 timestamp when the task was created."""

    last_updated_at: Optional[str] = None
    """ISO 8601 timestamp when the task was last updated."""

    poll_interval: Optional[int] = None
    """Suggested polling interval in milliseconds."""

    status: Optional[Status] = None
    """Current task state."""

    status_message: Optional[str] = None
    """Optional human-readable message describing the current task state.
    This can provide context for any status, including:
    - Reasons for "cancelled" status
    - Summaries for "completed" status
    - Diagnostic information for "failed" status (e.g., error details, what went wrong)
    """
    task_id: Optional[str] = None
    """The task identifier."""

    ttl: Optional[int] = None
    """Actual retention duration from creation in milliseconds, null for unlimited."""

    tasks: Optional[List[TaskElement]] = None
    completion: Optional[Completion] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "Serverresult":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        capabilities = from_union([Capabilities.from_dict, from_none], obj.get("capabilities"))
        instructions = from_union([from_str, from_none], obj.get("instructions"))
        protocol_version = from_union([from_str, from_none], obj.get("protocolVersion"))
        server_info = from_union([ClientInfo.from_dict, from_none], obj.get("serverInfo"))
        next_cursor = from_union([from_str, from_none], obj.get("nextCursor"))
        resources = from_union(
            [lambda x: from_list(ResourceElement.from_dict, x), from_none], obj.get("resources")
        )
        resource_templates = from_union(
            [lambda x: from_list(ResourcetemplateElement.from_dict, x), from_none],
            obj.get("resourceTemplates"),
        )
        contents = from_union(
            [lambda x: from_list(Resource.from_dict, x), from_none], obj.get("contents")
        )
        prompts = from_union(
            [lambda x: from_list(PromptElement.from_dict, x), from_none], obj.get("prompts")
        )
        description = from_union([from_str, from_none], obj.get("description"))
        messages = from_union(
            [lambda x: from_list(PromptmessageElement.from_dict, x), from_none], obj.get("messages")
        )
        tools = from_union(
            [lambda x: from_list(ToolElement.from_dict, x), from_none], obj.get("tools")
        )
        content = from_union(
            [lambda x: from_list(ContentblockElement.from_dict, x), from_none], obj.get("content")
        )
        is_error = from_union([from_bool, from_none], obj.get("isError"))
        structured_content = from_union(
            [lambda x: from_dict(lambda x: x, x), from_none], obj.get("structuredContent")
        )
        created_at = from_union([from_str, from_none], obj.get("createdAt"))
        last_updated_at = from_union([from_str, from_none], obj.get("lastUpdatedAt"))
        poll_interval = from_union([from_int, from_none], obj.get("pollInterval"))
        status = from_union([Status, from_none], obj.get("status"))
        status_message = from_union([from_str, from_none], obj.get("statusMessage"))
        task_id = from_union([from_str, from_none], obj.get("taskId"))
        ttl = from_union([from_int, from_none], obj.get("ttl"))
        tasks = from_union(
            [lambda x: from_list(TaskElement.from_dict, x), from_none], obj.get("tasks")
        )
        completion = from_union([Completion.from_dict, from_none], obj.get("completion"))
        return Serverresult(
            meta,
            capabilities,
            instructions,
            protocol_version,
            server_info,
            next_cursor,
            resources,
            resource_templates,
            contents,
            prompts,
            description,
            messages,
            tools,
            content,
            is_error,
            structured_content,
            created_at,
            last_updated_at,
            poll_interval,
            status,
            status_message,
            task_id,
            ttl,
            tasks,
            completion,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.capabilities is not None:
            result["capabilities"] = from_union(
                [lambda x: to_class(Capabilities, x), from_none], self.capabilities
            )
        if self.instructions is not None:
            result["instructions"] = from_union([from_str, from_none], self.instructions)
        if self.protocol_version is not None:
            result["protocolVersion"] = from_union([from_str, from_none], self.protocol_version)
        if self.server_info is not None:
            result["serverInfo"] = from_union(
                [lambda x: to_class(ClientInfo, x), from_none], self.server_info
            )
        if self.next_cursor is not None:
            result["nextCursor"] = from_union([from_str, from_none], self.next_cursor)
        if self.resources is not None:
            result["resources"] = from_union(
                [lambda x: from_list(lambda x: to_class(ResourceElement, x), x), from_none],
                self.resources,
            )
        if self.resource_templates is not None:
            result["resourceTemplates"] = from_union(
                [lambda x: from_list(lambda x: to_class(ResourcetemplateElement, x), x), from_none],
                self.resource_templates,
            )
        if self.contents is not None:
            result["contents"] = from_union(
                [lambda x: from_list(lambda x: to_class(Resource, x), x), from_none], self.contents
            )
        if self.prompts is not None:
            result["prompts"] = from_union(
                [lambda x: from_list(lambda x: to_class(PromptElement, x), x), from_none],
                self.prompts,
            )
        if self.description is not None:
            result["description"] = from_union([from_str, from_none], self.description)
        if self.messages is not None:
            result["messages"] = from_union(
                [lambda x: from_list(lambda x: to_class(PromptmessageElement, x), x), from_none],
                self.messages,
            )
        if self.tools is not None:
            result["tools"] = from_union(
                [lambda x: from_list(lambda x: to_class(ToolElement, x), x), from_none], self.tools
            )
        if self.content is not None:
            result["content"] = from_union(
                [lambda x: from_list(lambda x: to_class(ContentblockElement, x), x), from_none],
                self.content,
            )
        if self.is_error is not None:
            result["isError"] = from_union([from_bool, from_none], self.is_error)
        if self.structured_content is not None:
            result["structuredContent"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.structured_content
            )
        if self.created_at is not None:
            result["createdAt"] = from_union([from_str, from_none], self.created_at)
        if self.last_updated_at is not None:
            result["lastUpdatedAt"] = from_union([from_str, from_none], self.last_updated_at)
        if self.poll_interval is not None:
            result["pollInterval"] = from_union([from_int, from_none], self.poll_interval)
        if self.status is not None:
            result["status"] = from_union([lambda x: to_enum(Status, x), from_none], self.status)
        if self.status_message is not None:
            result["statusMessage"] = from_union([from_str, from_none], self.status_message)
        if self.task_id is not None:
            result["taskId"] = from_union([from_str, from_none], self.task_id)
        if self.ttl is not None:
            result["ttl"] = from_union([from_int, from_none], self.ttl)
        if self.tasks is not None:
            result["tasks"] = from_union(
                [lambda x: from_list(lambda x: to_class(TaskElement, x), x), from_none], self.tasks
            )
        if self.completion is not None:
            result["completion"] = from_union(
                [lambda x: to_class(Completion, x), from_none], self.completion
            )
        return result


class SetlevelrequestMethod(Enum):
    LOGGING_SET_LEVEL = "logging/setLevel"


@dataclass
class MischievousMeta(DataModelHelper):
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """

    progress_token: Optional[Union[int, str]] = None
    """If specified, the caller is requesting out-of-band progress notifications for this
    request (as represented by notifications/progress). The value of this parameter is an
    opaque token that will be attached to any subsequent notifications. The receiver is not
    obligated to provide these notifications.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "MischievousMeta":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        progress_token = from_union([from_int, from_str, from_none], obj.get("progressToken"))
        return MischievousMeta(progress_token)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.progress_token is not None:
            result["progressToken"] = from_union(
                [from_int, from_str, from_none], self.progress_token
            )
        return result


@dataclass
class SetlevelrequestParams(DataModelHelper):
    """Parameters for a `logging/setLevel` request."""

    level: Level
    """The level of logging that the client wants to receive from the server. The server should
    send all logs at this level and higher (i.e., more severe) to the client as
    notifications/message.
    """
    meta: Optional[MischievousMeta] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "SetlevelrequestParams":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        level = Level(obj.get("level"))
        meta = from_union([MischievousMeta.from_dict, from_none], obj.get("_meta"))
        return SetlevelrequestParams(level, meta)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["level"] = to_enum(Level, self.level)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: to_class(MischievousMeta, x), from_none], self.meta
            )
        return result


@dataclass
class SetlevelrequestClass(DataModelHelper):
    """A request from the client to the server, to enable or adjust logging."""

    id: Union[int, str]
    jsonrpc: Jsonrpc
    method: SetlevelrequestMethod
    params: SetlevelrequestParams

    @classmethod
    def from_dict(cls, obj: Any) -> "SetlevelrequestClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        id = from_union([from_int, from_str], obj.get("id"))
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        method = SetlevelrequestMethod(obj.get("method"))
        params = SetlevelrequestParams.from_dict(obj.get("params"))
        return SetlevelrequestClass(id, jsonrpc, method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["id"] = from_union([from_int, from_str], self.id)
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        result["method"] = to_enum(SetlevelrequestMethod, self.method)
        result["params"] = to_class(SetlevelrequestParams, self.params)
        return result


@dataclass
class StringschemaClass(DataModelHelper):
    type: ItemsType
    default: Optional[str] = None
    description: Optional[str] = None
    format: Optional[Format] = None
    max_length: Optional[int] = None
    min_length: Optional[int] = None
    title: Optional[str] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "StringschemaClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        type = ItemsType(obj.get("type"))
        default = from_union([from_str, from_none], obj.get("default"))
        description = from_union([from_str, from_none], obj.get("description"))
        format = from_union([Format, from_none], obj.get("format"))
        max_length = from_union([from_int, from_none], obj.get("maxLength"))
        min_length = from_union([from_int, from_none], obj.get("minLength"))
        title = from_union([from_str, from_none], obj.get("title"))
        return StringschemaClass(type, default, description, format, max_length, min_length, title)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["type"] = to_enum(ItemsType, self.type)
        if self.default is not None:
            result["default"] = from_union([from_str, from_none], self.default)
        if self.description is not None:
            result["description"] = from_union([from_str, from_none], self.description)
        if self.format is not None:
            result["format"] = from_union([lambda x: to_enum(Format, x), from_none], self.format)
        if self.max_length is not None:
            result["maxLength"] = from_union([from_int, from_none], self.max_length)
        if self.min_length is not None:
            result["minLength"] = from_union([from_int, from_none], self.min_length)
        if self.title is not None:
            result["title"] = from_union([from_str, from_none], self.title)
        return result


class SubscriberequestMethod(Enum):
    RESOURCES_SUBSCRIBE = "resources/subscribe"


@dataclass
class BraggadociousMeta(DataModelHelper):
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """

    progress_token: Optional[Union[int, str]] = None
    """If specified, the caller is requesting out-of-band progress notifications for this
    request (as represented by notifications/progress). The value of this parameter is an
    opaque token that will be attached to any subsequent notifications. The receiver is not
    obligated to provide these notifications.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "BraggadociousMeta":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        progress_token = from_union([from_int, from_str, from_none], obj.get("progressToken"))
        return BraggadociousMeta(progress_token)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.progress_token is not None:
            result["progressToken"] = from_union(
                [from_int, from_str, from_none], self.progress_token
            )
        return result


@dataclass
class SubscriberequestParams(DataModelHelper):
    """Parameters for a `resources/subscribe` request."""

    uri: str
    """The URI of the resource. The URI can use any protocol; it is up to the server how to
    interpret it.
    """
    meta: Optional[BraggadociousMeta] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "SubscriberequestParams":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        uri = from_str(obj.get("uri"))
        meta = from_union([BraggadociousMeta.from_dict, from_none], obj.get("_meta"))
        return SubscriberequestParams(uri, meta)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["uri"] = from_str(self.uri)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: to_class(BraggadociousMeta, x), from_none], self.meta
            )
        return result


@dataclass
class SubscriberequestClass(DataModelHelper):
    """Sent from the client to request resources/updated notifications from the server whenever
    a particular resource changes.
    """

    id: Union[int, str]
    jsonrpc: Jsonrpc
    method: SubscriberequestMethod
    params: SubscriberequestParams

    @classmethod
    def from_dict(cls, obj: Any) -> "SubscriberequestClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        id = from_union([from_int, from_str], obj.get("id"))
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        method = SubscriberequestMethod(obj.get("method"))
        params = SubscriberequestParams.from_dict(obj.get("params"))
        return SubscriberequestClass(id, jsonrpc, method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["id"] = from_union([from_int, from_str], self.id)
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        result["method"] = to_enum(SubscriberequestMethod, self.method)
        result["params"] = to_class(SubscriberequestParams, self.params)
        return result


class TextcontentType(Enum):
    TEXT = "text"


@dataclass
class TextcontentClass(DataModelHelper):
    """Text provided to or from an LLM."""

    text: str
    """The text content of the message."""

    type: TextcontentType
    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    annotations: Optional[AudiocontentAnnotations] = None
    """Optional annotations for the client."""

    @classmethod
    def from_dict(cls, obj: Any) -> "TextcontentClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        text = from_str(obj.get("text"))
        type = TextcontentType(obj.get("type"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        annotations = from_union(
            [AudiocontentAnnotations.from_dict, from_none], obj.get("annotations")
        )
        return TextcontentClass(text, type, meta, annotations)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["text"] = from_str(self.text)
        result["type"] = to_enum(TextcontentType, self.type)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.annotations is not None:
            result["annotations"] = from_union(
                [lambda x: to_class(AudiocontentAnnotations, x), from_none], self.annotations
            )
        return result


@dataclass
class TextresourcecontentsClass(DataModelHelper):
    text: str
    """The text of the item. This must only be set if the item can actually be represented as
    text (not binary data).
    """
    uri: str
    """The URI of this resource."""

    meta: Optional[Dict[str, Any]] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """
    mime_type: Optional[str] = None
    """The MIME type of this resource, if known."""

    @classmethod
    def from_dict(cls, obj: Any) -> "TextresourcecontentsClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        text = from_str(obj.get("text"))
        uri = from_str(obj.get("uri"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        mime_type = from_union([from_str, from_none], obj.get("mimeType"))
        return TextresourcecontentsClass(text, uri, meta, mime_type)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["text"] = from_str(self.text)
        result["uri"] = from_str(self.uri)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.mime_type is not None:
            result["mimeType"] = from_union([from_str, from_none], self.mime_type)
        return result


class ToollistchangednotificationMethod(Enum):
    NOTIFICATIONS_TOOLS_LIST_CHANGED = "notifications/tools/list_changed"


@dataclass
class ToollistchangednotificationClass(DataModelHelper):
    """An optional notification from the server to the client, informing it that the list of
    tools it offers has changed. This may be issued by servers without any previous
    subscription from the client.
    """

    jsonrpc: Jsonrpc
    method: ToollistchangednotificationMethod
    params: Optional[InitializednotificationParams] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "ToollistchangednotificationClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        method = ToollistchangednotificationMethod(obj.get("method"))
        params = from_union([InitializednotificationParams.from_dict, from_none], obj.get("params"))
        return ToollistchangednotificationClass(jsonrpc, method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        result["method"] = to_enum(ToollistchangednotificationMethod, self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(InitializednotificationParams, x), from_none], self.params
            )
        return result


class UnsubscriberequestMethod(Enum):
    RESOURCES_UNSUBSCRIBE = "resources/unsubscribe"


@dataclass
class Meta1(DataModelHelper):
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """

    progress_token: Optional[Union[int, str]] = None
    """If specified, the caller is requesting out-of-band progress notifications for this
    request (as represented by notifications/progress). The value of this parameter is an
    opaque token that will be attached to any subsequent notifications. The receiver is not
    obligated to provide these notifications.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "Meta1":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        progress_token = from_union([from_int, from_str, from_none], obj.get("progressToken"))
        return Meta1(progress_token)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.progress_token is not None:
            result["progressToken"] = from_union(
                [from_int, from_str, from_none], self.progress_token
            )
        return result


@dataclass
class UnsubscriberequestParams(DataModelHelper):
    """Parameters for a `resources/unsubscribe` request."""

    uri: str
    """The URI of the resource. The URI can use any protocol; it is up to the server how to
    interpret it.
    """
    meta: Optional[Meta1] = None
    """See [General fields: `_meta`](/specification/2025-11-25/basic/index#meta) for notes on
    `_meta` usage.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "UnsubscriberequestParams":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        uri = from_str(obj.get("uri"))
        meta = from_union([Meta1.from_dict, from_none], obj.get("_meta"))
        return UnsubscriberequestParams(uri, meta)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["uri"] = from_str(self.uri)
        if self.meta is not None:
            result["_meta"] = from_union([lambda x: to_class(Meta1, x), from_none], self.meta)
        return result


@dataclass
class UnsubscriberequestClass(DataModelHelper):
    """Sent from the client to request cancellation of resources/updated notifications from the
    server. This should follow a previous resources/subscribe request.
    """

    id: Union[int, str]
    jsonrpc: Jsonrpc
    method: UnsubscriberequestMethod
    params: UnsubscriberequestParams

    @classmethod
    def from_dict(cls, obj: Any) -> "UnsubscriberequestClass":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        id = from_union([from_int, from_str], obj.get("id"))
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        method = UnsubscriberequestMethod(obj.get("method"))
        params = UnsubscriberequestParams.from_dict(obj.get("params"))
        return UnsubscriberequestClass(id, jsonrpc, method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["id"] = from_union([from_int, from_str], self.id)
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        result["method"] = to_enum(UnsubscriberequestMethod, self.method)
        result["params"] = to_class(UnsubscriberequestParams, self.params)
        return result


@dataclass
class ModelContextProtocolTypesSchema(DataModelHelper):
    annotations: AudiocontentAnnotations
    audiocontent: Optional[Audiocontent] = None
    basemetadata: Optional[Basemetadata] = None
    blobresourcecontents: Optional[Blobresourcecontents] = None
    booleanschema: Optional[BooleanschemaClass] = None
    calltoolrequest: Optional[Calltoolrequest] = None
    calltoolresult: Optional[Calltoolresult] = None
    cancellednotification: Optional[Cancellednotification] = None
    clientcapabilities: Optional[Clientcapabilities] = None
    clientnotification: Optional[Clientnotification] = None
    clientrequest: Optional[Clientrequest] = None
    clientresult: Optional[Clientresult] = None
    completerequest: Optional[CompleterequestClass] = None
    completeresult: Optional[Completeresult] = None
    contentblock: Optional[ContentblockElement] = None
    createmessagerequest: Optional[Createmessagerequest] = None
    createmessageresult: Optional[CreatemessageresultClass] = None
    cursor: Optional[str] = None
    elicitrequest: Optional[Elicitrequest] = None
    elicitresult: Optional[ElicitresultClass] = None
    embeddedresource: Optional[EmbeddedresourceClass] = None
    emptyresult: Optional[EmptyresultClass] = None
    enumschema: Optional[EnumschemaClass] = None
    getpromptrequest: Optional[GetpromptrequestClass] = None
    getpromptresult: Optional[Getpromptresult] = None
    imagecontent: Optional[ImagecontentClass] = None
    implementation: Optional[ClientInfo] = None
    initializednotification: Optional[InitializednotificationClass] = None
    initializerequest: Optional[InitializerequestClass] = None
    initializeresult: Optional[Initializeresult] = None
    jsonrpcerror: Optional[Jsonrpcerror] = None
    jsonrpcmessage: Optional[Jsonrpcmessage] = None
    jsonrpcnotification: Optional[JsonrpcnotificationClass] = None
    jsonrpcrequest: Optional[JsonrpcrequestClass] = None
    jsonrpcresponse: Optional[Jsonrpcresponse] = None
    listpromptsrequest: Optional[ListpromptsrequestClass] = None
    listpromptsresult: Optional[Listpromptsresult] = None
    listresourcesrequest: Optional[ListresourcesrequestClass] = None
    listresourcesresult: Optional[Listresourcesresult] = None
    listresourcetemplatesrequest: Optional[ListresourcetemplatesrequestClass] = None
    listresourcetemplatesresult: Optional[Listresourcetemplatesresult] = None
    listrootsrequest: Optional[Listrootsrequest] = None
    listrootsresult: Optional[ListrootsresultClass] = None
    listtoolsrequest: Optional[ListtoolsrequestClass] = None
    listtoolsresult: Optional[Listtoolsresult] = None
    logginglevel: Optional[Level] = None
    loggingmessagenotification: Optional[Loggingmessagenotification] = None
    modelhint: Optional[ModelhintElement] = None
    modelpreferences: Optional[ModelpreferencesClass] = None
    notification: Optional[Notification] = None
    numberschema: Optional[NumberschemaClass] = None
    paginatedrequest: Optional[Paginatedrequest] = None
    paginatedresult: Optional[Paginatedresult] = None
    pingrequest: Optional[PingrequestClass] = None
    primitiveschemadefinition: Optional[PrimitiveschemadefinitionValue] = None
    progressnotification: Optional[ProgressnotificationClass] = None
    progresstoken: Optional[Union[int, str]] = None
    prompt: Optional[PromptElement] = None
    promptargument: Optional[PromptargumentElement] = None
    promptlistchangednotification: Optional[Promptlistchangednotification] = None
    promptmessage: Optional[PromptmessageElement] = None
    promptreference: Optional[PromptreferenceClass] = None
    readresourcerequest: Optional[ReadresourcerequestClass] = None
    readresourceresult: Optional[Readresourceresult] = None
    request: Optional[Request] = None
    requestid: Optional[Union[int, str]] = None
    resource: Optional[ResourceElement] = None
    resourcecontents: Optional[Resourcecontents] = None
    resourcelink: Optional[ResourcelinkClass] = None
    resourcelistchangednotification: Optional[Resourcelistchangednotification] = None
    resourcetemplate: Optional[ResourcetemplateElement] = None
    resourcetemplatereference: Optional[ResourcetemplatereferenceClass] = None
    resourceupdatednotification: Optional[Resourceupdatednotification] = None
    result: Optional[EmptyresultClass] = None
    role: Optional[RoleElement] = None
    root: Optional[RootElement] = None
    rootslistchangednotification: Optional[RootslistchangednotificationClass] = None
    samplingmessage: Optional[SamplingmessageElement] = None
    servercapabilities: Optional[Capabilities] = None
    servernotification: Optional[Servernotification] = None
    serverrequest: Optional[Serverrequest] = None
    serverresult: Optional[Serverresult] = None
    setlevelrequest: Optional[SetlevelrequestClass] = None
    stringschema: Optional[StringschemaClass] = None
    subscriberequest: Optional[SubscriberequestClass] = None
    textcontent: Optional[TextcontentClass] = None
    textresourcecontents: Optional[TextresourcecontentsClass] = None
    tool: Optional[ToolElement] = None
    toolannotations: Optional[ToolannotationsClass] = None
    toollistchangednotification: Optional[ToollistchangednotificationClass] = None
    unsubscriberequest: Optional[UnsubscriberequestClass] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "ModelContextProtocolTypesSchema":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        annotations = AudiocontentAnnotations.from_dict(obj.get("annotations"))
        audiocontent = from_union([Audiocontent.from_dict, from_none], obj.get("audiocontent"))
        basemetadata = from_union([Basemetadata.from_dict, from_none], obj.get("basemetadata"))
        blobresourcecontents = from_union(
            [Blobresourcecontents.from_dict, from_none], obj.get("blobresourcecontents")
        )
        booleanschema = from_union(
            [BooleanschemaClass.from_dict, from_none], obj.get("booleanschema")
        )
        calltoolrequest = from_union(
            [Calltoolrequest.from_dict, from_none], obj.get("calltoolrequest")
        )
        calltoolresult = from_union(
            [Calltoolresult.from_dict, from_none], obj.get("calltoolresult")
        )
        cancellednotification = from_union(
            [Cancellednotification.from_dict, from_none], obj.get("cancellednotification")
        )
        clientcapabilities = from_union(
            [Clientcapabilities.from_dict, from_none], obj.get("clientcapabilities")
        )
        clientnotification = from_union(
            [Clientnotification.from_dict, from_none], obj.get("clientnotification")
        )
        clientrequest = from_union([Clientrequest.from_dict, from_none], obj.get("clientrequest"))
        clientresult = from_union([Clientresult.from_dict, from_none], obj.get("clientresult"))
        completerequest = from_union(
            [CompleterequestClass.from_dict, from_none], obj.get("completerequest")
        )
        completeresult = from_union(
            [Completeresult.from_dict, from_none], obj.get("completeresult")
        )
        contentblock = from_union(
            [ContentblockElement.from_dict, from_none], obj.get("contentblock")
        )
        createmessagerequest = from_union(
            [Createmessagerequest.from_dict, from_none], obj.get("createmessagerequest")
        )
        createmessageresult = from_union(
            [CreatemessageresultClass.from_dict, from_none], obj.get("createmessageresult")
        )
        cursor = from_union([from_str, from_none], obj.get("cursor"))
        elicitrequest = from_union([Elicitrequest.from_dict, from_none], obj.get("elicitrequest"))
        elicitresult = from_union([ElicitresultClass.from_dict, from_none], obj.get("elicitresult"))
        embeddedresource = from_union(
            [EmbeddedresourceClass.from_dict, from_none], obj.get("embeddedresource")
        )
        emptyresult = from_union([EmptyresultClass.from_dict, from_none], obj.get("emptyresult"))
        enumschema = from_union([EnumschemaClass.from_dict, from_none], obj.get("enumschema"))
        getpromptrequest = from_union(
            [GetpromptrequestClass.from_dict, from_none], obj.get("getpromptrequest")
        )
        getpromptresult = from_union(
            [Getpromptresult.from_dict, from_none], obj.get("getpromptresult")
        )
        imagecontent = from_union([ImagecontentClass.from_dict, from_none], obj.get("imagecontent"))
        implementation = from_union([ClientInfo.from_dict, from_none], obj.get("implementation"))
        initializednotification = from_union(
            [InitializednotificationClass.from_dict, from_none], obj.get("initializednotification")
        )
        initializerequest = from_union(
            [InitializerequestClass.from_dict, from_none], obj.get("initializerequest")
        )
        initializeresult = from_union(
            [Initializeresult.from_dict, from_none], obj.get("initializeresult")
        )
        jsonrpcerror = from_union([Jsonrpcerror.from_dict, from_none], obj.get("jsonrpcerror"))
        jsonrpcmessage = from_union(
            [Jsonrpcmessage.from_dict, from_none], obj.get("jsonrpcmessage")
        )
        jsonrpcnotification = from_union(
            [JsonrpcnotificationClass.from_dict, from_none], obj.get("jsonrpcnotification")
        )
        jsonrpcrequest = from_union(
            [JsonrpcrequestClass.from_dict, from_none], obj.get("jsonrpcrequest")
        )
        jsonrpcresponse = from_union(
            [Jsonrpcresponse.from_dict, from_none], obj.get("jsonrpcresponse")
        )
        listpromptsrequest = from_union(
            [ListpromptsrequestClass.from_dict, from_none], obj.get("listpromptsrequest")
        )
        listpromptsresult = from_union(
            [Listpromptsresult.from_dict, from_none], obj.get("listpromptsresult")
        )
        listresourcesrequest = from_union(
            [ListresourcesrequestClass.from_dict, from_none], obj.get("listresourcesrequest")
        )
        listresourcesresult = from_union(
            [Listresourcesresult.from_dict, from_none], obj.get("listresourcesresult")
        )
        listresourcetemplatesrequest = from_union(
            [ListresourcetemplatesrequestClass.from_dict, from_none],
            obj.get("listresourcetemplatesrequest"),
        )
        listresourcetemplatesresult = from_union(
            [Listresourcetemplatesresult.from_dict, from_none],
            obj.get("listresourcetemplatesresult"),
        )
        listrootsrequest = from_union(
            [Listrootsrequest.from_dict, from_none], obj.get("listrootsrequest")
        )
        listrootsresult = from_union(
            [ListrootsresultClass.from_dict, from_none], obj.get("listrootsresult")
        )
        listtoolsrequest = from_union(
            [ListtoolsrequestClass.from_dict, from_none], obj.get("listtoolsrequest")
        )
        listtoolsresult = from_union(
            [Listtoolsresult.from_dict, from_none], obj.get("listtoolsresult")
        )
        logginglevel = from_union([Level, from_none], obj.get("logginglevel"))
        loggingmessagenotification = from_union(
            [Loggingmessagenotification.from_dict, from_none], obj.get("loggingmessagenotification")
        )
        modelhint = from_union([ModelhintElement.from_dict, from_none], obj.get("modelhint"))
        modelpreferences = from_union(
            [ModelpreferencesClass.from_dict, from_none], obj.get("modelpreferences")
        )
        notification = from_union([Notification.from_dict, from_none], obj.get("notification"))
        numberschema = from_union([NumberschemaClass.from_dict, from_none], obj.get("numberschema"))
        paginatedrequest = from_union(
            [Paginatedrequest.from_dict, from_none], obj.get("paginatedrequest")
        )
        paginatedresult = from_union(
            [Paginatedresult.from_dict, from_none], obj.get("paginatedresult")
        )
        pingrequest = from_union([PingrequestClass.from_dict, from_none], obj.get("pingrequest"))
        primitiveschemadefinition = from_union(
            [PrimitiveschemadefinitionValue.from_dict, from_none],
            obj.get("primitiveschemadefinition"),
        )
        progressnotification = from_union(
            [ProgressnotificationClass.from_dict, from_none], obj.get("progressnotification")
        )
        progresstoken = from_union([from_int, from_str, from_none], obj.get("progresstoken"))
        prompt = from_union([PromptElement.from_dict, from_none], obj.get("prompt"))
        promptargument = from_union(
            [PromptargumentElement.from_dict, from_none], obj.get("promptargument")
        )
        promptlistchangednotification = from_union(
            [Promptlistchangednotification.from_dict, from_none],
            obj.get("promptlistchangednotification"),
        )
        promptmessage = from_union(
            [PromptmessageElement.from_dict, from_none], obj.get("promptmessage")
        )
        promptreference = from_union(
            [PromptreferenceClass.from_dict, from_none], obj.get("promptreference")
        )
        readresourcerequest = from_union(
            [ReadresourcerequestClass.from_dict, from_none], obj.get("readresourcerequest")
        )
        readresourceresult = from_union(
            [Readresourceresult.from_dict, from_none], obj.get("readresourceresult")
        )
        request = from_union([Request.from_dict, from_none], obj.get("request"))
        requestid = from_union([from_int, from_str, from_none], obj.get("requestid"))
        resource = from_union([ResourceElement.from_dict, from_none], obj.get("resource"))
        resourcecontents = from_union(
            [Resourcecontents.from_dict, from_none], obj.get("resourcecontents")
        )
        resourcelink = from_union([ResourcelinkClass.from_dict, from_none], obj.get("resourcelink"))
        resourcelistchangednotification = from_union(
            [Resourcelistchangednotification.from_dict, from_none],
            obj.get("resourcelistchangednotification"),
        )
        resourcetemplate = from_union(
            [ResourcetemplateElement.from_dict, from_none], obj.get("resourcetemplate")
        )
        resourcetemplatereference = from_union(
            [ResourcetemplatereferenceClass.from_dict, from_none],
            obj.get("resourcetemplatereference"),
        )
        resourceupdatednotification = from_union(
            [Resourceupdatednotification.from_dict, from_none],
            obj.get("resourceupdatednotification"),
        )
        result = from_union([EmptyresultClass.from_dict, from_none], obj.get("result"))
        role = from_union([RoleElement, from_none], obj.get("role"))
        root = from_union([RootElement.from_dict, from_none], obj.get("root"))
        rootslistchangednotification = from_union(
            [RootslistchangednotificationClass.from_dict, from_none],
            obj.get("rootslistchangednotification"),
        )
        samplingmessage = from_union(
            [SamplingmessageElement.from_dict, from_none], obj.get("samplingmessage")
        )
        servercapabilities = from_union(
            [Capabilities.from_dict, from_none], obj.get("servercapabilities")
        )
        servernotification = from_union(
            [Servernotification.from_dict, from_none], obj.get("servernotification")
        )
        serverrequest = from_union([Serverrequest.from_dict, from_none], obj.get("serverrequest"))
        serverresult = from_union([Serverresult.from_dict, from_none], obj.get("serverresult"))
        setlevelrequest = from_union(
            [SetlevelrequestClass.from_dict, from_none], obj.get("setlevelrequest")
        )
        stringschema = from_union([StringschemaClass.from_dict, from_none], obj.get("stringschema"))
        subscriberequest = from_union(
            [SubscriberequestClass.from_dict, from_none], obj.get("subscriberequest")
        )
        textcontent = from_union([TextcontentClass.from_dict, from_none], obj.get("textcontent"))
        textresourcecontents = from_union(
            [TextresourcecontentsClass.from_dict, from_none], obj.get("textresourcecontents")
        )
        tool = from_union([ToolElement.from_dict, from_none], obj.get("tool"))
        toolannotations = from_union(
            [ToolannotationsClass.from_dict, from_none], obj.get("toolannotations")
        )
        toollistchangednotification = from_union(
            [ToollistchangednotificationClass.from_dict, from_none],
            obj.get("toollistchangednotification"),
        )
        unsubscriberequest = from_union(
            [UnsubscriberequestClass.from_dict, from_none], obj.get("unsubscriberequest")
        )
        return ModelContextProtocolTypesSchema(
            annotations,
            audiocontent,
            basemetadata,
            blobresourcecontents,
            booleanschema,
            calltoolrequest,
            calltoolresult,
            cancellednotification,
            clientcapabilities,
            clientnotification,
            clientrequest,
            clientresult,
            completerequest,
            completeresult,
            contentblock,
            createmessagerequest,
            createmessageresult,
            cursor,
            elicitrequest,
            elicitresult,
            embeddedresource,
            emptyresult,
            enumschema,
            getpromptrequest,
            getpromptresult,
            imagecontent,
            implementation,
            initializednotification,
            initializerequest,
            initializeresult,
            jsonrpcerror,
            jsonrpcmessage,
            jsonrpcnotification,
            jsonrpcrequest,
            jsonrpcresponse,
            listpromptsrequest,
            listpromptsresult,
            listresourcesrequest,
            listresourcesresult,
            listresourcetemplatesrequest,
            listresourcetemplatesresult,
            listrootsrequest,
            listrootsresult,
            listtoolsrequest,
            listtoolsresult,
            logginglevel,
            loggingmessagenotification,
            modelhint,
            modelpreferences,
            notification,
            numberschema,
            paginatedrequest,
            paginatedresult,
            pingrequest,
            primitiveschemadefinition,
            progressnotification,
            progresstoken,
            prompt,
            promptargument,
            promptlistchangednotification,
            promptmessage,
            promptreference,
            readresourcerequest,
            readresourceresult,
            request,
            requestid,
            resource,
            resourcecontents,
            resourcelink,
            resourcelistchangednotification,
            resourcetemplate,
            resourcetemplatereference,
            resourceupdatednotification,
            result,
            role,
            root,
            rootslistchangednotification,
            samplingmessage,
            servercapabilities,
            servernotification,
            serverrequest,
            serverresult,
            setlevelrequest,
            stringschema,
            subscriberequest,
            textcontent,
            textresourcecontents,
            tool,
            toolannotations,
            toollistchangednotification,
            unsubscriberequest,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["annotations"] = to_class(AudiocontentAnnotations, self.annotations)
        if self.audiocontent is not None:
            result["audiocontent"] = from_union(
                [lambda x: to_class(Audiocontent, x), from_none], self.audiocontent
            )
        if self.basemetadata is not None:
            result["basemetadata"] = from_union(
                [lambda x: to_class(Basemetadata, x), from_none], self.basemetadata
            )
        if self.blobresourcecontents is not None:
            result["blobresourcecontents"] = from_union(
                [lambda x: to_class(Blobresourcecontents, x), from_none], self.blobresourcecontents
            )
        if self.booleanschema is not None:
            result["booleanschema"] = from_union(
                [lambda x: to_class(BooleanschemaClass, x), from_none], self.booleanschema
            )
        if self.calltoolrequest is not None:
            result["calltoolrequest"] = from_union(
                [lambda x: to_class(Calltoolrequest, x), from_none], self.calltoolrequest
            )
        if self.calltoolresult is not None:
            result["calltoolresult"] = from_union(
                [lambda x: to_class(Calltoolresult, x), from_none], self.calltoolresult
            )
        if self.cancellednotification is not None:
            result["cancellednotification"] = from_union(
                [lambda x: to_class(Cancellednotification, x), from_none],
                self.cancellednotification,
            )
        if self.clientcapabilities is not None:
            result["clientcapabilities"] = from_union(
                [lambda x: to_class(Clientcapabilities, x), from_none], self.clientcapabilities
            )
        if self.clientnotification is not None:
            result["clientnotification"] = from_union(
                [lambda x: to_class(Clientnotification, x), from_none], self.clientnotification
            )
        if self.clientrequest is not None:
            result["clientrequest"] = from_union(
                [lambda x: to_class(Clientrequest, x), from_none], self.clientrequest
            )
        if self.clientresult is not None:
            result["clientresult"] = from_union(
                [lambda x: to_class(Clientresult, x), from_none], self.clientresult
            )
        if self.completerequest is not None:
            result["completerequest"] = from_union(
                [lambda x: to_class(CompleterequestClass, x), from_none], self.completerequest
            )
        if self.completeresult is not None:
            result["completeresult"] = from_union(
                [lambda x: to_class(Completeresult, x), from_none], self.completeresult
            )
        if self.contentblock is not None:
            result["contentblock"] = from_union(
                [lambda x: to_class(ContentblockElement, x), from_none], self.contentblock
            )
        if self.createmessagerequest is not None:
            result["createmessagerequest"] = from_union(
                [lambda x: to_class(Createmessagerequest, x), from_none], self.createmessagerequest
            )
        if self.createmessageresult is not None:
            result["createmessageresult"] = from_union(
                [lambda x: to_class(CreatemessageresultClass, x), from_none],
                self.createmessageresult,
            )
        if self.cursor is not None:
            result["cursor"] = from_union([from_str, from_none], self.cursor)
        if self.elicitrequest is not None:
            result["elicitrequest"] = from_union(
                [lambda x: to_class(Elicitrequest, x), from_none], self.elicitrequest
            )
        if self.elicitresult is not None:
            result["elicitresult"] = from_union(
                [lambda x: to_class(ElicitresultClass, x), from_none], self.elicitresult
            )
        if self.embeddedresource is not None:
            result["embeddedresource"] = from_union(
                [lambda x: to_class(EmbeddedresourceClass, x), from_none], self.embeddedresource
            )
        if self.emptyresult is not None:
            result["emptyresult"] = from_union(
                [lambda x: to_class(EmptyresultClass, x), from_none], self.emptyresult
            )
        if self.enumschema is not None:
            result["enumschema"] = from_union(
                [lambda x: to_class(EnumschemaClass, x), from_none], self.enumschema
            )
        if self.getpromptrequest is not None:
            result["getpromptrequest"] = from_union(
                [lambda x: to_class(GetpromptrequestClass, x), from_none], self.getpromptrequest
            )
        if self.getpromptresult is not None:
            result["getpromptresult"] = from_union(
                [lambda x: to_class(Getpromptresult, x), from_none], self.getpromptresult
            )
        if self.imagecontent is not None:
            result["imagecontent"] = from_union(
                [lambda x: to_class(ImagecontentClass, x), from_none], self.imagecontent
            )
        if self.implementation is not None:
            result["implementation"] = from_union(
                [lambda x: to_class(ClientInfo, x), from_none], self.implementation
            )
        if self.initializednotification is not None:
            result["initializednotification"] = from_union(
                [lambda x: to_class(InitializednotificationClass, x), from_none],
                self.initializednotification,
            )
        if self.initializerequest is not None:
            result["initializerequest"] = from_union(
                [lambda x: to_class(InitializerequestClass, x), from_none], self.initializerequest
            )
        if self.initializeresult is not None:
            result["initializeresult"] = from_union(
                [lambda x: to_class(Initializeresult, x), from_none], self.initializeresult
            )
        if self.jsonrpcerror is not None:
            result["jsonrpcerror"] = from_union(
                [lambda x: to_class(Jsonrpcerror, x), from_none], self.jsonrpcerror
            )
        if self.jsonrpcmessage is not None:
            result["jsonrpcmessage"] = from_union(
                [lambda x: to_class(Jsonrpcmessage, x), from_none], self.jsonrpcmessage
            )
        if self.jsonrpcnotification is not None:
            result["jsonrpcnotification"] = from_union(
                [lambda x: to_class(JsonrpcnotificationClass, x), from_none],
                self.jsonrpcnotification,
            )
        if self.jsonrpcrequest is not None:
            result["jsonrpcrequest"] = from_union(
                [lambda x: to_class(JsonrpcrequestClass, x), from_none], self.jsonrpcrequest
            )
        if self.jsonrpcresponse is not None:
            result["jsonrpcresponse"] = from_union(
                [lambda x: to_class(Jsonrpcresponse, x), from_none], self.jsonrpcresponse
            )
        if self.listpromptsrequest is not None:
            result["listpromptsrequest"] = from_union(
                [lambda x: to_class(ListpromptsrequestClass, x), from_none], self.listpromptsrequest
            )
        if self.listpromptsresult is not None:
            result["listpromptsresult"] = from_union(
                [lambda x: to_class(Listpromptsresult, x), from_none], self.listpromptsresult
            )
        if self.listresourcesrequest is not None:
            result["listresourcesrequest"] = from_union(
                [lambda x: to_class(ListresourcesrequestClass, x), from_none],
                self.listresourcesrequest,
            )
        if self.listresourcesresult is not None:
            result["listresourcesresult"] = from_union(
                [lambda x: to_class(Listresourcesresult, x), from_none], self.listresourcesresult
            )
        if self.listresourcetemplatesrequest is not None:
            result["listresourcetemplatesrequest"] = from_union(
                [lambda x: to_class(ListresourcetemplatesrequestClass, x), from_none],
                self.listresourcetemplatesrequest,
            )
        if self.listresourcetemplatesresult is not None:
            result["listresourcetemplatesresult"] = from_union(
                [lambda x: to_class(Listresourcetemplatesresult, x), from_none],
                self.listresourcetemplatesresult,
            )
        if self.listrootsrequest is not None:
            result["listrootsrequest"] = from_union(
                [lambda x: to_class(Listrootsrequest, x), from_none], self.listrootsrequest
            )
        if self.listrootsresult is not None:
            result["listrootsresult"] = from_union(
                [lambda x: to_class(ListrootsresultClass, x), from_none], self.listrootsresult
            )
        if self.listtoolsrequest is not None:
            result["listtoolsrequest"] = from_union(
                [lambda x: to_class(ListtoolsrequestClass, x), from_none], self.listtoolsrequest
            )
        if self.listtoolsresult is not None:
            result["listtoolsresult"] = from_union(
                [lambda x: to_class(Listtoolsresult, x), from_none], self.listtoolsresult
            )
        if self.logginglevel is not None:
            result["logginglevel"] = from_union(
                [lambda x: to_enum(Level, x), from_none], self.logginglevel
            )
        if self.loggingmessagenotification is not None:
            result["loggingmessagenotification"] = from_union(
                [lambda x: to_class(Loggingmessagenotification, x), from_none],
                self.loggingmessagenotification,
            )
        if self.modelhint is not None:
            result["modelhint"] = from_union(
                [lambda x: to_class(ModelhintElement, x), from_none], self.modelhint
            )
        if self.modelpreferences is not None:
            result["modelpreferences"] = from_union(
                [lambda x: to_class(ModelpreferencesClass, x), from_none], self.modelpreferences
            )
        if self.notification is not None:
            result["notification"] = from_union(
                [lambda x: to_class(Notification, x), from_none], self.notification
            )
        if self.numberschema is not None:
            result["numberschema"] = from_union(
                [lambda x: to_class(NumberschemaClass, x), from_none], self.numberschema
            )
        if self.paginatedrequest is not None:
            result["paginatedrequest"] = from_union(
                [lambda x: to_class(Paginatedrequest, x), from_none], self.paginatedrequest
            )
        if self.paginatedresult is not None:
            result["paginatedresult"] = from_union(
                [lambda x: to_class(Paginatedresult, x), from_none], self.paginatedresult
            )
        if self.pingrequest is not None:
            result["pingrequest"] = from_union(
                [lambda x: to_class(PingrequestClass, x), from_none], self.pingrequest
            )
        if self.primitiveschemadefinition is not None:
            result["primitiveschemadefinition"] = from_union(
                [lambda x: to_class(PrimitiveschemadefinitionValue, x), from_none],
                self.primitiveschemadefinition,
            )
        if self.progressnotification is not None:
            result["progressnotification"] = from_union(
                [lambda x: to_class(ProgressnotificationClass, x), from_none],
                self.progressnotification,
            )
        if self.progresstoken is not None:
            result["progresstoken"] = from_union(
                [from_int, from_str, from_none], self.progresstoken
            )
        if self.prompt is not None:
            result["prompt"] = from_union(
                [lambda x: to_class(PromptElement, x), from_none], self.prompt
            )
        if self.promptargument is not None:
            result["promptargument"] = from_union(
                [lambda x: to_class(PromptargumentElement, x), from_none], self.promptargument
            )
        if self.promptlistchangednotification is not None:
            result["promptlistchangednotification"] = from_union(
                [lambda x: to_class(Promptlistchangednotification, x), from_none],
                self.promptlistchangednotification,
            )
        if self.promptmessage is not None:
            result["promptmessage"] = from_union(
                [lambda x: to_class(PromptmessageElement, x), from_none], self.promptmessage
            )
        if self.promptreference is not None:
            result["promptreference"] = from_union(
                [lambda x: to_class(PromptreferenceClass, x), from_none], self.promptreference
            )
        if self.readresourcerequest is not None:
            result["readresourcerequest"] = from_union(
                [lambda x: to_class(ReadresourcerequestClass, x), from_none],
                self.readresourcerequest,
            )
        if self.readresourceresult is not None:
            result["readresourceresult"] = from_union(
                [lambda x: to_class(Readresourceresult, x), from_none], self.readresourceresult
            )
        if self.request is not None:
            result["request"] = from_union(
                [lambda x: to_class(Request, x), from_none], self.request
            )
        if self.requestid is not None:
            result["requestid"] = from_union([from_int, from_str, from_none], self.requestid)
        if self.resource is not None:
            result["resource"] = from_union(
                [lambda x: to_class(ResourceElement, x), from_none], self.resource
            )
        if self.resourcecontents is not None:
            result["resourcecontents"] = from_union(
                [lambda x: to_class(Resourcecontents, x), from_none], self.resourcecontents
            )
        if self.resourcelink is not None:
            result["resourcelink"] = from_union(
                [lambda x: to_class(ResourcelinkClass, x), from_none], self.resourcelink
            )
        if self.resourcelistchangednotification is not None:
            result["resourcelistchangednotification"] = from_union(
                [lambda x: to_class(Resourcelistchangednotification, x), from_none],
                self.resourcelistchangednotification,
            )
        if self.resourcetemplate is not None:
            result["resourcetemplate"] = from_union(
                [lambda x: to_class(ResourcetemplateElement, x), from_none], self.resourcetemplate
            )
        if self.resourcetemplatereference is not None:
            result["resourcetemplatereference"] = from_union(
                [lambda x: to_class(ResourcetemplatereferenceClass, x), from_none],
                self.resourcetemplatereference,
            )
        if self.resourceupdatednotification is not None:
            result["resourceupdatednotification"] = from_union(
                [lambda x: to_class(Resourceupdatednotification, x), from_none],
                self.resourceupdatednotification,
            )
        if self.result is not None:
            result["result"] = from_union(
                [lambda x: to_class(EmptyresultClass, x), from_none], self.result
            )
        if self.role is not None:
            result["role"] = from_union([lambda x: to_enum(RoleElement, x), from_none], self.role)
        if self.root is not None:
            result["root"] = from_union([lambda x: to_class(RootElement, x), from_none], self.root)
        if self.rootslistchangednotification is not None:
            result["rootslistchangednotification"] = from_union(
                [lambda x: to_class(RootslistchangednotificationClass, x), from_none],
                self.rootslistchangednotification,
            )
        if self.samplingmessage is not None:
            result["samplingmessage"] = from_union(
                [lambda x: to_class(SamplingmessageElement, x), from_none], self.samplingmessage
            )
        if self.servercapabilities is not None:
            result["servercapabilities"] = from_union(
                [lambda x: to_class(Capabilities, x), from_none], self.servercapabilities
            )
        if self.servernotification is not None:
            result["servernotification"] = from_union(
                [lambda x: to_class(Servernotification, x), from_none], self.servernotification
            )
        if self.serverrequest is not None:
            result["serverrequest"] = from_union(
                [lambda x: to_class(Serverrequest, x), from_none], self.serverrequest
            )
        if self.serverresult is not None:
            result["serverresult"] = from_union(
                [lambda x: to_class(Serverresult, x), from_none], self.serverresult
            )
        if self.setlevelrequest is not None:
            result["setlevelrequest"] = from_union(
                [lambda x: to_class(SetlevelrequestClass, x), from_none], self.setlevelrequest
            )
        if self.stringschema is not None:
            result["stringschema"] = from_union(
                [lambda x: to_class(StringschemaClass, x), from_none], self.stringschema
            )
        if self.subscriberequest is not None:
            result["subscriberequest"] = from_union(
                [lambda x: to_class(SubscriberequestClass, x), from_none], self.subscriberequest
            )
        if self.textcontent is not None:
            result["textcontent"] = from_union(
                [lambda x: to_class(TextcontentClass, x), from_none], self.textcontent
            )
        if self.textresourcecontents is not None:
            result["textresourcecontents"] = from_union(
                [lambda x: to_class(TextresourcecontentsClass, x), from_none],
                self.textresourcecontents,
            )
        if self.tool is not None:
            result["tool"] = from_union([lambda x: to_class(ToolElement, x), from_none], self.tool)
        if self.toolannotations is not None:
            result["toolannotations"] = from_union(
                [lambda x: to_class(ToolannotationsClass, x), from_none], self.toolannotations
            )
        if self.toollistchangednotification is not None:
            result["toollistchangednotification"] = from_union(
                [lambda x: to_class(ToollistchangednotificationClass, x), from_none],
                self.toollistchangednotification,
            )
        if self.unsubscriberequest is not None:
            result["unsubscriberequest"] = from_union(
                [lambda x: to_class(UnsubscriberequestClass, x), from_none], self.unsubscriberequest
            )
        return result


def model_context_protocol_types_schema_from_dict(s: Any) -> ModelContextProtocolTypesSchema:
    return ModelContextProtocolTypesSchema.from_dict(s)


def model_context_protocol_types_schema_to_dict(x: ModelContextProtocolTypesSchema) -> Any:
    return to_class(ModelContextProtocolTypesSchema, x)


def model_context_protocol20250618_schema_from_dict(s: Any) -> Any:
    return s


def model_context_protocol20250618_schema_to_dict(x: Any) -> Any:
    return x
