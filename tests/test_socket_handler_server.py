"""
Tests for ``SocketHandlerServer`` (plan 25, chunk 10): the listener half of
the single-client server -- bind/listen, actual bound-address publication,
listener epochs independent of the inherited connection epoch, a bounded
daemon accept worker, repeated-listen warning/no-op, and idempotent,
epoch-safe ``stop``.

Chunk 11 owns admission decisions and active-client publication; this file
only asserts that the accepted-candidate hook closes every candidate
unconditionally while chunk 11 is absent.

Fake-socket tests monkeypatch ``socket.socket`` with a recording double so
construction, options, bind/listen failures, repeated listen, address
publication, and stop ordering can be asserted deterministically without
real network I/O. Event-gated fake-socket tests prove a stale accept worker
(one still running against a retired listener epoch) cannot affect a
listener that was stopped and restarted, per the chunk's stale-listener
recipe. Real ``port=0`` tests exercise actual bind/listen/accept/close
behavior end-to-end via ``listening_address``/``is_listening``. No test in
this file uses a sleep or random delay; blocking points are gated by
``threading.Event`` and bounded by ``tests.threaded_socket_helpers.TEST_TIMEOUT``.
"""

from __future__ import annotations

import logging
import math
import socket
import threading

import pytest

from foundation_tools.socket_transaction.socket_handler_server import SocketHandlerServer
from tests.threaded_socket_helpers import TEST_TIMEOUT, WorkerTimeoutError

SHORT_TIMEOUT = 0.2


def _logger(name: str) -> logging.Logger:
    return logging.getLogger(f"test.socket_handler_server.{name}")


class _HarnessSocketHandlerServer(SocketHandlerServer):
    """Exposes protected listener internals for white-box testing.

    ``candidate_handled`` is set every time the accepted-candidate hook
    runs, so a test can deterministically wait for one accept-loop pass
    without relying on the (still-running) accept worker ever exiting.
    """

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)  # type: ignore[arg-type]
        self.candidate_handled = threading.Event()

    def current_accept_thread(self) -> threading.Thread | None:
        state = self._listener_state
        return state.thread if state is not None else None

    def current_listener_epoch(self) -> int | None:
        state = self._listener_state
        return state.epoch if state is not None else None

    def handle_accepted_candidate(
        self, epoch: int, candidate: socket.socket, peer: tuple[str, int]
    ) -> None:
        self._handle_accepted_candidate(epoch, candidate, peer)

    def _handle_accepted_candidate(
        self, epoch: int, candidate: socket.socket, peer: tuple[str, int]
    ) -> None:
        super()._handle_accepted_candidate(epoch, candidate, peer)
        self.candidate_handled.set()


class _FakeAcceptedSocket:
    """A minimal accepted-connection double that only records ``close()``."""

    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


class _FakeListenerSocket:
    """Records ``socket.socket``-shaped listener calls.

    ``accept()`` is synchronous and non-blocking by default: it returns a
    prepared candidate if one was staged with ``prepare_accept``, otherwise
    it raises immediately -- a fake stand-in for "nothing pending", so
    ordinary tests never need to wait on the daemon accept worker.

    When constructed with ``block_accept=True``, ``accept()`` instead blocks
    on an internal ``threading.Event`` until the test calls
    ``release_accept()``, independent of ``close()``. This lets a test drive
    the exact interleaving in the chunk's stale-listener recipe: the worker
    is parked inside ``accept()`` while the test retires its listener epoch
    (``stop()``) and starts a replacement (``listen()``) before the stale
    ``accept()`` is finally allowed to return.
    """

    def __init__(
        self,
        *,
        bind_error: OSError | None = None,
        listen_error: OSError | None = None,
        address: tuple[str, int] = ("0.0.0.0", 0),
        block_accept: bool = False,
    ) -> None:
        self.family: int | None = None
        self.type: int | None = None
        self.setsockopt_calls: list[tuple[int, int, int]] = []
        self.bind_calls: list[tuple[str, int]] = []
        self.listen_calls = 0
        self.close_calls = 0
        self.timeout_calls: list[float | None] = []
        self._bind_error = bind_error
        self._listen_error = listen_error
        self._address = address
        self._block_accept = block_accept
        self._release_accept = threading.Event()
        self._prepared: tuple[_FakeAcceptedSocket, tuple[str, int]] | None = None

    def setsockopt(self, level: int, optname: int, value: int) -> None:
        self.setsockopt_calls.append((level, optname, value))

    def bind(self, address: tuple[str, int]) -> None:
        self.bind_calls.append(address)
        if self._bind_error is not None:
            raise self._bind_error

    def listen(self, *args: object) -> None:
        self.listen_calls += 1
        if self._listen_error is not None:
            raise self._listen_error

    def getsockname(self) -> tuple[str, int]:
        return self._address

    def settimeout(self, value: float | None) -> None:
        self.timeout_calls.append(value)

    def prepare_accept(self, candidate: _FakeAcceptedSocket, peer: tuple[str, int]) -> None:
        self._prepared = (candidate, peer)

    def release_accept(self) -> None:
        self._release_accept.set()

    def accept(self) -> tuple[_FakeAcceptedSocket, tuple[str, int]]:
        if self._block_accept:
            if not self._release_accept.wait(TEST_TIMEOUT):
                raise WorkerTimeoutError("fake listener socket: accept() never released")
            self._release_accept.clear()
        if self._prepared is not None:
            result = self._prepared
            self._prepared = None
            return result
        raise OSError("fake listener socket: nothing pending to accept")

    def close(self) -> None:
        self.close_calls += 1


