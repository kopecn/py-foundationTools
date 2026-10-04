"""
Tests for the threaded transaction core: transaction id sequencing,
epoch-bound registration, duplicate rejection, idempotent discard,
race-safe ACK/completion waits, plus frame routing, epoch-scoped failure,
isolated callbacks, and atomic outcome finalization.

Contract: ``.claude/specs/threadedTransactionProtocol.md`` ("Pending
transaction", "Transaction core", and "Routing" sections).

Every concurrency assertion uses ``threading.Barrier``/``threading.Event`` and
bounded joins (via ``tests.threaded_socket_helpers.start_worker``) — never a
fixed or nondeterministic sleep.
"""

import ast
import inspect
import logging
import math
import threading
from collections.abc import Callable

import pytest

from foundation_tools.socket_transaction import transaction_core
from foundation_tools.socket_transaction.transaction_core import (
    PendingTransaction,
    TransactionCore,
)
from foundation_tools.socket_transaction.transaction_models import (
    AckStatus,
    CompletionStatus,
    SendStatus,
    TransactionFrame,
    TransactionOutcome,
)
from tests.threaded_socket_helpers import TEST_TIMEOUT, start_worker

SHORT_TIMEOUT = 0.1


def _core(**kwargs: object) -> TransactionCore:
    logger = logging.getLogger("test-transaction-core")
    return TransactionCore(logger, **kwargs)  # type: ignore[arg-type]


class TestConstructorValidation:
    @pytest.mark.parametrize("value", [0, -1, -100])
    def test_rejects_non_positive_first_tx_id(self, value: int) -> None:
        with pytest.raises(ValueError):
            _core(first_tx_id=value)

    @pytest.mark.parametrize("value", [0, -1, -100])
    def test_rejects_non_positive_tx_id_step(self, value: int) -> None:
        with pytest.raises(ValueError):
            _core(tx_id_step=value)

    @pytest.mark.parametrize("value", [True, False])
    def test_rejects_boolean_first_tx_id(self, value: bool) -> None:
        with pytest.raises(ValueError):
            _core(first_tx_id=value)

    @pytest.mark.parametrize("value", [True, False])
    def test_rejects_boolean_tx_id_step(self, value: bool) -> None:
        with pytest.raises(ValueError):
            _core(tx_id_step=value)

    @pytest.mark.parametrize("value", [1.5, "1", None])
    def test_rejects_non_int_first_tx_id(self, value: object) -> None:
        with pytest.raises(ValueError):
            _core(first_tx_id=value)

    @pytest.mark.parametrize("value", [1.5, "1", None])
    def test_rejects_non_int_tx_id_step(self, value: object) -> None:
        with pytest.raises(ValueError):
            _core(tx_id_step=value)

    def test_module_never_calls_getlogger(self) -> None:
        """The core must use the injected logger, never instantiate its own."""
        source = inspect.getsource(transaction_core)
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                assert node.func.id != "getLogger"
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                assert node.func.attr != "getLogger"


class TestSequenceGeneration:
    def test_client_style_sequence_is_odd(self) -> None:
        core = _core(first_tx_id=1, tx_id_step=2)
        assert [core.next_tx_id() for _ in range(3)] == [1, 3, 5]

    def test_server_style_sequence_is_even(self) -> None:
        core = _core(first_tx_id=2, tx_id_step=2)
        assert [core.next_tx_id() for _ in range(3)] == [2, 4, 6]

    def test_default_sequence_steps_by_one(self) -> None:
        core = _core()
        assert [core.next_tx_id() for _ in range(3)] == [1, 2, 3]

    def test_concurrent_allocation_never_duplicates(self) -> None:
        core = _core(first_tx_id=1, tx_id_step=2)
        thread_count = 16
        allocations_per_thread = 50
        barrier = threading.Barrier(thread_count)
        results: list[list[int]] = [[] for _ in range(thread_count)]

        def _allocate(index: int) -> Callable[[], None]:
            def _run() -> None:
                barrier.wait(TEST_TIMEOUT)
                for _ in range(allocations_per_thread):
                    results[index].append(core.next_tx_id())

            return _run

        handles = [start_worker(f"allocator-{i}", _allocate(i)) for i in range(thread_count)]
        for handle in handles:
            handle.join(TEST_TIMEOUT)

        flattened = [tx_id for bucket in results for tx_id in bucket]
        assert len(flattened) == len(set(flattened)), "duplicate transaction id allocated"

        expected = {1 + 2 * n for n in range(thread_count * allocations_per_thread)}
        assert set(flattened) == expected


class TestRegister:
    def test_returns_freshly_initialized_pending_transaction(self) -> None:
        core = _core()
        pending = core.register(epoch=7, tx_id=1)

        assert isinstance(pending, PendingTransaction)
        assert pending.epoch == 7
        assert pending.tx_id == 1
        assert pending.ack_status is None
        assert pending.completion_status is None
        assert pending.acked is False
        assert pending.result is None
        assert pending.ack_error is None
        assert pending.completion_error is None
        assert pending.events == []
        assert isinstance(pending.ack_event, threading.Event)
        assert isinstance(pending.done_event, threading.Event)
        assert not pending.ack_event.is_set()
        assert not pending.done_event.is_set()

    def test_duplicate_registration_raises_runtime_error(self) -> None:
        core = _core()
        core.register(epoch=1, tx_id=1)
        with pytest.raises(RuntimeError):
            core.register(epoch=1, tx_id=1)

    def test_duplicate_registration_preserves_incumbent_identity_and_state(self) -> None:
        core = _core()
        incumbent = core.register(epoch=1, tx_id=1)
        # Simulate state that route()'s dispatch would apply, to prove the
        # incumbent object — not a fresh replacement — is what the core
        # still consults afterward.
        incumbent.ack_status = AckStatus.ACKNOWLEDGED
        incumbent.events.append(object())  # type: ignore[arg-type]

        with pytest.raises(RuntimeError):
            core.register(epoch=99, tx_id=1)

        # The duplicate attempt must not have replaced or mutated the
        # incumbent: waiting now must observe the incumbent's own state
        # (ACKNOWLEDGED, not a fresh None-settling-to-TIMED_OUT) and the event
        # object identity must be unchanged.
        assert core.wait_ack(1, timeout=0) is AckStatus.ACKNOWLEDGED
        assert len(incumbent.events) == 1
        assert incumbent.epoch == 1

    def test_different_ids_register_independently(self) -> None:
        core = _core()
        first = core.register(epoch=1, tx_id=1)
        second = core.register(epoch=1, tx_id=2)
        assert first is not second


