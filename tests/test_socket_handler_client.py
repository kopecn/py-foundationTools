"""
Tests for ``SocketHandlerClient`` (plan 25, chunk 09): synchronous IPv4
connect with incumbent-safe reconnect, connection-timeout validation ordered
before incumbent teardown, blocking-mode restoration after a successful
connect, and candidate-socket cleanup with the original ``OSError``
propagated on failure.

Also covers chunk 17's lifecycle serialization (PA25-01): concurrent
``connect()`` calls, and a ``connect()``/``disconnect()`` race, must not
orphan a socket or receive worker.

Socket-double tests monkeypatch ``socket.socket`` itself with a recording
fake so constructor forwarding, timeout-validation order, socket
family/type, the ``connect`` call, blocking-mode restoration, and candidate
cleanup can be asserted deterministically without any real network I/O. Real
loopback tests use ``tests/threaded_socket_helpers.ThreadedLoopbackListener``
for actual connect/send/receive/disconnect and successful-reconnect
behavior. The lifecycle-serialization tests use ``threading.Event``-gated
fake candidates (never a sleep or a barrier that would deadlock once
serialization makes true internal overlap impossible) to force a
deterministic ordering between two concurrent lifecycle calls. No sleeps or
randomness are used anywhere in this file.
"""

from __future__ import annotations

import logging
import math
import queue
import socket
import threading

import pytest

from foundation_tools.socket_transaction.socket_handler_client import SocketHandlerClient
from tests.threaded_socket_helpers import TEST_TIMEOUT, ThreadedLoopbackListener, start_worker

SHORT_TIMEOUT = 0.2


def _logger(name: str) -> logging.Logger:
    return logging.getLogger(f"test.socket_handler_client.{name}")


class _HarnessSocketHandlerClient(SocketHandlerClient):
    """Exposes the protected receive-thread reference for white-box testing.

    Also records every receive thread this handler has ever attached (not
    just the current one), so a lifecycle-race test can assert that no
    worker from a superseded attach survives -- the PA25-01 failure mode was
    two live receive workers after two concurrent successful ``connect()``
    calls.
    """

    def __init__(
        self,
        logger: logging.Logger,
        *,
        string_delimiter: str = "\n",
        join_timeout: float = 1.0,
    ) -> None:
        super().__init__(logger, string_delimiter=string_delimiter, join_timeout=join_timeout)
        self.attached_threads: list[threading.Thread] = []

    def receive_thread(self) -> threading.Thread | None:
        return self._receive_thread

    def _attach(self, sock: socket.socket) -> int:
        epoch = super()._attach(sock)
        if self._receive_thread is not None:
            self.attached_threads.append(self._receive_thread)
        return epoch


class _FakeConnectSocket:
    """Records ``socket.socket``-shaped calls made by ``connect``.

    ``recv`` blocks on an internal event until ``close`` releases it, then
    raises ``OSError`` -- mirroring a real socket's behavior when a receive
    thread is blocked in ``recv`` while the socket is closed out from under
    it -- so the daemon receive thread started by a successful ``_attach``
    exits promptly once a test is done asserting connect-time state, without
    ever delivering fabricated data.
    """

    def __init__(self, connect_error: OSError | None = None) -> None:
        self.connect_error = connect_error
        self.family: int | None = None
        self.type: int | None = None
        self.settimeout_calls: list[float | None] = []
        self.connect_calls: list[tuple[str, int]] = []
        self.closed = False
        self._closed_event = threading.Event()

    def settimeout(self, value: float | None) -> None:
        self.settimeout_calls.append(value)

    def connect(self, address: tuple[str, int]) -> None:
        self.connect_calls.append(address)
        if self.connect_error is not None:
            raise self.connect_error

    def recv(self, bufsize: int) -> bytes:
        self._closed_event.wait(TEST_TIMEOUT)
        raise OSError("fake socket closed")

    def sendall(self, data: bytes) -> None:
        pass

    def shutdown(self, how: int) -> None:
        pass

    def close(self) -> None:
        self.closed = True
        self._closed_event.set()

    def fileno(self) -> int:
        return -1


