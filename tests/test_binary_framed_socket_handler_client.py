"""
Tests for ``BinaryFramedSocketHandlerClient`` (plan 25, chunk 12): accumulated
binary-frame decoding layered over the inherited raw/text receive channels.

Uses a simple length-prefixed test decoder (one length byte, then that many
payload bytes) exercised over ``tests/threaded_socket_helpers.socketpair_context``
via the protected ``_attach``/``_detach`` primitives, the same white-box
pattern ``tests/test_socket_handler.py`` uses. Reconnect tests use
``ThreadedLoopbackListener`` and the public ``connect``/``disconnect``
surface. Every concurrency assertion uses ``threading.Event`` gates or
bounded ``queue.Queue.get(timeout=...)`` -- no sleeps or randomness.
"""

from __future__ import annotations

import logging
import queue
import socket
import threading

import pytest

from foundation_tools.socket_transaction.binary_framed_socket_handler_client import (
    BinaryFramedSocketHandlerClient,
    FrameDecoder,
)
from tests.threaded_socket_helpers import TEST_TIMEOUT, ThreadedLoopbackListener, socketpair_context

SHORT_TIMEOUT = 0.2


def _logger(name: str) -> logging.Logger:
    return logging.getLogger(f"test.binary_framed_socket_handler_client.{name}")


def _length_prefixed_decoder(buffer: bytes) -> tuple[object | None, bytes]:
    """One length byte followed by that many payload bytes."""
    if not buffer:
        return None, buffer
    length = buffer[0]
    if len(buffer) < 1 + length:
        return None, buffer
    frame = buffer[1 : 1 + length]
    remainder = buffer[1 + length :]
    return frame, remainder


def _frame(payload: bytes) -> bytes:
    """Encode ``payload`` using the same scheme ``_length_prefixed_decoder`` expects."""
    assert len(payload) < 256
    return bytes([len(payload)]) + payload


class _HarnessBinaryFramedClient(BinaryFramedSocketHandlerClient):
    """Exposes the protected attach/detach primitives for white-box testing."""

    def attach(self, sock: socket.socket) -> int:
        return self._attach(sock)

    def detach(self, expected_epoch: int, cause: str = "test disconnect") -> bool:
        return self._detach(expected_epoch, cause)


def _make_client(
    name: str, decoder: FrameDecoder = _length_prefixed_decoder
) -> _HarnessBinaryFramedClient:
    return _HarnessBinaryFramedClient(_logger(name), decoder)


class TestFragmentedAndMultiFrameDecoding:
    def test_byte_at_a_time_delivery_yields_one_frame_exactly_once(self) -> None:
        client = _make_client("byte-at-a-time")
        frames: queue.Queue[object] = queue.Queue()
        client.set_frame_handler(frames.put)
        with socketpair_context() as (left, right):
            epoch = client.attach(left)
            for byte in _frame(b"hello"):
                right.sendall(bytes([byte]))
            assert frames.get(timeout=TEST_TIMEOUT) == b"hello"
            with pytest.raises(queue.Empty):
                frames.get(timeout=SHORT_TIMEOUT)
            client.detach(epoch)

    def test_multiple_frames_in_one_chunk_are_delivered_in_order(self) -> None:
        client = _make_client("multi-frame")
        frames: queue.Queue[object] = queue.Queue()
        client.set_frame_handler(frames.put)
        with socketpair_context() as (left, right):
            epoch = client.attach(left)
            right.sendall(_frame(b"one") + _frame(b"two") + _frame(b"three"))
            assert frames.get(timeout=TEST_TIMEOUT) == b"one"
            assert frames.get(timeout=TEST_TIMEOUT) == b"two"
            assert frames.get(timeout=TEST_TIMEOUT) == b"three"
            with pytest.raises(queue.Empty):
                frames.get(timeout=SHORT_TIMEOUT)
            client.detach(epoch)

    def test_incomplete_frame_is_retained_until_completed_by_a_later_chunk(self) -> None:
        client = _make_client("retained-partial")
        frames: queue.Queue[object] = queue.Queue()
        client.set_frame_handler(frames.put)
        with socketpair_context() as (left, right):
            epoch = client.attach(left)
            full = _frame(b"payload")
            right.sendall(full[:3])
            with pytest.raises(queue.Empty):
                frames.get(timeout=SHORT_TIMEOUT)
            right.sendall(full[3:])
            assert frames.get(timeout=TEST_TIMEOUT) == b"payload"
            client.detach(epoch)

    def test_raw_and_text_callbacks_still_observe_the_same_received_chunks(self) -> None:
        client = _make_client("raw-text-preserved")
        raw_chunks: queue.Queue[bytes] = queue.Queue()
        tokens: queue.Queue[str] = queue.Queue()
        frames: queue.Queue[object] = queue.Queue()
        client.set_data_message_handler(raw_chunks.put)
        client.set_string_message_handler(tokens.put)
        client.set_frame_handler(frames.put)
        with socketpair_context() as (left, right):
            epoch = client.attach(left)
            # The binary and text channels independently decode the same raw
            # chunk: the frame's length-prefix byte (0x02) is itself valid
            # single-byte UTF-8, so it is part of the delimited text token
            # too. That is expected -- this test only asserts both channels
            # observe the identical raw bytes, not that they parse
            # independently of each other's framing.
            chunk = _frame(b"ab") + b"hi\n"
            right.sendall(chunk)
            assert raw_chunks.get(timeout=TEST_TIMEOUT) == chunk
            assert frames.get(timeout=TEST_TIMEOUT) == b"ab"
            assert tokens.get(timeout=TEST_TIMEOUT) == "\x02abhi"
            client.detach(epoch)