class TestDiscard:
    def test_discard_removes_pending_transaction(self) -> None:
        core = _core()
        core.register(epoch=1, tx_id=1)
        core.discard(1)
        assert core.wait_ack(1, timeout=0) is None
        assert core.wait_completion(1, timeout=0) is None

    def test_discard_is_idempotent_for_registered_id(self) -> None:
        core = _core()
        core.register(epoch=1, tx_id=1)
        core.discard(1)
        core.discard(1)  # must not raise

    def test_discard_is_idempotent_for_unknown_id(self) -> None:
        core = _core()
        core.discard(12345)  # must not raise

    def test_id_may_be_re_registered_after_discard(self) -> None:
        core = _core()
        original = core.register(epoch=1, tx_id=1)
        core.discard(1)
        replacement = core.register(epoch=2, tx_id=1)
        assert replacement is not original
        assert replacement.epoch == 2


class TestWaitTimeoutValidation:
    @pytest.mark.parametrize("bad_timeout", [-0.001, -1, math.inf, -math.inf, math.nan, "1", []])
    def test_wait_ack_rejects_invalid_timeout(self, bad_timeout: object) -> None:
        core = _core()
        core.register(epoch=1, tx_id=1)
        with pytest.raises(ValueError):
            core.wait_ack(1, timeout=bad_timeout)  # type: ignore[arg-type]

    @pytest.mark.parametrize("bad_timeout", [-0.001, -1, math.inf, -math.inf, math.nan, "1", []])
    def test_wait_completion_rejects_invalid_timeout(self, bad_timeout: object) -> None:
        core = _core()
        core.register(epoch=1, tx_id=1)
        with pytest.raises(ValueError):
            core.wait_completion(1, timeout=bad_timeout)  # type: ignore[arg-type]

    def test_wait_ack_accepts_none_and_zero(self) -> None:
        core = _core()
        core.register(epoch=1, tx_id=1)
        assert core.wait_ack(1, timeout=0) is AckStatus.TIMED_OUT

    def test_wait_completion_accepts_none_and_zero(self) -> None:
        core = _core()
        core.register(epoch=1, tx_id=1)
        assert core.wait_completion(1, timeout=0) is CompletionStatus.TIMED_OUT


class TestWaitUnknownIdentifier:
    def test_wait_ack_returns_none_for_unregistered_id(self) -> None:
        core = _core()
        assert core.wait_ack(999, timeout=0) is None

    def test_wait_completion_returns_none_for_unregistered_id(self) -> None:
        core = _core()
        assert core.wait_completion(999, timeout=0) is None


class TestNoneTimeoutWaitsWokenDeterministically:
    """Design constraint: a ``timeout=None`` wait selects
    an unbounded public wait; exercise it by actually blocking a worker on
    it and waking that block through the real ``route()``/``fail_epoch()``
    production paths (not the private ``_settle_*`` test-only shortcuts used
    elsewhere in this file), then join it with a single bound. Because
    ``threading.Event.set()`` before ``wait()`` still makes ``wait()``
    return immediately, ordering between "worker enters wait" and "this test
    wakes it" cannot race here -- either way the join stays bounded and no
    worker is ever left running past ``TEST_TIMEOUT``.
    """

    def test_wait_ack_with_none_timeout_is_woken_by_a_successful_ack_route(self) -> None:
        core = _core()
        core.register(epoch=1, tx_id=1)
        started = threading.Event()
        results: list[AckStatus | None] = []

        def _wait() -> None:
            started.set()
            results.append(core.wait_ack(1, timeout=None))

        handle = start_worker("none-ack-wait", _wait)
        assert started.wait(TEST_TIMEOUT)
        core.route(epoch=1, frame=TransactionFrame(tx_id=1, msg_type="ack", code=0, payload=None))
        handle.join(TEST_TIMEOUT)

        assert results == [AckStatus.ACKNOWLEDGED]

    def test_wait_completion_with_none_timeout_is_woken_by_a_successful_result_route(self) -> None:
        core = _core()
        core.register(epoch=1, tx_id=1)
        started = threading.Event()
        results: list[CompletionStatus | None] = []

        def _wait() -> None:
            started.set()
            results.append(core.wait_completion(1, timeout=None))

        handle = start_worker("none-completion-wait", _wait)
        assert started.wait(TEST_TIMEOUT)
        core.route(epoch=1, frame=TransactionFrame(tx_id=1, msg_type="res", code=0, payload="ok"))
        handle.join(TEST_TIMEOUT)

        assert results == [CompletionStatus.RESULT]

    def test_wait_ack_with_none_timeout_is_woken_by_epoch_failure(self) -> None:
        core = _core()
        core.register(epoch=1, tx_id=1)
        started = threading.Event()
        results: list[AckStatus | None] = []

        def _wait() -> None:
            started.set()
            results.append(core.wait_ack(1, timeout=None))

        handle = start_worker("none-ack-wait-epoch-fail", _wait)
        assert started.wait(TEST_TIMEOUT)
        core.fail_epoch(1, "connection lost")
        handle.join(TEST_TIMEOUT)

        assert results == [AckStatus.CONNECTION_CLOSED]

    def test_wait_completion_with_none_timeout_is_woken_by_epoch_failure(self) -> None:
        core = _core()
        core.register(epoch=1, tx_id=1)
        started = threading.Event()
        results: list[CompletionStatus | None] = []

        def _wait() -> None:
            started.set()
            results.append(core.wait_completion(1, timeout=None))

        handle = start_worker("none-completion-wait-epoch-fail", _wait)
        assert started.wait(TEST_TIMEOUT)
        core.fail_epoch(1, "connection lost")
        handle.join(TEST_TIMEOUT)

        assert results == [CompletionStatus.CONNECTION_CLOSED]


class TestWaitAckTimeoutSettlement:
    def test_unresolved_stage_settles_as_timed_out(self) -> None:
        core = _core()
        core.register(epoch=1, tx_id=1)
        assert core.wait_ack(1, timeout=SHORT_TIMEOUT) is AckStatus.TIMED_OUT

    def test_settled_timeout_is_returned_consistently_on_repeat_wait(self) -> None:
        core = _core()
        core.register(epoch=1, tx_id=1)
        first = core.wait_ack(1, timeout=SHORT_TIMEOUT)
        second = core.wait_ack(1, timeout=0)
        assert first is AckStatus.TIMED_OUT
        assert second is AckStatus.TIMED_OUT