def _install_fake_socket_factory(
    monkeypatch: pytest.MonkeyPatch, connect_error: OSError | None = None
) -> list[_FakeConnectSocket]:
    """Monkeypatch ``socket.socket`` to return recording fakes.

    Returns the list of fakes created, in creation order, for the test to
    inspect.
    """
    created: list[_FakeConnectSocket] = []

    def _factory(family: int, type_: int, *args: object, **kwargs: object) -> _FakeConnectSocket:
        fake = _FakeConnectSocket(connect_error)
        fake.family = family
        fake.type = type_
        created.append(fake)
        return fake

    monkeypatch.setattr(socket, "socket", _factory)
    return created


class TestConstructorForwarding:
    def test_forwards_logger_delimiter_and_join_timeout_to_socket_handler(self) -> None:
        client = SocketHandlerClient(_logger("ctor"), string_delimiter=";", join_timeout=0.5)
        assert client.string_delimiter == ";"
        assert client.is_connected is False
        assert client.snapshot_active_epoch() is None

    def test_defaults_match_socket_handler_defaults(self) -> None:
        client = SocketHandlerClient(_logger("ctor-defaults"))
        assert client.string_delimiter == "\n"

    def test_empty_delimiter_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="string_delimiter"):
            SocketHandlerClient(_logger("ctor-bad-delim"), string_delimiter="")

    @pytest.mark.parametrize("bad_timeout", [0.0, -1.0, math.inf, -math.inf, math.nan])
    def test_non_finite_or_non_positive_join_timeout_raises(self, bad_timeout: float) -> None:
        with pytest.raises(ValueError, match="join_timeout"):
            SocketHandlerClient(_logger("ctor-bad-join"), join_timeout=bad_timeout)


class TestTimeoutValidationOrder:
    @pytest.mark.parametrize("bad_timeout", [0.0, -1.0, math.inf, -math.inf, math.nan])
    def test_invalid_timeout_raises_before_disconnecting_or_creating_a_socket(
        self, monkeypatch: pytest.MonkeyPatch, bad_timeout: float
    ) -> None:
        client = SocketHandlerClient(_logger("bad-timeout"))
        with ThreadedLoopbackListener() as listener:
            host, port = listener.address
            client.connect(host, port, timeout=TEST_TIMEOUT)
            assert listener.accepted.wait(TEST_TIMEOUT)
            incumbent_epoch = client.snapshot_active_epoch()
            assert incumbent_epoch is not None

            def _fail_if_called(
                *_args: object, **_kwargs: object
            ) -> socket.socket:  # pragma: no cover - must never run
                raise AssertionError(
                    "socket.socket must not be created before timeout validation"
                )

            monkeypatch.setattr(socket, "socket", _fail_if_called)

            with pytest.raises(ValueError, match="timeout"):
                client.connect(host, port, timeout=bad_timeout)

            assert client.is_connected is True
            assert client.snapshot_active_epoch() == incumbent_epoch

            client.disconnect()
            listener.release.set()


