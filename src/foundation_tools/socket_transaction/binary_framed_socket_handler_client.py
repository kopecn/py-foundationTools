"""
BinaryFramedSocketHandlerClient -- binary-frame decoding specialization of the
threaded socket client (plan 25, chunk 12).

Extends ``SocketHandlerClient`` (chunks 08-09) by accumulating an
epoch-scoped binary buffer alongside the inherited raw/text channels and
repeatedly applying an injected frame decoder to it, delivering each decoded
frame in order to a registered frame handler. See
``.claude/specs/threadedSocketTransport.md#binary-framed-client`` for the
full behavioral contract.

Outbound binary data continues to use the inherited raw ``send``; this
module adds no outbound frame encoder, no binary transaction codec, and no
server specialization. Deliberately not built on
``foundation_abc.PeripheralByteTransport`` -- that ABC is fully asynchronous
and out of scope for this synchronous, threaded design.
"""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable

from foundation_tools.socket_transaction.socket_handler_client import SocketHandlerClient

FrameDecoder = Callable[[bytes], tuple[object | None, bytes]]


class BinaryFramedSocketHandlerClient(SocketHandlerClient):
    """Adds accumulated binary-frame decoding to the threaded socket client.

    ``frame_decoder`` is called with the complete accumulated per-epoch
    buffer and must return ``(frame, remainder)`` where ``remainder`` is the
    unconsumed suffix of that buffer. Returning ``(None, buffer)`` unchanged
    is the only valid "incomplete frame" stop signal; any other no-frame
    result, or any result whose remainder is not a strict byte suffix of the
    input, is treated as decoder failure.

    ``_process_received_chunk`` calls the inherited raw/text dispatch first
    (unconditionally, exactly once), then extends the epoch's binary buffer
    and decodes as many complete frames as are available, delivering each to
    the registered frame handler outside of any internal lock. A decoder
    exception or invalid result clears that epoch's binary buffer and logs,
    without terminating reception; frame-handler exceptions are contained
    the same way. The binary buffer resets whenever a chunk is first
    observed for a new connection epoch, so a reconnect never sees a prior
    epoch's leftover partial frame.
    """

    def __init__(
        self,
        logger: logging.Logger,
        frame_decoder: FrameDecoder,
        *,
        string_delimiter: str = "\n",
        join_timeout: float = 1.0,
    ) -> None:
        super().__init__(logger, string_delimiter=string_delimiter, join_timeout=join_timeout)
        self._frame_decoder = frame_decoder

        self._binary_lock = threading.Lock()
        self._binary_epoch: int | None = None
        self._binary_buffer: bytes = b""

        self._frame_handler_lock = threading.Lock()
        self._frame_handler: Callable[[object], None] | None = None

    def set_frame_handler(self, handler: Callable[[object], None] | None) -> None:
        """Replace the frame handler. Only subsequently decoded frames observe it."""
        with self._frame_handler_lock:
            self._frame_handler = handler

    def _process_received_chunk(self, epoch: int, data: bytes) -> None:
        super()._process_received_chunk(epoch, data)
        for frame in self._decode_frames_for_epoch(epoch, data):
            self._invoke_frame_handler(frame)

    def _decode_frames_for_epoch(self, epoch: int, data: bytes) -> list[object]:
        """Extend this epoch's binary buffer and decode complete frames.

        Re-checks epoch identity under the same lock that guards the binary
        buffer, mirroring the base class's own epoch-safe text-tokenization
        pattern, so a lingering worker from a superseded epoch can neither
        read nor mutate a newer epoch's binary state. Resets the buffer the
        first time a chunk is observed for a not-yet-seen epoch (covers both
        the first chunk of a fresh connection and any reconnect). Follows
        the decoder-loop recipe exactly: a valid remainder must be a byte
        suffix of the input, a frame must strictly shorten the buffer, and
        ``(None, identical_input)`` is the only incomplete-frame stop result.
        Any decoder exception or invalid progress clears the buffer and
        stops decoding this chunk without propagating.
        """
        with self._binary_lock:
            if not self._epoch_is_current(epoch):
                return []

            if self._binary_epoch != epoch:
                self._binary_epoch = epoch
                self._binary_buffer = b""

            buffer = self._binary_buffer + data
            frames: list[object] = []
            try:
                while buffer:
                    frame, remainder = self._frame_decoder(buffer)
                    if frame is None and remainder == buffer:
                        break
                    if not isinstance(remainder, bytes) or not buffer.endswith(remainder):
                        raise ValueError(
                            "binary frame decoder remainder is not a suffix of the input buffer"
                        )
                    if frame is None or len(remainder) >= len(buffer):
                        raise ValueError("binary frame decoder made no valid progress")
                    buffer = remainder
                    frames.append(frame)
            except Exception:
                self._logger.exception(
                    "binary framed client: frame decoder failed for epoch %s; "
                    "clearing binary buffer",
                    epoch,
                )
                if self._binary_epoch == epoch:
                    self._binary_buffer = b""
                return []

            if self._binary_epoch == epoch:
                self._binary_buffer = buffer
            return frames

    def _invoke_frame_handler(self, frame: object) -> None:
        with self._frame_handler_lock:
            handler = self._frame_handler
        if handler is None:
            return
        try:
            handler(frame)
        except Exception:
            self._logger.exception("binary framed client: frame handler raised")