class TestWaitCompletionTimeoutSettlement:
    def test_unresolved_stage_settles_as_timed_out(self) -> None:
        core = _core()
        core.register(epoch=1, tx_id=1)
        assert core.wait_completion(1, timeout=SHORT_TIMEOUT) is CompletionStatus.TIMED_OUT

    def test_settled_timeout_is_returned_consistently_on_repeat_wait(self) -> None:
        core = _core()
        core.register(epoch=1, tx_id=1)
        first = core.wait_completion(1, timeout=SHORT_TIMEOUT)
        second = core.wait_completion(1, timeout=0)
        assert first is CompletionStatus.TIMED_OUT
        assert second is CompletionStatus.TIMED_OUT


def _settle_ack(core: TransactionCore, tx_id: int, status: AckStatus) -> None:
    """Simulate a routing-style settlement under the core's own lock,
    mirroring the terminal race recipe: mutate state, then signal the event,
    all without ever holding the lock across the ``Event.wait``. Reaches into
    the internal lock/pending map deliberately — this white-box race test
    isolates the core's pending-state primitives from ``route()``'s own
    message-type dispatch logic, which is exercised separately.
    """
    with core._lock:
        pending = core._pending.get(tx_id)
        if pending is not None and pending.ack_status is None:
            pending.ack_status = status
    if pending is not None:
        pending.ack_event.set()


def _settle_completion(core: TransactionCore, tx_id: int, status: CompletionStatus) -> None:
    with core._lock:
        pending = core._pending.get(tx_id)
        if pending is not None and pending.completion_status is None:
            pending.completion_status = status
    if pending is not None:
        pending.done_event.set()


class TestBarrierControlledAckArrivalVersusTimeout:
    def test_arrival_before_timeout_wins(self) -> None:
        core = _core()
        core.register(epoch=1, tx_id=1)
        barrier = threading.Barrier(2)

        def _arrive() -> None:
            barrier.wait(TEST_TIMEOUT)
            _settle_ack(core, 1, AckStatus.ACKNOWLEDGED)

        handle = start_worker("ack-arrival", _arrive)
        barrier.wait(TEST_TIMEOUT)
        status = core.wait_ack(1, timeout=TEST_TIMEOUT)
        handle.join(TEST_TIMEOUT)

        assert status is AckStatus.ACKNOWLEDGED

    def test_timeout_before_arrival_wins_and_is_never_overwritten(self) -> None:
        core = _core()
        core.register(epoch=1, tx_id=1)
        proceed = threading.Event()

        def _late_arrival() -> None:
            # Deliberately wait for the main thread's short-timeout wait_ack
            # to have already settled the stage before attempting to arrive.
            proceed.wait(TEST_TIMEOUT)
            _settle_ack(core, 1, AckStatus.ACKNOWLEDGED)

        handle = start_worker("late-ack-arrival", _late_arrival)
        status = core.wait_ack(1, timeout=SHORT_TIMEOUT)
        assert status is AckStatus.TIMED_OUT

        proceed.set()
        handle.join(TEST_TIMEOUT)

        # The late arrival must not have overwritten the already-settled
        # TIMED_OUT status with a hybrid or replacement value.
        assert core.wait_ack(1, timeout=0) is AckStatus.TIMED_OUT

    def test_exactly_one_side_settles_under_concurrent_contention(self) -> None:
        """Stress the race repeatedly: whichever side wins, the result must
        always be a single legal status, never a corrupted/hybrid outcome."""
        for _ in range(50):
            core = _core()
            core.register(epoch=1, tx_id=1)
            barrier = threading.Barrier(2)

            def _arrive(core: TransactionCore = core, barrier: threading.Barrier = barrier) -> None:
                barrier.wait(TEST_TIMEOUT)
                _settle_ack(core, 1, AckStatus.ACKNOWLEDGED)

            handle = start_worker("contended-ack-arrival", _arrive)
            barrier.wait(TEST_TIMEOUT)
            status = core.wait_ack(1, timeout=0.02)
            handle.join(TEST_TIMEOUT)

            assert status in (AckStatus.ACKNOWLEDGED, AckStatus.TIMED_OUT)
            # Idempotent re-read must agree with the settled value.
            assert core.wait_ack(1, timeout=0) is status


class TestBarrierControlledCompletionArrivalVersusTimeout:
    def test_arrival_before_timeout_wins(self) -> None:
        core = _core()
        core.register(epoch=1, tx_id=1)
        barrier = threading.Barrier(2)

        def _arrive() -> None:
            barrier.wait(TEST_TIMEOUT)
            _settle_completion(core, 1, CompletionStatus.RESULT)

        handle = start_worker("completion-arrival", _arrive)
        barrier.wait(TEST_TIMEOUT)
        status = core.wait_completion(1, timeout=TEST_TIMEOUT)
        handle.join(TEST_TIMEOUT)

        assert status is CompletionStatus.RESULT

    def test_timeout_before_arrival_wins_and_is_never_overwritten(self) -> None:
        core = _core()
        core.register(epoch=1, tx_id=1)
        proceed = threading.Event()

        def _late_arrival() -> None:
            proceed.wait(TEST_TIMEOUT)
            _settle_completion(core, 1, CompletionStatus.RESULT)

        handle = start_worker("late-completion-arrival", _late_arrival)
        status = core.wait_completion(1, timeout=SHORT_TIMEOUT)
        assert status is CompletionStatus.TIMED_OUT

        proceed.set()
        handle.join(TEST_TIMEOUT)

        assert core.wait_completion(1, timeout=0) is CompletionStatus.TIMED_OUT