class TestConnectSocketDouble:
    def test_creates_af_inet_sock_stream_socket(self, monkeypatch: pytest.MonkeyPatch) -> None:
        created = _install_fake_socket_factory(monkeypatch)
        client = SocketHandlerClient(_logger("family-type"))
        client.connect("example.invalid", 12345, timeout=1.0)
        assert len(created) == 1
        assert created[0].family == socket.AF_INET
        assert created[0].type == socket.SOCK_STREAM
        client.disconnect()

    def test_connect_is_called_with_host_and_port(self, monkeypatch: pytest.MonkeyPatch) -> None:
        created = _install_fake_socket_factory(monkeypatch)
        client = SocketHandlerClient(_logger("connect-call"))
        client.connect("example.invalid", 12345, timeout=1.0)
        assert created[0].connect_calls == [("example.invalid", 12345)]
        client.disconnect()

    def test_timeout_is_applied_then_blocking_mode_is_restored_after_success(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        created = _install_fake_socket_factory(monkeypatch)
        client = SocketHandlerClient(_logger("blocking-restore"))
        client.connect("example.invalid", 12345, timeout=2.5)
        assert created[0].settimeout_calls == [2.5, None]
        client.disconnect()

    def test_none_timeout_selects_default_blocking_connect_behavior(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        created = _install_fake_socket_factory(monkeypatch)
        client = SocketHandlerClient(_logger("none-timeout"))
        client.connect("example.invalid", 12345, timeout=None)
        assert created[0].settimeout_calls == [None, None]
        client.disconnect()

    def test_successful_connect_attaches_and_reports_connected(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        created = _install_fake_socket_factory(monkeypatch)
        client = _HarnessSocketHandlerClient(_logger("attach"))
        client.connect("example.invalid", 12345, timeout=1.0)
        assert client.is_connected is True
        assert client.snapshot_active_epoch() == 1
        assert client.receive_thread() is not None
        client.disconnect()
        assert created[0].closed is True

    def test_failed_connect_closes_the_candidate_and_reraises_the_original_oserror(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        original_error = OSError("simulated connection refused")
        created = _install_fake_socket_factory(monkeypatch, connect_error=original_error)
        client = _HarnessSocketHandlerClient(_logger("candidate-cleanup"))

        with pytest.raises(OSError) as exc_info:
            client.connect("example.invalid", 12345, timeout=1.0)

        assert exc_info.value is original_error
        assert created[0].closed is True
        assert client.is_connected is False
        assert client.snapshot_active_epoch() is None
        assert client.receive_thread() is None

    def test_failed_replacement_leaves_the_handler_disconnected_and_candidate_closed(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # First connect succeeds (attaches a fresh fake socket); the second
        # connect's candidate fails, so the incumbent -- already disconnected
        # by the second call before its candidate is even created -- must
        # not come back, and the failed candidate must be closed.
        client = _HarnessSocketHandlerClient(_logger("failed-replacement"))
        _install_fake_socket_factory(monkeypatch)
        client.connect("example.invalid", 12345, timeout=1.0)
        assert client.is_connected is True

        failing_error = OSError("simulated replacement failure")
        created = _install_fake_socket_factory(monkeypatch, connect_error=failing_error)

        with pytest.raises(OSError) as exc_info:
            client.connect("example.invalid", 12346, timeout=1.0)

        assert exc_info.value is failing_error
        assert created[0].closed is True
        assert client.is_connected is False
        assert client.snapshot_active_epoch() is None
        assert client.receive_thread() is None


class TestConcurrentConnectLifecycleSerialization:
    """PA25-01 regression: two concurrent successful ``connect()`` calls must
    not publish two live receive workers or leave a candidate unclosed.

    The first candidate's ``connect()`` blocks (via an ``Event``) until the
    test releases it, which -- once the lifecycle lock in chunk 17 is held
    across candidate connect -- guarantees the second ``connect()`` call
    cannot even begin its own critical section until the first finishes.
    This makes the winning epoch, and which candidate ends up closed,
    deterministic instead of scheduler-dependent.
    """

    def test_concurrent_connects_leave_one_incumbent_and_no_orphaned_worker(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        entered_first_connect = threading.Event()
        release_first_connect = threading.Event()
        created: list[_FakeConnectSocket] = []

        class _BlockingFirstSocket(_FakeConnectSocket):
            def connect(self, address: tuple[str, int]) -> None:
                entered_first_connect.set()
                assert release_first_connect.wait(TEST_TIMEOUT)
                super().connect(address)

        def _factory(family: int, type_: int, *_a: object, **_k: object) -> _FakeConnectSocket:
            fake: _FakeConnectSocket
            fake = _BlockingFirstSocket() if not created else _FakeConnectSocket()
            fake.family = family
            fake.type = type_
            created.append(fake)
            return fake

        monkeypatch.setattr(socket, "socket", _factory)

        client = _HarnessSocketHandlerClient(_logger("concurrent-connect"))

        first = start_worker(
            "connect-first", lambda: client.connect("example.invalid", 1, timeout=1.0)
        )
        assert entered_first_connect.wait(TEST_TIMEOUT)

        second = start_worker(
            "connect-second", lambda: client.connect("example.invalid", 2, timeout=1.0)
        )

        release_first_connect.set()

        first.join(TEST_TIMEOUT)
        second.join(TEST_TIMEOUT)

        assert len(created) == 2
        first_candidate, second_candidate = created

        alive_after_connects = [t for t in client.attached_threads if t.is_alive()]
        assert len(alive_after_connects) == 1
        assert alive_after_connects[0] is client.receive_thread()

        assert client.is_connected is True
        assert first_candidate.closed is True
        assert second_candidate.closed is False

        client.disconnect()

        assert client.is_connected is False
        assert second_candidate.closed is True
        assert all(not t.is_alive() for t in client.attached_threads)


class TestConnectDisconnectInterleaving:
    """A public ``disconnect()`` racing an in-flight ``connect()`` must
    serialize behind it and then tear down what it attached, rather than
    completing as a no-op against a not-yet-attached candidate.
    """

    def test_disconnect_started_during_connect_waits_then_tears_it_down(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        entered_connect = threading.Event()
        release_connect = threading.Event()

        class _BlockingSocket(_FakeConnectSocket):
            def connect(self, address: tuple[str, int]) -> None:
                entered_connect.set()
                assert release_connect.wait(TEST_TIMEOUT)
                super().connect(address)

        created: list[_FakeConnectSocket] = []

        def _factory(family: int, type_: int, *_a: object, **_k: object) -> _FakeConnectSocket:
            fake = _BlockingSocket()
            fake.family = family
            fake.type = type_
            created.append(fake)
            return fake

        monkeypatch.setattr(socket, "socket", _factory)

        client = _HarnessSocketHandlerClient(_logger("connect-disconnect-race"))

        connect_worker = start_worker(
            "connect-in-flight",
            lambda: client.connect("example.invalid", 12345, timeout=1.0),
        )
        assert entered_connect.wait(TEST_TIMEOUT)

        disconnect_worker = start_worker("disconnect-in-flight", client.disconnect)

        release_connect.set()

        connect_worker.join(TEST_TIMEOUT)
        disconnect_worker.join(TEST_TIMEOUT)

        assert client.is_connected is False
        assert client.snapshot_active_epoch() is None
        assert len(created) == 1
        assert created[0].closed is True
        assert all(not t.is_alive() for t in client.attached_threads)


class TestConnectRealLoopback:
    def test_connect_send_receive_and_disconnect_over_real_loopback(self) -> None:
        client = SocketHandlerClient(_logger("real-loopback"))
        received: queue.Queue[bytes] = queue.Queue()
        client.set_data_message_handler(received.put)

        with ThreadedLoopbackListener() as listener:
            host, port = listener.address
            client.connect(host, port, timeout=TEST_TIMEOUT)
            assert listener.accepted.wait(TEST_TIMEOUT)
            server_socket = listener.accepted_socket
            assert server_socket is not None

            assert client.is_connected is True
            assert client.send(b"hello") is True
            assert server_socket.recv(16) == b"hello"

            server_socket.sendall(b"world")
            assert received.get(timeout=TEST_TIMEOUT) == b"world"

            client.disconnect()
            assert client.is_connected is False

            listener.release.set()

    def test_successful_reconnect_disconnects_incumbent_and_starts_fresh_epoch(self) -> None:
        client = SocketHandlerClient(_logger("reconnect"))
        with ThreadedLoopbackListener() as first_listener:
            host1, port1 = first_listener.address
            client.connect(host1, port1, timeout=TEST_TIMEOUT)
            assert first_listener.accepted.wait(TEST_TIMEOUT)
            epoch1 = client.snapshot_active_epoch()
            assert epoch1 is not None
            first_server_socket = first_listener.accepted_socket
            assert first_server_socket is not None

            with ThreadedLoopbackListener() as second_listener:
                host2, port2 = second_listener.address
                client.connect(host2, port2, timeout=TEST_TIMEOUT)
                assert second_listener.accepted.wait(TEST_TIMEOUT)
                epoch2 = client.snapshot_active_epoch()
                assert epoch2 is not None
                assert epoch2 > epoch1

                # The incumbent (epoch1) must have been disconnected before
                # the replacement was attached: its peer socket observes EOF.
                first_server_socket.settimeout(TEST_TIMEOUT)
                assert first_server_socket.recv(16) == b""

                second_server_socket = second_listener.accepted_socket
                assert second_server_socket is not None
                assert client.send(b"fresh") is True
                assert second_server_socket.recv(16) == b"fresh"

                client.disconnect()
                second_listener.release.set()
            first_listener.release.set()
