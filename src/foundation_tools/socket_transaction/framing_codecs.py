"""
Framing Codecs — Layer 2 of the socket-transaction stack.

A codec converts between a raw byte stream and discrete frames. Codecs frame bytes
only; model conversion composes on top via ``DataModelHelper.to_wire``/``from_wire``
(see the Wire Serialization Bridge section of
``.claude/specs/transport_transaction_architecture.md``). The only stateful part of
a codec is its reassembly buffer, used to hold partial frames across ``feed`` calls.
See ``.claude/specs/socketTransact.md`` (Layer 2) for the full contract.
"""

from typing import Literal, Protocol, runtime_checkable


@runtime_checkable
class FramingCodec(Protocol):
    """Structural protocol satisfied by any bytes-to-frames codec."""

    def encode(self, payload: bytes) -> bytes:
        """Wrap one outbound payload into wire bytes."""
        ...

    def feed(self, data: bytes) -> list[bytes]:
        """Accept an inbound chunk and return zero or more complete frames.

        Partial frames are buffered internally and returned once completed by a
        later call.
        """
        ...


class DelimiterCodec:
    """Frames are payloads terminated by a configurable delimiter (default ``\\n``).

    Suited to line/token protocols and ``DataModelHelper.to_wire`` string payloads
    (encoded UTF-8).
    """

    def __init__(self, delimiter: bytes = b"\n") -> None:
        if len(delimiter) == 0:
            raise ValueError(
                "delimiter must be non-empty; an empty delimiter never terminates a frame"
            )
        self._delimiter = delimiter
        self._buffer = bytearray()

    def encode(self, payload: bytes) -> bytes:
        """Append the delimiter to ``payload``.

        Raises:
            ValueError: If ``payload`` already contains the delimiter.
        """
        if self._delimiter in payload:
            raise ValueError(f"payload contains the frame delimiter {self._delimiter!r}")
        return payload + self._delimiter

    def feed(self, data: bytes) -> list[bytes]:
        """Extract every complete (delimiter-terminated) frame from ``data``."""
        self._buffer.extend(data)
        frames: list[bytes] = []
        while True:
            index = self._buffer.find(self._delimiter)
            if index == -1:
                break
            frames.append(bytes(self._buffer[:index]))
            del self._buffer[: index + len(self._delimiter)]
        return frames


class LengthPrefixedCodec:
    """Frames are ``<length prefix><payload>``, suited to binary protocols.

    The prefix is a fixed-width unsigned integer (default 4-byte big-endian)
    giving the payload's length in bytes.

    ``max_frame_size`` bounds the declared length accepted from the wire (default:
    the largest value representable by ``prefix_width``, i.e. no additional
    restriction). Setting it lower guards against a corrupted or malicious length
    prefix forcing unbounded reassembly-buffer growth — such a prefix is reported as
    malformed immediately rather than waiting indefinitely for bytes that will
    never arrive.
    """

    def __init__(
        self,
        prefix_width: int = 4,
        byteorder: Literal["big", "little"] = "big",
        *,
        max_frame_size: int | None = None,
    ) -> None:
        if prefix_width < 1:
            raise ValueError(f"prefix_width must be a positive integer; got {prefix_width}")
        self._prefix_width = prefix_width
        self._byteorder = byteorder
        self._max_representable = (1 << (prefix_width * 8)) - 1
        if max_frame_size is not None:
            if max_frame_size < 0:
                raise ValueError(f"max_frame_size must be non-negative; got {max_frame_size}")
            if max_frame_size > self._max_representable:
                raise ValueError(
                    f"max_frame_size {max_frame_size} exceeds the {prefix_width}-byte "
                    f"prefix's max representable value of {self._max_representable}"
                )
        self._max_frame_size = (
            max_frame_size if max_frame_size is not None else self._max_representable
        )
        self._buffer = bytearray()

    def encode(self, payload: bytes) -> bytes:
        """Prefix ``payload`` with its length.

        Raises:
            ValueError: If ``payload`` is too long to represent in ``prefix_width``
                bytes.
        """
        if len(payload) > self._max_representable:
            raise ValueError(
                f"payload of {len(payload)} bytes exceeds the "
                f"{self._prefix_width}-byte prefix's max of {self._max_representable}"
            )
        prefix = len(payload).to_bytes(self._prefix_width, byteorder=self._byteorder)
        return prefix + payload

    def feed(self, data: bytes) -> list[bytes]:
        """Extract every complete length-prefixed frame from ``data``.

        Raises:
            ValueError: If a decoded length prefix exceeds ``max_frame_size``.
        """
        self._buffer.extend(data)
        frames: list[bytes] = []
        while True:
            if len(self._buffer) < self._prefix_width:
                break
            length = int.from_bytes(self._buffer[: self._prefix_width], byteorder=self._byteorder)
            if length > self._max_frame_size:
                raise ValueError(
                    f"declared frame length {length} exceeds max_frame_size "
                    f"{self._max_frame_size} — malformed or corrupt length prefix"
                )
            frame_end = self._prefix_width + length
            if len(self._buffer) < frame_end:
                break
            frames.append(bytes(self._buffer[self._prefix_width : frame_end]))
            del self._buffer[:frame_end]
        return frames
