"""
Self-tests for tests/threaded_socket_helpers.py (plan 25, chunk 01): the shared
deterministic threading/socket test support future threaded-socket-transaction
chunks depend on. No test in this file uses a fixed or nondeterministic delay;
every coordination point is a ``threading.Event`` wait or a bounded join.
"""

from __future__ import annotations

import socket
import threading

import pytest

from tests.threaded_socket_helpers import (
    TEST_TIMEOUT,
    ThreadedLoopbackListener,
    WorkerTimeoutError,
    socketpair_context,
    start_worker,
)

SHORT_TIMEOUT = 0.2


class TestThreadedLoopbackListener:
    def test_publishes_actual_bound_address(self) -> None:
        with ThreadedLoopbackListener() as listener:
            host, port = listener.address
            assert host == "127.0.0.1"
            assert port > 0

            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                client.connect((host, port))
                assert listener.accepted.wait(listener.timeout)
                assert listener.accepted_socket is not None
            finally:
                listener.release.set()
                client.close()

    def test_accepted_then_release_then_stopped_ordering(self) -> None:
        with ThreadedLoopbackListener() as listener:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                client.connect(listener.address)
                assert listener.accepted.wait(listener.timeout)

                # The accept thread is parked on `release`; it must not stop yet.
                assert not listener.stopped.wait(SHORT_TIMEOUT)

                listener.release.set()
                assert listener.stopped.wait(listener.timeout)
            finally:
                client.close()

    def test_sockets_closed_after_context_exit(self) -> None:
        with ThreadedLoopbackListener() as listener:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                client.connect(listener.address)
                assert listener.accepted.wait(listener.timeout)
            finally:
                listener.release.set()
                client.close()

        assert listener.accepted_socket is not None
        assert listener.accepted_socket.fileno() == -1
        assert listener.listen_socket.fileno() == -1

    def test_context_exit_raises_when_release_never_set(self) -> None:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            with pytest.raises(WorkerTimeoutError, match="threaded-loopback-listener"):
                with ThreadedLoopbackListener(timeout=SHORT_TIMEOUT) as listener:
                    client.connect(listener.address)
                    assert listener.accepted.wait(listener.timeout)
                    # Deliberately never set `release` — the bound must trip.
        finally:
            client.close()


class TestWorkerHandle:
    def test_exception_propagates_from_owning_context_manager(self) -> None:
        def _boom() -> None:
            raise ValueError("boom")

        with pytest.raises(ValueError, match="boom"):
            with start_worker("boom-worker", _boom):
                pass

    def test_join_raises_with_worker_name_when_bound_exceeded(self) -> None:
        release = threading.Event()

        def _blocks_until_released() -> None:
            release.wait(TEST_TIMEOUT)

        handle = start_worker("stuck-worker", _blocks_until_released)
        try:
            with pytest.raises(WorkerTimeoutError, match="stuck-worker"):
                handle.join(timeout=SHORT_TIMEOUT)
            assert handle.is_alive()
        finally:
            release.set()
            handle.join(TEST_TIMEOUT)
        assert not handle.is_alive()


class TestSocketpairContext:
    def test_pair_is_connected_and_closed_after_exit(self) -> None:
        with socketpair_context() as (left, right):
            left.sendall(b"ping")
            assert right.recv(4) == b"ping"

        assert left.fileno() == -1
        assert right.fileno() == -1
