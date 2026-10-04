"""
Tests for the threaded transaction protocol values (Action Plan 25, chunk 02):
``TransactionFrame``, ``SendStatus``, ``AckStatus``, ``CompletionStatus``, and
the immutable ``TransactionOutcome``.

Contract: ``.claude/specs/threadedTransactionProtocol.md`` ("Transaction frame"
and "Pending transaction" sections). This module intentionally has no socket
or transaction-core behavior — codecs, routing, and mutable pending state are
out of scope for this chunk.
"""

import ast
import dataclasses
import inspect

import pytest

from foundation_tools.socket_transaction import transaction_models
from foundation_tools.socket_transaction.transaction_models import (
    AckStatus,
    CompletionStatus,
    SendStatus,
    TransactionFrame,
    TransactionOutcome,
)


def test_transaction_models_has_no_socket_or_asyncio_import() -> None:
    """Acceptance: this module imports neither ``socket`` nor ``asyncio``."""
    source = inspect.getsource(transaction_models)
    tree = ast.parse(source)
    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_modules.add(node.module.split(".")[0])

    assert "socket" not in imported_modules
    assert "asyncio" not in imported_modules


class TestSendStatus:
    def test_members(self) -> None:
        assert {member.name for member in SendStatus} == {"SENT", "NOT_CONNECTED", "FAILED"}


class TestAckStatus:
    def test_members(self) -> None:
        assert {member.name for member in AckStatus} == {
            "NOT_REQUESTED",
            "ACKNOWLEDGED",
            "REJECTED",
            "TIMED_OUT",
            "CONNECTION_CLOSED",
        }


class TestCompletionStatus:
    def test_members(self) -> None:
        assert {member.name for member in CompletionStatus} == {
            "NOT_REQUESTED",
            "RESULT",
            "ERROR",
            "TIMED_OUT",
            "CONNECTION_CLOSED",
        }


class TestTransactionFrame:
    def test_construct_with_all_payload_shapes(self) -> None:
        assert TransactionFrame(tx_id=1, msg_type="req", code=0).payload is None
        assert (
            TransactionFrame(tx_id=1, msg_type="req", code=0, payload=b"bytes").payload == b"bytes"
        )
        assert TransactionFrame(tx_id=1, msg_type="req", code=0, payload="text").payload == "text"
        assert TransactionFrame(tx_id=1, msg_type="req", code=0, payload={"a": 1}).payload == {
            "a": 1
        }

    def test_is_frozen(self) -> None:
        frame = TransactionFrame(tx_id=1, msg_type="req", code=0)
        with pytest.raises(dataclasses.FrozenInstanceError):
            frame.tx_id = 2  # type: ignore[misc]

    def test_frozen_rejects_every_field(self) -> None:
        frame = TransactionFrame(tx_id=1, msg_type="req", code=0)
        for field_name, value in (
            ("msg_type", "res"),
            ("code", 1),
            ("payload", "x"),
        ):
            with pytest.raises(dataclasses.FrozenInstanceError):
                setattr(frame, field_name, value)


class TestTransactionOutcomeImmutability:
    def _outcome(self, **overrides: object) -> TransactionOutcome:
        defaults: dict[str, object] = {
            "tx_id": 1,
            "send_status": SendStatus.SENT,
            "ack_status": AckStatus.NOT_REQUESTED,
            "completion_status": CompletionStatus.NOT_REQUESTED,
            "result": None,
            "ack_error": None,
            "completion_error": None,
        }
        defaults.update(overrides)
        return TransactionOutcome(**defaults)  # type: ignore[arg-type]

    def test_is_frozen(self) -> None:
        outcome = self._outcome()
        with pytest.raises(dataclasses.FrozenInstanceError):
            outcome.tx_id = 2  # type: ignore[misc]

    def test_events_defaults_to_empty_tuple(self) -> None:
        outcome = self._outcome()
        assert outcome.events == ()
        assert isinstance(outcome.events, tuple)

    def test_events_is_always_a_tuple_not_a_caller_owned_list(self) -> None:
        event_frame = TransactionFrame(tx_id=1, msg_type="evt", code=0)
        mutable_source: list[TransactionFrame] = [event_frame]

        outcome = self._outcome(events=mutable_source)

        assert isinstance(outcome.events, tuple)
        assert outcome.events == (event_frame,)

        # Mutating the caller's original list afterward must not affect the
        # outcome's stored events.
        mutable_source.append(TransactionFrame(tx_id=1, msg_type="evt", code=1))
        assert outcome.events == (event_frame,)

    def test_events_tuple_rejects_item_assignment(self) -> None:
        event_frame = TransactionFrame(tx_id=1, msg_type="evt", code=0)
        outcome = self._outcome(events=(event_frame,))
        with pytest.raises(TypeError):
            outcome.events[0] = event_frame  # type: ignore[index]


