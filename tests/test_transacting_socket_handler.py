"""
Tests for the shared threaded transacting engine (Action Plan 25, chunk 13):
disconnected/fire-and-forget/send-failure outcomes, register-before-send
correlation, encode/send rollback, independent ACK/completion timeouts,
mixed-stage settlement, event retention, epoch-close wakeup, malformed-token
passthrough, callback isolation, codec-call serialization, broadcast
encoding, and a retained inbound responder after epoch replacement.

Contract: ``.claude/specs/transactingSocketHandlers.md`` ("Composition and
roles", "Receive pipeline", "Synchronous transaction operation", and
"Lifecycle coupling" sections).

A ``FakeTransport`` (not a real socket) satisfies the engine's own narrow
``TransactionTransport`` protocol so these tests exercise the engine in
isolation from any real socket I/O, per this chunk's TDD step of adding "a
fake epoch-aware handler". All concurrency assertions use
``threading.Event``/bounded joins via ``tests/threaded_socket_helpers.py`` --
no test in this file uses a sleep or random delay. The two tests that
observe a real timeout (``SHORT_TIMEOUT``) are asserting timeout behavior
itself, not working around a race.
"""

import logging
import threading
from collections.abc import Callable

import pytest

from foundation_tools.socket_transaction.socket_handler import ConnectionObserver, EpochSendStatus
from foundation_tools.socket_transaction.transacting_socket_handler import (
    InboundTransaction,
    TransactingSocketHandler,
)
from foundation_tools.socket_transaction.transaction_codecs import (
    JsonTransactionCodec,
    TransactionCodec,
)
from foundation_tools.socket_transaction.transaction_core import TransactionCore
from foundation_tools.socket_transaction.transaction_models import (
    AckStatus,
    CompletionStatus,
    SendStatus,
    TransactionFrame,
    TransactionOutcome,
)
from foundationTypes.data_model_helper import DataModelHelper
from tests.threaded_socket_helpers import TEST_TIMEOUT, WorkerTimeoutError, start_worker

SHORT_TIMEOUT = 0.1

_JSON_CODEC = JsonTransactionCodec()


def _logger(name: str) -> logging.Logger:
    return logging.getLogger(f"test.transacting_socket_handler.{name}")


def _token(
    tx_id: int,
    msg_type: str,
    code: int,
    payload: DataModelHelper | bytes | str | None = None,
) -> str:
    """Build a raw string token (no trailing delimiter) as if already
    tokenized by ``SocketHandler``'s receive pipeline."""
    return _JSON_CODEC.encode(tx_id, msg_type, code, payload).decode("utf-8").rstrip("\n")