class TestInvalidProgressAndDecoderExceptionRecovery:
    def test_decoder_raising_clears_buffer_and_a_later_valid_frame_still_arrives(self) -> None:
        call_count = 0

        def _flaky_decoder(buffer: bytes) -> tuple[object | None, bytes]:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise RuntimeError("simulated decoder failure")
            return _length_prefixed_decoder(buffer)

        client = _make_client("decoder-raises", _flaky_decoder)
        frames: queue.Queue[object] = queue.Queue()
        client.set_frame_handler(frames.put)
        with socketpair_context() as (left, right):
            epoch = client.attach(left)
            right.sendall(_frame(b"lost"))
            with pytest.raises(queue.Empty):
                frames.get(timeout=SHORT_TIMEOUT)

            # Continue on the same connection: the buffer was cleared, so a
            # fresh frame sent afterward must still be decoded by the same
            # receive worker.
            right.sendall(_frame(b"found"))
            assert frames.get(timeout=TEST_TIMEOUT) == b"found"
            client.detach(epoch)

    def test_non_bytes_remainder_is_invalid_progress_and_clears_buffer(self) -> None:
        def _bad_type_decoder(buffer: bytes) -> tuple[object | None, bytes]:
            return None, "not-bytes"  # type: ignore[return-value]

        client = _make_client("bad-remainder-type", _bad_type_decoder)
        frames: queue.Queue[object] = queue.Queue()
        client.set_frame_handler(frames.put)
        with socketpair_context() as (left, right):
            epoch = client.attach(left)
            right.sendall(b"\x01x")
            with pytest.raises(queue.Empty):
                frames.get(timeout=SHORT_TIMEOUT)
            client.detach(epoch)

    def test_remainder_not_a_suffix_of_input_is_invalid_progress(self) -> None:
        def _non_suffix_decoder(buffer: bytes) -> tuple[object | None, bytes]:
            return b"frame", b"not-a-suffix"

        client = _make_client("non-suffix-remainder", _non_suffix_decoder)
        frames: queue.Queue[object] = queue.Queue()
        client.set_frame_handler(frames.put)
        with socketpair_context() as (left, right):
            epoch = client.attach(left)
            right.sendall(b"\x01x")
            with pytest.raises(queue.Empty):
                frames.get(timeout=SHORT_TIMEOUT)
            client.detach(epoch)

    def test_frame_with_remainder_no_shorter_than_input_is_invalid_progress(self) -> None:
        def _no_progress_decoder(buffer: bytes) -> tuple[object | None, bytes]:
            return b"frame", buffer

        client = _make_client("no-progress-with-frame", _no_progress_decoder)
        frames: queue.Queue[object] = queue.Queue()
        client.set_frame_handler(frames.put)
        with socketpair_context() as (left, right):
            epoch = client.attach(left)
            right.sendall(b"\x01x")
            with pytest.raises(queue.Empty):
                frames.get(timeout=SHORT_TIMEOUT)
            client.detach(epoch)

    def test_none_frame_with_changed_remainder_is_invalid_progress(self) -> None:
        def _changed_none_decoder(buffer: bytes) -> tuple[object | None, bytes]:
            return None, buffer[1:]

        client = _make_client("changed-none-remainder", _changed_none_decoder)
        frames: queue.Queue[object] = queue.Queue()
        client.set_frame_handler(frames.put)
        with socketpair_context() as (left, right):
            epoch = client.attach(left)
            right.sendall(b"\x01x")
            with pytest.raises(queue.Empty):
                frames.get(timeout=SHORT_TIMEOUT)
            client.detach(epoch)


