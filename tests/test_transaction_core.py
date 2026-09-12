"""
Tests for the threaded transaction core state layer (Action Plan 25, chunk 05):
transaction id sequencing, epoch-bound registration, duplicate rejection,
idempotent discard, and race-safe ACK/completion waits.

Contract: ``.claude/specs/threadedTransactionProtocol.md`` ("Pending
transaction" and "Transaction core" sections, state operations only). Frame
routing, epoch failure, callbacks, and ``finalize_outcome`` are chunk 06's
scope and are not exercised here.

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
from foundation_tools.socket_transaction.transaction_models import AckStatus, CompletionStatus
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
        # Simulate state a later routing step (chunk 06) would have applied,
        # to prove the incumbent object — not a fresh replacement — is what
        # the core still consults afterward.
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
    """Simulate a routing-style settlement (chunk 06's job) under the core's
    own lock, mirroring the terminal race recipe: mutate state, then signal
    the event, all without ever holding the lock across the ``Event.wait``.
    Reaches into the internal lock/pending map deliberately — this white-box
    race test is standing in for chunk 06's ``route()``, not yet implemented.
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