class TestTransactionOutcomeSuccessTruthTable:
    def _outcome(
        self,
        *,
        send_status: SendStatus,
        ack_status: AckStatus,
        completion_status: CompletionStatus,
    ) -> TransactionOutcome:
        return TransactionOutcome(
            tx_id=1,
            send_status=send_status,
            ack_status=ack_status,
            completion_status=completion_status,
            result=None,
            ack_error=None,
            completion_error=None,
        )

    @pytest.mark.parametrize(
        ("send_status", "ack_status", "completion_status", "expected"),
        [
            # Fire-and-forget: neither ACK nor completion requested.
            (SendStatus.SENT, AckStatus.NOT_REQUESTED, CompletionStatus.NOT_REQUESTED, True),
            (
                SendStatus.NOT_CONNECTED,
                AckStatus.NOT_REQUESTED,
                CompletionStatus.NOT_REQUESTED,
                False,
            ),
            (SendStatus.FAILED, AckStatus.NOT_REQUESTED, CompletionStatus.NOT_REQUESTED, False),
            # ACK requested only.
            (SendStatus.SENT, AckStatus.ACKNOWLEDGED, CompletionStatus.NOT_REQUESTED, True),
            (SendStatus.SENT, AckStatus.REJECTED, CompletionStatus.NOT_REQUESTED, False),
            (SendStatus.SENT, AckStatus.TIMED_OUT, CompletionStatus.NOT_REQUESTED, False),
            (SendStatus.SENT, AckStatus.CONNECTION_CLOSED, CompletionStatus.NOT_REQUESTED, False),
            # Completion requested only.
            (SendStatus.SENT, AckStatus.NOT_REQUESTED, CompletionStatus.RESULT, True),
            (SendStatus.SENT, AckStatus.NOT_REQUESTED, CompletionStatus.ERROR, False),
            (SendStatus.SENT, AckStatus.NOT_REQUESTED, CompletionStatus.TIMED_OUT, False),
            (SendStatus.SENT, AckStatus.NOT_REQUESTED, CompletionStatus.CONNECTION_CLOSED, False),
            # Both requested and both succeed.
            (SendStatus.SENT, AckStatus.ACKNOWLEDGED, CompletionStatus.RESULT, True),
            # ACK timed out but completion still resolved with a result: this
            # must be representable and unsuccessful without corrupting the
            # result frame (acceptance criterion).
            (SendStatus.SENT, AckStatus.TIMED_OUT, CompletionStatus.RESULT, False),
            # Send never went out: unsuccessful regardless of other stages.
            (SendStatus.NOT_CONNECTED, AckStatus.ACKNOWLEDGED, CompletionStatus.RESULT, False),
            (SendStatus.FAILED, AckStatus.ACKNOWLEDGED, CompletionStatus.RESULT, False),
        ],
    )
    def test_success_truth_table(
        self,
        send_status: SendStatus,
        ack_status: AckStatus,
        completion_status: CompletionStatus,
        expected: bool,
    ) -> None:
        outcome = self._outcome(
            send_status=send_status,
            ack_status=ack_status,
            completion_status=completion_status,
        )
        assert outcome.success is expected

    def test_ack_timeout_does_not_corrupt_the_result_frame(self) -> None:
        result_frame = TransactionFrame(tx_id=1, msg_type="res", code=0, payload="ok")
        outcome = TransactionOutcome(
            tx_id=1,
            send_status=SendStatus.SENT,
            ack_status=AckStatus.TIMED_OUT,
            completion_status=CompletionStatus.RESULT,
            result=result_frame,
            ack_error="ack timed out",
            completion_error=None,
        )
        assert outcome.success is False
        assert outcome.result == result_frame
        assert outcome.ack_error == "ack timed out"
        assert outcome.completion_error is None