class TestLockNotHeldAcrossEventWait:
    def test_other_operations_proceed_while_a_wait_is_blocked(self) -> None:
        core = _core()
        core.register(epoch=1, tx_id=1)
        blocked_wait_started = threading.Event()
        blocked_wait_result: list[AckStatus | None] = []

        def _blocked_wait() -> None:
            blocked_wait_started.set()
            # Blocks until settled from outside or TEST_TIMEOUT elapses. If
            # the core held its lock across this wait, the lock-guarded
            # operations below (on a different transaction id, from the main
            # thread) would themselves block for the same duration.
            blocked_wait_result.append(core.wait_ack(1, timeout=TEST_TIMEOUT))

        handle = start_worker("blocked-ack-wait", _blocked_wait)
        assert blocked_wait_started.wait(TEST_TIMEOUT)

        # While the above wait is still blocked inside Event.wait(), these
        # lock-guarded operations on a *different* transaction id must
        # complete promptly — proving the lock is not held across the wait.
        core.next_tx_id()
        core.register(epoch=2, tx_id=2)
        core.discard(2)

        # Unblock the worker directly (rather than waiting out TEST_TIMEOUT)
        # for a fast, bounded join.
        _settle_ack(core, 1, AckStatus.ACKNOWLEDGED)
        handle.join(TEST_TIMEOUT)
        assert blocked_wait_result == [AckStatus.ACKNOWLEDGED]


def _recorder() -> tuple[Callable[..., None], list[tuple[object, ...]]]:
    """A handler that records every call's positional arguments."""
    calls: list[tuple[object, ...]] = []

    def _handler(*args: object) -> None:
        calls.append(args)

    return _handler, calls


def _raising(exc: Exception) -> Callable[..., None]:
    def _handler(*_args: object) -> None:
        raise exc

    return _handler


class TestRouteBroadcastEvent:
    """Routing table row: ``msg_type == "evt"`` and ``tx_id < 0``."""

    def test_negative_tx_id_evt_invokes_broadcast_handler_without_consulting_pending(
        self,
    ) -> None:
        core = _core()
        handler, calls = _recorder()
        core.set_broadcast_event_handler(handler)
        frame = TransactionFrame(tx_id=-1, msg_type="evt", code=0, payload="ping")

        core.route(epoch=1, frame=frame)

        assert calls == [(frame,)]

    def test_negative_tx_id_evt_does_not_touch_a_same_id_pending_entry(self) -> None:
        # -1 is the defined broadcast id; nothing should ever be registered
        # under it, but routing must not consult self._pending at all for
        # this row regardless.
        core = _core()
        pending = core.register(epoch=1, tx_id=-1)
        frame = TransactionFrame(tx_id=-1, msg_type="evt", code=0, payload=None)

        core.route(epoch=1, frame=frame)

        assert pending.completion_status is None
        assert pending.events == []

    def test_no_broadcast_handler_registered_is_a_silent_no_op(self) -> None:
        core = _core()
        frame = TransactionFrame(tx_id=-5, msg_type="evt", code=0, payload=None)
        core.route(epoch=1, frame=frame)  # must not raise


class TestRouteOrphanControlFrames:
    """Routing table row: ack/res/err/non-broadcast-evt with no pending entry."""

    @pytest.mark.parametrize("msg_type", ["ack", "res", "err", "evt"])
    def test_control_frame_with_no_pending_entry_is_logged_and_dropped(
        self, msg_type: str, caplog: pytest.LogCaptureFixture
    ) -> None:
        core = _core()
        inbound_handler, inbound_calls = _recorder()
        core.set_inbound_transaction_handler(inbound_handler)
        frame = TransactionFrame(tx_id=999, msg_type=msg_type, code=0, payload=None)

        with caplog.at_level(logging.WARNING, logger="test-transaction-core"):
            core.route(epoch=1, frame=frame)

        assert inbound_calls == []
        assert any("orphan" in record.message for record in caplog.records)

    @pytest.mark.parametrize("msg_type", ["ack", "res", "err", "evt"])
    def test_control_frame_for_mismatched_epoch_is_orphan_not_the_stale_pending(
        self, msg_type: str
    ) -> None:
        core = _core()
        pending = core.register(epoch=1, tx_id=1)
        frame = TransactionFrame(tx_id=1, msg_type=msg_type, code=0, payload=None)

        core.route(epoch=2, frame=frame)

        # An old epoch must never resolve a new epoch's waiter: the pending
        # entry registered under epoch 1 must be untouched.
        assert pending.ack_status is None
        assert pending.completion_status is None
        assert pending.events == []


class TestRouteApplicationRequestNoPendingEntry:
    """Routing table row: no pending entry -> invoke inbound handler."""

    def test_application_type_with_no_pending_entry_invokes_inbound_handler(self) -> None:
        core = _core()
        handler, calls = _recorder()
        core.set_inbound_transaction_handler(handler)
        frame = TransactionFrame(tx_id=42, msg_type="do_thing", code=0, payload={"a": 1})

        core.route(epoch=7, frame=frame)

        assert calls == [(7, frame)]

    def test_application_type_for_mismatched_epoch_still_invokes_inbound_handler(self) -> None:
        core = _core()
        core.register(epoch=1, tx_id=1)
        handler, calls = _recorder()
        core.set_inbound_transaction_handler(handler)
        frame = TransactionFrame(tx_id=1, msg_type="do_thing", code=0, payload=None)

        core.route(epoch=2, frame=frame)

        assert calls == [(2, frame)]

    def test_no_inbound_handler_registered_is_a_silent_no_op(self) -> None:
        core = _core()
        frame = TransactionFrame(tx_id=42, msg_type="do_thing", code=0, payload=None)
        core.route(epoch=1, frame=frame)  # must not raise


class TestRouteAckSuccess:
    """Routing table row: ``msg_type == "ack"`` and ``code == 0``."""

    def test_ack_code_zero_settles_acknowledged(self) -> None:
        core = _core()
        pending = core.register(epoch=1, tx_id=1)
        frame = TransactionFrame(tx_id=1, msg_type="ack", code=0, payload=None)

        core.route(epoch=1, frame=frame)

        assert pending.acked is True
        assert pending.ack_status is AckStatus.ACKNOWLEDGED
        assert pending.ack_event.is_set()
        assert pending.completion_status is None  # ACK never settles completion on success
        assert core.wait_ack(1, timeout=0) is AckStatus.ACKNOWLEDGED