class TestFrameHandlerFailureAndReconnectBufferReset:
    def test_frame_handler_exception_is_logged_and_a_later_frame_still_arrives(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        client = _make_client("handler-raises")
        frames: queue.Queue[object] = queue.Queue()
        fail_next = threading.Event()
        fail_next.set()

        def _handler(frame: object) -> None:
            if fail_next.is_set():
                fail_next.clear()
                raise RuntimeError("simulated frame handler failure")
            frames.put(frame)

        client.set_frame_handler(_handler)
        with socketpair_context() as (left, right), caplog.at_level(logging.ERROR):
            epoch = client.attach(left)
            right.sendall(_frame(b"dropped"))
            right.sendall(_frame(b"delivered"))
            assert frames.get(timeout=TEST_TIMEOUT) == b"delivered"
            client.detach(epoch)
        assert "frame handler raised" in caplog.text

    def test_replacing_the_frame_handler_only_affects_subsequent_frames(self) -> None:
        client = _make_client("replace-handler")
        first: queue.Queue[object] = queue.Queue()
        second: queue.Queue[object] = queue.Queue()
        client.set_frame_handler(first.put)
        with socketpair_context() as (left, right):
            epoch = client.attach(left)
            right.sendall(_frame(b"one"))
            assert first.get(timeout=TEST_TIMEOUT) == b"one"

            client.set_frame_handler(second.put)
            right.sendall(_frame(b"two"))
            assert second.get(timeout=TEST_TIMEOUT) == b"two"
            with pytest.raises(queue.Empty):
                first.get(timeout=SHORT_TIMEOUT)
            client.detach(epoch)

    def test_reconnect_does_not_leak_a_prior_epochs_partial_frame(self) -> None:
        client = BinaryFramedSocketHandlerClient(
            _logger("reconnect-reset"), _length_prefixed_decoder
        )
        frames: queue.Queue[object] = queue.Queue()
        client.set_frame_handler(frames.put)

        with ThreadedLoopbackListener() as first_listener:
            host1, port1 = first_listener.address
            client.connect(host1, port1, timeout=TEST_TIMEOUT)
            assert first_listener.accepted.wait(TEST_TIMEOUT)
            first_server = first_listener.accepted_socket
            assert first_server is not None

            # Leave an incomplete frame header (length byte 5) with no
            # payload buffered on the first connection.
            first_server.sendall(bytes([5]))
            with pytest.raises(queue.Empty):
                frames.get(timeout=SHORT_TIMEOUT)

            with ThreadedLoopbackListener() as second_listener:
                host2, port2 = second_listener.address
                client.connect(host2, port2, timeout=TEST_TIMEOUT)
                assert second_listener.accepted.wait(TEST_TIMEOUT)
                second_server = second_listener.accepted_socket
                assert second_server is not None

                # If the stale "expects 5 more bytes" state leaked, sending a
                # single complete short frame here would be misread as a
                # continuation of the old partial header instead of a fresh
                # length-prefixed frame.
                second_server.sendall(_frame(b"hi"))
                assert frames.get(timeout=TEST_TIMEOUT) == b"hi"

                client.disconnect()
                second_listener.release.set()
            first_listener.release.set()
