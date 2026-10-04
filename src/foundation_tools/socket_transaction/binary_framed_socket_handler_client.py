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
    epoch's leftover partial frame. The epoch is revalidated after every
    decoder return and again immediately before every frame-handler call,
    so a decoder blocked on a stale epoch -- or a callback that itself
    triggers connection replacement -- can never deliver output once that
    epoch is no longer active (plan 25, chunk 19).
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
        self._decode_and_dispatch_frames(epoch, data)

    def _decode_and_dispatch_frames(self, epoch: int, data: bytes) -> None:
        """Extend this epoch's binary buffer, decode complete frames, and
        deliver each to the frame handler in order.

        The caller-supplied decoder and the frame handler are invoked
        outside every internal lock -- ``_binary_lock`` is held only to
        snapshot or publish buffer/epoch state, never across a callback.
        Because a decoder call can block for an unbounded time (see the
        plan's blocked-decoder race), the epoch is revalidated immediately
        after every decoder return -- before that decode's progress is
        committed to the shared buffer -- and again immediately before the
        matching frame-handler call, since a frame-handler invocation for an
        earlier frame in this same chunk may itself trigger a replacement
        before a later, already-decoded frame is delivered. Either window
        closing on a no-longer-active epoch discards that decode's output
        instead of committing or delivering it, and never mutates a newer
        epoch's binary buffer. A decoder exception or invalid result is
        still treated as decoder failure: log the error, clear the buffer
        (only if this epoch still owns it), and stop decoding this chunk
        without terminating reception.
        """
        with self._binary_lock:
            if not self._epoch_is_current(epoch):
                return
            if self._binary_epoch != epoch:
                self._binary_epoch = epoch
                self._binary_buffer = b""
            buffer = self._binary_buffer + data

        while buffer:
            try:
                frame, remainder = self._frame_decoder(buffer)
                if frame is None and remainder == buffer:
                    self._commit_binary_buffer(epoch, buffer)
                    return
                if not isinstance(remainder, bytes) or not buffer.endswith(remainder):
                    raise ValueError(
                        "binary frame decoder remainder is not a suffix of the input buffer"
                    )
                if frame is None or len(remainder) >= len(buffer):
                    raise ValueError("binary frame decoder made no valid progress")
            except Exception:
                self._logger.exception(
                    "binary framed client: frame decoder failed for epoch %s; "
                    "clearing binary buffer",
                    epoch,
                )
                self._clear_binary_buffer(epoch)
                return

            buffer = remainder
            if not self._commit_binary_buffer(epoch, buffer):
                return  # stale epoch: discard this frame and stop this chunk
            if not self._epoch_is_current(epoch):
                return  # replaced between commit and delivery: discard
            self._invoke_frame_handler(frame)

    def _commit_binary_buffer(self, epoch: int, buffer: bytes) -> bool:
        """Publish ``buffer`` as ``epoch``'s binary state iff still active.

        Returns ``False`` without writing anything when ``epoch`` is no
        longer the active connection or no longer owns the binary buffer --
        the caller must then discard whatever it decoded rather than commit
        or deliver it, so a stale worker never mutates a newer epoch's state.
        """
        with self._binary_lock:
            if self._binary_epoch != epoch or not self._epoch_is_current(epoch):
                return False
            self._binary_buffer = buffer
            return True

    def _clear_binary_buffer(self, epoch: int) -> None:
        """Clear the binary buffer after a decoder failure, iff still owned by ``epoch``."""
        with self._binary_lock:
            if self._binary_epoch == epoch:
                self._binary_buffer = b""

    def _invoke_frame_handler(self, frame: object) -> None:
        with self._frame_handler_lock:
            handler = self._frame_handler
        if handler is None:
            return
        try:
            handler(frame)
        except Exception:
            self._logger.exception("binary framed client: frame handler raised")
