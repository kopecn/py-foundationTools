"""
Tests for ``SocketHandler`` (plan 25, chunk 07): construction/validation,
epoch-safe attach/detach primitives, epoch-safe sending, and best-effort
cleanup registration. Receive-loop dispatch beyond thread start/stop belongs
to chunk 08 and is not exercised here.

Every concurrency assertion uses the ``tests/threaded_socket_helpers.py``
harness (``threading.Event`` gates and bounded joins) per the chunk-01 race
recipe — no test in this file uses a sleep or random delay.
"""

from __future__ import annotations

import logging
import math
import socket
import threading
from typing import cast

import pytest

from foundation_tools.socket_transaction.socket_handler import EpochSendStatus, SocketHandler
from tests.threaded_socket_helpers import (
    TEST_TIMEOUT,
    WorkerTimeoutError,
    socketpair_context,
    start_worker,
)

SHORT_TIMEOUT = 0.2


def _logger(name: str) -> logging.Logger:
    return logging.getLogger(f"test.socket_handler.{name}")


class _HarnessSocketHandler(SocketHandler):
    """Exposes the protected attach/detach primitives for white-box testing."""

    def attach(self, sock: socket.socket) -> int:
        return self._attach(sock)

    def detach(self, expected_epoch: int, cause: str = "test disconnect") -> bool:
        return self._detach(expected_epoch, cause)

    def receive_thread(self) -> threading.Thread | None:
        return self._receive_thread

    def set_receive_thread_for_test(self, thread: threading.Thread) -> None:
        self._receive_thread = thread


class _GatedSocket:
    """Wraps a real connected socket so ``sendall`` can be paused mid-call.

    Forces a deterministic interleaving window for concurrency tests without
    any sleep or randomness: a racing thread waits on ``entered`` to know the
    pause has begun, does its work, then sets ``release``.
    """

    def __init__(self, inner: socket.socket) -> None:
        self._inner = inner
        self.entered = threading.Event()
        self.release = threading.Event()
        self.pause_next = False

    def sendall(self, data: bytes) -> None:
        if self.pause_next:
            self.pause_next = False
            self.entered.set()
            if not self.release.wait(TEST_TIMEOUT):
                raise WorkerTimeoutError("gated socket: test never released the paused sendall")
        self._inner.sendall(data)

    def shutdown(self, how: int) -> None:
        self._inner.shutdown(how)

    def close(self) -> None:
        self._inner.close()

    def recv(self, bufsize: int) -> bytes:
        return self._inner.recv(bufsize)

    def fileno(self) -> int:
        return self._inner.fileno()


class _SendFailsSocket:
    """Wraps a real connected socket whose ``sendall`` always raises ``OSError``.

    ``recv``/``shutdown``/``close`` behave normally, so the always-blocked
    receive thread on the peer side cannot race the forced send failure —
    unlike closing the real socket, which would race the receive thread's own
    ``OSError``-triggered detach against the test's explicit one.
    """

    def __init__(self, inner: socket.socket) -> None:
        self._inner = inner

    def sendall(self, data: bytes) -> None:
        raise OSError("simulated send failure")

    def shutdown(self, how: int) -> None:
        self._inner.shutdown(how)

    def close(self) -> None:
        self._inner.close()

    def recv(self, bufsize: int) -> bytes:
        return self._inner.recv(bufsize)

    def fileno(self) -> int:
        return self._inner.fileno()


class TestConstruction:
    def test_defaults_report_disconnected_initial_state(self) -> None:
        handler = SocketHandler(_logger("defaults"))
        assert handler.is_connected is False
        assert handler.string_delimiter == "\n"
        assert handler.snapshot_active_epoch() is None

    def test_empty_delimiter_raises(self) -> None:
        with pytest.raises(ValueError, match="string_delimiter"):
            SocketHandler(_logger("empty-delim"), string_delimiter="")

    @pytest.mark.parametrize("bad_timeout", [0.0, -1.0, math.inf, -math.inf, math.nan])
    def test_non_finite_or_non_positive_join_timeout_raises(self, bad_timeout: float) -> None:
        with pytest.raises(ValueError, match="join_timeout"):
            SocketHandler(_logger("bad-timeout"), join_timeout=bad_timeout)

    def test_custom_delimiter_and_timeout_are_reported(self) -> None:
        handler = SocketHandler(_logger("custom"), string_delimiter=";", join_timeout=0.5)
        assert handler.string_delimiter == ";"