class TestRouteAckFailure:
    """Routing table row: ``msg_type == "ack"`` and ``code != 0``."""

    def test_failed_ack_with_payload_stores_exact_diagnostic_text(self) -> None:
        core = _core()
        pending = core.register(epoch=1, tx_id=1)
        frame = TransactionFrame(tx_id=1, msg_type="ack", code=5, payload="bad request")

        core.route(epoch=1, frame=frame)

        assert pending.ack_status is AckStatus.REJECTED
        assert pending.ack_error == "ack code 5: bad request"
        assert pending.ack_event.is_set()

    def test_failed_ack_without_payload_stores_exact_diagnostic_text(self) -> None:
        core = _core()
        pending = core.register(epoch=1, tx_id=1)
        frame = TransactionFrame(tx_id=1, msg_type="ack", code=7, payload=None)

        core.route(epoch=1, frame=frame)

        assert pending.ack_status is AckStatus.REJECTED
        assert pending.ack_error == "ack code 7"

    def test_failed_ack_settles_unresolved_completion_as_error(self) -> None:
        core = _core()
        pending = core.register(epoch=1, tx_id=1)
        frame = TransactionFrame(tx_id=1, msg_type="ack", code=5, payload="bad request")

        core.route(epoch=1, frame=frame)

        assert pending.completion_status is CompletionStatus.ERROR
        assert pending.completion_error == "ack code 5: bad request"
        assert pending.done_event.is_set()

    def test_failed_ack_does_not_overwrite_an_already_settled_completion(self) -> None:
        core = _core()
        pending = core.register(epoch=1, tx_id=1)
        res_frame = TransactionFrame(tx_id=1, msg_type="res", code=0, payload="ok")
        core.route(epoch=1, frame=res_frame)

        ack_frame = TransactionFrame(tx_id=1, msg_type="ack", code=5, payload="too late")
        core.route(epoch=1, frame=ack_frame)

        assert pending.completion_status is CompletionStatus.RESULT
        assert pending.result is res_frame
        # The ACK stage itself still settles independently.
        assert pending.ack_status is AckStatus.REJECTED


class TestLateFailedAckAfterAckTimeout:
    """PA25-07: a failed ACK arriving after ACK timeout must still settle an
    independently unresolved completion stage, without ever overwriting the
    already-settled ``AckStatus.TIMED_OUT``.

    ``timeout=0`` deterministically settles the ACK stage to ``TIMED_OUT`` in
    the calling thread (an immediate check, per ``TestWaitAckTimeoutSettlement``)
    with no real wait, so these synchronous cases need no worker thread.
    """

    def test_late_failed_ack_settles_unresolved_completion_as_error(self) -> None:
        core = _core()
        pending = core.register(epoch=1, tx_id=1)
        assert core.wait_ack(1, timeout=0) is AckStatus.TIMED_OUT

        core.route(epoch=1, frame=TransactionFrame(tx_id=1, msg_type="ack", code=5, payload="bad"))

        assert pending.completion_status is CompletionStatus.ERROR
        assert pending.completion_error == "ack code 5: bad"
        assert pending.done_event.is_set()

    def test_late_failed_ack_never_overwrites_ack_timed_out(self) -> None:
        core = _core()
        pending = core.register(epoch=1, tx_id=1)
        assert core.wait_ack(1, timeout=0) is AckStatus.TIMED_OUT

        core.route(epoch=1, frame=TransactionFrame(tx_id=1, msg_type="ack", code=5, payload="bad"))

        assert pending.ack_status is AckStatus.TIMED_OUT
        assert core.wait_ack(1, timeout=0) is AckStatus.TIMED_OUT

    def test_late_successful_ack_after_ack_timeout_remains_non_terminal(self) -> None:
        core = _core()
        pending = core.register(epoch=1, tx_id=1)
        assert core.wait_ack(1, timeout=0) is AckStatus.TIMED_OUT

        core.route(epoch=1, frame=TransactionFrame(tx_id=1, msg_type="ack", code=0, payload=None))

        assert pending.ack_status is AckStatus.TIMED_OUT
        assert pending.acked is False
        assert pending.completion_status is None
        assert not pending.done_event.is_set()

    def test_late_failed_ack_does_not_overwrite_a_result_settled_first(self) -> None:
        core = _core()
        pending = core.register(epoch=1, tx_id=1)
        assert core.wait_ack(1, timeout=0) is AckStatus.TIMED_OUT
        res = TransactionFrame(tx_id=1, msg_type="res", code=0, payload="ok")
        core.route(epoch=1, frame=res)

        core.route(epoch=1, frame=TransactionFrame(tx_id=1, msg_type="ack", code=5, payload="late"))

        assert pending.completion_status is CompletionStatus.RESULT
        assert pending.result is res
        assert pending.completion_error is None

    def test_late_failed_ack_does_not_overwrite_a_protocol_error_settled_first(self) -> None:
        core = _core()
        pending = core.register(epoch=1, tx_id=1)
        assert core.wait_ack(1, timeout=0) is AckStatus.TIMED_OUT
        core.route(epoch=1, frame=TransactionFrame(tx_id=1, msg_type="err", code=1, payload="no"))

        core.route(epoch=1, frame=TransactionFrame(tx_id=1, msg_type="ack", code=5, payload="late"))

        assert pending.completion_status is CompletionStatus.ERROR
        assert pending.completion_error == "no"

    def test_late_failed_ack_does_not_overwrite_a_completion_timeout_settled_first(self) -> None:
        core = _core()
        pending = core.register(epoch=1, tx_id=1)
        assert core.wait_ack(1, timeout=0) is AckStatus.TIMED_OUT
        assert core.wait_completion(1, timeout=0) is CompletionStatus.TIMED_OUT

        core.route(epoch=1, frame=TransactionFrame(tx_id=1, msg_type="ack", code=5, payload="late"))

        assert pending.completion_status is CompletionStatus.TIMED_OUT
        assert pending.completion_error is None

    def test_late_failed_ack_does_not_overwrite_connection_closed_settled_first(self) -> None:
        core = _core()
        pending = core.register(epoch=1, tx_id=1)
        assert core.wait_ack(1, timeout=0) is AckStatus.TIMED_OUT
        core.fail_epoch(1, "connection lost")

        core.route(epoch=1, frame=TransactionFrame(tx_id=1, msg_type="ack", code=5, payload="late"))

        assert pending.completion_status is CompletionStatus.CONNECTION_CLOSED
        assert pending.completion_error == "connection lost"
        assert pending.ack_status is AckStatus.TIMED_OUT