def _install_fake_listener_factory(
    monkeypatch: pytest.MonkeyPatch, *fakes: _FakeListenerSocket
) -> list[_FakeListenerSocket]:
    """Monkeypatch ``socket.socket`` to hand out ``fakes`` in order.

    Returns the list of fakes actually created (mirrors chunk 09's factory
    double so counting calls proves whether a candidate was created at all).
    """
    created: list[_FakeListenerSocket] = []
    remaining = list(fakes)

    def _factory(family: int, type_: int, *args: object, **kwargs: object) -> _FakeListenerSocket:
        fake = remaining.pop(0) if remaining else _FakeListenerSocket()
        fake.family = family
        fake.type = type_
        created.append(fake)
        return fake

    monkeypatch.setattr(socket, "socket", _factory)
    return created


class TestConstructorValidation:
    def test_defaults_construct_successfully(self) -> None:
        server = SocketHandlerServer(_logger("ctor-defaults"))
        assert server.is_listening is False
        assert server.listening_address is None

    def test_custom_accept_poll_interval_is_accepted(self) -> None:
        server = SocketHandlerServer(_logger("ctor-custom"), accept_poll_interval=0.05)
        assert server.is_listening is False

    @pytest.mark.parametrize("bad_interval", [0.0, -1.0, math.inf, -math.inf, math.nan])
    def test_non_finite_or_non_positive_accept_poll_interval_raises(
        self, bad_interval: float
    ) -> None:
        with pytest.raises(ValueError, match="accept_poll_interval"):
            SocketHandlerServer(_logger("ctor-bad-interval"), accept_poll_interval=bad_interval)

    @pytest.mark.parametrize("bad_timeout", [0.0, -1.0, math.inf, -math.inf, math.nan])
    def test_inherited_join_timeout_validation_still_applies(self, bad_timeout: float) -> None:
        with pytest.raises(ValueError, match="join_timeout"):
            SocketHandlerServer(_logger("ctor-bad-join"), join_timeout=bad_timeout)

    def test_empty_delimiter_still_raises(self) -> None:
        with pytest.raises(ValueError, match="string_delimiter"):
            SocketHandlerServer(_logger("ctor-bad-delim"), string_delimiter="")