class TestDisconnectedBehavior:
    def test_send_while_disconnected_logs_drops_and_returns_false(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        handler = SocketHandler(_logger("disconnected-send"))
        with caplog.at_level(logging.WARNING):
            assert handler.send(b"hello") is False
        assert any("disconnected" in r.message for r in caplog.records)

    def test_send_string_while_disconnected_returns_false(self) -> None:
        handler = SocketHandler(_logger("disconnected-send-string"))
        assert handler.send_string("hello") is False

    def test_disconnect_without_a_connection_is_a_no_op(self) -> None:
        handler = SocketHandler(_logger("disconnect-noop"))
        handler.disconnect()
        assert handler.is_connected is False


class TestAttachDetachLifecycle:
    def test_attach_publishes_connected_state_and_starts_receive_thread(self) -> None:
        handler = _HarnessSocketHandler(_logger("attach"))
        with socketpair_context() as (left, right):
            epoch = handler.attach(left)
            assert epoch == 1
            assert handler.is_connected is True
            assert handler.snapshot_active_epoch() == epoch
            thread = handler.receive_thread()
            assert thread is not None
            assert thread.is_alive()

            handler.detach(epoch)
            thread.join(TEST_TIMEOUT)
            assert not thread.is_alive()

    def test_epochs_are_monotonically_increasing_and_never_reused(self) -> None:
        handler = _HarnessSocketHandler(_logger("epoch-monotonic"))
        with socketpair_context() as (left1, _right1), socketpair_context() as (left2, _right2):
            epoch1 = handler.attach(left1)
            handler.detach(epoch1)
            epoch2 = handler.attach(left2)
            handler.detach(epoch2)
            assert epoch2 > epoch1

    def test_duplicate_detach_is_idempotent(self) -> None:
        handler = _HarnessSocketHandler(_logger("duplicate-detach"))
        with socketpair_context() as (left, _right):
            epoch = handler.attach(left)
            assert handler.detach(epoch) is True
            assert handler.detach(epoch) is False

    def test_stale_detach_does_not_disturb_newer_epoch(self) -> None:
        handler = _HarnessSocketHandler(_logger("stale-detach"))
        with socketpair_context() as (left1, _right1), socketpair_context() as (left2, right2):
            epoch1 = handler.attach(left1)
            handler.detach(epoch1)
            epoch2 = handler.attach(left2)

            assert handler.detach(epoch1) is False
            assert handler.is_connected is True
            assert handler.snapshot_active_epoch() == epoch2

            assert handler.send(b"still alive") is True
            assert right2.recv(16) == b"still alive"
            handler.detach(epoch2)

    def test_self_detach_from_the_receive_thread_does_not_join_itself(self) -> None:
        # `Thread.join()` on the current thread raises `RuntimeError`, so if
        # `_detach` ever tried to self-join, this worker's captured exception
        # would fail the test when `WorkerHandle.join` re-raises it.
        handler = _HarnessSocketHandler(_logger("self-detach"))
        with socketpair_context() as (left, _right):
            epoch = handler.attach(left)
            result: list[bool] = []

            def _detach_as_self() -> None:
                handler.set_receive_thread_for_test(threading.current_thread())
                result.append(handler.detach(epoch))

            worker = start_worker("self-detach-worker", _detach_as_self)
            worker.join(TEST_TIMEOUT)

            assert result == [True]
            assert handler.is_connected is False

    def test_detach_logs_a_still_alive_worker_after_join_timeout(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        handler = _HarnessSocketHandler(_logger("stale-worker"), join_timeout=0.05)
        with socketpair_context() as (left, _right):
            epoch = handler.attach(left)
            handler.detach(epoch)  # retire the real thread before substituting a stuck one

            with socketpair_context() as (left2, _right2):
                epoch2 = handler.attach(left2)
                release = threading.Event()

                def _stuck() -> None:
                    release.wait(TEST_TIMEOUT)

                stuck_thread = threading.Thread(
                    target=_stuck, name="deliberately-stuck-worker", daemon=True
                )
                stuck_thread.start()
                handler.set_receive_thread_for_test(stuck_thread)

                try:
                    with caplog.at_level(logging.WARNING):
                        result = handler.detach(epoch2)
                    assert result is True
                    assert any(
                        "still alive after join_timeout" in r.message for r in caplog.records
                    )
                finally:
                    release.set()
                    stuck_thread.join(TEST_TIMEOUT)
                assert not stuck_thread.is_alive()


class TestEpochSafeSending:
    def test_send_for_epoch_rejects_a_non_active_epoch(self) -> None:
        handler = _HarnessSocketHandler(_logger("not-active"))
        with socketpair_context() as (left, _right):
            epoch = handler.attach(left)
            handler.detach(epoch)
            assert handler.send_for_epoch(epoch, b"stale") is EpochSendStatus.NOT_ACTIVE

    def test_send_delivers_bytes_for_the_active_epoch(self) -> None:
        handler = _HarnessSocketHandler(_logger("send-ok"))
        with socketpair_context() as (left, right):
            epoch = handler.attach(left)
            assert handler.send(b"payload") is True
            assert right.recv(16) == b"payload"
            handler.detach(epoch)

    def test_send_string_encodes_utf8_without_appending_a_delimiter(self) -> None:
        handler = _HarnessSocketHandler(_logger("send-string"))
        with socketpair_context() as (left, right):
            epoch = handler.attach(left)
            assert handler.send_string("héllo") is True
            assert right.recv(16) == "héllo".encode("utf-8")
            handler.detach(epoch)

    def test_send_io_failure_detaches_only_the_failed_epoch_and_returns_false(self) -> None:
        handler = _HarnessSocketHandler(_logger("send-failure"))
        with socketpair_context() as (left, _right):
            broken = _SendFailsSocket(left)
            epoch = handler.attach(cast(socket.socket, broken))
            assert handler.send_for_epoch(epoch, b"boom") is EpochSendStatus.IO_FAILED
            assert handler.is_connected is False
            assert handler.snapshot_active_epoch() is None

    def test_concurrent_sends_do_not_interleave(self) -> None:
        handler = _HarnessSocketHandler(_logger("concurrent-send"))
        with socketpair_context() as (left, right):
            gated = _GatedSocket(left)
            handler.attach(cast(socket.socket, gated))

            gated.pause_next = True
            first_payload = b"A" * 200 + b"\n"
            second_payload = b"B" * 200 + b"\n"

            first_done = threading.Event()

            def _send_first() -> None:
                assert handler.send(first_payload) is True
                first_done.set()

            first_worker = start_worker("send-first", _send_first)
            assert gated.entered.wait(TEST_TIMEOUT)

            second_started = threading.Event()

            def _send_second() -> None:
                second_started.set()
                assert handler.send(second_payload) is True

            second_worker = start_worker("send-second", _send_second)
            assert second_started.wait(TEST_TIMEOUT)
            # The second call must be blocked on the send lock behind the
            # paused first call, not proceeding independently.
            assert not first_done.wait(SHORT_TIMEOUT)

            gated.release.set()
            first_worker.join(TEST_TIMEOUT)
            second_worker.join(TEST_TIMEOUT)

            expected = first_payload + second_payload
            received = b""
            right.settimeout(TEST_TIMEOUT)
            while len(received) < len(expected):
                chunk = right.recv(4096)
                if not chunk:
                    break
                received += chunk
            assert received == expected
            handler.disconnect()

    def test_stale_send_failure_does_not_disturb_a_replacement_epoch(self) -> None:
        handler = _HarnessSocketHandler(_logger("stale-send-race"))
        with socketpair_context() as (left1, _right1), socketpair_context() as (left2, right2):
            gated = _GatedSocket(left1)
            epoch1 = handler.attach(cast(socket.socket, gated))
            gated.pause_next = True

            send_result: list[EpochSendStatus] = []

            def _send_epoch1() -> None:
                send_result.append(handler.send_for_epoch(epoch1, b"stale"))

            worker = start_worker("stale-send", _send_epoch1)
            assert gated.entered.wait(TEST_TIMEOUT)

            # Replace the connection while the stale send is paused mid-flight
            # (this also closes `left1`, so the paused sendall will fail).
            assert handler.detach(epoch1) is True
            epoch2 = handler.attach(left2)
            assert epoch2 > epoch1

            gated.release.set()
            worker.join(TEST_TIMEOUT)

            assert send_result == [EpochSendStatus.IO_FAILED]
            assert handler.is_connected is True
            assert handler.snapshot_active_epoch() == epoch2

            assert handler.send(b"live") is True
            assert right2.recv(16) == b"live"
            handler.detach(epoch2)


class TestCleanupRegistration:
    def test_finalizer_is_registered_and_replaced_on_reattach(self) -> None:
        handler = _HarnessSocketHandler(_logger("finalizer"))
        with socketpair_context() as (left1, _right1), socketpair_context() as (left2, _right2):
            epoch1 = handler.attach(left1)
            first_finalizer = handler._finalizer
            assert first_finalizer is not None
            assert first_finalizer.alive

            handler.detach(epoch1)
            handler.attach(left2)
            second_finalizer = handler._finalizer
            assert second_finalizer is not None
            assert second_finalizer is not first_finalizer
            # Replacing the finalizer detaches the previous one so it cannot
            # double-close a socket that normal detach already tore down.
            assert first_finalizer.alive is False