class TestLateFailedAckWakesBlockedCompletionWait:
    def test_late_failed_ack_wakes_a_blocked_completion_wait(self) -> None:
        core = _core()
        pending = core.register(epoch=1, tx_id=1)
        assert core.wait_ack(1, timeout=0) is AckStatus.TIMED_OUT
        barrier = threading.Barrier(2)

        def _late_failed_ack(
            core: TransactionCore = core, barrier: threading.Barrier = barrier
        ) -> None:
            barrier.wait(TEST_TIMEOUT)
            core.route(1, TransactionFrame(tx_id=1, msg_type="ack", code=5, payload="late"))

        handle = start_worker("late-failed-ack", _late_failed_ack)
        barrier.wait(TEST_TIMEOUT)
        status = core.wait_completion(1, timeout=TEST_TIMEOUT)
        handle.join(TEST_TIMEOUT)

        assert status is CompletionStatus.ERROR
        assert pending.completion_error == "ack code 5: late"


class TestRouteResult:
    """Routing table row: ``msg_type == "res"``."""

    def test_result_settles_completion_and_stores_the_frame(self) -> None:
        core = _core()
        pending = core.register(epoch=1, tx_id=1)
        frame = TransactionFrame(tx_id=1, msg_type="res", code=0, payload={"ok": True})

        core.route(epoch=1, frame=frame)

        assert pending.result is frame
        assert pending.completion_status is CompletionStatus.RESULT
        assert pending.done_event.is_set()

    def test_result_before_ack_leaves_ack_unresolved(self) -> None:
        core = _core()
        pending = core.register(epoch=1, tx_id=1)
        frame = TransactionFrame(tx_id=1, msg_type="res", code=0, payload=None)

        core.route(epoch=1, frame=frame)

        assert pending.ack_status is None
        assert not pending.ack_event.is_set()


class TestRouteEvent:
    """Routing table row: ``msg_type == "evt"`` (non-broadcast, pending exists)."""

    def test_event_is_appended_and_does_not_signal_completion(self) -> None:
        core = _core()
        pending = core.register(epoch=1, tx_id=1)
        frame = TransactionFrame(tx_id=1, msg_type="evt", code=0, payload="progress")

        core.route(epoch=1, frame=frame)

        assert pending.events == [frame]
        assert pending.completion_status is None
        assert not pending.done_event.is_set()

    def test_events_accumulate_in_arrival_order(self) -> None:
        core = _core()
        pending = core.register(epoch=1, tx_id=1)
        first = TransactionFrame(tx_id=1, msg_type="evt", code=0, payload="1")
        second = TransactionFrame(tx_id=1, msg_type="evt", code=0, payload="2")

        core.route(epoch=1, frame=first)
        core.route(epoch=1, frame=second)

        assert pending.events == [first, second]

    def test_late_event_after_completion_settled_is_dropped(self) -> None:
        core = _core()
        pending = core.register(epoch=1, tx_id=1)
        core.route(epoch=1, frame=TransactionFrame(tx_id=1, msg_type="res", code=0, payload="ok"))

        late = TransactionFrame(tx_id=1, msg_type="evt", code=0, payload="late")
        core.route(epoch=1, frame=late)

        assert pending.events == []


class TestRouteError:
    """Routing table row: ``msg_type == "err"``."""

    def test_error_with_payload_stores_str_of_payload(self) -> None:
        core = _core()
        pending = core.register(epoch=1, tx_id=1)
        frame = TransactionFrame(tx_id=1, msg_type="err", code=3, payload="boom")

        core.route(epoch=1, frame=frame)

        assert pending.completion_status is CompletionStatus.ERROR
        assert pending.completion_error == "boom"
        assert pending.done_event.is_set()

    def test_error_without_payload_stores_exact_diagnostic_text(self) -> None:
        core = _core()
        pending = core.register(epoch=1, tx_id=1)
        frame = TransactionFrame(tx_id=1, msg_type="err", code=9, payload=None)

        core.route(epoch=1, frame=frame)

        assert pending.completion_error == "error code 9"


class TestRouteLateAndDuplicateFrames:
    def test_second_ack_after_success_is_dropped(self) -> None:
        core = _core()
        pending = core.register(epoch=1, tx_id=1)
        core.route(epoch=1, frame=TransactionFrame(tx_id=1, msg_type="ack", code=0, payload=None))
        core.route(epoch=1, frame=TransactionFrame(tx_id=1, msg_type="ack", code=9, payload="x"))

        assert pending.ack_status is AckStatus.ACKNOWLEDGED
        assert pending.ack_error is None

    def test_second_res_after_first_res_is_dropped(self) -> None:
        core = _core()
        pending = core.register(epoch=1, tx_id=1)
        first = TransactionFrame(tx_id=1, msg_type="res", code=0, payload="first")
        second = TransactionFrame(tx_id=1, msg_type="res", code=0, payload="second")

        core.route(epoch=1, frame=first)
        core.route(epoch=1, frame=second)

        assert pending.result is first

    def test_err_after_res_is_dropped(self) -> None:
        core = _core()
        pending = core.register(epoch=1, tx_id=1)
        res = TransactionFrame(tx_id=1, msg_type="res", code=0, payload="ok")
        core.route(epoch=1, frame=res)
        core.route(epoch=1, frame=TransactionFrame(tx_id=1, msg_type="err", code=1, payload="no"))

        assert pending.completion_status is CompletionStatus.RESULT
        assert pending.completion_error is None
        assert pending.result is res


