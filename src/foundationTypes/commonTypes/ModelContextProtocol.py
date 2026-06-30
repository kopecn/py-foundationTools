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

T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


class Role(Enum):
    """The sender or recipient of messages and data in a conversation."""

    ASSISTANT = "assistant"
    USER = "user"


@dataclass
class Annotations(DataModelHelper):
    """Optional annotations for the client. The client can use annotations to inform how objects
    are used or displayed

    Optional annotations for the client.
    """

    audience: list[Role] | None = None
    """Describes who the intended customer of this object or data is.
    
    It can include multiple entries to indicate content useful for multiple audiences (e.g.,
    `["user", "assistant"]`).
    """
    last_modified: str | None = None
    """The moment the resource was last modified, as an ISO 8601 formatted string.
    
    Should be an ISO 8601 formatted string (e.g., "2025-01-12T15:00:58Z").
    
    Examples: last activity timestamp in an open file, timestamp when the resource
    was attached, etc.
    """
    priority: float | None = None
    """Describes how important this data is for operating the server.
    
    A value of 1 means "most important," and indicates that the data is
    effectively required, while 0 means "least important," and indicates that
    the data is entirely optional.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "Annotations":
        assert isinstance(obj, dict)
        audience = from_union([lambda x: from_list(Role, x), from_none], obj.get("audience"))
        last_modified = from_union([from_str, from_none], obj.get("lastModified"))
        priority = from_union([from_float, from_none], obj.get("priority"))
        return Annotations(audience, last_modified, priority)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.audience is not None:
            result["audience"] = from_union(
                [lambda x: from_list(lambda x: to_enum(Role, x), x), from_none], self.audience
            )
        if self.last_modified is not None:
            result["lastModified"] = from_union([from_str, from_none], self.last_modified)
        if self.priority is not None:
            result["priority"] = from_union([to_float, from_none], self.priority)
        return result


class AudiocontentType(Enum):
    AUDIO = "audio"


@dataclass
class AudioContent(DataModelHelper):
    """Audio provided to or from an LLM."""

    data: str
    """The base64-encoded audio data."""

    mime_type: str
    """The MIME type of the audio. Different providers may support different audio types."""

    type: AudiocontentType
    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """
    annotations: Annotations | None = None
    """Optional annotations for the client."""

    @classmethod
    def from_dict(cls, obj: Any) -> "AudioContent":
        assert isinstance(obj, dict)
        data = from_str(obj.get("data"))
        mime_type = from_str(obj.get("mimeType"))
        type = AudiocontentType(obj.get("type"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        annotations = from_union([Annotations.from_dict, from_none], obj.get("annotations"))
        return AudioContent(data, mime_type, type, meta, annotations)

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
                [lambda x: to_class(Annotations, x), from_none], self.annotations
            )
        return result


@dataclass
class BaseMetadata(DataModelHelper):
    """Base interface for metadata with name (identifier) and title (display name) properties."""

    name: str
    """Intended for programmatic or logical use, but used as a display name in past specs or
    fallback (if title isn't present).
    """
    title: str | None = None
    """Intended for UI and end-user contexts — optimized to be human-readable and easily
    understood,
    even by those unfamiliar with domain-specific terminology.
    
    If not provided, the name should be used for display (except for Tool,
    where `annotations.title` should be given precedence over using `name`,
    if present).
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "BaseMetadata":
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        title = from_union([from_str, from_none], obj.get("title"))
        return BaseMetadata(name, title)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["name"] = from_str(self.name)
        if self.title is not None:
            result["title"] = from_union([from_str, from_none], self.title)
        return result


@dataclass
class BlobResourceContents(DataModelHelper):
    blob: str
    """A base64-encoded string representing the binary data of the item."""

    uri: str
    """The URI of this resource."""

    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """
    mime_type: str | None = None
    """The MIME type of this resource, if known."""

    @classmethod
    def from_dict(cls, obj: Any) -> "BlobResourceContents":
        assert isinstance(obj, dict)
        blob = from_str(obj.get("blob"))
        uri = from_str(obj.get("uri"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        mime_type = from_union([from_str, from_none], obj.get("mimeType"))
        return BlobResourceContents(blob, uri, meta, mime_type)

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
class BooleanSchema(DataModelHelper):
    type: BooleanschemaType
    default: bool | None = None
    description: str | None = None
    title: str | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "BooleanSchema":
        assert isinstance(obj, dict)
        type = BooleanschemaType(obj.get("type"))
        default = from_union([from_bool, from_none], obj.get("default"))
        description = from_union([from_str, from_none], obj.get("description"))
        title = from_union([from_str, from_none], obj.get("title"))
        return BooleanSchema(type, default, description, title)

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


class CalltoolrequestMethod(Enum):
    TOOLS_CALL = "tools/call"


@dataclass
class CalltoolrequestParams(DataModelHelper):
    name: str
    arguments: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "CalltoolrequestParams":
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        arguments = from_union(
            [lambda x: from_dict(lambda x: x, x), from_none], obj.get("arguments")
        )
        return CalltoolrequestParams(name, arguments)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["name"] = from_str(self.name)
        if self.arguments is not None:
            result["arguments"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.arguments
            )
        return result


@dataclass
class CallToolRequest(DataModelHelper):
    """Used by the client to invoke a tool provided by the server."""

    method: CalltoolrequestMethod
    params: CalltoolrequestParams

    @classmethod
    def from_dict(cls, obj: Any) -> "CallToolRequest":
        assert isinstance(obj, dict)
        method = CalltoolrequestMethod(obj.get("method"))
        params = CalltoolrequestParams.from_dict(obj.get("params"))
        return CallToolRequest(method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["method"] = to_enum(CalltoolrequestMethod, self.method)
        result["params"] = to_class(CalltoolrequestParams, self.params)
        return result


@dataclass
class ResourceContents(DataModelHelper):
    uri: str
    """The URI of this resource."""

    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """
    mime_type: str | None = None
    """The MIME type of this resource, if known."""

    text: str | None = None
    """The text of the item. This must only be set if the item can actually be represented as
    text (not binary data).
    """
    blob: str | None = None
    """A base64-encoded string representing the binary data of the item."""

    @classmethod
    def from_dict(cls, obj: Any) -> "ResourceContents":
        assert isinstance(obj, dict)
        uri = from_str(obj.get("uri"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        mime_type = from_union([from_str, from_none], obj.get("mimeType"))
        text = from_union([from_str, from_none], obj.get("text"))
        blob = from_union([from_str, from_none], obj.get("blob"))
        return ResourceContents(uri, meta, mime_type, text, blob)

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


class ContentBlockType(Enum):
    AUDIO = "audio"
    IMAGE = "image"
    RESOURCE = "resource"
    RESOURCE_LINK = "resource_link"
    TEXT = "text"


@dataclass
class ContentBlock(DataModelHelper):
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

    type: ContentBlockType
    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """
    annotations: Annotations | None = None
    """Optional annotations for the client."""

    text: str | None = None
    """The text content of the message."""

    data: str | None = None
    """The base64-encoded image data.
    
    The base64-encoded audio data.
    """
    mime_type: str | None = None
    """The MIME type of the image. Different providers may support different image types.
    
    The MIME type of the audio. Different providers may support different audio types.
    
    The MIME type of this resource, if known.
    """
    description: str | None = None
    """A description of what this resource represents.
    
    This can be used by clients to improve the LLM's understanding of available resources. It
    can be thought of like a "hint" to the model.
    """
    name: str | None = None
    """Intended for programmatic or logical use, but used as a display name in past specs or
    fallback (if title isn't present).
    """
    size: int | None = None
    """The size of the raw resource content, in bytes (i.e., before base64 encoding or any
    tokenization), if known.
    
    This can be used by Hosts to display file sizes and estimate context window usage.
    """
    title: str | None = None
    """Intended for UI and end-user contexts — optimized to be human-readable and easily
    understood,
    even by those unfamiliar with domain-specific terminology.
    
    If not provided, the name should be used for display (except for Tool,
    where `annotations.title` should be given precedence over using `name`,
    if present).
    """
    uri: str | None = None
    """The URI of this resource."""

    resource: ResourceContents | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "ContentBlock":
        assert isinstance(obj, dict)
        type = ContentBlockType(obj.get("type"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        annotations = from_union([Annotations.from_dict, from_none], obj.get("annotations"))
        text = from_union([from_str, from_none], obj.get("text"))
        data = from_union([from_str, from_none], obj.get("data"))
        mime_type = from_union([from_str, from_none], obj.get("mimeType"))
        description = from_union([from_str, from_none], obj.get("description"))
        name = from_union([from_str, from_none], obj.get("name"))
        size = from_union([from_int, from_none], obj.get("size"))
        title = from_union([from_str, from_none], obj.get("title"))
        uri = from_union([from_str, from_none], obj.get("uri"))
        resource = from_union([ResourceContents.from_dict, from_none], obj.get("resource"))
        return ContentBlock(
            type,
            meta,
            annotations,
            text,
            data,
            mime_type,
            description,
            name,
            size,
            title,
            uri,
            resource,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["type"] = to_enum(ContentBlockType, self.type)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.annotations is not None:
            result["annotations"] = from_union(
                [lambda x: to_class(Annotations, x), from_none], self.annotations
            )
        if self.text is not None:
            result["text"] = from_union([from_str, from_none], self.text)
        if self.data is not None:
            result["data"] = from_union([from_str, from_none], self.data)
        if self.mime_type is not None:
            result["mimeType"] = from_union([from_str, from_none], self.mime_type)
        if self.description is not None:
            result["description"] = from_union([from_str, from_none], self.description)
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
                [lambda x: to_class(ResourceContents, x), from_none], self.resource
            )
        return result


@dataclass
class CallToolResult(DataModelHelper):
    """The server's response to a tool call."""

    content: list[ContentBlock]
    """A list of content objects that represent the unstructured result of the tool call."""

    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """
    is_error: bool | None = None
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
    structured_content: dict[str, Any] | None = None
    """An optional JSON object that represents the structured result of the tool call."""

    @classmethod
    def from_dict(cls, obj: Any) -> "CallToolResult":
        assert isinstance(obj, dict)
        content = from_list(ContentBlock.from_dict, obj.get("content"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        is_error = from_union([from_bool, from_none], obj.get("isError"))
        structured_content = from_union(
            [lambda x: from_dict(lambda x: x, x), from_none], obj.get("structuredContent")
        )
        return CallToolResult(content, meta, is_error, structured_content)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["content"] = from_list(lambda x: to_class(ContentBlock, x), self.content)
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
    request_id: int | str
    """The ID of the request to cancel.
    
    This MUST correspond to the ID of a request previously issued in the same direction.
    """
    reason: str | None = None
    """An optional string describing the reason for the cancellation. This MAY be logged or
    presented to the user.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "CancellednotificationParams":
        assert isinstance(obj, dict)
        request_id = from_union([from_int, from_str], obj.get("requestId"))
        reason = from_union([from_str, from_none], obj.get("reason"))
        return CancellednotificationParams(request_id, reason)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["requestId"] = from_union([from_int, from_str], self.request_id)
        if self.reason is not None:
            result["reason"] = from_union([from_str, from_none], self.reason)
        return result


@dataclass
class CancelledNotification(DataModelHelper):
    """This notification can be sent by either side to indicate that it is cancelling a
    previously-issued request.

    The request SHOULD still be in-flight, but due to communication latency, it is always
    possible that this notification MAY arrive after the request has already finished.

    This notification indicates that the result will be unused, so any associated processing
    SHOULD cease.

    A client MUST NOT attempt to cancel its `initialize` request.
    """

    method: CancellednotificationMethod
    params: CancellednotificationParams

    @classmethod
    def from_dict(cls, obj: Any) -> "CancelledNotification":
        assert isinstance(obj, dict)
        method = CancellednotificationMethod(obj.get("method"))
        params = CancellednotificationParams.from_dict(obj.get("params"))
        return CancelledNotification(method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["method"] = to_enum(CancellednotificationMethod, self.method)
        result["params"] = to_class(CancellednotificationParams, self.params)
        return result


@dataclass
class Roots(DataModelHelper):
    """Present if the client supports listing roots."""

    list_changed: bool | None = None
    """Whether the client supports notifications for changes to the roots list."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Roots":
        assert isinstance(obj, dict)
        list_changed = from_union([from_bool, from_none], obj.get("listChanged"))
        return Roots(list_changed)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.list_changed is not None:
            result["listChanged"] = from_union([from_bool, from_none], self.list_changed)
        return result


@dataclass
class ClientCapabilities(DataModelHelper):
    """Capabilities a client may support. Known capabilities are defined here, in this schema,
    but this is not a closed set: any client can define its own, additional capabilities.
    """

    elicitation: dict[str, Any] | None = None
    """Present if the client supports elicitation from the server."""

    experimental: dict[str, dict[str, Any]] | None = None
    """Experimental, non-standard capabilities that the client supports."""

    roots: Roots | None = None
    """Present if the client supports listing roots."""

    sampling: dict[str, Any] | None = None
    """Present if the client supports sampling from an LLM."""

    @classmethod
    def from_dict(cls, obj: Any) -> "ClientCapabilities":
        assert isinstance(obj, dict)
        elicitation = from_union(
            [lambda x: from_dict(lambda x: x, x), from_none], obj.get("elicitation")
        )
        experimental = from_union(
            [lambda x: from_dict(lambda x: from_dict(lambda x: x, x), x), from_none],
            obj.get("experimental"),
        )
        roots = from_union([Roots.from_dict, from_none], obj.get("roots"))
        sampling = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("sampling"))
        return ClientCapabilities(elicitation, experimental, roots, sampling)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.elicitation is not None:
            result["elicitation"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.elicitation
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
                [lambda x: from_dict(lambda x: x, x), from_none], self.sampling
            )
        return result


class ClientNotificationMethod(Enum):
    NOTIFICATIONS_CANCELLED = "notifications/cancelled"
    NOTIFICATIONS_INITIALIZED = "notifications/initialized"
    NOTIFICATIONS_PROGRESS = "notifications/progress"
    NOTIFICATIONS_ROOTS_LIST_CHANGED = "notifications/roots/list_changed"


@dataclass
class ClientNotificationParams(DataModelHelper):
    reason: str | None = None
    """An optional string describing the reason for the cancellation. This MAY be logged or
    presented to the user.
    """
    request_id: int | str | None = None
    """The ID of the request to cancel.
    
    This MUST correspond to the ID of a request previously issued in the same direction.
    """
    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """
    message: str | None = None
    """An optional message describing the current progress."""

    progress: float | None = None
    """The progress thus far. This should increase every time progress is made, even if the
    total is unknown.
    """
    progress_token: int | str | None = None
    """The progress token which was given in the initial request, used to associate this
    notification with the request that is proceeding.
    """
    total: float | None = None
    """Total number of items to process (or total progress required), if known."""

    @classmethod
    def from_dict(cls, obj: Any) -> "ClientNotificationParams":
        assert isinstance(obj, dict)
        reason = from_union([from_str, from_none], obj.get("reason"))
        request_id = from_union([from_int, from_str, from_none], obj.get("requestId"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        message = from_union([from_str, from_none], obj.get("message"))
        progress = from_union([from_float, from_none], obj.get("progress"))
        progress_token = from_union([from_int, from_str, from_none], obj.get("progressToken"))
        total = from_union([from_float, from_none], obj.get("total"))
        return ClientNotificationParams(
            reason, request_id, meta, message, progress, progress_token, total
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.reason is not None:
            result["reason"] = from_union([from_str, from_none], self.reason)
        if self.request_id is not None:
            result["requestId"] = from_union([from_int, from_str, from_none], self.request_id)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
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
        return result


@dataclass
class ClientNotification(DataModelHelper):
    """This notification can be sent by either side to indicate that it is cancelling a
    previously-issued request.

    The request SHOULD still be in-flight, but due to communication latency, it is always
    possible that this notification MAY arrive after the request has already finished.

    This notification indicates that the result will be unused, so any associated processing
    SHOULD cease.

    A client MUST NOT attempt to cancel its `initialize` request.

    This notification is sent from the client to the server after initialization has
    finished.

    An out-of-band notification used to inform the receiver of a progress update for a
    long-running request.

    A notification from the client to the server, informing it that the list of roots has
    changed.
    This notification should be sent whenever the client adds, removes, or modifies any root.
    The server should then request an updated list of roots using the ListRootsRequest.
    """

    method: ClientNotificationMethod
    params: ClientNotificationParams | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "ClientNotification":
        assert isinstance(obj, dict)
        method = ClientNotificationMethod(obj.get("method"))
        params = from_union([ClientNotificationParams.from_dict, from_none], obj.get("params"))
        return ClientNotification(method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["method"] = to_enum(ClientNotificationMethod, self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(ClientNotificationParams, x), from_none], self.params
            )
        return result


class ClientRequestMethod(Enum):
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
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        value = from_str(obj.get("value"))
        return Argument(name, value)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["name"] = from_str(self.name)
        result["value"] = from_str(self.value)
        return result


@dataclass
class Implementation(DataModelHelper):
    """Describes the name and version of an MCP implementation, with an optional title for UI
    representation.
    """

    name: str
    """Intended for programmatic or logical use, but used as a display name in past specs or
    fallback (if title isn't present).
    """
    version: str
    title: str | None = None
    """Intended for UI and end-user contexts — optimized to be human-readable and easily
    understood,
    even by those unfamiliar with domain-specific terminology.
    
    If not provided, the name should be used for display (except for Tool,
    where `annotations.title` should be given precedence over using `name`,
    if present).
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "Implementation":
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        version = from_str(obj.get("version"))
        title = from_union([from_str, from_none], obj.get("title"))
        return Implementation(name, version, title)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["name"] = from_str(self.name)
        result["version"] = from_str(self.version)
        if self.title is not None:
            result["title"] = from_union([from_str, from_none], self.title)
        return result


@dataclass
class Context(DataModelHelper):
    """Additional, optional context for completions"""

    arguments: dict[str, str] | None = None
    """Previously-resolved variables in a URI template or prompt."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Context":
        assert isinstance(obj, dict)
        arguments = from_union([lambda x: from_dict(from_str, x), from_none], obj.get("arguments"))
        return Context(arguments)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.arguments is not None:
            result["arguments"] = from_union(
                [lambda x: from_dict(from_str, x), from_none], self.arguments
            )
        return result


class LoggingLevel(Enum):
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
class PurpleMeta(DataModelHelper):
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """

    progress_token: int | str | None = None
    """If specified, the caller is requesting out-of-band progress notifications for this
    request (as represented by notifications/progress). The value of this parameter is an
    opaque token that will be attached to any subsequent notifications. The receiver is not
    obligated to provide these notifications.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "PurpleMeta":
        assert isinstance(obj, dict)
        progress_token = from_union([from_int, from_str, from_none], obj.get("progressToken"))
        return PurpleMeta(progress_token)

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
class Reference(DataModelHelper):
    """Identifies a prompt.

    A reference to a resource or resource template definition.
    """

    type: RefType
    name: str | None = None
    """Intended for programmatic or logical use, but used as a display name in past specs or
    fallback (if title isn't present).
    """
    title: str | None = None
    """Intended for UI and end-user contexts — optimized to be human-readable and easily
    understood,
    even by those unfamiliar with domain-specific terminology.
    
    If not provided, the name should be used for display (except for Tool,
    where `annotations.title` should be given precedence over using `name`,
    if present).
    """
    uri: str | None = None
    """The URI or URI template of the resource."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Reference":
        assert isinstance(obj, dict)
        type = RefType(obj.get("type"))
        name = from_union([from_str, from_none], obj.get("name"))
        title = from_union([from_str, from_none], obj.get("title"))
        uri = from_union([from_str, from_none], obj.get("uri"))
        return Reference(type, name, title, uri)

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
class ClientRequestParams(DataModelHelper):
    capabilities: ClientCapabilities | None = None
    client_info: Implementation | None = None
    protocol_version: str | None = None
    """The latest version of the Model Context Protocol that the client supports. The client MAY
    decide to support older versions as well.
    """
    meta: PurpleMeta | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """
    cursor: str | None = None
    """An opaque token representing the current pagination position.
    If provided, the server should return results starting after this cursor.
    """
    uri: str | None = None
    """The URI of the resource to read. The URI can use any protocol; it is up to the server how
    to interpret it.
    
    The URI of the resource to subscribe to. The URI can use any protocol; it is up to the
    server how to interpret it.
    
    The URI of the resource to unsubscribe from.
    """
    arguments: dict[str, Any] | None = None
    """Arguments to use for templating the prompt."""

    name: str | None = None
    """The name of the prompt or prompt template."""

    level: LoggingLevel | None = None
    """The level of logging that the client wants to receive from the server. The server should
    send all logs at this level and higher (i.e., more severe) to the client as
    notifications/message.
    """
    argument: Argument | None = None
    """The argument's information"""

    context: Context | None = None
    """Additional, optional context for completions"""

    ref: Reference | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "ClientRequestParams":
        assert isinstance(obj, dict)
        capabilities = from_union(
            [ClientCapabilities.from_dict, from_none], obj.get("capabilities")
        )
        client_info = from_union([Implementation.from_dict, from_none], obj.get("clientInfo"))
        protocol_version = from_union([from_str, from_none], obj.get("protocolVersion"))
        meta = from_union([PurpleMeta.from_dict, from_none], obj.get("_meta"))
        cursor = from_union([from_str, from_none], obj.get("cursor"))
        uri = from_union([from_str, from_none], obj.get("uri"))
        arguments = from_union(
            [lambda x: from_dict(lambda x: x, x), from_none], obj.get("arguments")
        )
        name = from_union([from_str, from_none], obj.get("name"))
        level = from_union([LoggingLevel, from_none], obj.get("level"))
        argument = from_union([Argument.from_dict, from_none], obj.get("argument"))
        context = from_union([Context.from_dict, from_none], obj.get("context"))
        ref = from_union([Reference.from_dict, from_none], obj.get("ref"))
        return ClientRequestParams(
            capabilities,
            client_info,
            protocol_version,
            meta,
            cursor,
            uri,
            arguments,
            name,
            level,
            argument,
            context,
            ref,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.capabilities is not None:
            result["capabilities"] = from_union(
                [lambda x: to_class(ClientCapabilities, x), from_none], self.capabilities
            )
        if self.client_info is not None:
            result["clientInfo"] = from_union(
                [lambda x: to_class(Implementation, x), from_none], self.client_info
            )
        if self.protocol_version is not None:
            result["protocolVersion"] = from_union([from_str, from_none], self.protocol_version)
        if self.meta is not None:
            result["_meta"] = from_union([lambda x: to_class(PurpleMeta, x), from_none], self.meta)
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
        if self.level is not None:
            result["level"] = from_union(
                [lambda x: to_enum(LoggingLevel, x), from_none], self.level
            )
        if self.argument is not None:
            result["argument"] = from_union(
                [lambda x: to_class(Argument, x), from_none], self.argument
            )
        if self.context is not None:
            result["context"] = from_union(
                [lambda x: to_class(Context, x), from_none], self.context
            )
        if self.ref is not None:
            result["ref"] = from_union([lambda x: to_class(Reference, x), from_none], self.ref)
        return result


@dataclass
class ClientRequest(DataModelHelper):
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

    A request from the client to the server, to enable or adjust logging.

    A request from the client to the server, to ask for completion options.
    """

    method: ClientRequestMethod
    params: ClientRequestParams | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "ClientRequest":
        assert isinstance(obj, dict)
        method = ClientRequestMethod(obj.get("method"))
        params = from_union([ClientRequestParams.from_dict, from_none], obj.get("params"))
        return ClientRequest(method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["method"] = to_enum(ClientRequestMethod, self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(ClientRequestParams, x), from_none], self.params
            )
        return result


class Action(Enum):
    """The user action in response to the elicitation.
    - "accept": User submitted the form/confirmed the action
    - "decline": User explicitly declined the action
    - "cancel": User dismissed without making an explicit choice
    """

    ACCEPT = "accept"
    CANCEL = "cancel"
    DECLINE = "decline"


@dataclass
class ClientResultContent(DataModelHelper):
    """Text provided to or from an LLM.

    An image provided to or from an LLM.

    Audio provided to or from an LLM.

    The submitted form data, only present when action is "accept".
    Contains values matching the requested schema.
    """

    meta: dict[str, Any] | int | bool | str | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """
    annotations: Annotations | int | bool | str | None = None
    """Optional annotations for the client."""

    text: int | bool | str | None = None
    """The text content of the message."""

    type: int | bool | str | None = None
    data: int | bool | str | None = None
    """The base64-encoded image data.
    
    The base64-encoded audio data.
    """
    mime_type: int | bool | str | None = None
    """The MIME type of the image. Different providers may support different image types.
    
    The MIME type of the audio. Different providers may support different audio types.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ClientResultContent":
        assert isinstance(obj, dict)
        meta = from_union(
            [lambda x: from_dict(lambda x: x, x), from_int, from_bool, from_str, from_none],
            obj.get("_meta"),
        )
        annotations = from_union(
            [Annotations.from_dict, from_int, from_bool, from_str, from_none],
            obj.get("annotations"),
        )
        text = from_union([from_int, from_bool, from_str, from_none], obj.get("text"))
        type = from_union([from_int, from_bool, from_str, from_none], obj.get("type"))
        data = from_union([from_int, from_bool, from_str, from_none], obj.get("data"))
        mime_type = from_union([from_int, from_bool, from_str, from_none], obj.get("mimeType"))
        return ClientResultContent(meta, annotations, text, type, data, mime_type)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_int, from_bool, from_str, from_none],
                self.meta,
            )
        if self.annotations is not None:
            result["annotations"] = from_union(
                [lambda x: to_class(Annotations, x), from_int, from_bool, from_str, from_none],
                self.annotations,
            )
        if self.text is not None:
            result["text"] = from_union([from_int, from_bool, from_str, from_none], self.text)
        if self.type is not None:
            result["type"] = from_union([from_int, from_bool, from_str, from_none], self.type)
        if self.data is not None:
            result["data"] = from_union([from_int, from_bool, from_str, from_none], self.data)
        if self.mime_type is not None:
            result["mimeType"] = from_union(
                [from_int, from_bool, from_str, from_none], self.mime_type
            )
        return result


@dataclass
class Root(DataModelHelper):
    """Represents a root directory or file that the server can operate on."""

    uri: str
    """The URI identifying the root. This *must* start with file:// for now.
    This restriction may be relaxed in future versions of the protocol to allow
    other URI schemes.
    """
    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """
    name: str | None = None
    """An optional name for the root. This can be used to provide a human-readable
    identifier for the root, which may be useful for display purposes or for
    referencing the root in other parts of the application.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "Root":
        assert isinstance(obj, dict)
        uri = from_str(obj.get("uri"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        name = from_union([from_str, from_none], obj.get("name"))
        return Root(uri, meta, name)

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
class ClientResult(DataModelHelper):
    """The client's response to a sampling/create_message request from the server. The client
    should inform the user before returning the sampled message, to allow them to inspect the
    response (human in the loop) and decide whether to allow the server to see it.

    The client's response to a roots/list request from the server.
    This result contains an array of Root objects, each representing a root directory
    or file that the server can operate on.

    The client's response to an elicitation request.
    """

    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """
    content: ClientResultContent | None = None
    """The submitted form data, only present when action is "accept".
    Contains values matching the requested schema.
    """
    model: str | None = None
    """The name of the model that generated the message."""

    role: Role | None = None
    stop_reason: str | None = None
    """The reason why sampling stopped, if known."""

    roots: list[Root] | None = None
    action: Action | None = None
    """The user action in response to the elicitation.
    - "accept": User submitted the form/confirmed the action
    - "decline": User explicitly declined the action
    - "cancel": User dismissed without making an explicit choice
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ClientResult":
        assert isinstance(obj, dict)
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        content = from_union([ClientResultContent.from_dict, from_none], obj.get("content"))
        model = from_union([from_str, from_none], obj.get("model"))
        role = from_union([Role, from_none], obj.get("role"))
        stop_reason = from_union([from_str, from_none], obj.get("stopReason"))
        roots = from_union([lambda x: from_list(Root.from_dict, x), from_none], obj.get("roots"))
        action = from_union([Action, from_none], obj.get("action"))
        return ClientResult(meta, content, model, role, stop_reason, roots, action)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.content is not None:
            result["content"] = from_union(
                [lambda x: to_class(ClientResultContent, x), from_none], self.content
            )
        if self.model is not None:
            result["model"] = from_union([from_str, from_none], self.model)
        if self.role is not None:
            result["role"] = from_union([lambda x: to_enum(Role, x), from_none], self.role)
        if self.stop_reason is not None:
            result["stopReason"] = from_union([from_str, from_none], self.stop_reason)
        if self.roots is not None:
            result["roots"] = from_union(
                [lambda x: from_list(lambda x: to_class(Root, x), x), from_none], self.roots
            )
        if self.action is not None:
            result["action"] = from_union([lambda x: to_enum(Action, x), from_none], self.action)
        return result


class CompleterequestMethod(Enum):
    COMPLETION_COMPLETE = "completion/complete"


@dataclass
class CompleterequestParams(DataModelHelper):
    argument: Argument
    """The argument's information"""

    ref: Reference
    context: Context | None = None
    """Additional, optional context for completions"""

    @classmethod
    def from_dict(cls, obj: Any) -> "CompleterequestParams":
        assert isinstance(obj, dict)
        argument = Argument.from_dict(obj.get("argument"))
        ref = Reference.from_dict(obj.get("ref"))
        context = from_union([Context.from_dict, from_none], obj.get("context"))
        return CompleterequestParams(argument, ref, context)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["argument"] = to_class(Argument, self.argument)
        result["ref"] = to_class(Reference, self.ref)
        if self.context is not None:
            result["context"] = from_union(
                [lambda x: to_class(Context, x), from_none], self.context
            )
        return result


@dataclass
class CompleteRequest(DataModelHelper):
    """A request from the client to the server, to ask for completion options."""

    method: CompleterequestMethod
    params: CompleterequestParams

    @classmethod
    def from_dict(cls, obj: Any) -> "CompleteRequest":
        assert isinstance(obj, dict)
        method = CompleterequestMethod(obj.get("method"))
        params = CompleterequestParams.from_dict(obj.get("params"))
        return CompleteRequest(method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["method"] = to_enum(CompleterequestMethod, self.method)
        result["params"] = to_class(CompleterequestParams, self.params)
        return result


@dataclass
class Completion(DataModelHelper):
    values: list[str]
    """An array of completion values. Must not exceed 100 items."""

    has_more: bool | None = None
    """Indicates whether there are additional completion options beyond those provided in the
    current response, even if the exact total is unknown.
    """
    total: int | None = None
    """The total number of completion options available. This can exceed the number of values
    actually sent in the response.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "Completion":
        assert isinstance(obj, dict)
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
class CompleteResult(DataModelHelper):
    """The server's response to a completion/complete request"""

    completion: Completion
    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "CompleteResult":
        assert isinstance(obj, dict)
        completion = Completion.from_dict(obj.get("completion"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        return CompleteResult(completion, meta)

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
    attached to the prompt. The client MAY ignore this request.
    """

    ALL_SERVERS = "allServers"
    NONE = "none"
    THIS_SERVER = "thisServer"


class ContentType(Enum):
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"


@dataclass
class SamplingmessageContent(DataModelHelper):
    """Text provided to or from an LLM.

    An image provided to or from an LLM.

    Audio provided to or from an LLM.
    """

    type: ContentType
    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """
    annotations: Annotations | None = None
    """Optional annotations for the client."""

    text: str | None = None
    """The text content of the message."""

    data: str | None = None
    """The base64-encoded image data.
    
    The base64-encoded audio data.
    """
    mime_type: str | None = None
    """The MIME type of the image. Different providers may support different image types.
    
    The MIME type of the audio. Different providers may support different audio types.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "SamplingmessageContent":
        assert isinstance(obj, dict)
        type = ContentType(obj.get("type"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        annotations = from_union([Annotations.from_dict, from_none], obj.get("annotations"))
        text = from_union([from_str, from_none], obj.get("text"))
        data = from_union([from_str, from_none], obj.get("data"))
        mime_type = from_union([from_str, from_none], obj.get("mimeType"))
        return SamplingmessageContent(type, meta, annotations, text, data, mime_type)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["type"] = to_enum(ContentType, self.type)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.annotations is not None:
            result["annotations"] = from_union(
                [lambda x: to_class(Annotations, x), from_none], self.annotations
            )
        if self.text is not None:
            result["text"] = from_union([from_str, from_none], self.text)
        if self.data is not None:
            result["data"] = from_union([from_str, from_none], self.data)
        if self.mime_type is not None:
            result["mimeType"] = from_union([from_str, from_none], self.mime_type)
        return result


@dataclass
class SamplingMessage(DataModelHelper):
    """Describes a message issued to or received from an LLM API."""

    content: SamplingmessageContent
    role: Role

    @classmethod
    def from_dict(cls, obj: Any) -> "SamplingMessage":
        assert isinstance(obj, dict)
        content = SamplingmessageContent.from_dict(obj.get("content"))
        role = Role(obj.get("role"))
        return SamplingMessage(content, role)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["content"] = to_class(SamplingmessageContent, self.content)
        result["role"] = to_enum(Role, self.role)
        return result


@dataclass
class ModelHint(DataModelHelper):
    """Hints to use for model selection.

    Keys not declared here are currently left unspecified by the spec and are up
    to the client to interpret.
    """

    name: str | None = None
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
    def from_dict(cls, obj: Any) -> "ModelHint":
        assert isinstance(obj, dict)
        name = from_union([from_str, from_none], obj.get("name"))
        return ModelHint(name)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.name is not None:
            result["name"] = from_union([from_str, from_none], self.name)
        return result


@dataclass
class ModelPreferences(DataModelHelper):
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

    cost_priority: float | None = None
    """How much to prioritize cost when selecting a model. A value of 0 means cost
    is not important, while a value of 1 means cost is the most important
    factor.
    """
    hints: list[ModelHint] | None = None
    """Optional hints to use for model selection.
    
    If multiple hints are specified, the client MUST evaluate them in order
    (such that the first match is taken).
    
    The client SHOULD prioritize these hints over the numeric priorities, but
    MAY still use the priorities to select from ambiguous matches.
    """
    intelligence_priority: float | None = None
    """How much to prioritize intelligence and capabilities when selecting a
    model. A value of 0 means intelligence is not important, while a value of 1
    means intelligence is the most important factor.
    """
    speed_priority: float | None = None
    """How much to prioritize sampling speed (latency) when selecting a model. A
    value of 0 means speed is not important, while a value of 1 means speed is
    the most important factor.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ModelPreferences":
        assert isinstance(obj, dict)
        cost_priority = from_union([from_float, from_none], obj.get("costPriority"))
        hints = from_union(
            [lambda x: from_list(ModelHint.from_dict, x), from_none], obj.get("hints")
        )
        intelligence_priority = from_union([from_float, from_none], obj.get("intelligencePriority"))
        speed_priority = from_union([from_float, from_none], obj.get("speedPriority"))
        return ModelPreferences(cost_priority, hints, intelligence_priority, speed_priority)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.cost_priority is not None:
            result["costPriority"] = from_union([to_float, from_none], self.cost_priority)
        if self.hints is not None:
            result["hints"] = from_union(
                [lambda x: from_list(lambda x: to_class(ModelHint, x), x), from_none], self.hints
            )
        if self.intelligence_priority is not None:
            result["intelligencePriority"] = from_union(
                [to_float, from_none], self.intelligence_priority
            )
        if self.speed_priority is not None:
            result["speedPriority"] = from_union([to_float, from_none], self.speed_priority)
        return result


@dataclass
class CreatemessagerequestParams(DataModelHelper):
    max_tokens: int
    """The maximum number of tokens to sample, as requested by the server. The client MAY choose
    to sample fewer tokens than requested.
    """
    messages: list[SamplingMessage]
    include_context: IncludeContext | None = None
    """A request to include context from one or more MCP servers (including the caller), to be
    attached to the prompt. The client MAY ignore this request.
    """
    metadata: dict[str, Any] | None = None
    """Optional metadata to pass through to the LLM provider. The format of this metadata is
    provider-specific.
    """
    model_preferences: ModelPreferences | None = None
    """The server's preferences for which model to select. The client MAY ignore these
    preferences.
    """
    stop_sequences: list[str] | None = None
    system_prompt: str | None = None
    """An optional system prompt the server wants to use for sampling. The client MAY modify or
    omit this prompt.
    """
    temperature: float | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "CreatemessagerequestParams":
        assert isinstance(obj, dict)
        max_tokens = from_int(obj.get("maxTokens"))
        messages = from_list(SamplingMessage.from_dict, obj.get("messages"))
        include_context = from_union([IncludeContext, from_none], obj.get("includeContext"))
        metadata = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("metadata"))
        model_preferences = from_union(
            [ModelPreferences.from_dict, from_none], obj.get("modelPreferences")
        )
        stop_sequences = from_union(
            [lambda x: from_list(from_str, x), from_none], obj.get("stopSequences")
        )
        system_prompt = from_union([from_str, from_none], obj.get("systemPrompt"))
        temperature = from_union([from_float, from_none], obj.get("temperature"))
        return CreatemessagerequestParams(
            max_tokens,
            messages,
            include_context,
            metadata,
            model_preferences,
            stop_sequences,
            system_prompt,
            temperature,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["maxTokens"] = from_int(self.max_tokens)
        result["messages"] = from_list(lambda x: to_class(SamplingMessage, x), self.messages)
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
                [lambda x: to_class(ModelPreferences, x), from_none], self.model_preferences
            )
        if self.stop_sequences is not None:
            result["stopSequences"] = from_union(
                [lambda x: from_list(from_str, x), from_none], self.stop_sequences
            )
        if self.system_prompt is not None:
            result["systemPrompt"] = from_union([from_str, from_none], self.system_prompt)
        if self.temperature is not None:
            result["temperature"] = from_union([to_float, from_none], self.temperature)
        return result


@dataclass
class CreateMessageRequest(DataModelHelper):
    """A request from the server to sample an LLM via the client. The client has full discretion
    over which model to select. The client should also inform the user before beginning
    sampling, to allow them to inspect the request (human in the loop) and decide whether to
    approve it.
    """

    method: CreatemessagerequestMethod
    params: CreatemessagerequestParams

    @classmethod
    def from_dict(cls, obj: Any) -> "CreateMessageRequest":
        assert isinstance(obj, dict)
        method = CreatemessagerequestMethod(obj.get("method"))
        params = CreatemessagerequestParams.from_dict(obj.get("params"))
        return CreateMessageRequest(method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["method"] = to_enum(CreatemessagerequestMethod, self.method)
        result["params"] = to_class(CreatemessagerequestParams, self.params)
        return result


@dataclass
class CreateMessageResult(DataModelHelper):
    """The client's response to a sampling/create_message request from the server. The client
    should inform the user before returning the sampled message, to allow them to inspect the
    response (human in the loop) and decide whether to allow the server to see it.
    """

    content: SamplingmessageContent
    model: str
    """The name of the model that generated the message."""

    role: Role
    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """
    stop_reason: str | None = None
    """The reason why sampling stopped, if known."""

    @classmethod
    def from_dict(cls, obj: Any) -> "CreateMessageResult":
        assert isinstance(obj, dict)
        content = SamplingmessageContent.from_dict(obj.get("content"))
        model = from_str(obj.get("model"))
        role = Role(obj.get("role"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        stop_reason = from_union([from_str, from_none], obj.get("stopReason"))
        return CreateMessageResult(content, model, role, meta, stop_reason)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["content"] = to_class(SamplingmessageContent, self.content)
        result["model"] = from_str(self.model)
        result["role"] = to_enum(Role, self.role)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.stop_reason is not None:
            result["stopReason"] = from_union([from_str, from_none], self.stop_reason)
        return result


class ElicitrequestMethod(Enum):
    ELICITATION_CREATE = "elicitation/create"


class Format(Enum):
    DATE = "date"
    DATE_TIME = "date-time"
    EMAIL = "email"
    URI = "uri"


class PrimitiveSchemaDefinitionType(Enum):
    BOOLEAN = "boolean"
    INTEGER = "integer"
    NUMBER = "number"
    STRING = "string"


@dataclass
class PrimitiveSchemaDefinition(DataModelHelper):
    """Restricted schema definitions that only allow primitive types
    without nested objects or arrays.
    """

    type: PrimitiveSchemaDefinitionType
    description: str | None = None
    format: Format | None = None
    max_length: int | None = None
    min_length: int | None = None
    title: str | None = None
    maximum: int | None = None
    minimum: int | None = None
    default: bool | None = None
    enum: list[str] | None = None
    enum_names: list[str] | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "PrimitiveSchemaDefinition":
        assert isinstance(obj, dict)
        type = PrimitiveSchemaDefinitionType(obj.get("type"))
        description = from_union([from_str, from_none], obj.get("description"))
        format = from_union([Format, from_none], obj.get("format"))
        max_length = from_union([from_int, from_none], obj.get("maxLength"))
        min_length = from_union([from_int, from_none], obj.get("minLength"))
        title = from_union([from_str, from_none], obj.get("title"))
        maximum = from_union([from_int, from_none], obj.get("maximum"))
        minimum = from_union([from_int, from_none], obj.get("minimum"))
        default = from_union([from_bool, from_none], obj.get("default"))
        enum = from_union([lambda x: from_list(from_str, x), from_none], obj.get("enum"))
        enum_names = from_union([lambda x: from_list(from_str, x), from_none], obj.get("enumNames"))
        return PrimitiveSchemaDefinition(
            type,
            description,
            format,
            max_length,
            min_length,
            title,
            maximum,
            minimum,
            default,
            enum,
            enum_names,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["type"] = to_enum(PrimitiveSchemaDefinitionType, self.type)
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
        if self.default is not None:
            result["default"] = from_union([from_bool, from_none], self.default)
        if self.enum is not None:
            result["enum"] = from_union([lambda x: from_list(from_str, x), from_none], self.enum)
        if self.enum_names is not None:
            result["enumNames"] = from_union(
                [lambda x: from_list(from_str, x), from_none], self.enum_names
            )
        return result


class RequestedSchemaType(Enum):
    OBJECT = "object"


@dataclass
class RequestedSchema(DataModelHelper):
    """A restricted subset of JSON Schema.
    Only top-level properties are allowed, without nesting.
    """

    properties: dict[str, PrimitiveSchemaDefinition]
    type: RequestedSchemaType
    required: list[str] | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "RequestedSchema":
        assert isinstance(obj, dict)
        properties = from_dict(PrimitiveSchemaDefinition.from_dict, obj.get("properties"))
        type = RequestedSchemaType(obj.get("type"))
        required = from_union([lambda x: from_list(from_str, x), from_none], obj.get("required"))
        return RequestedSchema(properties, type, required)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["properties"] = from_dict(
            lambda x: to_class(PrimitiveSchemaDefinition, x), self.properties
        )
        result["type"] = to_enum(RequestedSchemaType, self.type)
        if self.required is not None:
            result["required"] = from_union(
                [lambda x: from_list(from_str, x), from_none], self.required
            )
        return result


@dataclass
class ElicitrequestParams(DataModelHelper):
    message: str
    """The message to present to the user."""

    requested_schema: RequestedSchema
    """A restricted subset of JSON Schema.
    Only top-level properties are allowed, without nesting.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ElicitrequestParams":
        assert isinstance(obj, dict)
        message = from_str(obj.get("message"))
        requested_schema = RequestedSchema.from_dict(obj.get("requestedSchema"))
        return ElicitrequestParams(message, requested_schema)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["message"] = from_str(self.message)
        result["requestedSchema"] = to_class(RequestedSchema, self.requested_schema)
        return result


@dataclass
class ElicitRequest(DataModelHelper):
    """A request from the server to elicit additional information from the user via the client."""

    method: ElicitrequestMethod
    params: ElicitrequestParams

    @classmethod
    def from_dict(cls, obj: Any) -> "ElicitRequest":
        assert isinstance(obj, dict)
        method = ElicitrequestMethod(obj.get("method"))
        params = ElicitrequestParams.from_dict(obj.get("params"))
        return ElicitRequest(method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["method"] = to_enum(ElicitrequestMethod, self.method)
        result["params"] = to_class(ElicitrequestParams, self.params)
        return result


@dataclass
class ElicitResult(DataModelHelper):
    """The client's response to an elicitation request."""

    action: Action
    """The user action in response to the elicitation.
    - "accept": User submitted the form/confirmed the action
    - "decline": User explicitly declined the action
    - "cancel": User dismissed without making an explicit choice
    """
    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """
    content: dict[str, int | bool | str] | None = None
    """The submitted form data, only present when action is "accept".
    Contains values matching the requested schema.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ElicitResult":
        assert isinstance(obj, dict)
        action = Action(obj.get("action"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        content = from_union(
            [
                lambda x: from_dict(lambda x: from_union([from_int, from_bool, from_str], x), x),
                from_none,
            ],
            obj.get("content"),
        )
        return ElicitResult(action, meta, content)

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
                        lambda x: from_union([from_int, from_bool, from_str], x), x
                    ),
                    from_none,
                ],
                self.content,
            )
        return result


class EmbeddedresourceType(Enum):
    RESOURCE = "resource"


@dataclass
class EmbeddedResource(DataModelHelper):
    """The contents of a resource, embedded into a prompt or tool call result.

    It is up to the client how best to render embedded resources for the benefit
    of the LLM and/or the user.
    """

    resource: ResourceContents
    type: EmbeddedresourceType
    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """
    annotations: Annotations | None = None
    """Optional annotations for the client."""

    @classmethod
    def from_dict(cls, obj: Any) -> "EmbeddedResource":
        assert isinstance(obj, dict)
        resource = ResourceContents.from_dict(obj.get("resource"))
        type = EmbeddedresourceType(obj.get("type"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        annotations = from_union([Annotations.from_dict, from_none], obj.get("annotations"))
        return EmbeddedResource(resource, type, meta, annotations)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["resource"] = to_class(ResourceContents, self.resource)
        result["type"] = to_enum(EmbeddedresourceType, self.type)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.annotations is not None:
            result["annotations"] = from_union(
                [lambda x: to_class(Annotations, x), from_none], self.annotations
            )
        return result


@dataclass
class Result(DataModelHelper):
    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "Result":
        assert isinstance(obj, dict)
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        return Result(meta)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        return result


class EnumschemaType(Enum):
    STRING = "string"


@dataclass
class EnumSchema(DataModelHelper):
    enum: list[str]
    type: EnumschemaType
    description: str | None = None
    enum_names: list[str] | None = None
    title: str | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "EnumSchema":
        assert isinstance(obj, dict)
        enum = from_list(from_str, obj.get("enum"))
        type = EnumschemaType(obj.get("type"))
        description = from_union([from_str, from_none], obj.get("description"))
        enum_names = from_union([lambda x: from_list(from_str, x), from_none], obj.get("enumNames"))
        title = from_union([from_str, from_none], obj.get("title"))
        return EnumSchema(enum, type, description, enum_names, title)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["enum"] = from_list(from_str, self.enum)
        result["type"] = to_enum(EnumschemaType, self.type)
        if self.description is not None:
            result["description"] = from_union([from_str, from_none], self.description)
        if self.enum_names is not None:
            result["enumNames"] = from_union(
                [lambda x: from_list(from_str, x), from_none], self.enum_names
            )
        if self.title is not None:
            result["title"] = from_union([from_str, from_none], self.title)
        return result


class GetpromptrequestMethod(Enum):
    PROMPTS_GET = "prompts/get"


@dataclass
class GetpromptrequestParams(DataModelHelper):
    name: str
    """The name of the prompt or prompt template."""

    arguments: dict[str, str] | None = None
    """Arguments to use for templating the prompt."""

    @classmethod
    def from_dict(cls, obj: Any) -> "GetpromptrequestParams":
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        arguments = from_union([lambda x: from_dict(from_str, x), from_none], obj.get("arguments"))
        return GetpromptrequestParams(name, arguments)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["name"] = from_str(self.name)
        if self.arguments is not None:
            result["arguments"] = from_union(
                [lambda x: from_dict(from_str, x), from_none], self.arguments
            )
        return result


@dataclass
class GetPromptRequest(DataModelHelper):
    """Used by the client to get a prompt provided by the server."""

    method: GetpromptrequestMethod
    params: GetpromptrequestParams

    @classmethod
    def from_dict(cls, obj: Any) -> "GetPromptRequest":
        assert isinstance(obj, dict)
        method = GetpromptrequestMethod(obj.get("method"))
        params = GetpromptrequestParams.from_dict(obj.get("params"))
        return GetPromptRequest(method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["method"] = to_enum(GetpromptrequestMethod, self.method)
        result["params"] = to_class(GetpromptrequestParams, self.params)
        return result


@dataclass
class PromptMessage(DataModelHelper):
    """Describes a message returned as part of a prompt.

    This is similar to `SamplingMessage`, but also supports the embedding of
    resources from the MCP server.
    """

    content: ContentBlock
    role: Role

    @classmethod
    def from_dict(cls, obj: Any) -> "PromptMessage":
        assert isinstance(obj, dict)
        content = ContentBlock.from_dict(obj.get("content"))
        role = Role(obj.get("role"))
        return PromptMessage(content, role)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["content"] = to_class(ContentBlock, self.content)
        result["role"] = to_enum(Role, self.role)
        return result


@dataclass
class GetPromptResult(DataModelHelper):
    """The server's response to a prompts/get request from the client."""

    messages: list[PromptMessage]
    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """
    description: str | None = None
    """An optional description for the prompt."""

    @classmethod
    def from_dict(cls, obj: Any) -> "GetPromptResult":
        assert isinstance(obj, dict)
        messages = from_list(PromptMessage.from_dict, obj.get("messages"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        description = from_union([from_str, from_none], obj.get("description"))
        return GetPromptResult(messages, meta, description)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["messages"] = from_list(lambda x: to_class(PromptMessage, x), self.messages)
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
class ImageContent(DataModelHelper):
    """An image provided to or from an LLM."""

    data: str
    """The base64-encoded image data."""

    mime_type: str
    """The MIME type of the image. Different providers may support different image types."""

    type: ImagecontentType
    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """
    annotations: Annotations | None = None
    """Optional annotations for the client."""

    @classmethod
    def from_dict(cls, obj: Any) -> "ImageContent":
        assert isinstance(obj, dict)
        data = from_str(obj.get("data"))
        mime_type = from_str(obj.get("mimeType"))
        type = ImagecontentType(obj.get("type"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        annotations = from_union([Annotations.from_dict, from_none], obj.get("annotations"))
        return ImageContent(data, mime_type, type, meta, annotations)

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
                [lambda x: to_class(Annotations, x), from_none], self.annotations
            )
        return result


class InitializednotificationMethod(Enum):
    NOTIFICATIONS_INITIALIZED = "notifications/initialized"


@dataclass
class InitializednotificationParams(DataModelHelper):
    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "InitializednotificationParams":
        assert isinstance(obj, dict)
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
class InitializedNotification(DataModelHelper):
    """This notification is sent from the client to the server after initialization has finished."""

    method: InitializednotificationMethod
    params: InitializednotificationParams | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "InitializedNotification":
        assert isinstance(obj, dict)
        method = InitializednotificationMethod(obj.get("method"))
        params = from_union([InitializednotificationParams.from_dict, from_none], obj.get("params"))
        return InitializedNotification(method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["method"] = to_enum(InitializednotificationMethod, self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(InitializednotificationParams, x), from_none], self.params
            )
        return result


class InitializerequestMethod(Enum):
    INITIALIZE = "initialize"


@dataclass
class InitializerequestParams(DataModelHelper):
    capabilities: ClientCapabilities
    client_info: Implementation
    protocol_version: str
    """The latest version of the Model Context Protocol that the client supports. The client MAY
    decide to support older versions as well.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "InitializerequestParams":
        assert isinstance(obj, dict)
        capabilities = ClientCapabilities.from_dict(obj.get("capabilities"))
        client_info = Implementation.from_dict(obj.get("clientInfo"))
        protocol_version = from_str(obj.get("protocolVersion"))
        return InitializerequestParams(capabilities, client_info, protocol_version)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["capabilities"] = to_class(ClientCapabilities, self.capabilities)
        result["clientInfo"] = to_class(Implementation, self.client_info)
        result["protocolVersion"] = from_str(self.protocol_version)
        return result


@dataclass
class InitializeRequest(DataModelHelper):
    """This request is sent from the client to the server when it first connects, asking it to
    begin initialization.
    """

    method: InitializerequestMethod
    params: InitializerequestParams

    @classmethod
    def from_dict(cls, obj: Any) -> "InitializeRequest":
        assert isinstance(obj, dict)
        method = InitializerequestMethod(obj.get("method"))
        params = InitializerequestParams.from_dict(obj.get("params"))
        return InitializeRequest(method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["method"] = to_enum(InitializerequestMethod, self.method)
        result["params"] = to_class(InitializerequestParams, self.params)
        return result


@dataclass
class Prompts(DataModelHelper):
    """Present if the server offers any prompt templates."""

    list_changed: bool | None = None
    """Whether this server supports notifications for changes to the prompt list."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Prompts":
        assert isinstance(obj, dict)
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

    list_changed: bool | None = None
    """Whether this server supports notifications for changes to the resource list."""

    subscribe: bool | None = None
    """Whether this server supports subscribing to resource updates."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Resources":
        assert isinstance(obj, dict)
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
class Tools(DataModelHelper):
    """Present if the server offers any tools to call."""

    list_changed: bool | None = None
    """Whether this server supports notifications for changes to the tool list."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Tools":
        assert isinstance(obj, dict)
        list_changed = from_union([from_bool, from_none], obj.get("listChanged"))
        return Tools(list_changed)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.list_changed is not None:
            result["listChanged"] = from_union([from_bool, from_none], self.list_changed)
        return result


@dataclass
class ServerCapabilities(DataModelHelper):
    """Capabilities that a server may support. Known capabilities are defined here, in this
    schema, but this is not a closed set: any server can define its own, additional
    capabilities.
    """

    completions: dict[str, Any] | None = None
    """Present if the server supports argument autocompletion suggestions."""

    experimental: dict[str, dict[str, Any]] | None = None
    """Experimental, non-standard capabilities that the server supports."""

    logging: dict[str, Any] | None = None
    """Present if the server supports sending log messages to the client."""

    prompts: Prompts | None = None
    """Present if the server offers any prompt templates."""

    resources: Resources | None = None
    """Present if the server offers any resources to read."""

    tools: Tools | None = None
    """Present if the server offers any tools to call."""

    @classmethod
    def from_dict(cls, obj: Any) -> "ServerCapabilities":
        assert isinstance(obj, dict)
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
        tools = from_union([Tools.from_dict, from_none], obj.get("tools"))
        return ServerCapabilities(completions, experimental, logging, prompts, resources, tools)

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
        if self.tools is not None:
            result["tools"] = from_union([lambda x: to_class(Tools, x), from_none], self.tools)
        return result


@dataclass
class InitializeResult(DataModelHelper):
    """After receiving an initialize request from the client, the server sends this response."""

    capabilities: ServerCapabilities
    protocol_version: str
    """The version of the Model Context Protocol that the server wants to use. This may not
    match the version that the client requested. If the client cannot support this version,
    it MUST disconnect.
    """
    server_info: Implementation
    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """
    instructions: str | None = None
    """Instructions describing how to use the server and its features.
    
    This can be used by clients to improve the LLM's understanding of available tools,
    resources, etc. It can be thought of like a "hint" to the model. For example, this
    information MAY be added to the system prompt.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "InitializeResult":
        assert isinstance(obj, dict)
        capabilities = ServerCapabilities.from_dict(obj.get("capabilities"))
        protocol_version = from_str(obj.get("protocolVersion"))
        server_info = Implementation.from_dict(obj.get("serverInfo"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        instructions = from_union([from_str, from_none], obj.get("instructions"))
        return InitializeResult(capabilities, protocol_version, server_info, meta, instructions)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["capabilities"] = to_class(ServerCapabilities, self.capabilities)
        result["protocolVersion"] = from_str(self.protocol_version)
        result["serverInfo"] = to_class(Implementation, self.server_info)
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
        assert isinstance(obj, dict)
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


class Jsonrpc(Enum):
    THE_20 = "2.0"


@dataclass
class JSONRPCError(DataModelHelper):
    """A response to a request that indicates an error occurred."""

    error: Error
    id: int | str
    jsonrpc: Jsonrpc

    @classmethod
    def from_dict(cls, obj: Any) -> "JSONRPCError":
        assert isinstance(obj, dict)
        error = Error.from_dict(obj.get("error"))
        id = from_union([from_int, from_str], obj.get("id"))
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        return JSONRPCError(error, id, jsonrpc)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["error"] = to_class(Error, self.error)
        result["id"] = from_union([from_int, from_str], self.id)
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        return result


@dataclass
class FluffyMeta(DataModelHelper):
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """

    progress_token: int | str | None = None
    """If specified, the caller is requesting out-of-band progress notifications for this
    request (as represented by notifications/progress). The value of this parameter is an
    opaque token that will be attached to any subsequent notifications. The receiver is not
    obligated to provide these notifications.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "FluffyMeta":
        assert isinstance(obj, dict)
        progress_token = from_union([from_int, from_str, from_none], obj.get("progressToken"))
        return FluffyMeta(progress_token)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.progress_token is not None:
            result["progressToken"] = from_union(
                [from_int, from_str, from_none], self.progress_token
            )
        return result


@dataclass
class JSONRPCMessageParams(DataModelHelper):
    meta: FluffyMeta | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "JSONRPCMessageParams":
        assert isinstance(obj, dict)
        meta = from_union([FluffyMeta.from_dict, from_none], obj.get("_meta"))
        return JSONRPCMessageParams(meta)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.meta is not None:
            result["_meta"] = from_union([lambda x: to_class(FluffyMeta, x), from_none], self.meta)
        return result


@dataclass
class JSONRPCMessage(DataModelHelper):
    """Refers to any valid JSON-RPC object that can be decoded off the wire, or encoded to be
    sent.

    A request that expects a response.

    A notification which does not expect a response.

    A successful (non-error) response to a request.

    A response to a request that indicates an error occurred.
    """

    jsonrpc: Jsonrpc
    id: int | str | None = None
    method: str | None = None
    params: JSONRPCMessageParams | None = None
    result: Result | None = None
    error: Error | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "JSONRPCMessage":
        assert isinstance(obj, dict)
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        id = from_union([from_int, from_str, from_none], obj.get("id"))
        method = from_union([from_str, from_none], obj.get("method"))
        params = from_union([JSONRPCMessageParams.from_dict, from_none], obj.get("params"))
        result = from_union([Result.from_dict, from_none], obj.get("result"))
        error = from_union([Error.from_dict, from_none], obj.get("error"))
        return JSONRPCMessage(jsonrpc, id, method, params, result, error)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        if self.id is not None:
            result["id"] = from_union([from_int, from_str, from_none], self.id)
        if self.method is not None:
            result["method"] = from_union([from_str, from_none], self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(JSONRPCMessageParams, x), from_none], self.params
            )
        if self.result is not None:
            result["result"] = from_union([lambda x: to_class(Result, x), from_none], self.result)
        if self.error is not None:
            result["error"] = from_union([lambda x: to_class(Error, x), from_none], self.error)
        return result


@dataclass
class JsonrpcnotificationParams(DataModelHelper):
    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "JsonrpcnotificationParams":
        assert isinstance(obj, dict)
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        return JsonrpcnotificationParams(meta)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        return result


@dataclass
class JSONRPCNotification(DataModelHelper):
    """A notification which does not expect a response."""

    jsonrpc: Jsonrpc
    method: str
    params: JsonrpcnotificationParams | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "JSONRPCNotification":
        assert isinstance(obj, dict)
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        method = from_str(obj.get("method"))
        params = from_union([JsonrpcnotificationParams.from_dict, from_none], obj.get("params"))
        return JSONRPCNotification(jsonrpc, method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        result["method"] = from_str(self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(JsonrpcnotificationParams, x), from_none], self.params
            )
        return result


@dataclass
class TentacledMeta(DataModelHelper):
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """

    progress_token: int | str | None = None
    """If specified, the caller is requesting out-of-band progress notifications for this
    request (as represented by notifications/progress). The value of this parameter is an
    opaque token that will be attached to any subsequent notifications. The receiver is not
    obligated to provide these notifications.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "TentacledMeta":
        assert isinstance(obj, dict)
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
class JsonrpcrequestParams(DataModelHelper):
    meta: TentacledMeta | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "JsonrpcrequestParams":
        assert isinstance(obj, dict)
        meta = from_union([TentacledMeta.from_dict, from_none], obj.get("_meta"))
        return JsonrpcrequestParams(meta)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: to_class(TentacledMeta, x), from_none], self.meta
            )
        return result


@dataclass
class JSONRPCRequest(DataModelHelper):
    """A request that expects a response."""

    id: int | str
    jsonrpc: Jsonrpc
    method: str
    params: JsonrpcrequestParams | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "JSONRPCRequest":
        assert isinstance(obj, dict)
        id = from_union([from_int, from_str], obj.get("id"))
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        method = from_str(obj.get("method"))
        params = from_union([JsonrpcrequestParams.from_dict, from_none], obj.get("params"))
        return JSONRPCRequest(id, jsonrpc, method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["id"] = from_union([from_int, from_str], self.id)
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        result["method"] = from_str(self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(JsonrpcrequestParams, x), from_none], self.params
            )
        return result


@dataclass
class JSONRPCResponse(DataModelHelper):
    """A successful (non-error) response to a request."""

    id: int | str
    jsonrpc: Jsonrpc
    result: Result

    @classmethod
    def from_dict(cls, obj: Any) -> "JSONRPCResponse":
        assert isinstance(obj, dict)
        id = from_union([from_int, from_str], obj.get("id"))
        jsonrpc = Jsonrpc(obj.get("jsonrpc"))
        result = Result.from_dict(obj.get("result"))
        return JSONRPCResponse(id, jsonrpc, result)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["id"] = from_union([from_int, from_str], self.id)
        result["jsonrpc"] = to_enum(Jsonrpc, self.jsonrpc)
        result["result"] = to_class(Result, self.result)
        return result


class ListpromptsrequestMethod(Enum):
    PROMPTS_LIST = "prompts/list"


@dataclass
class ListpromptsrequestParams(DataModelHelper):
    cursor: str | None = None
    """An opaque token representing the current pagination position.
    If provided, the server should return results starting after this cursor.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ListpromptsrequestParams":
        assert isinstance(obj, dict)
        cursor = from_union([from_str, from_none], obj.get("cursor"))
        return ListpromptsrequestParams(cursor)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.cursor is not None:
            result["cursor"] = from_union([from_str, from_none], self.cursor)
        return result


@dataclass
class ListPromptsRequest(DataModelHelper):
    """Sent from the client to request a list of prompts and prompt templates the server has."""

    method: ListpromptsrequestMethod
    params: ListpromptsrequestParams | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "ListPromptsRequest":
        assert isinstance(obj, dict)
        method = ListpromptsrequestMethod(obj.get("method"))
        params = from_union([ListpromptsrequestParams.from_dict, from_none], obj.get("params"))
        return ListPromptsRequest(method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["method"] = to_enum(ListpromptsrequestMethod, self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(ListpromptsrequestParams, x), from_none], self.params
            )
        return result


@dataclass
class PromptArgument(DataModelHelper):
    """Describes an argument that a prompt can accept."""

    name: str
    """Intended for programmatic or logical use, but used as a display name in past specs or
    fallback (if title isn't present).
    """
    description: str | None = None
    """A human-readable description of the argument."""

    required: bool | None = None
    """Whether this argument must be provided."""

    title: str | None = None
    """Intended for UI and end-user contexts — optimized to be human-readable and easily
    understood,
    even by those unfamiliar with domain-specific terminology.
    
    If not provided, the name should be used for display (except for Tool,
    where `annotations.title` should be given precedence over using `name`,
    if present).
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "PromptArgument":
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        description = from_union([from_str, from_none], obj.get("description"))
        required = from_union([from_bool, from_none], obj.get("required"))
        title = from_union([from_str, from_none], obj.get("title"))
        return PromptArgument(name, description, required, title)

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
class Prompt(DataModelHelper):
    """A prompt or prompt template that the server offers."""

    name: str
    """Intended for programmatic or logical use, but used as a display name in past specs or
    fallback (if title isn't present).
    """
    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """
    arguments: list[PromptArgument] | None = None
    """A list of arguments to use for templating the prompt."""

    description: str | None = None
    """An optional description of what this prompt provides"""

    title: str | None = None
    """Intended for UI and end-user contexts — optimized to be human-readable and easily
    understood,
    even by those unfamiliar with domain-specific terminology.
    
    If not provided, the name should be used for display (except for Tool,
    where `annotations.title` should be given precedence over using `name`,
    if present).
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "Prompt":
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        arguments = from_union(
            [lambda x: from_list(PromptArgument.from_dict, x), from_none], obj.get("arguments")
        )
        description = from_union([from_str, from_none], obj.get("description"))
        title = from_union([from_str, from_none], obj.get("title"))
        return Prompt(name, meta, arguments, description, title)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["name"] = from_str(self.name)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.arguments is not None:
            result["arguments"] = from_union(
                [lambda x: from_list(lambda x: to_class(PromptArgument, x), x), from_none],
                self.arguments,
            )
        if self.description is not None:
            result["description"] = from_union([from_str, from_none], self.description)
        if self.title is not None:
            result["title"] = from_union([from_str, from_none], self.title)
        return result


@dataclass
class ListPromptsResult(DataModelHelper):
    """The server's response to a prompts/list request from the client."""

    prompts: list[Prompt]
    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """
    next_cursor: str | None = None
    """An opaque token representing the pagination position after the last returned result.
    If present, there may be more results available.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ListPromptsResult":
        assert isinstance(obj, dict)
        prompts = from_list(Prompt.from_dict, obj.get("prompts"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        next_cursor = from_union([from_str, from_none], obj.get("nextCursor"))
        return ListPromptsResult(prompts, meta, next_cursor)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["prompts"] = from_list(lambda x: to_class(Prompt, x), self.prompts)
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
class ListresourcesrequestParams(DataModelHelper):
    cursor: str | None = None
    """An opaque token representing the current pagination position.
    If provided, the server should return results starting after this cursor.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ListresourcesrequestParams":
        assert isinstance(obj, dict)
        cursor = from_union([from_str, from_none], obj.get("cursor"))
        return ListresourcesrequestParams(cursor)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.cursor is not None:
            result["cursor"] = from_union([from_str, from_none], self.cursor)
        return result


@dataclass
class ListResourcesRequest(DataModelHelper):
    """Sent from the client to request a list of resources the server has."""

    method: ListresourcesrequestMethod
    params: ListresourcesrequestParams | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "ListResourcesRequest":
        assert isinstance(obj, dict)
        method = ListresourcesrequestMethod(obj.get("method"))
        params = from_union([ListresourcesrequestParams.from_dict, from_none], obj.get("params"))
        return ListResourcesRequest(method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["method"] = to_enum(ListresourcesrequestMethod, self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(ListresourcesrequestParams, x), from_none], self.params
            )
        return result


@dataclass
class Resource(DataModelHelper):
    """A known resource that the server is capable of reading."""

    name: str
    """Intended for programmatic or logical use, but used as a display name in past specs or
    fallback (if title isn't present).
    """
    uri: str
    """The URI of this resource."""

    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """
    annotations: Annotations | None = None
    """Optional annotations for the client."""

    description: str | None = None
    """A description of what this resource represents.
    
    This can be used by clients to improve the LLM's understanding of available resources. It
    can be thought of like a "hint" to the model.
    """
    mime_type: str | None = None
    """The MIME type of this resource, if known."""

    size: int | None = None
    """The size of the raw resource content, in bytes (i.e., before base64 encoding or any
    tokenization), if known.
    
    This can be used by Hosts to display file sizes and estimate context window usage.
    """
    title: str | None = None
    """Intended for UI and end-user contexts — optimized to be human-readable and easily
    understood,
    even by those unfamiliar with domain-specific terminology.
    
    If not provided, the name should be used for display (except for Tool,
    where `annotations.title` should be given precedence over using `name`,
    if present).
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "Resource":
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        uri = from_str(obj.get("uri"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        annotations = from_union([Annotations.from_dict, from_none], obj.get("annotations"))
        description = from_union([from_str, from_none], obj.get("description"))
        mime_type = from_union([from_str, from_none], obj.get("mimeType"))
        size = from_union([from_int, from_none], obj.get("size"))
        title = from_union([from_str, from_none], obj.get("title"))
        return Resource(name, uri, meta, annotations, description, mime_type, size, title)

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
                [lambda x: to_class(Annotations, x), from_none], self.annotations
            )
        if self.description is not None:
            result["description"] = from_union([from_str, from_none], self.description)
        if self.mime_type is not None:
            result["mimeType"] = from_union([from_str, from_none], self.mime_type)
        if self.size is not None:
            result["size"] = from_union([from_int, from_none], self.size)
        if self.title is not None:
            result["title"] = from_union([from_str, from_none], self.title)
        return result


@dataclass
class ListResourcesResult(DataModelHelper):
    """The server's response to a resources/list request from the client."""

    resources: list[Resource]
    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """
    next_cursor: str | None = None
    """An opaque token representing the pagination position after the last returned result.
    If present, there may be more results available.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ListResourcesResult":
        assert isinstance(obj, dict)
        resources = from_list(Resource.from_dict, obj.get("resources"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        next_cursor = from_union([from_str, from_none], obj.get("nextCursor"))
        return ListResourcesResult(resources, meta, next_cursor)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["resources"] = from_list(lambda x: to_class(Resource, x), self.resources)
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
class ListresourcetemplatesrequestParams(DataModelHelper):
    cursor: str | None = None
    """An opaque token representing the current pagination position.
    If provided, the server should return results starting after this cursor.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ListresourcetemplatesrequestParams":
        assert isinstance(obj, dict)
        cursor = from_union([from_str, from_none], obj.get("cursor"))
        return ListresourcetemplatesrequestParams(cursor)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.cursor is not None:
            result["cursor"] = from_union([from_str, from_none], self.cursor)
        return result


@dataclass
class ListResourceTemplatesRequest(DataModelHelper):
    """Sent from the client to request a list of resource templates the server has."""

    method: ListresourcetemplatesrequestMethod
    params: ListresourcetemplatesrequestParams | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "ListResourceTemplatesRequest":
        assert isinstance(obj, dict)
        method = ListresourcetemplatesrequestMethod(obj.get("method"))
        params = from_union(
            [ListresourcetemplatesrequestParams.from_dict, from_none], obj.get("params")
        )
        return ListResourceTemplatesRequest(method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["method"] = to_enum(ListresourcetemplatesrequestMethod, self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(ListresourcetemplatesrequestParams, x), from_none], self.params
            )
        return result


@dataclass
class ResourceTemplate(DataModelHelper):
    """A template description for resources available on the server."""

    name: str
    """Intended for programmatic or logical use, but used as a display name in past specs or
    fallback (if title isn't present).
    """
    uri_template: str
    """A URI template (according to RFC 6570) that can be used to construct resource URIs."""

    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """
    annotations: Annotations | None = None
    """Optional annotations for the client."""

    description: str | None = None
    """A description of what this template is for.
    
    This can be used by clients to improve the LLM's understanding of available resources. It
    can be thought of like a "hint" to the model.
    """
    mime_type: str | None = None
    """The MIME type for all resources that match this template. This should only be included if
    all resources matching this template have the same type.
    """
    title: str | None = None
    """Intended for UI and end-user contexts — optimized to be human-readable and easily
    understood,
    even by those unfamiliar with domain-specific terminology.
    
    If not provided, the name should be used for display (except for Tool,
    where `annotations.title` should be given precedence over using `name`,
    if present).
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ResourceTemplate":
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        uri_template = from_str(obj.get("uriTemplate"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        annotations = from_union([Annotations.from_dict, from_none], obj.get("annotations"))
        description = from_union([from_str, from_none], obj.get("description"))
        mime_type = from_union([from_str, from_none], obj.get("mimeType"))
        title = from_union([from_str, from_none], obj.get("title"))
        return ResourceTemplate(
            name, uri_template, meta, annotations, description, mime_type, title
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
                [lambda x: to_class(Annotations, x), from_none], self.annotations
            )
        if self.description is not None:
            result["description"] = from_union([from_str, from_none], self.description)
        if self.mime_type is not None:
            result["mimeType"] = from_union([from_str, from_none], self.mime_type)
        if self.title is not None:
            result["title"] = from_union([from_str, from_none], self.title)
        return result


@dataclass
class ListResourceTemplatesResult(DataModelHelper):
    """The server's response to a resources/templates/list request from the client."""

    resource_templates: list[ResourceTemplate]
    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """
    next_cursor: str | None = None
    """An opaque token representing the pagination position after the last returned result.
    If present, there may be more results available.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ListResourceTemplatesResult":
        assert isinstance(obj, dict)
        resource_templates = from_list(ResourceTemplate.from_dict, obj.get("resourceTemplates"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        next_cursor = from_union([from_str, from_none], obj.get("nextCursor"))
        return ListResourceTemplatesResult(resource_templates, meta, next_cursor)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["resourceTemplates"] = from_list(
            lambda x: to_class(ResourceTemplate, x), self.resource_templates
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
class StickyMeta(DataModelHelper):
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """

    progress_token: int | str | None = None
    """If specified, the caller is requesting out-of-band progress notifications for this
    request (as represented by notifications/progress). The value of this parameter is an
    opaque token that will be attached to any subsequent notifications. The receiver is not
    obligated to provide these notifications.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "StickyMeta":
        assert isinstance(obj, dict)
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
class ListrootsrequestParams(DataModelHelper):
    meta: StickyMeta | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ListrootsrequestParams":
        assert isinstance(obj, dict)
        meta = from_union([StickyMeta.from_dict, from_none], obj.get("_meta"))
        return ListrootsrequestParams(meta)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.meta is not None:
            result["_meta"] = from_union([lambda x: to_class(StickyMeta, x), from_none], self.meta)
        return result


@dataclass
class ListRootsRequest(DataModelHelper):
    """Sent from the server to request a list of root URIs from the client. Roots allow
    servers to ask for specific directories or files to operate on. A common example
    for roots is providing a set of repositories or directories a server should operate
    on.

    This request is typically used when the server needs to understand the file system
    structure or access specific locations that the client has permission to read from.
    """

    method: ListrootsrequestMethod
    params: ListrootsrequestParams | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "ListRootsRequest":
        assert isinstance(obj, dict)
        method = ListrootsrequestMethod(obj.get("method"))
        params = from_union([ListrootsrequestParams.from_dict, from_none], obj.get("params"))
        return ListRootsRequest(method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["method"] = to_enum(ListrootsrequestMethod, self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(ListrootsrequestParams, x), from_none], self.params
            )
        return result


@dataclass
class ListRootsResult(DataModelHelper):
    """The client's response to a roots/list request from the server.
    This result contains an array of Root objects, each representing a root directory
    or file that the server can operate on.
    """

    roots: list[Root]
    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ListRootsResult":
        assert isinstance(obj, dict)
        roots = from_list(Root.from_dict, obj.get("roots"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        return ListRootsResult(roots, meta)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["roots"] = from_list(lambda x: to_class(Root, x), self.roots)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        return result


class ListtoolsrequestMethod(Enum):
    TOOLS_LIST = "tools/list"


@dataclass
class ListtoolsrequestParams(DataModelHelper):
    cursor: str | None = None
    """An opaque token representing the current pagination position.
    If provided, the server should return results starting after this cursor.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ListtoolsrequestParams":
        assert isinstance(obj, dict)
        cursor = from_union([from_str, from_none], obj.get("cursor"))
        return ListtoolsrequestParams(cursor)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.cursor is not None:
            result["cursor"] = from_union([from_str, from_none], self.cursor)
        return result


@dataclass
class ListToolsRequest(DataModelHelper):
    """Sent from the client to request a list of tools the server has."""

    method: ListtoolsrequestMethod
    params: ListtoolsrequestParams | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "ListToolsRequest":
        assert isinstance(obj, dict)
        method = ListtoolsrequestMethod(obj.get("method"))
        params = from_union([ListtoolsrequestParams.from_dict, from_none], obj.get("params"))
        return ListToolsRequest(method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["method"] = to_enum(ListtoolsrequestMethod, self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(ListtoolsrequestParams, x), from_none], self.params
            )
        return result


@dataclass
class ToolAnnotations(DataModelHelper):
    """Optional additional tool information.

    Display name precedence order is: title, annotations.title, then name.

    Additional properties describing a Tool to clients.

    NOTE: all properties in ToolAnnotations are **hints**.
    They are not guaranteed to provide a faithful description of
    tool behavior (including descriptive properties like `title`).

    Clients should never make tool use decisions based on ToolAnnotations
    received from untrusted servers.
    """

    destructive_hint: bool | None = None
    """If true, the tool may perform destructive updates to its environment.
    If false, the tool performs only additive updates.
    
    (This property is meaningful only when `readOnlyHint == false`)
    
    Default: true
    """
    idempotent_hint: bool | None = None
    """If true, calling the tool repeatedly with the same arguments
    will have no additional effect on the its environment.
    
    (This property is meaningful only when `readOnlyHint == false`)
    
    Default: false
    """
    open_world_hint: bool | None = None
    """If true, this tool may interact with an "open world" of external
    entities. If false, the tool's domain of interaction is closed.
    For example, the world of a web search tool is open, whereas that
    of a memory tool is not.
    
    Default: true
    """
    read_only_hint: bool | None = None
    """If true, the tool does not modify its environment.
    
    Default: false
    """
    title: str | None = None
    """A human-readable title for the tool."""

    @classmethod
    def from_dict(cls, obj: Any) -> "ToolAnnotations":
        assert isinstance(obj, dict)
        destructive_hint = from_union([from_bool, from_none], obj.get("destructiveHint"))
        idempotent_hint = from_union([from_bool, from_none], obj.get("idempotentHint"))
        open_world_hint = from_union([from_bool, from_none], obj.get("openWorldHint"))
        read_only_hint = from_union([from_bool, from_none], obj.get("readOnlyHint"))
        title = from_union([from_str, from_none], obj.get("title"))
        return ToolAnnotations(
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


@dataclass
class InputSchema(DataModelHelper):
    """A JSON Schema object defining the expected parameters for the tool."""

    type: RequestedSchemaType
    properties: dict[str, dict[str, Any]] | None = None
    required: list[str] | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "InputSchema":
        assert isinstance(obj, dict)
        type = RequestedSchemaType(obj.get("type"))
        properties = from_union(
            [lambda x: from_dict(lambda x: from_dict(lambda x: x, x), x), from_none],
            obj.get("properties"),
        )
        required = from_union([lambda x: from_list(from_str, x), from_none], obj.get("required"))
        return InputSchema(type, properties, required)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["type"] = to_enum(RequestedSchemaType, self.type)
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
    """

    type: RequestedSchemaType
    properties: dict[str, dict[str, Any]] | None = None
    required: list[str] | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "OutputSchema":
        assert isinstance(obj, dict)
        type = RequestedSchemaType(obj.get("type"))
        properties = from_union(
            [lambda x: from_dict(lambda x: from_dict(lambda x: x, x), x), from_none],
            obj.get("properties"),
        )
        required = from_union([lambda x: from_list(from_str, x), from_none], obj.get("required"))
        return OutputSchema(type, properties, required)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["type"] = to_enum(RequestedSchemaType, self.type)
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
class Tool(DataModelHelper):
    """Definition for a tool the client can call."""

    input_schema: InputSchema
    """A JSON Schema object defining the expected parameters for the tool."""

    name: str
    """Intended for programmatic or logical use, but used as a display name in past specs or
    fallback (if title isn't present).
    """
    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """
    annotations: ToolAnnotations | None = None
    """Optional additional tool information.
    
    Display name precedence order is: title, annotations.title, then name.
    """
    description: str | None = None
    """A human-readable description of the tool.
    
    This can be used by clients to improve the LLM's understanding of available tools. It can
    be thought of like a "hint" to the model.
    """
    output_schema: OutputSchema | None = None
    """An optional JSON Schema object defining the structure of the tool's output returned in
    the structuredContent field of a CallToolResult.
    """
    title: str | None = None
    """Intended for UI and end-user contexts — optimized to be human-readable and easily
    understood,
    even by those unfamiliar with domain-specific terminology.
    
    If not provided, the name should be used for display (except for Tool,
    where `annotations.title` should be given precedence over using `name`,
    if present).
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "Tool":
        assert isinstance(obj, dict)
        input_schema = InputSchema.from_dict(obj.get("inputSchema"))
        name = from_str(obj.get("name"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        annotations = from_union([ToolAnnotations.from_dict, from_none], obj.get("annotations"))
        description = from_union([from_str, from_none], obj.get("description"))
        output_schema = from_union([OutputSchema.from_dict, from_none], obj.get("outputSchema"))
        title = from_union([from_str, from_none], obj.get("title"))
        return Tool(input_schema, name, meta, annotations, description, output_schema, title)

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
                [lambda x: to_class(ToolAnnotations, x), from_none], self.annotations
            )
        if self.description is not None:
            result["description"] = from_union([from_str, from_none], self.description)
        if self.output_schema is not None:
            result["outputSchema"] = from_union(
                [lambda x: to_class(OutputSchema, x), from_none], self.output_schema
            )
        if self.title is not None:
            result["title"] = from_union([from_str, from_none], self.title)
        return result


@dataclass
class ListToolsResult(DataModelHelper):
    """The server's response to a tools/list request from the client."""

    tools: list[Tool]
    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """
    next_cursor: str | None = None
    """An opaque token representing the pagination position after the last returned result.
    If present, there may be more results available.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ListToolsResult":
        assert isinstance(obj, dict)
        tools = from_list(Tool.from_dict, obj.get("tools"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        next_cursor = from_union([from_str, from_none], obj.get("nextCursor"))
        return ListToolsResult(tools, meta, next_cursor)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["tools"] = from_list(lambda x: to_class(Tool, x), self.tools)
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
    data: Any
    """The data to be logged, such as a string message or an object. Any JSON serializable type
    is allowed here.
    """
    level: LoggingLevel
    """The severity of this log message."""

    logger: str | None = None
    """An optional name of the logger issuing this message."""

    @classmethod
    def from_dict(cls, obj: Any) -> "LoggingmessagenotificationParams":
        assert isinstance(obj, dict)
        data = obj.get("data")
        level = LoggingLevel(obj.get("level"))
        logger = from_union([from_str, from_none], obj.get("logger"))
        return LoggingmessagenotificationParams(data, level, logger)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["data"] = self.data
        result["level"] = to_enum(LoggingLevel, self.level)
        if self.logger is not None:
            result["logger"] = from_union([from_str, from_none], self.logger)
        return result


@dataclass
class LoggingMessageNotification(DataModelHelper):
    """Notification of a log message passed from server to client. If no logging/setLevel
    request has been sent from the client, the server MAY decide which messages to send
    automatically.
    """

    method: LoggingmessagenotificationMethod
    params: LoggingmessagenotificationParams

    @classmethod
    def from_dict(cls, obj: Any) -> "LoggingMessageNotification":
        assert isinstance(obj, dict)
        method = LoggingmessagenotificationMethod(obj.get("method"))
        params = LoggingmessagenotificationParams.from_dict(obj.get("params"))
        return LoggingMessageNotification(method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["method"] = to_enum(LoggingmessagenotificationMethod, self.method)
        result["params"] = to_class(LoggingmessagenotificationParams, self.params)
        return result


@dataclass
class NotificationParams(DataModelHelper):
    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "NotificationParams":
        assert isinstance(obj, dict)
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        return NotificationParams(meta)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        return result


@dataclass
class Notification(DataModelHelper):
    method: str
    params: NotificationParams | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "Notification":
        assert isinstance(obj, dict)
        method = from_str(obj.get("method"))
        params = from_union([NotificationParams.from_dict, from_none], obj.get("params"))
        return Notification(method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["method"] = from_str(self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(NotificationParams, x), from_none], self.params
            )
        return result


class NumberschemaType(Enum):
    INTEGER = "integer"
    NUMBER = "number"


@dataclass
class NumberSchema(DataModelHelper):
    type: NumberschemaType
    description: str | None = None
    maximum: int | None = None
    minimum: int | None = None
    title: str | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "NumberSchema":
        assert isinstance(obj, dict)
        type = NumberschemaType(obj.get("type"))
        description = from_union([from_str, from_none], obj.get("description"))
        maximum = from_union([from_int, from_none], obj.get("maximum"))
        minimum = from_union([from_int, from_none], obj.get("minimum"))
        title = from_union([from_str, from_none], obj.get("title"))
        return NumberSchema(type, description, maximum, minimum, title)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["type"] = to_enum(NumberschemaType, self.type)
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
class PaginatedrequestParams(DataModelHelper):
    cursor: str | None = None
    """An opaque token representing the current pagination position.
    If provided, the server should return results starting after this cursor.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "PaginatedrequestParams":
        assert isinstance(obj, dict)
        cursor = from_union([from_str, from_none], obj.get("cursor"))
        return PaginatedrequestParams(cursor)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.cursor is not None:
            result["cursor"] = from_union([from_str, from_none], self.cursor)
        return result


@dataclass
class PaginatedRequest(DataModelHelper):
    method: str
    params: PaginatedrequestParams | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "PaginatedRequest":
        assert isinstance(obj, dict)
        method = from_str(obj.get("method"))
        params = from_union([PaginatedrequestParams.from_dict, from_none], obj.get("params"))
        return PaginatedRequest(method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["method"] = from_str(self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(PaginatedrequestParams, x), from_none], self.params
            )
        return result


@dataclass
class PaginatedResult(DataModelHelper):
    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """
    next_cursor: str | None = None
    """An opaque token representing the pagination position after the last returned result.
    If present, there may be more results available.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "PaginatedResult":
        assert isinstance(obj, dict)
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        next_cursor = from_union([from_str, from_none], obj.get("nextCursor"))
        return PaginatedResult(meta, next_cursor)

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
class PingrequestParams(DataModelHelper):
    meta: PurpleMeta | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "PingrequestParams":
        assert isinstance(obj, dict)
        meta = from_union([PurpleMeta.from_dict, from_none], obj.get("_meta"))
        return PingrequestParams(meta)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.meta is not None:
            result["_meta"] = from_union([lambda x: to_class(PurpleMeta, x), from_none], self.meta)
        return result


@dataclass
class PingRequest(DataModelHelper):
    """A ping, issued by either the server or the client, to check that the other party is still
    alive. The receiver must promptly respond, or else may be disconnected.
    """

    method: PingrequestMethod
    params: PingrequestParams | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "PingRequest":
        assert isinstance(obj, dict)
        method = PingrequestMethod(obj.get("method"))
        params = from_union([PingrequestParams.from_dict, from_none], obj.get("params"))
        return PingRequest(method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["method"] = to_enum(PingrequestMethod, self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(PingrequestParams, x), from_none], self.params
            )
        return result


class ProgressnotificationMethod(Enum):
    NOTIFICATIONS_PROGRESS = "notifications/progress"


@dataclass
class ProgressnotificationParams(DataModelHelper):
    progress: float
    """The progress thus far. This should increase every time progress is made, even if the
    total is unknown.
    """
    progress_token: int | str
    """The progress token which was given in the initial request, used to associate this
    notification with the request that is proceeding.
    """
    message: str | None = None
    """An optional message describing the current progress."""

    total: float | None = None
    """Total number of items to process (or total progress required), if known."""

    @classmethod
    def from_dict(cls, obj: Any) -> "ProgressnotificationParams":
        assert isinstance(obj, dict)
        progress = from_float(obj.get("progress"))
        progress_token = from_union([from_int, from_str], obj.get("progressToken"))
        message = from_union([from_str, from_none], obj.get("message"))
        total = from_union([from_float, from_none], obj.get("total"))
        return ProgressnotificationParams(progress, progress_token, message, total)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["progress"] = to_float(self.progress)
        result["progressToken"] = from_union([from_int, from_str], self.progress_token)
        if self.message is not None:
            result["message"] = from_union([from_str, from_none], self.message)
        if self.total is not None:
            result["total"] = from_union([to_float, from_none], self.total)
        return result


@dataclass
class ProgressNotification(DataModelHelper):
    """An out-of-band notification used to inform the receiver of a progress update for a
    long-running request.
    """

    method: ProgressnotificationMethod
    params: ProgressnotificationParams

    @classmethod
    def from_dict(cls, obj: Any) -> "ProgressNotification":
        assert isinstance(obj, dict)
        method = ProgressnotificationMethod(obj.get("method"))
        params = ProgressnotificationParams.from_dict(obj.get("params"))
        return ProgressNotification(method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["method"] = to_enum(ProgressnotificationMethod, self.method)
        result["params"] = to_class(ProgressnotificationParams, self.params)
        return result


class PromptlistchangednotificationMethod(Enum):
    NOTIFICATIONS_PROMPTS_LIST_CHANGED = "notifications/prompts/list_changed"


@dataclass
class PromptlistchangednotificationParams(DataModelHelper):
    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "PromptlistchangednotificationParams":
        assert isinstance(obj, dict)
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        return PromptlistchangednotificationParams(meta)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        return result


@dataclass
class PromptListChangedNotification(DataModelHelper):
    """An optional notification from the server to the client, informing it that the list of
    prompts it offers has changed. This may be issued by servers without any previous
    subscription from the client.
    """

    method: PromptlistchangednotificationMethod
    params: PromptlistchangednotificationParams | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "PromptListChangedNotification":
        assert isinstance(obj, dict)
        method = PromptlistchangednotificationMethod(obj.get("method"))
        params = from_union(
            [PromptlistchangednotificationParams.from_dict, from_none], obj.get("params")
        )
        return PromptListChangedNotification(method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["method"] = to_enum(PromptlistchangednotificationMethod, self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(PromptlistchangednotificationParams, x), from_none], self.params
            )
        return result


class PromptreferenceType(Enum):
    REF_PROMPT = "ref/prompt"


@dataclass
class PromptReference(DataModelHelper):
    """Identifies a prompt."""

    name: str
    """Intended for programmatic or logical use, but used as a display name in past specs or
    fallback (if title isn't present).
    """
    type: PromptreferenceType
    title: str | None = None
    """Intended for UI and end-user contexts — optimized to be human-readable and easily
    understood,
    even by those unfamiliar with domain-specific terminology.
    
    If not provided, the name should be used for display (except for Tool,
    where `annotations.title` should be given precedence over using `name`,
    if present).
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "PromptReference":
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        type = PromptreferenceType(obj.get("type"))
        title = from_union([from_str, from_none], obj.get("title"))
        return PromptReference(name, type, title)

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
class ReadresourcerequestParams(DataModelHelper):
    uri: str
    """The URI of the resource to read. The URI can use any protocol; it is up to the server how
    to interpret it.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ReadresourcerequestParams":
        assert isinstance(obj, dict)
        uri = from_str(obj.get("uri"))
        return ReadresourcerequestParams(uri)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["uri"] = from_str(self.uri)
        return result


@dataclass
class ReadResourceRequest(DataModelHelper):
    """Sent from the client to the server, to read a specific resource URI."""

    method: ReadresourcerequestMethod
    params: ReadresourcerequestParams

    @classmethod
    def from_dict(cls, obj: Any) -> "ReadResourceRequest":
        assert isinstance(obj, dict)
        method = ReadresourcerequestMethod(obj.get("method"))
        params = ReadresourcerequestParams.from_dict(obj.get("params"))
        return ReadResourceRequest(method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["method"] = to_enum(ReadresourcerequestMethod, self.method)
        result["params"] = to_class(ReadresourcerequestParams, self.params)
        return result


@dataclass
class ReadResourceResult(DataModelHelper):
    """The server's response to a resources/read request from the client."""

    contents: list[ResourceContents]
    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ReadResourceResult":
        assert isinstance(obj, dict)
        contents = from_list(ResourceContents.from_dict, obj.get("contents"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        return ReadResourceResult(contents, meta)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["contents"] = from_list(lambda x: to_class(ResourceContents, x), self.contents)
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        return result


@dataclass
class IndigoMeta(DataModelHelper):
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """

    progress_token: int | str | None = None
    """If specified, the caller is requesting out-of-band progress notifications for this
    request (as represented by notifications/progress). The value of this parameter is an
    opaque token that will be attached to any subsequent notifications. The receiver is not
    obligated to provide these notifications.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "IndigoMeta":
        assert isinstance(obj, dict)
        progress_token = from_union([from_int, from_str, from_none], obj.get("progressToken"))
        return IndigoMeta(progress_token)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.progress_token is not None:
            result["progressToken"] = from_union(
                [from_int, from_str, from_none], self.progress_token
            )
        return result


@dataclass
class RequestParams(DataModelHelper):
    meta: IndigoMeta | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "RequestParams":
        assert isinstance(obj, dict)
        meta = from_union([IndigoMeta.from_dict, from_none], obj.get("_meta"))
        return RequestParams(meta)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.meta is not None:
            result["_meta"] = from_union([lambda x: to_class(IndigoMeta, x), from_none], self.meta)
        return result


@dataclass
class Request(DataModelHelper):
    method: str
    params: RequestParams | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "Request":
        assert isinstance(obj, dict)
        method = from_str(obj.get("method"))
        params = from_union([RequestParams.from_dict, from_none], obj.get("params"))
        return Request(method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["method"] = from_str(self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(RequestParams, x), from_none], self.params
            )
        return result


@dataclass
class ResourcecontentsClass(DataModelHelper):
    """The contents of a specific resource or sub-resource."""

    uri: str
    """The URI of this resource."""

    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """
    mime_type: str | None = None
    """The MIME type of this resource, if known."""

    @classmethod
    def from_dict(cls, obj: Any) -> "ResourcecontentsClass":
        assert isinstance(obj, dict)
        uri = from_str(obj.get("uri"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        mime_type = from_union([from_str, from_none], obj.get("mimeType"))
        return ResourcecontentsClass(uri, meta, mime_type)

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
class ResourceLink(DataModelHelper):
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

    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """
    annotations: Annotations | None = None
    """Optional annotations for the client."""

    description: str | None = None
    """A description of what this resource represents.
    
    This can be used by clients to improve the LLM's understanding of available resources. It
    can be thought of like a "hint" to the model.
    """
    mime_type: str | None = None
    """The MIME type of this resource, if known."""

    size: int | None = None
    """The size of the raw resource content, in bytes (i.e., before base64 encoding or any
    tokenization), if known.
    
    This can be used by Hosts to display file sizes and estimate context window usage.
    """
    title: str | None = None
    """Intended for UI and end-user contexts — optimized to be human-readable and easily
    understood,
    even by those unfamiliar with domain-specific terminology.
    
    If not provided, the name should be used for display (except for Tool,
    where `annotations.title` should be given precedence over using `name`,
    if present).
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ResourceLink":
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        type = ResourcelinkType(obj.get("type"))
        uri = from_str(obj.get("uri"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        annotations = from_union([Annotations.from_dict, from_none], obj.get("annotations"))
        description = from_union([from_str, from_none], obj.get("description"))
        mime_type = from_union([from_str, from_none], obj.get("mimeType"))
        size = from_union([from_int, from_none], obj.get("size"))
        title = from_union([from_str, from_none], obj.get("title"))
        return ResourceLink(name, type, uri, meta, annotations, description, mime_type, size, title)

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
                [lambda x: to_class(Annotations, x), from_none], self.annotations
            )
        if self.description is not None:
            result["description"] = from_union([from_str, from_none], self.description)
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
class ResourcelistchangednotificationParams(DataModelHelper):
    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ResourcelistchangednotificationParams":
        assert isinstance(obj, dict)
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        return ResourcelistchangednotificationParams(meta)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        return result


@dataclass
class ResourceListChangedNotification(DataModelHelper):
    """An optional notification from the server to the client, informing it that the list of
    resources it can read from has changed. This may be issued by servers without any
    previous subscription from the client.
    """

    method: ResourcelistchangednotificationMethod
    params: ResourcelistchangednotificationParams | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "ResourceListChangedNotification":
        assert isinstance(obj, dict)
        method = ResourcelistchangednotificationMethod(obj.get("method"))
        params = from_union(
            [ResourcelistchangednotificationParams.from_dict, from_none], obj.get("params")
        )
        return ResourceListChangedNotification(method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["method"] = to_enum(ResourcelistchangednotificationMethod, self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(ResourcelistchangednotificationParams, x), from_none],
                self.params,
            )
        return result


class ResourcetemplatereferenceType(Enum):
    REF_RESOURCE = "ref/resource"


@dataclass
class ResourceTemplateReference(DataModelHelper):
    """A reference to a resource or resource template definition."""

    type: ResourcetemplatereferenceType
    uri: str
    """The URI or URI template of the resource."""

    @classmethod
    def from_dict(cls, obj: Any) -> "ResourceTemplateReference":
        assert isinstance(obj, dict)
        type = ResourcetemplatereferenceType(obj.get("type"))
        uri = from_str(obj.get("uri"))
        return ResourceTemplateReference(type, uri)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["type"] = to_enum(ResourcetemplatereferenceType, self.type)
        result["uri"] = from_str(self.uri)
        return result


class ResourceupdatednotificationMethod(Enum):
    NOTIFICATIONS_RESOURCES_UPDATED = "notifications/resources/updated"


@dataclass
class ResourceupdatednotificationParams(DataModelHelper):
    uri: str
    """The URI of the resource that has been updated. This might be a sub-resource of the one
    that the client actually subscribed to.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ResourceupdatednotificationParams":
        assert isinstance(obj, dict)
        uri = from_str(obj.get("uri"))
        return ResourceupdatednotificationParams(uri)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["uri"] = from_str(self.uri)
        return result


@dataclass
class ResourceUpdatedNotification(DataModelHelper):
    """A notification from the server to the client, informing it that a resource has changed
    and may need to be read again. This should only be sent if the client previously sent a
    resources/subscribe request.
    """

    method: ResourceupdatednotificationMethod
    params: ResourceupdatednotificationParams

    @classmethod
    def from_dict(cls, obj: Any) -> "ResourceUpdatedNotification":
        assert isinstance(obj, dict)
        method = ResourceupdatednotificationMethod(obj.get("method"))
        params = ResourceupdatednotificationParams.from_dict(obj.get("params"))
        return ResourceUpdatedNotification(method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["method"] = to_enum(ResourceupdatednotificationMethod, self.method)
        result["params"] = to_class(ResourceupdatednotificationParams, self.params)
        return result


class RootslistchangednotificationMethod(Enum):
    NOTIFICATIONS_ROOTS_LIST_CHANGED = "notifications/roots/list_changed"


@dataclass
class RootslistchangednotificationParams(DataModelHelper):
    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "RootslistchangednotificationParams":
        assert isinstance(obj, dict)
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        return RootslistchangednotificationParams(meta)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        return result


@dataclass
class RootsListChangedNotification(DataModelHelper):
    """A notification from the client to the server, informing it that the list of roots has
    changed.
    This notification should be sent whenever the client adds, removes, or modifies any root.
    The server should then request an updated list of roots using the ListRootsRequest.
    """

    method: RootslistchangednotificationMethod
    params: RootslistchangednotificationParams | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "RootsListChangedNotification":
        assert isinstance(obj, dict)
        method = RootslistchangednotificationMethod(obj.get("method"))
        params = from_union(
            [RootslistchangednotificationParams.from_dict, from_none], obj.get("params")
        )
        return RootsListChangedNotification(method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["method"] = to_enum(RootslistchangednotificationMethod, self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(RootslistchangednotificationParams, x), from_none], self.params
            )
        return result


class ServerNotificationMethod(Enum):
    NOTIFICATIONS_CANCELLED = "notifications/cancelled"
    NOTIFICATIONS_MESSAGE = "notifications/message"
    NOTIFICATIONS_PROGRESS = "notifications/progress"
    NOTIFICATIONS_PROMPTS_LIST_CHANGED = "notifications/prompts/list_changed"
    NOTIFICATIONS_RESOURCES_LIST_CHANGED = "notifications/resources/list_changed"
    NOTIFICATIONS_RESOURCES_UPDATED = "notifications/resources/updated"
    NOTIFICATIONS_TOOLS_LIST_CHANGED = "notifications/tools/list_changed"


@dataclass
class ServerNotificationParams(DataModelHelper):
    data: Any
    """The data to be logged, such as a string message or an object. Any JSON serializable type
    is allowed here.
    """
    reason: str | None = None
    """An optional string describing the reason for the cancellation. This MAY be logged or
    presented to the user.
    """
    request_id: int | str | None = None
    """The ID of the request to cancel.
    
    This MUST correspond to the ID of a request previously issued in the same direction.
    """
    message: str | None = None
    """An optional message describing the current progress."""

    progress: float | None = None
    """The progress thus far. This should increase every time progress is made, even if the
    total is unknown.
    """
    progress_token: int | str | None = None
    """The progress token which was given in the initial request, used to associate this
    notification with the request that is proceeding.
    """
    total: float | None = None
    """Total number of items to process (or total progress required), if known."""

    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """
    uri: str | None = None
    """The URI of the resource that has been updated. This might be a sub-resource of the one
    that the client actually subscribed to.
    """
    level: LoggingLevel | None = None
    """The severity of this log message."""

    logger: str | None = None
    """An optional name of the logger issuing this message."""

    @classmethod
    def from_dict(cls, obj: Any) -> "ServerNotificationParams":
        assert isinstance(obj, dict)
        reason = from_union([from_str, from_none], obj.get("reason"))
        request_id = from_union([from_int, from_str, from_none], obj.get("requestId"))
        message = from_union([from_str, from_none], obj.get("message"))
        progress = from_union([from_float, from_none], obj.get("progress"))
        progress_token = from_union([from_int, from_str, from_none], obj.get("progressToken"))
        total = from_union([from_float, from_none], obj.get("total"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        uri = from_union([from_str, from_none], obj.get("uri"))
        data = obj.get("data")
        level = from_union([LoggingLevel, from_none], obj.get("level"))
        logger = from_union([from_str, from_none], obj.get("logger"))
        return ServerNotificationParams(
            reason,
            request_id,
            message,
            progress,
            progress_token,
            total,
            meta,
            uri,
            data,
            level,
            logger,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
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
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        if self.uri is not None:
            result["uri"] = from_union([from_str, from_none], self.uri)
        if self.data is not None:
            result["data"] = self.data
        if self.level is not None:
            result["level"] = from_union(
                [lambda x: to_enum(LoggingLevel, x), from_none], self.level
            )
        if self.logger is not None:
            result["logger"] = from_union([from_str, from_none], self.logger)
        return result


@dataclass
class ServerNotification(DataModelHelper):
    """This notification can be sent by either side to indicate that it is cancelling a
    previously-issued request.

    The request SHOULD still be in-flight, but due to communication latency, it is always
    possible that this notification MAY arrive after the request has already finished.

    This notification indicates that the result will be unused, so any associated processing
    SHOULD cease.

    A client MUST NOT attempt to cancel its `initialize` request.

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

    Notification of a log message passed from server to client. If no logging/setLevel
    request has been sent from the client, the server MAY decide which messages to send
    automatically.
    """

    method: ServerNotificationMethod
    params: ServerNotificationParams | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "ServerNotification":
        assert isinstance(obj, dict)
        method = ServerNotificationMethod(obj.get("method"))
        params = from_union([ServerNotificationParams.from_dict, from_none], obj.get("params"))
        return ServerNotification(method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["method"] = to_enum(ServerNotificationMethod, self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(ServerNotificationParams, x), from_none], self.params
            )
        return result


class ServerRequestMethod(Enum):
    ELICITATION_CREATE = "elicitation/create"
    PING = "ping"
    ROOTS_LIST = "roots/list"
    SAMPLING_CREATE_MESSAGE = "sampling/createMessage"


@dataclass
class IndecentMeta(DataModelHelper):
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """

    progress_token: int | str | None = None
    """If specified, the caller is requesting out-of-band progress notifications for this
    request (as represented by notifications/progress). The value of this parameter is an
    opaque token that will be attached to any subsequent notifications. The receiver is not
    obligated to provide these notifications.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "IndecentMeta":
        assert isinstance(obj, dict)
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
class ServerRequestParams(DataModelHelper):
    meta: IndecentMeta | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """
    include_context: IncludeContext | None = None
    """A request to include context from one or more MCP servers (including the caller), to be
    attached to the prompt. The client MAY ignore this request.
    """
    max_tokens: int | None = None
    """The maximum number of tokens to sample, as requested by the server. The client MAY choose
    to sample fewer tokens than requested.
    """
    messages: list[SamplingMessage] | None = None
    metadata: dict[str, Any] | None = None
    """Optional metadata to pass through to the LLM provider. The format of this metadata is
    provider-specific.
    """
    model_preferences: ModelPreferences | None = None
    """The server's preferences for which model to select. The client MAY ignore these
    preferences.
    """
    stop_sequences: list[str] | None = None
    system_prompt: str | None = None
    """An optional system prompt the server wants to use for sampling. The client MAY modify or
    omit this prompt.
    """
    temperature: float | None = None
    message: str | None = None
    """The message to present to the user."""

    requested_schema: RequestedSchema | None = None
    """A restricted subset of JSON Schema.
    Only top-level properties are allowed, without nesting.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ServerRequestParams":
        assert isinstance(obj, dict)
        meta = from_union([IndecentMeta.from_dict, from_none], obj.get("_meta"))
        include_context = from_union([IncludeContext, from_none], obj.get("includeContext"))
        max_tokens = from_union([from_int, from_none], obj.get("maxTokens"))
        messages = from_union(
            [lambda x: from_list(SamplingMessage.from_dict, x), from_none], obj.get("messages")
        )
        metadata = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("metadata"))
        model_preferences = from_union(
            [ModelPreferences.from_dict, from_none], obj.get("modelPreferences")
        )
        stop_sequences = from_union(
            [lambda x: from_list(from_str, x), from_none], obj.get("stopSequences")
        )
        system_prompt = from_union([from_str, from_none], obj.get("systemPrompt"))
        temperature = from_union([from_float, from_none], obj.get("temperature"))
        message = from_union([from_str, from_none], obj.get("message"))
        requested_schema = from_union(
            [RequestedSchema.from_dict, from_none], obj.get("requestedSchema")
        )
        return ServerRequestParams(
            meta,
            include_context,
            max_tokens,
            messages,
            metadata,
            model_preferences,
            stop_sequences,
            system_prompt,
            temperature,
            message,
            requested_schema,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: to_class(IndecentMeta, x), from_none], self.meta
            )
        if self.include_context is not None:
            result["includeContext"] = from_union(
                [lambda x: to_enum(IncludeContext, x), from_none], self.include_context
            )
        if self.max_tokens is not None:
            result["maxTokens"] = from_union([from_int, from_none], self.max_tokens)
        if self.messages is not None:
            result["messages"] = from_union(
                [lambda x: from_list(lambda x: to_class(SamplingMessage, x), x), from_none],
                self.messages,
            )
        if self.metadata is not None:
            result["metadata"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.metadata
            )
        if self.model_preferences is not None:
            result["modelPreferences"] = from_union(
                [lambda x: to_class(ModelPreferences, x), from_none], self.model_preferences
            )
        if self.stop_sequences is not None:
            result["stopSequences"] = from_union(
                [lambda x: from_list(from_str, x), from_none], self.stop_sequences
            )
        if self.system_prompt is not None:
            result["systemPrompt"] = from_union([from_str, from_none], self.system_prompt)
        if self.temperature is not None:
            result["temperature"] = from_union([to_float, from_none], self.temperature)
        if self.message is not None:
            result["message"] = from_union([from_str, from_none], self.message)
        if self.requested_schema is not None:
            result["requestedSchema"] = from_union(
                [lambda x: to_class(RequestedSchema, x), from_none], self.requested_schema
            )
        return result


@dataclass
class ServerRequest(DataModelHelper):
    """A ping, issued by either the server or the client, to check that the other party is still
    alive. The receiver must promptly respond, or else may be disconnected.

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

    method: ServerRequestMethod
    params: ServerRequestParams | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "ServerRequest":
        assert isinstance(obj, dict)
        method = ServerRequestMethod(obj.get("method"))
        params = from_union([ServerRequestParams.from_dict, from_none], obj.get("params"))
        return ServerRequest(method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["method"] = to_enum(ServerRequestMethod, self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(ServerRequestParams, x), from_none], self.params
            )
        return result


@dataclass
class ServerResult(DataModelHelper):
    """After receiving an initialize request from the client, the server sends this response.

    The server's response to a resources/list request from the client.

    The server's response to a resources/templates/list request from the client.

    The server's response to a resources/read request from the client.

    The server's response to a prompts/list request from the client.

    The server's response to a prompts/get request from the client.

    The server's response to a tools/list request from the client.

    The server's response to a tool call.

    The server's response to a completion/complete request
    """

    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """
    capabilities: ServerCapabilities | None = None
    instructions: str | None = None
    """Instructions describing how to use the server and its features.
    
    This can be used by clients to improve the LLM's understanding of available tools,
    resources, etc. It can be thought of like a "hint" to the model. For example, this
    information MAY be added to the system prompt.
    """
    protocol_version: str | None = None
    """The version of the Model Context Protocol that the server wants to use. This may not
    match the version that the client requested. If the client cannot support this version,
    it MUST disconnect.
    """
    server_info: Implementation | None = None
    next_cursor: str | None = None
    """An opaque token representing the pagination position after the last returned result.
    If present, there may be more results available.
    """
    resources: list[Resource] | None = None
    resource_templates: list[ResourceTemplate] | None = None
    contents: list[ResourceContents] | None = None
    prompts: list[Prompt] | None = None
    description: str | None = None
    """An optional description for the prompt."""

    messages: list[PromptMessage] | None = None
    tools: list[Tool] | None = None
    content: list[ContentBlock] | None = None
    """A list of content objects that represent the unstructured result of the tool call."""

    is_error: bool | None = None
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
    structured_content: dict[str, Any] | None = None
    """An optional JSON object that represents the structured result of the tool call."""

    completion: Completion | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "ServerResult":
        assert isinstance(obj, dict)
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        capabilities = from_union(
            [ServerCapabilities.from_dict, from_none], obj.get("capabilities")
        )
        instructions = from_union([from_str, from_none], obj.get("instructions"))
        protocol_version = from_union([from_str, from_none], obj.get("protocolVersion"))
        server_info = from_union([Implementation.from_dict, from_none], obj.get("serverInfo"))
        next_cursor = from_union([from_str, from_none], obj.get("nextCursor"))
        resources = from_union(
            [lambda x: from_list(Resource.from_dict, x), from_none], obj.get("resources")
        )
        resource_templates = from_union(
            [lambda x: from_list(ResourceTemplate.from_dict, x), from_none],
            obj.get("resourceTemplates"),
        )
        contents = from_union(
            [lambda x: from_list(ResourceContents.from_dict, x), from_none], obj.get("contents")
        )
        prompts = from_union(
            [lambda x: from_list(Prompt.from_dict, x), from_none], obj.get("prompts")
        )
        description = from_union([from_str, from_none], obj.get("description"))
        messages = from_union(
            [lambda x: from_list(PromptMessage.from_dict, x), from_none], obj.get("messages")
        )
        tools = from_union([lambda x: from_list(Tool.from_dict, x), from_none], obj.get("tools"))
        content = from_union(
            [lambda x: from_list(ContentBlock.from_dict, x), from_none], obj.get("content")
        )
        is_error = from_union([from_bool, from_none], obj.get("isError"))
        structured_content = from_union(
            [lambda x: from_dict(lambda x: x, x), from_none], obj.get("structuredContent")
        )
        completion = from_union([Completion.from_dict, from_none], obj.get("completion"))
        return ServerResult(
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
                [lambda x: to_class(ServerCapabilities, x), from_none], self.capabilities
            )
        if self.instructions is not None:
            result["instructions"] = from_union([from_str, from_none], self.instructions)
        if self.protocol_version is not None:
            result["protocolVersion"] = from_union([from_str, from_none], self.protocol_version)
        if self.server_info is not None:
            result["serverInfo"] = from_union(
                [lambda x: to_class(Implementation, x), from_none], self.server_info
            )
        if self.next_cursor is not None:
            result["nextCursor"] = from_union([from_str, from_none], self.next_cursor)
        if self.resources is not None:
            result["resources"] = from_union(
                [lambda x: from_list(lambda x: to_class(Resource, x), x), from_none], self.resources
            )
        if self.resource_templates is not None:
            result["resourceTemplates"] = from_union(
                [lambda x: from_list(lambda x: to_class(ResourceTemplate, x), x), from_none],
                self.resource_templates,
            )
        if self.contents is not None:
            result["contents"] = from_union(
                [lambda x: from_list(lambda x: to_class(ResourceContents, x), x), from_none],
                self.contents,
            )
        if self.prompts is not None:
            result["prompts"] = from_union(
                [lambda x: from_list(lambda x: to_class(Prompt, x), x), from_none], self.prompts
            )
        if self.description is not None:
            result["description"] = from_union([from_str, from_none], self.description)
        if self.messages is not None:
            result["messages"] = from_union(
                [lambda x: from_list(lambda x: to_class(PromptMessage, x), x), from_none],
                self.messages,
            )
        if self.tools is not None:
            result["tools"] = from_union(
                [lambda x: from_list(lambda x: to_class(Tool, x), x), from_none], self.tools
            )
        if self.content is not None:
            result["content"] = from_union(
                [lambda x: from_list(lambda x: to_class(ContentBlock, x), x), from_none],
                self.content,
            )
        if self.is_error is not None:
            result["isError"] = from_union([from_bool, from_none], self.is_error)
        if self.structured_content is not None:
            result["structuredContent"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.structured_content
            )
        if self.completion is not None:
            result["completion"] = from_union(
                [lambda x: to_class(Completion, x), from_none], self.completion
            )
        return result


class SetlevelrequestMethod(Enum):
    LOGGING_SET_LEVEL = "logging/setLevel"


@dataclass
class SetlevelrequestParams(DataModelHelper):
    level: LoggingLevel
    """The level of logging that the client wants to receive from the server. The server should
    send all logs at this level and higher (i.e., more severe) to the client as
    notifications/message.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "SetlevelrequestParams":
        assert isinstance(obj, dict)
        level = LoggingLevel(obj.get("level"))
        return SetlevelrequestParams(level)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["level"] = to_enum(LoggingLevel, self.level)
        return result


@dataclass
class SetLevelRequest(DataModelHelper):
    """A request from the client to the server, to enable or adjust logging."""

    method: SetlevelrequestMethod
    params: SetlevelrequestParams

    @classmethod
    def from_dict(cls, obj: Any) -> "SetLevelRequest":
        assert isinstance(obj, dict)
        method = SetlevelrequestMethod(obj.get("method"))
        params = SetlevelrequestParams.from_dict(obj.get("params"))
        return SetLevelRequest(method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["method"] = to_enum(SetlevelrequestMethod, self.method)
        result["params"] = to_class(SetlevelrequestParams, self.params)
        return result


@dataclass
class StringSchema(DataModelHelper):
    type: EnumschemaType
    description: str | None = None
    format: Format | None = None
    max_length: int | None = None
    min_length: int | None = None
    title: str | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "StringSchema":
        assert isinstance(obj, dict)
        type = EnumschemaType(obj.get("type"))
        description = from_union([from_str, from_none], obj.get("description"))
        format = from_union([Format, from_none], obj.get("format"))
        max_length = from_union([from_int, from_none], obj.get("maxLength"))
        min_length = from_union([from_int, from_none], obj.get("minLength"))
        title = from_union([from_str, from_none], obj.get("title"))
        return StringSchema(type, description, format, max_length, min_length, title)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["type"] = to_enum(EnumschemaType, self.type)
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
class SubscriberequestParams(DataModelHelper):
    uri: str
    """The URI of the resource to subscribe to. The URI can use any protocol; it is up to the
    server how to interpret it.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "SubscriberequestParams":
        assert isinstance(obj, dict)
        uri = from_str(obj.get("uri"))
        return SubscriberequestParams(uri)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["uri"] = from_str(self.uri)
        return result


@dataclass
class SubscribeRequest(DataModelHelper):
    """Sent from the client to request resources/updated notifications from the server whenever
    a particular resource changes.
    """

    method: SubscriberequestMethod
    params: SubscriberequestParams

    @classmethod
    def from_dict(cls, obj: Any) -> "SubscribeRequest":
        assert isinstance(obj, dict)
        method = SubscriberequestMethod(obj.get("method"))
        params = SubscriberequestParams.from_dict(obj.get("params"))
        return SubscribeRequest(method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["method"] = to_enum(SubscriberequestMethod, self.method)
        result["params"] = to_class(SubscriberequestParams, self.params)
        return result


class TextcontentType(Enum):
    TEXT = "text"


@dataclass
class TextContent(DataModelHelper):
    """Text provided to or from an LLM."""

    text: str
    """The text content of the message."""

    type: TextcontentType
    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """
    annotations: Annotations | None = None
    """Optional annotations for the client."""

    @classmethod
    def from_dict(cls, obj: Any) -> "TextContent":
        assert isinstance(obj, dict)
        text = from_str(obj.get("text"))
        type = TextcontentType(obj.get("type"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        annotations = from_union([Annotations.from_dict, from_none], obj.get("annotations"))
        return TextContent(text, type, meta, annotations)

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
                [lambda x: to_class(Annotations, x), from_none], self.annotations
            )
        return result


@dataclass
class TextResourceContents(DataModelHelper):
    text: str
    """The text of the item. This must only be set if the item can actually be represented as
    text (not binary data).
    """
    uri: str
    """The URI of this resource."""

    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """
    mime_type: str | None = None
    """The MIME type of this resource, if known."""

    @classmethod
    def from_dict(cls, obj: Any) -> "TextResourceContents":
        assert isinstance(obj, dict)
        text = from_str(obj.get("text"))
        uri = from_str(obj.get("uri"))
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        mime_type = from_union([from_str, from_none], obj.get("mimeType"))
        return TextResourceContents(text, uri, meta, mime_type)

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
class ToollistchangednotificationParams(DataModelHelper):
    meta: dict[str, Any] | None = None
    """See [General fields: `_meta`](/specification/2025-06-18/basic/index#meta) for notes on
    `_meta` usage.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ToollistchangednotificationParams":
        assert isinstance(obj, dict)
        meta = from_union([lambda x: from_dict(lambda x: x, x), from_none], obj.get("_meta"))
        return ToollistchangednotificationParams(meta)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.meta is not None:
            result["_meta"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.meta
            )
        return result


@dataclass
class ToolListChangedNotification(DataModelHelper):
    """An optional notification from the server to the client, informing it that the list of
    tools it offers has changed. This may be issued by servers without any previous
    subscription from the client.
    """

    method: ToollistchangednotificationMethod
    params: ToollistchangednotificationParams | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "ToolListChangedNotification":
        assert isinstance(obj, dict)
        method = ToollistchangednotificationMethod(obj.get("method"))
        params = from_union(
            [ToollistchangednotificationParams.from_dict, from_none], obj.get("params")
        )
        return ToolListChangedNotification(method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["method"] = to_enum(ToollistchangednotificationMethod, self.method)
        if self.params is not None:
            result["params"] = from_union(
                [lambda x: to_class(ToollistchangednotificationParams, x), from_none], self.params
            )
        return result


class UnsubscriberequestMethod(Enum):
    RESOURCES_UNSUBSCRIBE = "resources/unsubscribe"


@dataclass
class UnsubscriberequestParams(DataModelHelper):
    uri: str
    """The URI of the resource to unsubscribe from."""

    @classmethod
    def from_dict(cls, obj: Any) -> "UnsubscriberequestParams":
        assert isinstance(obj, dict)
        uri = from_str(obj.get("uri"))
        return UnsubscriberequestParams(uri)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["uri"] = from_str(self.uri)
        return result


@dataclass
class UnsubscribeRequest(DataModelHelper):
    """Sent from the client to request cancellation of resources/updated notifications from the
    server. This should follow a previous resources/subscribe request.
    """

    method: UnsubscriberequestMethod
    params: UnsubscriberequestParams

    @classmethod
    def from_dict(cls, obj: Any) -> "UnsubscribeRequest":
        assert isinstance(obj, dict)
        method = UnsubscriberequestMethod(obj.get("method"))
        params = UnsubscriberequestParams.from_dict(obj.get("params"))
        return UnsubscribeRequest(method, params)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["method"] = to_enum(UnsubscriberequestMethod, self.method)
        result["params"] = to_class(UnsubscriberequestParams, self.params)
        return result


@dataclass
class ModelContextProtocolTypesSchema(DataModelHelper):
    annotations: Annotations
    audiocontent: AudioContent | None = None
    basemetadata: BaseMetadata | None = None
    blobresourcecontents: BlobResourceContents | None = None
    booleanschema: BooleanSchema | None = None
    calltoolrequest: CallToolRequest | None = None
    calltoolresult: CallToolResult | None = None
    cancellednotification: CancelledNotification | None = None
    clientcapabilities: ClientCapabilities | None = None
    clientnotification: ClientNotification | None = None
    clientrequest: ClientRequest | None = None
    clientresult: ClientResult | None = None
    completerequest: CompleteRequest | None = None
    completeresult: CompleteResult | None = None
    contentblock: ContentBlock | None = None
    createmessagerequest: CreateMessageRequest | None = None
    createmessageresult: CreateMessageResult | None = None
    cursor: str | None = None
    elicitrequest: ElicitRequest | None = None
    elicitresult: ElicitResult | None = None
    embeddedresource: EmbeddedResource | None = None
    emptyresult: Result | None = None
    enumschema: EnumSchema | None = None
    getpromptrequest: GetPromptRequest | None = None
    getpromptresult: GetPromptResult | None = None
    imagecontent: ImageContent | None = None
    implementation: Implementation | None = None
    initializednotification: InitializedNotification | None = None
    initializerequest: InitializeRequest | None = None
    initializeresult: InitializeResult | None = None
    jsonrpcerror: JSONRPCError | None = None
    jsonrpcmessage: JSONRPCMessage | None = None
    jsonrpcnotification: JSONRPCNotification | None = None
    jsonrpcrequest: JSONRPCRequest | None = None
    jsonrpcresponse: JSONRPCResponse | None = None
    listpromptsrequest: ListPromptsRequest | None = None
    listpromptsresult: ListPromptsResult | None = None
    listresourcesrequest: ListResourcesRequest | None = None
    listresourcesresult: ListResourcesResult | None = None
    listresourcetemplatesrequest: ListResourceTemplatesRequest | None = None
    listresourcetemplatesresult: ListResourceTemplatesResult | None = None
    listrootsrequest: ListRootsRequest | None = None
    listrootsresult: ListRootsResult | None = None
    listtoolsrequest: ListToolsRequest | None = None
    listtoolsresult: ListToolsResult | None = None
    logginglevel: LoggingLevel | None = None
    loggingmessagenotification: LoggingMessageNotification | None = None
    modelhint: ModelHint | None = None
    modelpreferences: ModelPreferences | None = None
    notification: Notification | None = None
    numberschema: NumberSchema | None = None
    paginatedrequest: PaginatedRequest | None = None
    paginatedresult: PaginatedResult | None = None
    pingrequest: PingRequest | None = None
    primitiveschemadefinition: PrimitiveSchemaDefinition | None = None
    progressnotification: ProgressNotification | None = None
    progresstoken: int | str | None = None
    prompt: Prompt | None = None
    promptargument: PromptArgument | None = None
    promptlistchangednotification: PromptListChangedNotification | None = None
    promptmessage: PromptMessage | None = None
    promptreference: PromptReference | None = None
    readresourcerequest: ReadResourceRequest | None = None
    readresourceresult: ReadResourceResult | None = None
    request: Request | None = None
    requestid: int | str | None = None
    resource: Resource | None = None
    resourcecontents: ResourcecontentsClass | None = None
    resourcelink: ResourceLink | None = None
    resourcelistchangednotification: ResourceListChangedNotification | None = None
    resourcetemplate: ResourceTemplate | None = None
    resourcetemplatereference: ResourceTemplateReference | None = None
    resourceupdatednotification: ResourceUpdatedNotification | None = None
    result: Result | None = None
    role: Role | None = None
    root: Root | None = None
    rootslistchangednotification: RootsListChangedNotification | None = None
    samplingmessage: SamplingMessage | None = None
    servercapabilities: ServerCapabilities | None = None
    servernotification: ServerNotification | None = None
    serverrequest: ServerRequest | None = None
    serverresult: ServerResult | None = None
    setlevelrequest: SetLevelRequest | None = None
    stringschema: StringSchema | None = None
    subscriberequest: SubscribeRequest | None = None
    textcontent: TextContent | None = None
    textresourcecontents: TextResourceContents | None = None
    tool: Tool | None = None
    toolannotations: ToolAnnotations | None = None
    toollistchangednotification: ToolListChangedNotification | None = None
    unsubscriberequest: UnsubscribeRequest | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "ModelContextProtocolTypesSchema":
        assert isinstance(obj, dict)
        annotations = Annotations.from_dict(obj.get("annotations"))
        audiocontent = from_union([AudioContent.from_dict, from_none], obj.get("audiocontent"))
        basemetadata = from_union([BaseMetadata.from_dict, from_none], obj.get("basemetadata"))
        blobresourcecontents = from_union(
            [BlobResourceContents.from_dict, from_none], obj.get("blobresourcecontents")
        )
        booleanschema = from_union([BooleanSchema.from_dict, from_none], obj.get("booleanschema"))
        calltoolrequest = from_union(
            [CallToolRequest.from_dict, from_none], obj.get("calltoolrequest")
        )
        calltoolresult = from_union(
            [CallToolResult.from_dict, from_none], obj.get("calltoolresult")
        )
        cancellednotification = from_union(
            [CancelledNotification.from_dict, from_none], obj.get("cancellednotification")
        )
        clientcapabilities = from_union(
            [ClientCapabilities.from_dict, from_none], obj.get("clientcapabilities")
        )
        clientnotification = from_union(
            [ClientNotification.from_dict, from_none], obj.get("clientnotification")
        )
        clientrequest = from_union([ClientRequest.from_dict, from_none], obj.get("clientrequest"))
        clientresult = from_union([ClientResult.from_dict, from_none], obj.get("clientresult"))
        completerequest = from_union(
            [CompleteRequest.from_dict, from_none], obj.get("completerequest")
        )
        completeresult = from_union(
            [CompleteResult.from_dict, from_none], obj.get("completeresult")
        )
        contentblock = from_union([ContentBlock.from_dict, from_none], obj.get("contentblock"))
        createmessagerequest = from_union(
            [CreateMessageRequest.from_dict, from_none], obj.get("createmessagerequest")
        )
        createmessageresult = from_union(
            [CreateMessageResult.from_dict, from_none], obj.get("createmessageresult")
        )
        cursor = from_union([from_str, from_none], obj.get("cursor"))
        elicitrequest = from_union([ElicitRequest.from_dict, from_none], obj.get("elicitrequest"))
        elicitresult = from_union([ElicitResult.from_dict, from_none], obj.get("elicitresult"))
        embeddedresource = from_union(
            [EmbeddedResource.from_dict, from_none], obj.get("embeddedresource")
        )
        emptyresult = from_union([Result.from_dict, from_none], obj.get("emptyresult"))
        enumschema = from_union([EnumSchema.from_dict, from_none], obj.get("enumschema"))
        getpromptrequest = from_union(
            [GetPromptRequest.from_dict, from_none], obj.get("getpromptrequest")
        )
        getpromptresult = from_union(
            [GetPromptResult.from_dict, from_none], obj.get("getpromptresult")
        )
        imagecontent = from_union([ImageContent.from_dict, from_none], obj.get("imagecontent"))
        implementation = from_union(
            [Implementation.from_dict, from_none], obj.get("implementation")
        )
        initializednotification = from_union(
            [InitializedNotification.from_dict, from_none], obj.get("initializednotification")
        )
        initializerequest = from_union(
            [InitializeRequest.from_dict, from_none], obj.get("initializerequest")
        )
        initializeresult = from_union(
            [InitializeResult.from_dict, from_none], obj.get("initializeresult")
        )
        jsonrpcerror = from_union([JSONRPCError.from_dict, from_none], obj.get("jsonrpcerror"))
        jsonrpcmessage = from_union(
            [JSONRPCMessage.from_dict, from_none], obj.get("jsonrpcmessage")
        )
        jsonrpcnotification = from_union(
            [JSONRPCNotification.from_dict, from_none], obj.get("jsonrpcnotification")
        )
        jsonrpcrequest = from_union(
            [JSONRPCRequest.from_dict, from_none], obj.get("jsonrpcrequest")
        )
        jsonrpcresponse = from_union(
            [JSONRPCResponse.from_dict, from_none], obj.get("jsonrpcresponse")
        )
        listpromptsrequest = from_union(
            [ListPromptsRequest.from_dict, from_none], obj.get("listpromptsrequest")
        )
        listpromptsresult = from_union(
            [ListPromptsResult.from_dict, from_none], obj.get("listpromptsresult")
        )
        listresourcesrequest = from_union(
            [ListResourcesRequest.from_dict, from_none], obj.get("listresourcesrequest")
        )
        listresourcesresult = from_union(
            [ListResourcesResult.from_dict, from_none], obj.get("listresourcesresult")
        )
        listresourcetemplatesrequest = from_union(
            [ListResourceTemplatesRequest.from_dict, from_none],
            obj.get("listresourcetemplatesrequest"),
        )
        listresourcetemplatesresult = from_union(
            [ListResourceTemplatesResult.from_dict, from_none],
            obj.get("listresourcetemplatesresult"),
        )
        listrootsrequest = from_union(
            [ListRootsRequest.from_dict, from_none], obj.get("listrootsrequest")
        )
        listrootsresult = from_union(
            [ListRootsResult.from_dict, from_none], obj.get("listrootsresult")
        )
        listtoolsrequest = from_union(
            [ListToolsRequest.from_dict, from_none], obj.get("listtoolsrequest")
        )
        listtoolsresult = from_union(
            [ListToolsResult.from_dict, from_none], obj.get("listtoolsresult")
        )
        logginglevel = from_union([LoggingLevel, from_none], obj.get("logginglevel"))
        loggingmessagenotification = from_union(
            [LoggingMessageNotification.from_dict, from_none], obj.get("loggingmessagenotification")
        )
        modelhint = from_union([ModelHint.from_dict, from_none], obj.get("modelhint"))
        modelpreferences = from_union(
            [ModelPreferences.from_dict, from_none], obj.get("modelpreferences")
        )
        notification = from_union([Notification.from_dict, from_none], obj.get("notification"))
        numberschema = from_union([NumberSchema.from_dict, from_none], obj.get("numberschema"))
        paginatedrequest = from_union(
            [PaginatedRequest.from_dict, from_none], obj.get("paginatedrequest")
        )
        paginatedresult = from_union(
            [PaginatedResult.from_dict, from_none], obj.get("paginatedresult")
        )
        pingrequest = from_union([PingRequest.from_dict, from_none], obj.get("pingrequest"))
        primitiveschemadefinition = from_union(
            [PrimitiveSchemaDefinition.from_dict, from_none], obj.get("primitiveschemadefinition")
        )
        progressnotification = from_union(
            [ProgressNotification.from_dict, from_none], obj.get("progressnotification")
        )
        progresstoken = from_union([from_int, from_str, from_none], obj.get("progresstoken"))
        prompt = from_union([Prompt.from_dict, from_none], obj.get("prompt"))
        promptargument = from_union(
            [PromptArgument.from_dict, from_none], obj.get("promptargument")
        )
        promptlistchangednotification = from_union(
            [PromptListChangedNotification.from_dict, from_none],
            obj.get("promptlistchangednotification"),
        )
        promptmessage = from_union([PromptMessage.from_dict, from_none], obj.get("promptmessage"))
        promptreference = from_union(
            [PromptReference.from_dict, from_none], obj.get("promptreference")
        )
        readresourcerequest = from_union(
            [ReadResourceRequest.from_dict, from_none], obj.get("readresourcerequest")
        )
        readresourceresult = from_union(
            [ReadResourceResult.from_dict, from_none], obj.get("readresourceresult")
        )
        request = from_union([Request.from_dict, from_none], obj.get("request"))
        requestid = from_union([from_int, from_str, from_none], obj.get("requestid"))
        resource = from_union([Resource.from_dict, from_none], obj.get("resource"))
        resourcecontents = from_union(
            [ResourcecontentsClass.from_dict, from_none], obj.get("resourcecontents")
        )
        resourcelink = from_union([ResourceLink.from_dict, from_none], obj.get("resourcelink"))
        resourcelistchangednotification = from_union(
            [ResourceListChangedNotification.from_dict, from_none],
            obj.get("resourcelistchangednotification"),
        )
        resourcetemplate = from_union(
            [ResourceTemplate.from_dict, from_none], obj.get("resourcetemplate")
        )
        resourcetemplatereference = from_union(
            [ResourceTemplateReference.from_dict, from_none], obj.get("resourcetemplatereference")
        )
        resourceupdatednotification = from_union(
            [ResourceUpdatedNotification.from_dict, from_none],
            obj.get("resourceupdatednotification"),
        )
        result = from_union([Result.from_dict, from_none], obj.get("result"))
        role = from_union([Role, from_none], obj.get("role"))
        root = from_union([Root.from_dict, from_none], obj.get("root"))
        rootslistchangednotification = from_union(
            [RootsListChangedNotification.from_dict, from_none],
            obj.get("rootslistchangednotification"),
        )
        samplingmessage = from_union(
            [SamplingMessage.from_dict, from_none], obj.get("samplingmessage")
        )
        servercapabilities = from_union(
            [ServerCapabilities.from_dict, from_none], obj.get("servercapabilities")
        )
        servernotification = from_union(
            [ServerNotification.from_dict, from_none], obj.get("servernotification")
        )
        serverrequest = from_union([ServerRequest.from_dict, from_none], obj.get("serverrequest"))
        serverresult = from_union([ServerResult.from_dict, from_none], obj.get("serverresult"))
        setlevelrequest = from_union(
            [SetLevelRequest.from_dict, from_none], obj.get("setlevelrequest")
        )
        stringschema = from_union([StringSchema.from_dict, from_none], obj.get("stringschema"))
        subscriberequest = from_union(
            [SubscribeRequest.from_dict, from_none], obj.get("subscriberequest")
        )
        textcontent = from_union([TextContent.from_dict, from_none], obj.get("textcontent"))
        textresourcecontents = from_union(
            [TextResourceContents.from_dict, from_none], obj.get("textresourcecontents")
        )
        tool = from_union([Tool.from_dict, from_none], obj.get("tool"))
        toolannotations = from_union(
            [ToolAnnotations.from_dict, from_none], obj.get("toolannotations")
        )
        toollistchangednotification = from_union(
            [ToolListChangedNotification.from_dict, from_none],
            obj.get("toollistchangednotification"),
        )
        unsubscriberequest = from_union(
            [UnsubscribeRequest.from_dict, from_none], obj.get("unsubscriberequest")
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
        result["annotations"] = to_class(Annotations, self.annotations)
        if self.audiocontent is not None:
            result["audiocontent"] = from_union(
                [lambda x: to_class(AudioContent, x), from_none], self.audiocontent
            )
        if self.basemetadata is not None:
            result["basemetadata"] = from_union(
                [lambda x: to_class(BaseMetadata, x), from_none], self.basemetadata
            )
        if self.blobresourcecontents is not None:
            result["blobresourcecontents"] = from_union(
                [lambda x: to_class(BlobResourceContents, x), from_none], self.blobresourcecontents
            )
        if self.booleanschema is not None:
            result["booleanschema"] = from_union(
                [lambda x: to_class(BooleanSchema, x), from_none], self.booleanschema
            )
        if self.calltoolrequest is not None:
            result["calltoolrequest"] = from_union(
                [lambda x: to_class(CallToolRequest, x), from_none], self.calltoolrequest
            )
        if self.calltoolresult is not None:
            result["calltoolresult"] = from_union(
                [lambda x: to_class(CallToolResult, x), from_none], self.calltoolresult
            )
        if self.cancellednotification is not None:
            result["cancellednotification"] = from_union(
                [lambda x: to_class(CancelledNotification, x), from_none],
                self.cancellednotification,
            )
        if self.clientcapabilities is not None:
            result["clientcapabilities"] = from_union(
                [lambda x: to_class(ClientCapabilities, x), from_none], self.clientcapabilities
            )
        if self.clientnotification is not None:
            result["clientnotification"] = from_union(
                [lambda x: to_class(ClientNotification, x), from_none], self.clientnotification
            )
        if self.clientrequest is not None:
            result["clientrequest"] = from_union(
                [lambda x: to_class(ClientRequest, x), from_none], self.clientrequest
            )
        if self.clientresult is not None:
            result["clientresult"] = from_union(
                [lambda x: to_class(ClientResult, x), from_none], self.clientresult
            )
        if self.completerequest is not None:
            result["completerequest"] = from_union(
                [lambda x: to_class(CompleteRequest, x), from_none], self.completerequest
            )
        if self.completeresult is not None:
            result["completeresult"] = from_union(
                [lambda x: to_class(CompleteResult, x), from_none], self.completeresult
            )
        if self.contentblock is not None:
            result["contentblock"] = from_union(
                [lambda x: to_class(ContentBlock, x), from_none], self.contentblock
            )
        if self.createmessagerequest is not None:
            result["createmessagerequest"] = from_union(
                [lambda x: to_class(CreateMessageRequest, x), from_none], self.createmessagerequest
            )
        if self.createmessageresult is not None:
            result["createmessageresult"] = from_union(
                [lambda x: to_class(CreateMessageResult, x), from_none], self.createmessageresult
            )
        if self.cursor is not None:
            result["cursor"] = from_union([from_str, from_none], self.cursor)
        if self.elicitrequest is not None:
            result["elicitrequest"] = from_union(
                [lambda x: to_class(ElicitRequest, x), from_none], self.elicitrequest
            )
        if self.elicitresult is not None:
            result["elicitresult"] = from_union(
                [lambda x: to_class(ElicitResult, x), from_none], self.elicitresult
            )
        if self.embeddedresource is not None:
            result["embeddedresource"] = from_union(
                [lambda x: to_class(EmbeddedResource, x), from_none], self.embeddedresource
            )
        if self.emptyresult is not None:
            result["emptyresult"] = from_union(
                [lambda x: to_class(Result, x), from_none], self.emptyresult
            )
        if self.enumschema is not None:
            result["enumschema"] = from_union(
                [lambda x: to_class(EnumSchema, x), from_none], self.enumschema
            )
        if self.getpromptrequest is not None:
            result["getpromptrequest"] = from_union(
                [lambda x: to_class(GetPromptRequest, x), from_none], self.getpromptrequest
            )
        if self.getpromptresult is not None:
            result["getpromptresult"] = from_union(
                [lambda x: to_class(GetPromptResult, x), from_none], self.getpromptresult
            )
        if self.imagecontent is not None:
            result["imagecontent"] = from_union(
                [lambda x: to_class(ImageContent, x), from_none], self.imagecontent
            )
        if self.implementation is not None:
            result["implementation"] = from_union(
                [lambda x: to_class(Implementation, x), from_none], self.implementation
            )
        if self.initializednotification is not None:
            result["initializednotification"] = from_union(
                [lambda x: to_class(InitializedNotification, x), from_none],
                self.initializednotification,
            )
        if self.initializerequest is not None:
            result["initializerequest"] = from_union(
                [lambda x: to_class(InitializeRequest, x), from_none], self.initializerequest
            )
        if self.initializeresult is not None:
            result["initializeresult"] = from_union(
                [lambda x: to_class(InitializeResult, x), from_none], self.initializeresult
            )
        if self.jsonrpcerror is not None:
            result["jsonrpcerror"] = from_union(
                [lambda x: to_class(JSONRPCError, x), from_none], self.jsonrpcerror
            )
        if self.jsonrpcmessage is not None:
            result["jsonrpcmessage"] = from_union(
                [lambda x: to_class(JSONRPCMessage, x), from_none], self.jsonrpcmessage
            )
        if self.jsonrpcnotification is not None:
            result["jsonrpcnotification"] = from_union(
                [lambda x: to_class(JSONRPCNotification, x), from_none], self.jsonrpcnotification
            )
        if self.jsonrpcrequest is not None:
            result["jsonrpcrequest"] = from_union(
                [lambda x: to_class(JSONRPCRequest, x), from_none], self.jsonrpcrequest
            )
        if self.jsonrpcresponse is not None:
            result["jsonrpcresponse"] = from_union(
                [lambda x: to_class(JSONRPCResponse, x), from_none], self.jsonrpcresponse
            )
        if self.listpromptsrequest is not None:
            result["listpromptsrequest"] = from_union(
                [lambda x: to_class(ListPromptsRequest, x), from_none], self.listpromptsrequest
            )
        if self.listpromptsresult is not None:
            result["listpromptsresult"] = from_union(
                [lambda x: to_class(ListPromptsResult, x), from_none], self.listpromptsresult
            )
        if self.listresourcesrequest is not None:
            result["listresourcesrequest"] = from_union(
                [lambda x: to_class(ListResourcesRequest, x), from_none], self.listresourcesrequest
            )
        if self.listresourcesresult is not None:
            result["listresourcesresult"] = from_union(
                [lambda x: to_class(ListResourcesResult, x), from_none], self.listresourcesresult
            )
        if self.listresourcetemplatesrequest is not None:
            result["listresourcetemplatesrequest"] = from_union(
                [lambda x: to_class(ListResourceTemplatesRequest, x), from_none],
                self.listresourcetemplatesrequest,
            )
        if self.listresourcetemplatesresult is not None:
            result["listresourcetemplatesresult"] = from_union(
                [lambda x: to_class(ListResourceTemplatesResult, x), from_none],
                self.listresourcetemplatesresult,
            )
        if self.listrootsrequest is not None:
            result["listrootsrequest"] = from_union(
                [lambda x: to_class(ListRootsRequest, x), from_none], self.listrootsrequest
            )
        if self.listrootsresult is not None:
            result["listrootsresult"] = from_union(
                [lambda x: to_class(ListRootsResult, x), from_none], self.listrootsresult
            )
        if self.listtoolsrequest is not None:
            result["listtoolsrequest"] = from_union(
                [lambda x: to_class(ListToolsRequest, x), from_none], self.listtoolsrequest
            )
        if self.listtoolsresult is not None:
            result["listtoolsresult"] = from_union(
                [lambda x: to_class(ListToolsResult, x), from_none], self.listtoolsresult
            )
        if self.logginglevel is not None:
            result["logginglevel"] = from_union(
                [lambda x: to_enum(LoggingLevel, x), from_none], self.logginglevel
            )
        if self.loggingmessagenotification is not None:
            result["loggingmessagenotification"] = from_union(
                [lambda x: to_class(LoggingMessageNotification, x), from_none],
                self.loggingmessagenotification,
            )
        if self.modelhint is not None:
            result["modelhint"] = from_union(
                [lambda x: to_class(ModelHint, x), from_none], self.modelhint
            )
        if self.modelpreferences is not None:
            result["modelpreferences"] = from_union(
                [lambda x: to_class(ModelPreferences, x), from_none], self.modelpreferences
            )
        if self.notification is not None:
            result["notification"] = from_union(
                [lambda x: to_class(Notification, x), from_none], self.notification
            )
        if self.numberschema is not None:
            result["numberschema"] = from_union(
                [lambda x: to_class(NumberSchema, x), from_none], self.numberschema
            )
        if self.paginatedrequest is not None:
            result["paginatedrequest"] = from_union(
                [lambda x: to_class(PaginatedRequest, x), from_none], self.paginatedrequest
            )
        if self.paginatedresult is not None:
            result["paginatedresult"] = from_union(
                [lambda x: to_class(PaginatedResult, x), from_none], self.paginatedresult
            )
        if self.pingrequest is not None:
            result["pingrequest"] = from_union(
                [lambda x: to_class(PingRequest, x), from_none], self.pingrequest
            )
        if self.primitiveschemadefinition is not None:
            result["primitiveschemadefinition"] = from_union(
                [lambda x: to_class(PrimitiveSchemaDefinition, x), from_none],
                self.primitiveschemadefinition,
            )
        if self.progressnotification is not None:
            result["progressnotification"] = from_union(
                [lambda x: to_class(ProgressNotification, x), from_none], self.progressnotification
            )
        if self.progresstoken is not None:
            result["progresstoken"] = from_union(
                [from_int, from_str, from_none], self.progresstoken
            )
        if self.prompt is not None:
            result["prompt"] = from_union([lambda x: to_class(Prompt, x), from_none], self.prompt)
        if self.promptargument is not None:
            result["promptargument"] = from_union(
                [lambda x: to_class(PromptArgument, x), from_none], self.promptargument
            )
        if self.promptlistchangednotification is not None:
            result["promptlistchangednotification"] = from_union(
                [lambda x: to_class(PromptListChangedNotification, x), from_none],
                self.promptlistchangednotification,
            )
        if self.promptmessage is not None:
            result["promptmessage"] = from_union(
                [lambda x: to_class(PromptMessage, x), from_none], self.promptmessage
            )
        if self.promptreference is not None:
            result["promptreference"] = from_union(
                [lambda x: to_class(PromptReference, x), from_none], self.promptreference
            )
        if self.readresourcerequest is not None:
            result["readresourcerequest"] = from_union(
                [lambda x: to_class(ReadResourceRequest, x), from_none], self.readresourcerequest
            )
        if self.readresourceresult is not None:
            result["readresourceresult"] = from_union(
                [lambda x: to_class(ReadResourceResult, x), from_none], self.readresourceresult
            )
        if self.request is not None:
            result["request"] = from_union(
                [lambda x: to_class(Request, x), from_none], self.request
            )
        if self.requestid is not None:
            result["requestid"] = from_union([from_int, from_str, from_none], self.requestid)
        if self.resource is not None:
            result["resource"] = from_union(
                [lambda x: to_class(Resource, x), from_none], self.resource
            )
        if self.resourcecontents is not None:
            result["resourcecontents"] = from_union(
                [lambda x: to_class(ResourcecontentsClass, x), from_none], self.resourcecontents
            )
        if self.resourcelink is not None:
            result["resourcelink"] = from_union(
                [lambda x: to_class(ResourceLink, x), from_none], self.resourcelink
            )
        if self.resourcelistchangednotification is not None:
            result["resourcelistchangednotification"] = from_union(
                [lambda x: to_class(ResourceListChangedNotification, x), from_none],
                self.resourcelistchangednotification,
            )
        if self.resourcetemplate is not None:
            result["resourcetemplate"] = from_union(
                [lambda x: to_class(ResourceTemplate, x), from_none], self.resourcetemplate
            )
        if self.resourcetemplatereference is not None:
            result["resourcetemplatereference"] = from_union(
                [lambda x: to_class(ResourceTemplateReference, x), from_none],
                self.resourcetemplatereference,
            )
        if self.resourceupdatednotification is not None:
            result["resourceupdatednotification"] = from_union(
                [lambda x: to_class(ResourceUpdatedNotification, x), from_none],
                self.resourceupdatednotification,
            )
        if self.result is not None:
            result["result"] = from_union([lambda x: to_class(Result, x), from_none], self.result)
        if self.role is not None:
            result["role"] = from_union([lambda x: to_enum(Role, x), from_none], self.role)
        if self.root is not None:
            result["root"] = from_union([lambda x: to_class(Root, x), from_none], self.root)
        if self.rootslistchangednotification is not None:
            result["rootslistchangednotification"] = from_union(
                [lambda x: to_class(RootsListChangedNotification, x), from_none],
                self.rootslistchangednotification,
            )
        if self.samplingmessage is not None:
            result["samplingmessage"] = from_union(
                [lambda x: to_class(SamplingMessage, x), from_none], self.samplingmessage
            )
        if self.servercapabilities is not None:
            result["servercapabilities"] = from_union(
                [lambda x: to_class(ServerCapabilities, x), from_none], self.servercapabilities
            )
        if self.servernotification is not None:
            result["servernotification"] = from_union(
                [lambda x: to_class(ServerNotification, x), from_none], self.servernotification
            )
        if self.serverrequest is not None:
            result["serverrequest"] = from_union(
                [lambda x: to_class(ServerRequest, x), from_none], self.serverrequest
            )
        if self.serverresult is not None:
            result["serverresult"] = from_union(
                [lambda x: to_class(ServerResult, x), from_none], self.serverresult
            )
        if self.setlevelrequest is not None:
            result["setlevelrequest"] = from_union(
                [lambda x: to_class(SetLevelRequest, x), from_none], self.setlevelrequest
            )
        if self.stringschema is not None:
            result["stringschema"] = from_union(
                [lambda x: to_class(StringSchema, x), from_none], self.stringschema
            )
        if self.subscriberequest is not None:
            result["subscriberequest"] = from_union(
                [lambda x: to_class(SubscribeRequest, x), from_none], self.subscriberequest
            )
        if self.textcontent is not None:
            result["textcontent"] = from_union(
                [lambda x: to_class(TextContent, x), from_none], self.textcontent
            )
        if self.textresourcecontents is not None:
            result["textresourcecontents"] = from_union(
                [lambda x: to_class(TextResourceContents, x), from_none], self.textresourcecontents
            )
        if self.tool is not None:
            result["tool"] = from_union([lambda x: to_class(Tool, x), from_none], self.tool)
        if self.toolannotations is not None:
            result["toolannotations"] = from_union(
                [lambda x: to_class(ToolAnnotations, x), from_none], self.toolannotations
            )
        if self.toollistchangednotification is not None:
            result["toollistchangednotification"] = from_union(
                [lambda x: to_class(ToolListChangedNotification, x), from_none],
                self.toollistchangednotification,
            )
        if self.unsubscriberequest is not None:
            result["unsubscriberequest"] = from_union(
                [lambda x: to_class(UnsubscribeRequest, x), from_none], self.unsubscriberequest
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
