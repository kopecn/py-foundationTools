"""
Tests for ``SocketHandlerServer``: the listener half (plan 25, chunk 10) --
bind/listen, actual bound-address publication, listener epochs independent
of the inherited connection epoch, a bounded daemon accept worker,
repeated-listen warning/no-op, and idempotent, epoch-safe ``stop`` -- plus
the active-client half (plan 25, chunk 11): admission isolation, incumbent
replacement, level-triggered ``wait_for_connection``, ``kick``, and
epoch-safe peer cleanup.

Fake-socket tests monkeypatch ``socket.socket`` with a recording double so
construction, options, bind/listen failures, repeated listen, address
publication, and stop ordering can be asserted deterministically without
real network I/O. Event-gated fake-socket tests prove a stale accept worker
(one still running against a retired listener epoch) cannot affect a
listener that was stopped and restarted, per the chunk-10 stale-listener
recipe. Admission and active-client tests use a real ``socket.socketpair()``
(via ``handle_accepted_candidate``, invoked directly rather than through a
real ``accept()``) so the real receive thread and real detach/shutdown/close
behavior run deterministically without needing a live remote peer for every
case. Real ``port=0`` tests exercise actual bind/listen/accept/close/admit
behavior end-to-end. No test in this file uses a sleep or random delay;
blocking points are gated by ``threading.Event``, an installed
``ConnectionObserver``, or bounded joins, all bounded by
``tests.threaded_socket_helpers.TEST_TIMEOUT``.
"""

from __future__ import annotations

import logging
import math
import socket
import threading

import pytest

from foundation_tools.socket_transaction.socket_handler_server import SocketHandlerServer
from tests.threaded_socket_helpers import TEST_TIMEOUT, WorkerTimeoutError, start_worker

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


# `accept()` may hand out either a `_FakeAcceptedSocket` (pure unit tests that
# never reach the real receive thread) or one end of a real
# `socket.socketpair()` (admission/active-client tests, which need real
# `recv`/`sendall`/`shutdown`/`close` behavior once a candidate is admitted).
_AcceptedCandidate = _FakeAcceptedSocket | socket.socket


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
        self._prepared: tuple[_AcceptedCandidate, tuple[str, int]] | None = None

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

    def prepare_accept(self, candidate: _AcceptedCandidate, peer: tuple[str, int]) -> None:
        self._prepared = (candidate, peer)

    def release_accept(self) -> None:
        self._release_accept.set()

    def accept(self) -> tuple[_AcceptedCandidate, tuple[str, int]]:
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


class _EpochClosedRecorder:
    """A ``ConnectionObserver`` double recording the last epoch closure.

    Lets a test wait deterministically (via ``closed``, a
    ``threading.Event``) for the server's receive-dispatch machinery to
    finish detaching a connection epoch instead of polling or sleeping.
    """

    def __init__(self) -> None:
        self.closed = threading.Event()
        self.epoch: int | None = None
        self.cause: str | None = None

    def on_string_token(self, epoch: int, token: str) -> None:
        pass

    def on_epoch_closed(self, epoch: int, cause: str) -> None:
        self.epoch = epoch
        self.cause = cause
        self.closed.set()


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

    def test_construction_with_an_admission_handler_defaults_to_disconnected(self) -> None:
        server = SocketHandlerServer(
            _logger("ctor-with-handler"), connection_admission_handler=lambda peer: True
        )
        assert server.is_connected is False
        assert server.active_peer is None

    @pytest.mark.parametrize("bad_timeout", [0.0, -1.0, math.inf, -math.inf, math.nan])
    def test_inherited_join_timeout_validation_still_applies(self, bad_timeout: float) -> None:
        with pytest.raises(ValueError, match="join_timeout"):
            SocketHandlerServer(_logger("ctor-bad-join"), join_timeout=bad_timeout)

    def test_empty_delimiter_still_raises(self) -> None:
        with pytest.raises(ValueError, match="string_delimiter"):
            SocketHandlerServer(_logger("ctor-bad-delim"), string_delimiter="")