class TestRouteCallbackIsolation:
    def test_broadcast_handler_exception_is_contained_and_logged(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        core = _core()
        core.set_broadcast_event_handler(_raising(RuntimeError("boom")))
        frame = TransactionFrame(tx_id=-1, msg_type="evt", code=0, payload=None)

        with caplog.at_level(logging.ERROR, logger="test-transaction-core"):
            core.route(epoch=1, frame=frame)  # must not raise

        assert any(record.levelno >= logging.ERROR for record in caplog.records)

    def test_inbound_handler_exception_is_contained_and_routing_stays_usable(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        core = _core()
        core.set_inbound_transaction_handler(_raising(RuntimeError("boom")))
        failing_frame = TransactionFrame(tx_id=1, msg_type="do_thing", code=0, payload=None)

        with caplog.at_level(logging.ERROR, logger="test-transaction-core"):
            core.route(epoch=1, frame=failing_frame)  # must not raise

        # Routing must remain usable for a later, unrelated frame.
        pending = core.register(epoch=1, tx_id=2)
        core.route(epoch=1, frame=TransactionFrame(tx_id=2, msg_type="res", code=0, payload="ok"))
        assert pending.completion_status is CompletionStatus.RESULT

    def test_callback_is_invoked_outside_the_lock(self) -> None:
        """A callback that itself calls back into the core must not deadlock."""
        core = _core()

        def _reentrant_handler(epoch: int, frame: TransactionFrame) -> None:
            # This would deadlock on a non-reentrant lock if invoked while
            # route() still held self._lock.
            core.register(epoch=epoch, tx_id=999)
            core.discard(999)

        core.set_inbound_transaction_handler(_reentrant_handler)
        frame = TransactionFrame(tx_id=1, msg_type="do_thing", code=0, payload=None)

        handle = start_worker("reentrant-inbound-callback", lambda: core.route(1, frame))
        handle.join(TEST_TIMEOUT)  # would raise WorkerTimeoutError on deadlock


class TestFailEpoch:
    def test_settles_unresolved_ack_and_completion_as_connection_closed(self) -> None:
        core = _core()
        pending = core.register(epoch=1, tx_id=1)

        core.fail_epoch(1, "connection lost")

        assert pending.ack_status is AckStatus.CONNECTION_CLOSED
        assert pending.ack_error == "connection lost"
        assert pending.completion_status is CompletionStatus.CONNECTION_CLOSED
        assert pending.completion_error == "connection lost"
        assert pending.ack_event.is_set()
        assert pending.done_event.is_set()

    def test_does_not_overwrite_an_already_settled_ack(self) -> None:
        core = _core()
        pending = core.register(epoch=1, tx_id=1)
        core.route(epoch=1, frame=TransactionFrame(tx_id=1, msg_type="ack", code=0, payload=None))

        core.fail_epoch(1, "connection lost")

        assert pending.ack_status is AckStatus.ACKNOWLEDGED
        # Completion was unresolved and must still settle.
        assert pending.completion_status is CompletionStatus.CONNECTION_CLOSED

    def test_does_not_overwrite_an_already_settled_completion(self) -> None:
        core = _core()
        pending = core.register(epoch=1, tx_id=1)
        core.route(epoch=1, frame=TransactionFrame(tx_id=1, msg_type="res", code=0, payload="ok"))

        core.fail_epoch(1, "connection lost")

        assert pending.completion_status is CompletionStatus.RESULT
        assert pending.completion_error is None

    def test_only_settles_entries_belonging_to_the_failed_epoch(self) -> None:
        core = _core()
        other_epoch_pending = core.register(epoch=2, tx_id=1)
        target_pending = core.register(epoch=1, tx_id=2)

        core.fail_epoch(1, "connection lost")

        assert other_epoch_pending.ack_status is None
        assert target_pending.ack_status is AckStatus.CONNECTION_CLOSED

    def test_does_not_remove_pending_entries(self) -> None:
        core = _core()
        core.register(epoch=1, tx_id=1)

        core.fail_epoch(1, "connection lost")

        # Still registered: a later orphan-frame check would find it present.
        assert core.wait_ack(1, timeout=0) is AckStatus.CONNECTION_CLOSED


class TestFinalizeOutcome:
    def test_returns_none_for_unknown_identifier(self) -> None:
        core = _core()
        assert (
            core.finalize_outcome(
                999, SendStatus.SENT, ack_requested=True, completion_requested=True
            )
            is None
        )

    def test_snapshots_settled_values_and_maps_unrequested_stages(self) -> None:
        core = _core()
        core.register(epoch=1, tx_id=1)
        core.route(epoch=1, frame=TransactionFrame(tx_id=1, msg_type="ack", code=0, payload=None))
        result_frame = TransactionFrame(tx_id=1, msg_type="res", code=0, payload="ok")
        core.route(epoch=1, frame=result_frame)

        outcome = core.finalize_outcome(
            1, SendStatus.SENT, ack_requested=True, completion_requested=True
        )

        assert isinstance(outcome, TransactionOutcome)
        assert outcome.tx_id == 1
        assert outcome.send_status is SendStatus.SENT
        assert outcome.ack_status is AckStatus.ACKNOWLEDGED
        assert outcome.completion_status is CompletionStatus.RESULT
        assert outcome.result is result_frame
        assert outcome.events == ()
        assert outcome.success is True

    def test_unrequested_stages_map_to_not_requested_regardless_of_settlement(self) -> None:
        core = _core()
        core.register(epoch=1, tx_id=1)
        core.route(epoch=1, frame=TransactionFrame(tx_id=1, msg_type="ack", code=0, payload=None))

        outcome = core.finalize_outcome(
            1, SendStatus.SENT, ack_requested=False, completion_requested=False
        )

        assert outcome is not None
        assert outcome.ack_status is AckStatus.NOT_REQUESTED
        assert outcome.completion_status is CompletionStatus.NOT_REQUESTED

    def test_events_tuple_is_immutable_and_arrival_ordered(self) -> None:
        core = _core()
        core.register(epoch=1, tx_id=1)
        first = TransactionFrame(tx_id=1, msg_type="evt", code=0, payload="1")
        second = TransactionFrame(tx_id=1, msg_type="evt", code=0, payload="2")
        core.route(epoch=1, frame=first)
        core.route(epoch=1, frame=second)
        core.route(epoch=1, frame=TransactionFrame(tx_id=1, msg_type="res", code=0, payload="ok"))

        outcome = core.finalize_outcome(
            1, SendStatus.SENT, ack_requested=False, completion_requested=True
        )

        assert outcome is not None
        assert outcome.events == (first, second)
        assert isinstance(outcome.events, tuple)

    def test_removes_the_pending_entry_atomically(self) -> None:
        core = _core()
        core.register(epoch=1, tx_id=1)

        first = core.finalize_outcome(
            1, SendStatus.SENT, ack_requested=False, completion_requested=False
        )
        second = core.finalize_outcome(
            1, SendStatus.SENT, ack_requested=False, completion_requested=False
        )

        assert first is not None
        assert second is None

    def test_a_later_control_frame_for_a_finalized_id_follows_orphan_routing(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        core = _core()
        core.register(epoch=1, tx_id=1)
        core.finalize_outcome(1, SendStatus.SENT, ack_requested=False, completion_requested=False)

        with caplog.at_level(logging.WARNING, logger="test-transaction-core"):
            core.route(
                epoch=1, frame=TransactionFrame(tx_id=1, msg_type="res", code=0, payload="x")
            )

        assert any("orphan" in record.message for record in caplog.records)


class TestTerminalRaceBarrierControlled:
    """Race two frames/events for the same terminal completion settlement.

    Because ``route``/``fail_epoch`` fully serialize their state mutation
    under one lock, a genuine data race cannot corrupt state; these tests
    assert the result is always exactly one legal, non-hybrid outcome no
    matter which side wins, repeated to make an accidental un-locked window
    show up as flakiness.
    """

    ITERATIONS = 30

    def test_failed_ack_versus_res_settles_exactly_one_completion_outcome(self) -> None:
        for _ in range(self.ITERATIONS):
            core = _core()
            pending = core.register(epoch=1, tx_id=1)
            barrier = threading.Barrier(2)

            def _send_failed_ack(
                core: TransactionCore = core, barrier: threading.Barrier = barrier
            ) -> None:
                barrier.wait(TEST_TIMEOUT)
                core.route(1, TransactionFrame(tx_id=1, msg_type="ack", code=5, payload="bad"))

            def _send_res(
                core: TransactionCore = core, barrier: threading.Barrier = barrier
            ) -> None:
                barrier.wait(TEST_TIMEOUT)
                core.route(1, TransactionFrame(tx_id=1, msg_type="res", code=0, payload="ok"))

            first = start_worker("failed-ack", _send_failed_ack)
            second = start_worker("res", _send_res)
            first.join(TEST_TIMEOUT)
            second.join(TEST_TIMEOUT)

            assert pending.completion_status in (CompletionStatus.ERROR, CompletionStatus.RESULT)
            if pending.completion_status is CompletionStatus.RESULT:
                assert pending.result is not None
                assert pending.completion_error is None
            else:
                assert pending.completion_error == "ack code 5: bad"
                assert pending.result is None

    def test_err_versus_res_settles_exactly_one_completion_outcome(self) -> None:
        for _ in range(self.ITERATIONS):
            core = _core()
            pending = core.register(epoch=1, tx_id=1)
            barrier = threading.Barrier(2)

            def _send_err(
                core: TransactionCore = core, barrier: threading.Barrier = barrier
            ) -> None:
                barrier.wait(TEST_TIMEOUT)
                core.route(1, TransactionFrame(tx_id=1, msg_type="err", code=1, payload="no"))

            def _send_res(
                core: TransactionCore = core, barrier: threading.Barrier = barrier
            ) -> None:
                barrier.wait(TEST_TIMEOUT)
                core.route(1, TransactionFrame(tx_id=1, msg_type="res", code=0, payload="ok"))

            first = start_worker("err", _send_err)
            second = start_worker("res", _send_res)
            first.join(TEST_TIMEOUT)
            second.join(TEST_TIMEOUT)

            assert pending.completion_status in (CompletionStatus.ERROR, CompletionStatus.RESULT)
            settled_result = pending.result
            settled_error = pending.completion_error
            # Exactly one side's data landed, never a mix of both.
            assert (settled_result is not None) != (settled_error is not None)

    def test_close_versus_res_settles_exactly_one_completion_outcome(self) -> None:
        for _ in range(self.ITERATIONS):
            core = _core()
            pending = core.register(epoch=1, tx_id=1)
            barrier = threading.Barrier(2)

            def _close(core: TransactionCore = core, barrier: threading.Barrier = barrier) -> None:
                barrier.wait(TEST_TIMEOUT)
                core.fail_epoch(1, "connection lost")

            def _send_res(
                core: TransactionCore = core, barrier: threading.Barrier = barrier
            ) -> None:
                barrier.wait(TEST_TIMEOUT)
                core.route(1, TransactionFrame(tx_id=1, msg_type="res", code=0, payload="ok"))

            first = start_worker("close", _close)
            second = start_worker("res", _send_res)
            first.join(TEST_TIMEOUT)
            second.join(TEST_TIMEOUT)

            assert pending.completion_status in (
                CompletionStatus.CONNECTION_CLOSED,
                CompletionStatus.RESULT,
            )
            if pending.completion_status is CompletionStatus.RESULT:
                assert pending.result is not None
            else:
                assert pending.completion_error == "connection lost"
            # Whichever side lost, the event must still be signaled (either by
            # its own settlement or by fail_epoch's unconditional signal).
            assert pending.done_event.is_set()


class TestAtomicFinalizationVersusLateFrame:
    def test_finalize_and_a_late_frame_never_produce_a_hybrid_state(self) -> None:
        for _ in range(30):
            core = _core()
            core.register(epoch=1, tx_id=1)
            core.route(
                epoch=1, frame=TransactionFrame(tx_id=1, msg_type="res", code=0, payload="ok")
            )
            barrier = threading.Barrier(2)
            outcomes: list[TransactionOutcome | None] = []

            def _finalize(
                core: TransactionCore = core,
                barrier: threading.Barrier = barrier,
                outcomes: list[TransactionOutcome | None] = outcomes,
            ) -> None:
                barrier.wait(TEST_TIMEOUT)
                outcomes.append(
                    core.finalize_outcome(
                        1, SendStatus.SENT, ack_requested=False, completion_requested=True
                    )
                )

            def _late_frame(
                core: TransactionCore = core, barrier: threading.Barrier = barrier
            ) -> None:
                barrier.wait(TEST_TIMEOUT)
                # Late event: dropped if it arrives while still pending
                # (completion already RESULT), or orphan-routed if finalize
                # already removed the entry. Either way, must not raise and
                # must not appear in a snapshot finalize returns.
                core.route(1, TransactionFrame(tx_id=1, msg_type="evt", code=0, payload="late"))

            first = start_worker("finalize", _finalize)
            second = start_worker("late-frame", _late_frame)
            first.join(TEST_TIMEOUT)
            second.join(TEST_TIMEOUT)

            assert len(outcomes) == 1
            outcome = outcomes[0]
            assert outcome is not None
            assert outcome.events == ()  # the late evt never lands in the snapshot
            assert outcome.completion_status is CompletionStatus.RESULT

            # The entry is gone either way: a repeat finalize returns None.
            assert (
                core.finalize_outcome(
                    1, SendStatus.SENT, ack_requested=False, completion_requested=True
                )
                is None
            )