class FakeTransport:
    """Minimal fake satisfying the engine's ``TransactionTransport`` protocol.

    Not a real socket: ``attach``/``fail_current_epoch`` simulate the epoch
    lifecycle a real ``SocketHandler`` provides, and ``deliver`` simulates one
    complete inbound token reaching the registered connection observer.
    ``on_send``/``on_send_reply`` hooks let a test synchronize with, or
    inject a synchronous "immediate peer reply" during, a send.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._epoch: int | None = None
        self.observer: ConnectionObserver | None = None
        self.sent: list[tuple[int, bytes]] = []
        self.force_status: EpochSendStatus | None = None
        self.on_send: Callable[[], None] | None = None
        self.on_send_reply: Callable[[int, bytes], None] | None = None

    def attach(self, epoch: int) -> None:
        with self._lock:
            self._epoch = epoch

    def fail_current_epoch(self, cause: str = "test failure") -> None:
        with self._lock:
            epoch = self._epoch
            self._epoch = None
        if epoch is not None and self.observer is not None:
            self.observer.on_epoch_closed(epoch, cause)

    def snapshot_active_epoch(self) -> int | None:
        with self._lock:
            return self._epoch

    def send_for_epoch(self, epoch: int, data: bytes) -> EpochSendStatus:
        with self._lock:
            active = self._epoch
        if active != epoch:
            return EpochSendStatus.NOT_ACTIVE

        if self.force_status is not None:
            status = self.force_status
        else:
            self.sent.append((epoch, data))
            status = EpochSendStatus.SENT

        if self.on_send is not None:
            self.on_send()
        if status is EpochSendStatus.SENT and self.on_send_reply is not None:
            self.on_send_reply(epoch, data)
        return status

    def send(self, data: bytes) -> bool:
        epoch = self.snapshot_active_epoch()
        if epoch is None:
            return False
        return self.send_for_epoch(epoch, data) is EpochSendStatus.SENT

    def set_connection_observer(self, observer: ConnectionObserver | None) -> None:
        self.observer = observer

    def deliver(self, epoch: int, token: str) -> None:
        assert self.observer is not None, "no connection observer registered"
        self.observer.on_string_token(epoch, token)


class _RaisingEncodeCodec:
    """A ``TransactionCodec`` whose ``encode`` always fails, for the
    encode/send-rollback test."""

    @property
    def delimiter(self) -> str:
        return "\n"

    def encode(
        self,
        tx_id: int,
        msg_type: str,
        code: int,
        payload: DataModelHelper | bytes | str | None = None,
    ) -> bytes:
        raise ValueError("boom: encode failure for test")

    def decode(self, raw: bytes | str) -> TransactionFrame:
        raise NotImplementedError


class _BlockingCodec:
    """A ``TransactionCodec`` whose ``encode`` blocks on an ``Event`` and
    flags reentrancy, for the codec-lock serialization test."""

    def __init__(self) -> None:
        self.calls = 0
        self.in_call = threading.Event()
        self.release = threading.Event()

    @property
    def delimiter(self) -> str:
        return "\n"

    def encode(
        self,
        tx_id: int,
        msg_type: str,
        code: int,
        payload: DataModelHelper | bytes | str | None = None,
    ) -> bytes:
        assert not self.in_call.is_set(), "reentrant encode call detected"
        self.in_call.set()
        try:
            self.calls += 1
            if not self.release.wait(TEST_TIMEOUT):
                raise WorkerTimeoutError("blocking codec: release never set")
        finally:
            self.in_call.clear()
        return f"{tx_id}:{msg_type}:{code}\n".encode()

    def decode(self, raw: bytes | str) -> TransactionFrame:
        raise NotImplementedError


def _build(
    codec: TransactionCodec | None = None,
) -> tuple[FakeTransport, TransactionCore, TransactingSocketHandler]:
    transport = FakeTransport()
    core = TransactionCore(_logger("core"))
    engine = TransactingSocketHandler(_logger("engine"), transport, codec or _JSON_CODEC, core)
    return transport, core, engine


class TestConstruction:
    def test_registers_itself_as_the_transport_connection_observer(self) -> None:
        transport, _core, engine = _build()
        assert transport.observer is engine


class TestDisconnectedSendTransaction:
    def test_returns_not_connected_outcome_without_registering(self) -> None:
        transport, core, engine = _build()

        outcome = engine.send_transaction("ping", 1, wait_ack=True, wait_result=True)

        assert outcome.send_status is SendStatus.NOT_CONNECTED
        assert outcome.ack_status is AckStatus.CONNECTION_CLOSED
        assert outcome.completion_status is CompletionStatus.CONNECTION_CLOSED
        assert outcome.ack_error
        assert outcome.completion_error
        assert transport.sent == []
        assert len(core._pending) == 0

    def test_fire_and_forget_disconnected_call_has_no_diagnostics(self) -> None:
        _transport, _core, engine = _build()

        outcome = engine.send_transaction("ping", 1, wait_ack=False, wait_result=False)

        assert outcome.ack_status is AckStatus.NOT_REQUESTED
        assert outcome.completion_status is CompletionStatus.NOT_REQUESTED
        assert outcome.ack_error is None
        assert outcome.completion_error is None

    def test_every_disconnected_call_still_consumes_an_id(self) -> None:
        transport = FakeTransport()
        core = TransactionCore(_logger("core"), first_tx_id=1, tx_id_step=2)
        engine = TransactingSocketHandler(_logger("engine"), transport, _JSON_CODEC, core)

        first = engine.send_transaction("ping", 1, wait_ack=False)
        second = engine.send_transaction("ping", 1, wait_ack=False)

        assert first.tx_id == 1
        assert second.tx_id == 3


class TestTimeoutValidation:
    @pytest.mark.parametrize("bad_timeout", [-1.0, -0.001, float("nan"), float("inf")])
    def test_rejects_invalid_timeout_before_allocating_an_id(self, bad_timeout: float) -> None:
        _transport, core, engine = _build()

        with pytest.raises(ValueError):
            engine.send_transaction("ping", 1, timeout=bad_timeout)

        # Allocation happens only after validation: the next valid call still
        # receives the first id, proving the rejected call never consumed one.
        outcome = engine.send_transaction("ping", 1, wait_ack=False)
        assert outcome.tx_id == 1
        assert len(core._pending) == 0


class TestSendFailure:
    def test_send_failure_settles_requested_stages_as_connection_closed(self) -> None:
        transport, core, engine = _build()
        transport.attach(1)
        transport.force_status = EpochSendStatus.IO_FAILED

        outcome = engine.send_transaction("ping", 1, wait_ack=True, wait_result=True)

        assert outcome.send_status is SendStatus.FAILED
        assert outcome.ack_status is AckStatus.CONNECTION_CLOSED
        assert outcome.completion_status is CompletionStatus.CONNECTION_CLOSED
        assert outcome.ack_error
        assert outcome.completion_error
        assert transport.sent == []
        assert len(core._pending) == 0

    def test_send_failure_fire_and_forget_settles_unrequested_stages(self) -> None:
        transport, core, engine = _build()
        transport.attach(1)
        transport.force_status = EpochSendStatus.NOT_ACTIVE

        outcome = engine.send_transaction("ping", 1, wait_ack=False, wait_result=False)

        assert outcome.send_status is SendStatus.FAILED
        assert outcome.ack_status is AckStatus.NOT_REQUESTED
        assert outcome.completion_status is CompletionStatus.NOT_REQUESTED
        assert len(core._pending) == 0


class TestRegisterBeforeImmediateReply:
    def test_synchronous_ack_after_send_correlates_with_the_registered_transaction(self) -> None:
        transport, core, engine = _build()
        transport.attach(1)

        def _immediate_ack(epoch: int, wire: bytes) -> None:
            frame = _JSON_CODEC.decode(wire)
            transport.deliver(epoch, _token(frame.tx_id, "ack", 0))

        transport.on_send_reply = _immediate_ack

        outcome = engine.send_transaction("ping", 1, wait_ack=True, timeout=TEST_TIMEOUT)

        assert outcome.ack_status is AckStatus.ACKNOWLEDGED
        assert len(core._pending) == 0


class TestEncodeSendRollback:
    def test_encode_failure_discards_the_registration_and_propagates(self) -> None:
        transport, core, engine = _build(codec=_RaisingEncodeCodec())
        transport.attach(1)

        with pytest.raises(ValueError, match="boom"):
            engine.send_transaction("ping", 1)

        assert transport.sent == []
        assert len(core._pending) == 0


class TestIndependentTimeout:
    def test_ack_timeout_does_not_prevent_a_separately_requested_result_wait(self) -> None:
        transport, core, engine = _build()
        transport.attach(1)  # no peer reply is ever delivered

        outcome = engine.send_transaction(
            "ping", 1, wait_ack=True, wait_result=True, timeout=SHORT_TIMEOUT
        )

        assert outcome.ack_status is AckStatus.TIMED_OUT
        assert outcome.completion_status is CompletionStatus.TIMED_OUT
        assert len(core._pending) == 0


class TestMixedStageOutcomes:
    def test_ack_acknowledged_then_result_times_out(self) -> None:
        transport, core, engine = _build()
        transport.attach(1)

        def _ack_only(epoch: int, wire: bytes) -> None:
            frame = _JSON_CODEC.decode(wire)
            transport.deliver(epoch, _token(frame.tx_id, "ack", 0))

        transport.on_send_reply = _ack_only

        outcome = engine.send_transaction(
            "ping", 1, wait_ack=True, wait_result=True, timeout=SHORT_TIMEOUT
        )

        assert outcome.ack_status is AckStatus.ACKNOWLEDGED
        assert outcome.completion_status is CompletionStatus.TIMED_OUT
        assert len(core._pending) == 0

    def test_rejected_ack_settles_completion_as_error_without_a_separate_wait(self) -> None:
        transport, core, engine = _build()
        transport.attach(1)

        def _reject(epoch: int, wire: bytes) -> None:
            frame = _JSON_CODEC.decode(wire)
            transport.deliver(epoch, _token(frame.tx_id, "ack", 9, "bad request"))

        transport.on_send_reply = _reject

        outcome = engine.send_transaction(
            "ping", 1, wait_ack=True, wait_result=True, timeout=TEST_TIMEOUT
        )

        assert outcome.ack_status is AckStatus.REJECTED
        assert outcome.completion_status is CompletionStatus.ERROR
        assert outcome.completion_error == outcome.ack_error
        assert len(core._pending) == 0


class TestEventRetention:
    def test_events_received_before_completion_are_retained_in_the_outcome(self) -> None:
        transport, core, engine = _build()
        transport.attach(1)

        def _event_then_result(epoch: int, wire: bytes) -> None:
            frame = _JSON_CODEC.decode(wire)
            transport.deliver(epoch, _token(frame.tx_id, "evt", 7, "progress"))
            transport.deliver(epoch, _token(frame.tx_id, "res", 0, "done"))

        transport.on_send_reply = _event_then_result

        outcome = engine.send_transaction(
            "job", 1, wait_ack=False, wait_result=True, timeout=TEST_TIMEOUT
        )

        assert outcome.completion_status is CompletionStatus.RESULT
        assert outcome.result is not None
        assert outcome.result.payload == "done"
        assert len(outcome.events) == 1
        assert outcome.events[0].code == 7
        assert outcome.events[0].payload == "progress"
        assert len(core._pending) == 0


class TestCloseWakeup:
    def test_epoch_failure_wakes_a_blocked_ack_wait(self) -> None:
        transport, core, engine = _build()
        transport.attach(1)

        sent_event = threading.Event()
        transport.on_send = sent_event.set

        outcomes: list[TransactionOutcome] = []

        def _call() -> None:
            outcomes.append(
                engine.send_transaction(
                    "ping", 1, wait_ack=True, wait_result=False, timeout=TEST_TIMEOUT
                )
            )

        worker = start_worker("send-transaction", _call)
        assert sent_event.wait(TEST_TIMEOUT)
        transport.fail_current_epoch("connection closed for test")
        worker.join(TEST_TIMEOUT)

        assert len(outcomes) == 1
        outcome = outcomes[0]
        assert outcome.send_status is SendStatus.SENT
        assert outcome.ack_status is AckStatus.CONNECTION_CLOSED
        assert outcome.completion_status is CompletionStatus.NOT_REQUESTED
        assert len(core._pending) == 0


class TestReceivePipeline:
    def test_malformed_token_skips_routing_but_still_reaches_the_string_handler(self) -> None:
        transport, _core, engine = _build()
        transport.attach(1)

        received: list[str] = []
        inbound_calls: list[InboundTransaction] = []
        engine.set_string_message_handler(received.append)
        engine.set_inbound_transaction_handler(inbound_calls.append)

        transport.deliver(1, "not valid json")

        assert received == ["not valid json"]
        assert inbound_calls == []

    def test_decoded_frame_is_routed_before_the_string_handler_runs(self) -> None:
        transport, _core, engine = _build()
        transport.attach(1)

        order: list[str] = []
        engine.set_inbound_transaction_handler(lambda _tx: order.append("inbound"))
        engine.set_string_message_handler(lambda _token: order.append("string"))

        transport.deliver(1, _token(42, "req", 0, "hello"))

        assert order == ["inbound", "string"]

    def test_string_handler_exception_is_logged_and_contained(self) -> None:
        transport, _core, engine = _build()
        transport.attach(1)

        def _raise(_token: str) -> None:
            raise RuntimeError("string handler boom")

        engine.set_string_message_handler(_raise)

        transport.deliver(1, _token(-1, "evt", 0))  # must not raise

    def test_inbound_handler_exception_is_logged_and_contained(self) -> None:
        transport, _core, engine = _build()
        transport.attach(1)

        def _raise(_tx: InboundTransaction) -> None:
            raise RuntimeError("inbound handler boom")

        engine.set_inbound_transaction_handler(_raise)

        transport.deliver(1, _token(42, "req", 0))  # must not raise

    def test_broadcast_event_handler_is_delegated_to_the_core(self) -> None:
        transport, _core, engine = _build()
        transport.attach(1)

        received: list[TransactionFrame] = []
        engine.set_broadcast_event_handler(received.append)

        transport.deliver(1, _token(-1, "evt", 3, "hi all"))

        assert len(received) == 1
        assert received[0].tx_id == -1
        assert received[0].code == 3
        assert received[0].payload == "hi all"


class TestSendBroadcast:
    def test_encodes_negative_tx_id_and_evt_and_sends_on_the_active_epoch(self) -> None:
        transport, _core, engine = _build()
        transport.attach(3)

        assert engine.send_broadcast(payload="hello", code=5) is True

        assert len(transport.sent) == 1
        epoch, wire = transport.sent[0]
        assert epoch == 3
        frame = _JSON_CODEC.decode(wire)
        assert frame.tx_id == -1
        assert frame.msg_type == "evt"
        assert frame.code == 5
        assert frame.payload == "hello"

    def test_returns_false_and_sends_nothing_when_disconnected(self) -> None:
        transport, _core, engine = _build()

        assert engine.send_broadcast() is False
        assert transport.sent == []


class TestRetainedResponderAfterReplacement:
    def test_reply_after_epoch_replacement_returns_false_and_sends_nothing(self) -> None:
        transport, _core, engine = _build()
        transport.attach(1)

        captured: list[InboundTransaction] = []
        engine.set_inbound_transaction_handler(captured.append)
        transport.deliver(1, _token(42, "req", 0))
        assert len(captured) == 1
        retained = captured[0]

        transport.fail_current_epoch("closing for replacement")
        transport.attach(2)  # a replacement connection with a new epoch

        assert retained.reply("res", 0, "late reply") is False
        assert transport.sent == []

    def test_reply_succeeds_while_the_originating_epoch_is_still_active(self) -> None:
        transport, _core, engine = _build()
        transport.attach(1)

        captured: list[InboundTransaction] = []
        engine.set_inbound_transaction_handler(captured.append)
        transport.deliver(1, _token(42, "req", 0, "hi"))

        assert captured[0].reply("res", 0, "hello back") is True
        assert len(transport.sent) == 1
        epoch, wire = transport.sent[0]
        assert epoch == 1
        frame = _JSON_CODEC.decode(wire)
        assert frame.tx_id == 42
        assert frame.msg_type == "res"
        assert frame.payload == "hello back"

    def test_reply_rejects_a_non_reserved_message_type_before_encoding(self) -> None:
        transport, _core, engine = _build()
        transport.attach(1)

        captured: list[InboundTransaction] = []
        engine.set_inbound_transaction_handler(captured.append)
        transport.deliver(1, _token(42, "req", 0))

        with pytest.raises(ValueError):
            captured[0].reply("progress", 0)

        assert transport.sent == []


class TestCodecSerialization:
    def test_codec_lock_serializes_concurrent_encode_calls(self) -> None:
        transport, _core, engine = _build(codec=_BlockingCodec())
        transport.attach(1)
        codec = engine._codec
        assert isinstance(codec, _BlockingCodec)

        def _broadcast(code: int) -> Callable[[], None]:
            def _call() -> None:
                engine.send_broadcast(code=code)

            return _call

        worker1 = start_worker("broadcast-1", _broadcast(1))
        assert codec.in_call.wait(TEST_TIMEOUT)

        worker2 = start_worker("broadcast-2", _broadcast(2))

        # worker2 must still be blocked acquiring the codec lock -- it cannot
        # have entered `encode` while worker1 is still inside it.
        assert codec.calls == 1

        codec.release.set()
        worker1.join(TEST_TIMEOUT)
        worker2.join(TEST_TIMEOUT)

        assert codec.calls == 2