class TestListenSocketOptionsAndAddress:
    def test_creates_af_inet_sock_stream_socket(self, monkeypatch: pytest.MonkeyPatch) -> None:
        created = _install_fake_listener_factory(monkeypatch)
        server = _HarnessSocketHandlerServer(_logger("options-family-type"))
        server.listen(12345)
        assert len(created) == 1
        assert created[0].family == socket.AF_INET
        assert created[0].type == socket.SOCK_STREAM
        server.stop()

    def test_sets_so_reuseaddr(self, monkeypatch: pytest.MonkeyPatch) -> None:
        created = _install_fake_listener_factory(monkeypatch)
        server = _HarnessSocketHandlerServer(_logger("options-reuseaddr"))
        server.listen(12345)
        assert created[0].setsockopt_calls == [
            (socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ]
        server.stop()

    def test_binds_wildcard_host_with_requested_port(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        created = _install_fake_listener_factory(monkeypatch)
        server = _HarnessSocketHandlerServer(_logger("options-bind"))
        server.listen(54321)
        assert created[0].bind_calls == [("", 54321)]
        assert created[0].listen_calls == 1
        server.stop()

    def test_publishes_getsockname_as_listening_address(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        fake = _FakeListenerSocket(address=("0.0.0.0", 47000))
        _install_fake_listener_factory(monkeypatch, fake)
        server = _HarnessSocketHandlerServer(_logger("options-address"))
        server.listen(0)
        assert server.listening_address == ("0.0.0.0", 47000)
        assert server.is_listening is True
        server.stop()

    def test_bind_failure_closes_candidate_and_raises_oserror(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        bind_error = OSError("simulated bind failure")
        fake = _FakeListenerSocket(bind_error=bind_error)
        _install_fake_listener_factory(monkeypatch, fake)
        server = _HarnessSocketHandlerServer(_logger("options-bind-fail"))

        with pytest.raises(OSError) as exc_info:
            server.listen(0)

        assert exc_info.value is bind_error
        assert fake.close_calls == 1
        assert server.is_listening is False
        assert server.listening_address is None

    def test_listen_failure_closes_candidate_and_raises_oserror(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        listen_error = OSError("simulated listen failure")
        fake = _FakeListenerSocket(listen_error=listen_error)
        _install_fake_listener_factory(monkeypatch, fake)
        server = _HarnessSocketHandlerServer(_logger("options-listen-fail"))

        with pytest.raises(OSError) as exc_info:
            server.listen(0)

        assert exc_info.value is listen_error
        assert fake.close_calls == 1
        assert server.is_listening is False
        assert server.listening_address is None

    def test_bind_failure_leaves_an_incumbent_listener_untouched(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        incumbent = _FakeListenerSocket(address=("0.0.0.0", 9000))
        _install_fake_listener_factory(monkeypatch, incumbent)
        server = _HarnessSocketHandlerServer(_logger("options-bind-fail-incumbent"))
        server.listen(9000)
        incumbent_epoch = server.current_listener_epoch()

        # A repeated listen() while already listening never even creates a
        # candidate socket, so arm no further fakes and rely on the
        # early-return check.
        server.listen(9001)

        assert server.current_listener_epoch() == incumbent_epoch
        assert server.listening_address == ("0.0.0.0", 9000)
        server.stop()


class TestRepeatedListenIsNoOp:
    def test_repeated_listen_creates_no_second_candidate(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        fake = _FakeListenerSocket(address=("0.0.0.0", 8100))
        created = _install_fake_listener_factory(monkeypatch, fake)
        server = _HarnessSocketHandlerServer(_logger("repeat-no-candidate"))
        server.listen(8100)

        server.listen(9999)

        assert len(created) == 1
        assert server.listening_address == ("0.0.0.0", 8100)
        server.stop()

    def test_repeated_listen_logs_a_warning(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        fake = _FakeListenerSocket(address=("0.0.0.0", 8200))
        _install_fake_listener_factory(monkeypatch, fake)
        server = _HarnessSocketHandlerServer(_logger("repeat-warns"))
        server.listen(8200)

        with caplog.at_level(logging.WARNING):
            server.listen(8201)

        assert any("already listening" in r.message for r in caplog.records)
        server.stop()


class TestStopOrdering:
    def test_stop_clears_state_before_returning_and_is_idempotent(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        fake = _FakeListenerSocket(address=("0.0.0.0", 8300))
        _install_fake_listener_factory(monkeypatch, fake)
        server = _HarnessSocketHandlerServer(_logger("stop-ordering"))
        server.listen(8300)
        thread = server.current_accept_thread()
        assert thread is not None

        server.stop()

        assert server.is_listening is False
        assert server.listening_address is None
        assert fake.close_calls == 1
        thread.join(TEST_TIMEOUT)
        assert not thread.is_alive()

        # Idempotent: a second stop() is a no-op, not a second close.
        server.stop()
        assert fake.close_calls == 1

    def test_stale_timed_out_worker_is_logged_and_cannot_alter_state(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        stale = _FakeListenerSocket(address=("0.0.0.0", 8400), block_accept=True)
        _install_fake_listener_factory(monkeypatch, stale)
        server = _HarnessSocketHandlerServer(_logger("stop-stale-timeout"), join_timeout=0.05)
        server.listen(8400)
        stale_thread = server.current_accept_thread()
        assert stale_thread is not None

        # The stale worker is still parked inside accept(); stop() must not
        # block forever waiting for it, only log that it outlived the bound.
        with caplog.at_level(logging.WARNING):
            server.stop()

        assert server.is_listening is False
        assert any("still alive after join_timeout" in r.message for r in caplog.records)

        # Release it now purely so the test does not leak a blocked thread.
        stale.release_accept()
        stale_thread.join(TEST_TIMEOUT)


class TestStaleAcceptWorkerCannotAffectRestartedListener:
    def test_stale_worker_closes_stale_candidate_and_leaves_new_listener_untouched(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        stale_listener = _FakeListenerSocket(address=("0.0.0.0", 8500), block_accept=True)
        replacement_listener = _FakeListenerSocket(address=("0.0.0.0", 8501))
        _install_fake_listener_factory(monkeypatch, stale_listener, replacement_listener)

        server = _HarnessSocketHandlerServer(_logger("stale-race"), join_timeout=0.05)
        server.listen(8500)
        stale_thread = server.current_accept_thread()
        stale_epoch = server.current_listener_epoch()
        assert stale_thread is not None
        assert stale_epoch is not None

        # Prepare a candidate the stale worker's accept() will eventually
        # return, but do not release it yet: the worker stays parked while
        # the listener is retired and replaced underneath it.
        stale_candidate = _FakeAcceptedSocket()
        stale_listener.prepare_accept(stale_candidate, ("198.51.100.1", 40000))

        server.stop()
        server.listen(8501)
        new_epoch = server.current_listener_epoch()
        assert new_epoch is not None
        assert new_epoch != stale_epoch

        # Only now does the stale worker's accept() return the prepared
        # candidate -- after its epoch has already been retired.
        stale_listener.release_accept()
        stale_thread.join(TEST_TIMEOUT)
        assert not stale_thread.is_alive()

        assert stale_candidate.closed is True
        assert server.is_listening is True
        assert server.listening_address == ("0.0.0.0", 8501)
        assert server.current_listener_epoch() == new_epoch
        assert replacement_listener.close_calls == 0

        server.stop()


class TestAcceptedCandidateHookClosesEveryCandidate:
    def test_handle_accepted_candidate_closes_the_candidate_unconditionally(self) -> None:
        server = _HarnessSocketHandlerServer(_logger("hook-direct"))
        candidate = _FakeAcceptedSocket()
        server.handle_accepted_candidate(
            1, candidate, ("192.0.2.1", 5555)  # type: ignore[arg-type]
        )
        assert candidate.closed is True

    def test_current_epoch_accepted_candidate_is_closed_via_the_accept_loop(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        fake = _FakeListenerSocket(address=("0.0.0.0", 8600), block_accept=True)
        _install_fake_listener_factory(monkeypatch, fake)
        server = _HarnessSocketHandlerServer(_logger("hook-via-loop"))
        server.listen(8600)
        thread = server.current_accept_thread()
        assert thread is not None

        candidate = _FakeAcceptedSocket()
        fake.prepare_accept(candidate, ("192.0.2.2", 6666))
        fake.release_accept()

        # The accept loop keeps running after handling one candidate (it
        # will call accept() again), so wait for this one hook invocation
        # rather than for the worker thread to exit.
        assert server.candidate_handled.wait(TEST_TIMEOUT)
        assert candidate.closed is True
        assert server.is_listening is True

        server.stop()


class TestRealListenerLifecycle:
    def test_listen_zero_publishes_nonzero_port_and_stop_clears_it(self) -> None:
        server = SocketHandlerServer(_logger("real-lifecycle"))
        assert server.is_listening is False
        assert server.listening_address is None

        server.listen(0)
        try:
            address = server.listening_address
            assert server.is_listening is True
            assert address is not None
            _, port = address
            assert port != 0
        finally:
            server.stop()

        assert server.is_listening is False
        assert server.listening_address is None

    def test_restart_after_stop_publishes_a_usable_address_again(self) -> None:
        server = SocketHandlerServer(_logger("real-restart"))
        server.listen(0)
        first_address = server.listening_address
        server.stop()
        assert first_address is not None

        server.listen(0)
        try:
            second_address = server.listening_address
            assert second_address is not None
            assert server.is_listening is True
        finally:
            server.stop()

    def test_repeated_stop_is_a_no_op(self) -> None:
        server = SocketHandlerServer(_logger("real-repeat-stop"))
        server.listen(0)
        server.stop()
        server.stop()
        assert server.is_listening is False

    def test_real_client_connection_is_accepted_then_closed(self) -> None:
        server = SocketHandlerServer(_logger("real-accept-close"), accept_poll_interval=0.05)
        server.listen(0)
        address = server.listening_address
        assert address is not None
        _, port = address

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(TEST_TIMEOUT)
        try:
            client.connect(("127.0.0.1", port))
            # Chunk 10 closes every accepted candidate unconditionally --
            # admission/active-client semantics arrive in chunk 11.
            assert client.recv(16) == b""
        finally:
            client.close()
            server.stop()