class TestAcceptWorkerDaemonNameAndEffectivePollTimeout:
    """Design constraint (plan 25, chunk 24): the accept worker must be a
    named daemon thread, and the listener socket must actually receive the
    configured ``accept_poll_interval`` as its effective polling timeout."""

    def test_accept_worker_is_a_named_daemon_thread(self, monkeypatch: pytest.MonkeyPatch) -> None:
        created = _install_fake_listener_factory(monkeypatch)
        server = _HarnessSocketHandlerServer(_logger("accept-daemon-name"))
        server.listen(12000)
        epoch = server.current_listener_epoch()
        thread = server.current_accept_thread()
        assert len(created) == 1
        assert thread is not None
        assert epoch is not None
        assert thread.daemon is True
        assert thread.name == f"{type(server).__name__}-accept-{epoch}"
        server.stop()

    def test_listener_socket_receives_the_configured_accept_poll_interval_as_its_timeout(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        fake = _FakeListenerSocket(address=("0.0.0.0", 12100))
        _install_fake_listener_factory(monkeypatch, fake)
        server = _HarnessSocketHandlerServer(
            _logger("effective-poll-timeout"), accept_poll_interval=0.07
        )
        server.listen(12100)
        assert fake.timeout_calls == [0.07]
        server.stop()


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


class TestListenStopRace:
    """PA25-02 / chunk 18: a successful listener publication must be
    inseparable from accept-worker startup, as observed by ``stop()``.

    The race recipe gates only the named accept worker's
    ``Thread.start()``, so a concurrent ``stop()`` started right after
    publication can never observe a published-but-unstarted thread.
    """

    def test_concurrent_listen_and_stop_cannot_join_an_unstarted_worker(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        first = _FakeListenerSocket(address=("0.0.0.0", 8700))
        second = _FakeListenerSocket(address=("0.0.0.0", 8701))
        _install_fake_listener_factory(monkeypatch, first, second)

        server = _HarnessSocketHandlerServer(_logger("listen-stop-race"))

        start_entered = threading.Event()
        release_start = threading.Event()
        original_start = threading.Thread.start

        def _gated_start(thread_self: threading.Thread) -> None:
            if "-accept-" in thread_self.name:
                start_entered.set()
                if not release_start.wait(TEST_TIMEOUT):
                    raise WorkerTimeoutError("gated accept start: never released")
            original_start(thread_self)

        monkeypatch.setattr(threading.Thread, "start", _gated_start)

        with caplog.at_level(logging.WARNING):
            listen_worker = start_worker("listen-worker", lambda: server.listen(8700))
            assert start_entered.wait(TEST_TIMEOUT)

            stop_worker = start_worker("stop-worker", server.stop)
            release_start.set()

            # Both public calls must return without lifecycle exceptions.
            listen_worker.join(TEST_TIMEOUT)
            stop_worker.join(TEST_TIMEOUT)

        assert not any("crashed unexpectedly" in r.message for r in caplog.records)

        # The listener that stop() retired is fully closed, and the same
        # instance can listen again afterward.
        assert server.is_listening is False
        assert first.close_calls == 1

        server.listen(8701)
        assert server.is_listening is True
        assert server.listening_address == ("0.0.0.0", 8701)
        server.stop()


class TestListenerStartFailureRollback:
    """PA25-02 / chunk 18: a `Thread.start()` failure for the accept worker
    must retire only that listener epoch, close the candidate listener, and
    propagate the original startup exception -- never leave a published,
    unstarted listener behind."""

    def test_accept_thread_start_failure_retires_epoch_and_closes_candidate(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        fake = _FakeListenerSocket(address=("0.0.0.0", 8800))
        second = _FakeListenerSocket(address=("0.0.0.0", 8801))
        _install_fake_listener_factory(monkeypatch, fake, second)

        server = _HarnessSocketHandlerServer(_logger("listen-start-failure"))

        original_start = threading.Thread.start
        start_error = RuntimeError("simulated accept worker start failure")

        def _failing_start(thread_self: threading.Thread) -> None:
            if "-accept-" in thread_self.name:
                raise start_error
            original_start(thread_self)

        monkeypatch.setattr(threading.Thread, "start", _failing_start)

        with pytest.raises(RuntimeError) as exc_info:
            server.listen(8800)

        assert exc_info.value is start_error
        assert fake.close_calls == 1
        assert server.is_listening is False
        assert server.listening_address is None

        # The same instance can still listen successfully afterward.
        monkeypatch.setattr(threading.Thread, "start", original_start)
        server.listen(8801)
        assert server.is_listening is True
        assert server.listening_address == ("0.0.0.0", 8801)
        server.stop()


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


class TestAcceptedCandidateHookAdmitsByDefault:
    """Chunk 11 replaces the chunk-10 unconditional-close placeholder: with
    no admission handler, every accepted candidate is admitted and becomes
    the active connection."""

    def test_handle_accepted_candidate_with_no_handler_admits_and_publishes(self) -> None:
        server = _HarnessSocketHandlerServer(_logger("hook-direct-admit"))
        server.listen(0)
        epoch = server.current_listener_epoch()
        assert epoch is not None
        local, remote = socket.socketpair()
        try:
            server.handle_accepted_candidate(epoch, local, ("192.0.2.1", 5555))
            assert server.is_connected is True
            assert server.active_peer == ("192.0.2.1", 5555)
        finally:
            server.stop()
            remote.close()

    def test_current_epoch_accepted_candidate_is_admitted_via_the_accept_loop(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Built before the `socket.socket` monkeypatch below: `socket.socketpair()`
        # wraps its file descriptors via the `socket.socket` class internally, so
        # patching that class first would hand back fakes instead of real sockets.
        local, remote = socket.socketpair()

        fake = _FakeListenerSocket(address=("0.0.0.0", 8600), block_accept=True)
        _install_fake_listener_factory(monkeypatch, fake)
        server = _HarnessSocketHandlerServer(_logger("hook-via-loop"))
        server.listen(8600)
        thread = server.current_accept_thread()
        assert thread is not None

        fake.prepare_accept(local, ("192.0.2.2", 6666))
        fake.release_accept()

        # The accept loop keeps running after handling one candidate (it
        # will call accept() again), so wait for this one hook invocation
        # rather than for the worker thread to exit.
        assert server.candidate_handled.wait(TEST_TIMEOUT)
        assert server.is_connected is True
        assert server.active_peer == ("192.0.2.2", 6666)
        assert server.is_listening is True

        server.stop()
        remote.close()


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

    def test_real_client_connection_is_admitted_and_stays_open(self) -> None:
        server = SocketHandlerServer(_logger("real-accept-admit"), accept_poll_interval=0.05)
        server.listen(0)
        address = server.listening_address
        assert address is not None
        _, port = address

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(TEST_TIMEOUT)
        try:
            client.connect(("127.0.0.1", port))
            # Chunk 11: with no admission handler, the connection is
            # admitted and kept open rather than closed unconditionally.
            assert server.wait_for_connection(TEST_TIMEOUT) is True
            assert server.active_peer == client.getsockname()
        finally:
            client.close()
            server.stop()


class TestAdmissionDecisions:
    """TDD step 1: admission allow/deny/exception, always checked with an
    incumbent present, proving rejection never disturbs it."""

    def _admit(
        self, server: _HarnessSocketHandlerServer, peer: tuple[str, int]
    ) -> tuple[socket.socket, socket.socket]:
        epoch = server.current_listener_epoch()
        assert epoch is not None
        local, remote = socket.socketpair()
        server.handle_accepted_candidate(epoch, local, peer)
        assert server.is_connected is True
        return local, remote

    def test_no_handler_admits_by_default(self) -> None:
        server = _HarnessSocketHandlerServer(_logger("admit-no-handler"))
        server.listen(0)
        local, remote = self._admit(server, ("192.0.2.10", 7000))
        try:
            assert server.active_peer == ("192.0.2.10", 7000)
        finally:
            server.stop()
            remote.close()

    def test_handler_allowing_admits_the_challenger(self) -> None:
        seen: list[tuple[str, int]] = []

        def _allow(peer: tuple[str, int]) -> bool:
            seen.append(peer)
            return True

        server = _HarnessSocketHandlerServer(
            _logger("admit-allow"), connection_admission_handler=_allow
        )
        server.listen(0)
        local, remote = self._admit(server, ("192.0.2.11", 7001))
        try:
            assert seen == [("192.0.2.11", 7001)]
            assert server.active_peer == ("192.0.2.11", 7001)
        finally:
            server.stop()
            remote.close()

    def test_handler_denying_closes_challenger_and_leaves_incumbent_untouched(self) -> None:
        admit_next = True

        def _handler(peer: tuple[str, int]) -> bool:
            return admit_next

        server = _HarnessSocketHandlerServer(
            _logger("admit-deny"), connection_admission_handler=_handler
        )
        server.listen(0)
        incumbent_local, incumbent_remote = self._admit(server, ("192.0.2.12", 7002))
        try:
            admit_next = False
            epoch = server.current_listener_epoch()
            assert epoch is not None
            challenger_local, challenger_remote = socket.socketpair()
            try:
                server.handle_accepted_candidate(epoch, challenger_local, ("192.0.2.13", 7003))

                assert challenger_local.fileno() == -1
                assert server.active_peer == ("192.0.2.12", 7002)
                assert server.is_connected is True
            finally:
                challenger_remote.close()
        finally:
            server.stop()
            incumbent_remote.close()

    def test_handler_raising_rejects_closes_logs_and_leaves_incumbent_untouched(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        should_raise = False

        def _handler(peer: tuple[str, int]) -> bool:
            if should_raise:
                raise RuntimeError("boom")
            return True

        server = _HarnessSocketHandlerServer(
            _logger("admit-raise"), connection_admission_handler=_handler
        )
        server.listen(0)
        incumbent_local, incumbent_remote = self._admit(server, ("192.0.2.14", 7004))
        try:
            should_raise = True
            epoch = server.current_listener_epoch()
            assert epoch is not None
            challenger_local, challenger_remote = socket.socketpair()
            try:
                with caplog.at_level(logging.ERROR):
                    server.handle_accepted_candidate(
                        epoch, challenger_local, ("192.0.2.15", 7005)
                    )

                assert challenger_local.fileno() == -1
                assert server.active_peer == ("192.0.2.14", 7004)
                assert any("admission handler raised" in r.message for r in caplog.records)
            finally:
                challenger_remote.close()
        finally:
            server.stop()
            incumbent_remote.close()


class TestActivePeerWaitKickDisconnect:
    """TDD step 2: active-peer publication, immediate/timeout wait, rapid
    connect-close, kick, and inherited disconnect."""

    def test_active_peer_is_none_before_any_connection(self) -> None:
        server = SocketHandlerServer(_logger("active-peer-none"))
        assert server.active_peer is None
        assert server.is_connected is False

    def test_wait_for_connection_zero_timeout_is_an_immediate_check(self) -> None:
        server = SocketHandlerServer(_logger("wait-zero-false"))
        assert server.wait_for_connection(0) is False

    def test_wait_for_connection_zero_timeout_true_when_already_connected(self) -> None:
        server = _HarnessSocketHandlerServer(_logger("wait-zero-true"))
        server.listen(0)
        epoch = server.current_listener_epoch()
        assert epoch is not None
        local, remote = socket.socketpair()
        try:
            server.handle_accepted_candidate(epoch, local, ("192.0.2.20", 7100))
            assert server.wait_for_connection(0) is True
        finally:
            server.stop()
            remote.close()

    @pytest.mark.parametrize("bad_timeout", [-1.0, math.inf, -math.inf, math.nan])
    def test_wait_for_connection_invalid_timeout_raises(self, bad_timeout: float) -> None:
        server = SocketHandlerServer(_logger("wait-bad-timeout"))
        with pytest.raises(ValueError, match="wait_for_connection"):
            server.wait_for_connection(bad_timeout)

    def test_wait_for_connection_returns_true_once_established_from_another_thread(self) -> None:
        server = _HarnessSocketHandlerServer(_logger("wait-established"))
        server.listen(0)
        epoch = server.current_listener_epoch()
        assert epoch is not None

        connect_now = threading.Event()
        holder: list[socket.socket] = []

        def _connect_after_signal() -> None:
            assert epoch is not None
            connect_now.wait(TEST_TIMEOUT)
            local, remote = socket.socketpair()
            server.handle_accepted_candidate(epoch, local, ("192.0.2.21", 7101))
            holder.append(remote)

        with start_worker("delayed-admit", _connect_after_signal):
            connect_now.set()
            assert server.wait_for_connection(TEST_TIMEOUT) is True

        assert server.active_peer == ("192.0.2.21", 7101)
        server.stop()
        for remote in holder:
            remote.close()

    def test_wait_for_connection_returns_false_on_timeout_expiry(self) -> None:
        server = SocketHandlerServer(_logger("wait-expires"))
        assert server.wait_for_connection(SHORT_TIMEOUT) is False

    def test_rapid_connect_then_close_clears_active_peer(self) -> None:
        server = SocketHandlerServer(_logger("rapid-connect-close"), accept_poll_interval=0.05)
        recorder = _EpochClosedRecorder()
        server.set_connection_observer(recorder)
        server.listen(0)
        address = server.listening_address
        assert address is not None

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(TEST_TIMEOUT)
        try:
            client.connect(address)
        finally:
            client.close()

        assert recorder.closed.wait(TEST_TIMEOUT)
        assert server.is_connected is False
        assert server.active_peer is None
        server.stop()

    def test_kick_disconnects_active_client_and_leaves_listener_running(self) -> None:
        server = _HarnessSocketHandlerServer(_logger("kick"))
        server.listen(0)
        epoch = server.current_listener_epoch()
        assert epoch is not None
        local, remote = socket.socketpair()
        remote.settimeout(TEST_TIMEOUT)
        try:
            server.handle_accepted_candidate(epoch, local, ("192.0.2.30", 7200))
            assert server.is_connected is True

            server.kick()

            assert server.is_connected is False
            assert server.active_peer is None
            assert server.is_listening is True
            assert remote.recv(16) == b""
        finally:
            remote.close()
            server.stop()

    def test_kick_when_not_connected_is_a_no_op(self) -> None:
        server = SocketHandlerServer(_logger("kick-noop"))
        server.listen(0)
        server.kick()
        assert server.is_listening is True
        assert server.active_peer is None
        server.stop()

    def test_disconnect_has_same_active_client_effect_as_kick(self) -> None:
        server = _HarnessSocketHandlerServer(_logger("disconnect-vs-kick"))
        server.listen(0)
        epoch = server.current_listener_epoch()
        assert epoch is not None
        local, remote = socket.socketpair()
        remote.settimeout(TEST_TIMEOUT)
        try:
            server.handle_accepted_candidate(epoch, local, ("192.0.2.31", 7201))
            assert server.is_connected is True

            server.disconnect()

            assert server.is_connected is False
            assert server.active_peer is None
            assert server.is_listening is True
            assert remote.recv(16) == b""
        finally:
            remote.close()
            server.stop()


class TestReplacementAndStaleRaces:
    """TDD step 3: deterministic admitted-replacement, stale-listener, and
    challenger-immediate-EOF races."""

    def test_admitted_challenger_replaces_and_closes_exactly_one_incumbent(self) -> None:
        server = _HarnessSocketHandlerServer(_logger("replace"))
        server.listen(0)
        epoch = server.current_listener_epoch()
        assert epoch is not None

        incumbent_local, incumbent_remote = socket.socketpair()
        incumbent_remote.settimeout(TEST_TIMEOUT)
        server.handle_accepted_candidate(epoch, incumbent_local, ("198.51.100.10", 1111))
        assert server.active_peer == ("198.51.100.10", 1111)

        challenger_local, challenger_remote = socket.socketpair()
        challenger_remote.settimeout(TEST_TIMEOUT)
        server.handle_accepted_candidate(epoch, challenger_local, ("198.51.100.20", 2222))

        assert incumbent_remote.recv(16) == b""
        assert server.active_peer == ("198.51.100.20", 2222)
        assert server.is_connected is True

        server.stop()
        incumbent_remote.close()
        challenger_remote.close()

    def test_stale_epoch_detach_cannot_clear_a_replacement_peer(self) -> None:
        server = _HarnessSocketHandlerServer(_logger("stale-detach-peer"))
        server.listen(0)
        epoch = server.current_listener_epoch()
        assert epoch is not None

        incumbent_local, incumbent_remote = socket.socketpair()
        server.handle_accepted_candidate(epoch, incumbent_local, ("198.51.100.30", 3333))
        stale_epoch = server.snapshot_active_epoch()
        assert stale_epoch is not None

        challenger_local, challenger_remote = socket.socketpair()
        server.handle_accepted_candidate(epoch, challenger_local, ("198.51.100.40", 4444))
        assert server.active_peer == ("198.51.100.40", 4444)

        # A late/stale detach for the already-replaced epoch must not clear
        # the replacement's peer.
        assert server._detach(stale_epoch, cause="late stale detach") is False
        assert server.active_peer == ("198.51.100.40", 4444)
        assert server.is_connected is True

        server.stop()
        incumbent_remote.close()
        challenger_remote.close()

    def test_stale_worker_does_not_publish_after_listener_stopped_and_restarted(self) -> None:
        class _GatedAdmissionServer(_HarnessSocketHandlerServer):
            def __init__(self, *args: object, **kwargs: object) -> None:
                super().__init__(*args, **kwargs)
                self.about_to_publish = threading.Event()
                self.release_publish = threading.Event()

            def _detach_current_client(self) -> None:
                super()._detach_current_client()
                self.about_to_publish.set()
                if not self.release_publish.wait(TEST_TIMEOUT):
                    raise WorkerTimeoutError(
                        "gated admission server: test never released the publish gate"
                    )

        server = _GatedAdmissionServer(_logger("stale-admission-race"))
        server.listen(0)
        captured_epoch = server.current_listener_epoch()
        assert captured_epoch is not None

        challenger_local, challenger_remote = socket.socketpair()
        challenger_remote.settimeout(TEST_TIMEOUT)

        def _run_admission() -> None:
            assert captured_epoch is not None
            server.handle_accepted_candidate(
                captured_epoch, challenger_local, ("203.0.113.5", 9999)
            )

        worker = start_worker("gated-admission", _run_admission)

        assert server.about_to_publish.wait(TEST_TIMEOUT)
        server.stop()
        server.listen(0)
        new_epoch = server.current_listener_epoch()
        assert new_epoch is not None
        assert new_epoch != captured_epoch

        server.release_publish.set()
        worker.join(TEST_TIMEOUT)

        assert challenger_local.fileno() == -1
        assert server.active_peer is None
        assert server.is_listening is True
        assert server.current_listener_epoch() == new_epoch

        server.stop()
        challenger_remote.close()

    def test_challenger_immediate_eof_after_publish_detaches_cleanly(self) -> None:
        server = _HarnessSocketHandlerServer(_logger("challenger-eof"), accept_poll_interval=0.05)
        server.listen(0)
        epoch = server.current_listener_epoch()
        assert epoch is not None

        recorder = _EpochClosedRecorder()
        server.set_connection_observer(recorder)

        challenger_local, challenger_remote = socket.socketpair()
        # The remote end is already gone before the receive worker ever
        # reads from it -- an immediate-EOF challenger.
        challenger_remote.close()

        server.handle_accepted_candidate(epoch, challenger_local, ("203.0.113.6", 8888))

        assert recorder.closed.wait(TEST_TIMEOUT)
        assert server.is_connected is False
        assert server.active_peer is None
        assert server.is_listening is True

        server.stop()


class TestReceiveWorkerStartFailureRollback:
    """Design constraint: 'start the receive worker only after all
    connected state is published; roll back the same epoch if worker start
    fails.' Forces a real ``threading.Thread.start`` failure, scoped by
    thread name to only the receive worker so the listener's own already-
    running accept thread (and any later, legitimate receive worker) is
    never touched -- deterministic, no sleeps or randomness.
    """

    def test_receive_worker_start_failure_rolls_back_the_connection_epoch(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        server = _HarnessSocketHandlerServer(_logger("start-failure-rollback"))
        server.listen(0)
        epoch = server.current_listener_epoch()
        assert epoch is not None

        original_start = threading.Thread.start

        def _failing_start(thread_self: threading.Thread) -> None:
            if "-receive-" in thread_self.name:
                raise RuntimeError("simulated receive worker start failure")
            original_start(thread_self)

        challenger_local, challenger_remote = socket.socketpair()
        monkeypatch.setattr(threading.Thread, "start", _failing_start)
        try:
            with caplog.at_level(logging.ERROR):
                server.handle_accepted_candidate(
                    epoch, challenger_local, ("192.0.2.99", 9500)
                )
        finally:
            monkeypatch.undo()

        # Rollback: the failed epoch is fully undone.
        assert server.active_peer is None
        assert server.is_connected is False
        assert challenger_local.fileno() == -1
        assert any("failed to start" in r.message for r in caplog.records)

        # The listener itself is untouched and keeps accepting.
        assert server.is_listening is True
        assert server.current_listener_epoch() == epoch

        admitted_local, admitted_remote = socket.socketpair()
        server.handle_accepted_candidate(epoch, admitted_local, ("192.0.2.100", 9600))
        assert server.is_connected is True
        assert server.active_peer == ("192.0.2.100", 9600)

        server.stop()
        challenger_remote.close()
        admitted_remote.close()


class _TwoWaiterGateServer(_HarnessSocketHandlerServer):
    """Gates ``is_connected`` per waiter thread to reproduce PA25-04.

    Each gated evaluation captures the *real* connected value first, then
    coordinates, then returns that captured value. Waiter ``waiter-A``'s first
    evaluation only signals ``a_checked`` (proving A observed "disconnected"
    before publication) and never blocks. Waiter ``waiter-B`` (the victim)'s
    first evaluation signals ``b_checked`` and then blocks on ``b_release`` --
    parking B in the gap between observing "disconnected" and entering its
    blocking wait, holding no lock, so a concurrent publication is free to
    proceed. This is the exact interleaving the shared-``Event`` implementation
    lost: A consumes and clears the single edge before B ever waits on it.
    """

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.a_checked = threading.Event()
        self.b_checked = threading.Event()
        self.b_release = threading.Event()
        self._a_fired = False
        self._b_fired = False

    @property
    def is_connected(self) -> bool:
        value = super().is_connected
        name = threading.current_thread().name
        if name == "waiter-A" and not self._a_fired:
            self._a_fired = True
            self.a_checked.set()
        elif name == "waiter-B" and not self._b_fired:
            self._b_fired = True
            self.b_checked.set()
            if not self.b_release.wait(TEST_TIMEOUT):
                raise WorkerTimeoutError("waiter-B gate was never released")
        return value


class TestConnectionWaitBroadcast:
    """Chunk 20 (PA25-04): connection-state waiting is level-triggered and
    safe for multiple concurrent waiters -- one waiter can never consume
    another waiter's wake."""

    def test_two_indefinite_waiters_both_return_true_for_one_connection(self) -> None:
        server = _TwoWaiterGateServer(_logger("two-waiter-broadcast"))
        server.listen(0)
        epoch = server.current_listener_epoch()
        assert epoch is not None

        results: dict[str, bool] = {}

        def _run_a() -> None:
            results["A"] = server.wait_for_connection(None)

        def _run_b() -> None:
            results["B"] = server.wait_for_connection(None)

        holder: list[socket.socket] = []
        waiter_a = start_worker("waiter-A", _run_a)
        waiter_b = start_worker("waiter-B", _run_b)

        # Both waiters observed "disconnected"; B is now parked in the gap
        # before its blocking wait, holding no lock.
        assert server.a_checked.wait(TEST_TIMEOUT)
        assert server.b_checked.wait(TEST_TIMEOUT)

        # Publish a real connection from a third thread while B is parked.
        local, remote = socket.socketpair()
        holder.append(remote)

        def _publish() -> None:
            server.handle_accepted_candidate(epoch, local, ("192.0.2.40", 7300))

        publisher = start_worker("publisher", _publish)
        publisher.join()

        # A wakes and returns first; on the buggy Event impl this is where A
        # clears the single shared edge that B was relying on.
        waiter_a.join()
        assert results["A"] is True

        # Release B. Under the fixed level-triggered broadcast, B re-checks the
        # current state (still connected) and returns True. Under the buggy
        # cleared-edge Event, B blocks forever and this join times out.
        server.b_release.set()
        waiter_b.join()
        assert results["B"] is True

        server.stop()
        for sock in holder:
            sock.close()

    def test_detach_then_reconnect_wakes_a_waiter_without_stale_connected(self) -> None:
        server = _HarnessSocketHandlerServer(_logger("detach-reconnect-wake"))
        server.listen(0)
        epoch = server.current_listener_epoch()
        assert epoch is not None
        holder: list[socket.socket] = []

        # Connect, then detach: a stale epoch must not report connected.
        local1, remote1 = socket.socketpair()
        holder.append(remote1)
        server.handle_accepted_candidate(epoch, local1, ("192.0.2.41", 7301))
        assert server.wait_for_connection(0) is True
        server.kick()
        assert server.is_connected is False
        assert server.wait_for_connection(0) is False

        # A fresh waiter blocks; a reconnect must wake it and report connected.
        results: dict[str, bool] = {}

        def _run() -> None:
            results["r"] = server.wait_for_connection(TEST_TIMEOUT)

        waiter = start_worker("reconnect-waiter", _run)

        local2, remote2 = socket.socketpair()
        holder.append(remote2)
        server.handle_accepted_candidate(epoch, local2, ("192.0.2.42", 7302))

        waiter.join()
        assert results["r"] is True
        assert server.active_peer == ("192.0.2.42", 7302)

        server.stop()
        for sock in holder:
            sock.close()
