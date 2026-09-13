"""
Tests for ``TransactingSocketHandlerClient`` (Action Plan 25, chunk 14): the
thin public composition of ``SocketHandlerClient``, the shared
``TransactingSocketHandler`` engine, and an odd-sequence ``TransactionCore``.

Contract: ``.claude/specs/transactingSocketHandlers.md`` ("Composition and
roles" section, client facade).

Construction/wiring assertions use a distinctive fake codec (spy) so the
delimiter/logger/core wiring can be checked without depending on a specific
codec implementation. Connection-lifecycle and close-wakeup behavior use
real loopback sockets via ``tests/threaded_socket_helpers.py`` --
``ThreadedLoopbackListener`` and ``start_worker`` -- with
``threading.Event``-based synchronization only; no test in this file uses a
sleep or random delay.
"""

from __future__ import annotations

import inspect
import logging
import threading
from typing import Any

import pytest

from foundation_tools.socket_transaction.socket_handler_client import SocketHandlerClient
from foundation_tools.socket_transaction.transacting_socket_handler import (
    TransactingSocketHandler,
)
from foundation_tools.socket_transaction.transacting_socket_handler_client import (
    TransactingSocketHandlerClient,
)
from foundation_tools.socket_transaction.transaction_codecs import JsonTransactionCodec
from foundation_tools.socket_transaction.transaction_core import TransactionCore
from foundation_tools.socket_transaction.transaction_models import (
    AckStatus,
    CompletionStatus,
    SendStatus,
    TransactionOutcome,
)
from tests.threaded_socket_helpers import TEST_TIMEOUT, ThreadedLoopbackListener, start_worker


def _logger(name: str) -> logging.Logger:
    return logging.getLogger(f"test.transacting_socket_handler_client.{name}")


class _SpyCodec:
    """A distinctive ``TransactionCodec``-shaped spy (not the real JSON codec).

    Its odd delimiter lets construction tests prove the contained
    ``SocketHandlerClient`` was configured from *this* codec's delimiter,
    not a hardcoded default.
    """

    @property
    def delimiter(self) -> str:
        return "|"

    def encode(
        self,
        tx_id: int,
        msg_type: str,
        code: int,
        payload: Any = None,
    ) -> bytes:
        return f"{tx_id}:{msg_type}:{code}".encode("utf-8")

    def decode(self, raw: bytes | str) -> Any:  # pragma: no cover - unused by these tests
        raise ValueError("spy codec decode not exercised")


class TestConstructionAndWiring:
    def test_transport_is_configured_from_codec_delimiter(self) -> None:
        client = TransactingSocketHandlerClient(_logger("delimiter"), _SpyCodec())
        assert isinstance(client._socket, SocketHandlerClient)
        assert client._socket.string_delimiter == "|"

    def test_logger_identity_reaches_transport_core_and_engine_unchanged(self) -> None:
        logger = _logger("identity")
        client = TransactingSocketHandlerClient(logger, JsonTransactionCodec())
        assert client._socket._logger is logger
        assert client._core._logger is logger
        assert client._engine._logger is logger

    def test_core_is_configured_with_the_standard_odd_client_sequence(self) -> None:
        client = TransactingSocketHandlerClient(_logger("sequence"), JsonTransactionCodec())
        assert isinstance(client._core, TransactionCore)
        assert client._core._next_tx_id == 1
        assert client._core._tx_id_step == 2

    def test_engine_is_built_over_the_same_socket_and_core(self) -> None:
        client = TransactingSocketHandlerClient(_logger("engine-wiring"), JsonTransactionCodec())
        assert isinstance(client._engine, TransactingSocketHandler)
        assert client._engine._transport is client._socket
        assert client._engine._core is client._core

    def test_join_timeout_forwards_to_the_contained_socket_handler(self) -> None:
        client = TransactingSocketHandlerClient(
            _logger("join-timeout"), JsonTransactionCodec(), join_timeout=2.5
        )
        assert client._socket._join_timeout == 2.5

    def test_no_coroutine_or_async_context_manager_method_exists(self) -> None:
        client = TransactingSocketHandlerClient(_logger("no-async"), JsonTransactionCodec())
        assert not hasattr(client, "__aenter__")
        assert not hasattr(client, "__aexit__")
        for name in dir(client):
            if name.startswith("__"):
                continue
            attribute = getattr(type(client), name, None)
            assert not inspect.iscoroutinefunction(
                attribute
            ), f"{name!r} must not be a coroutine function"


class TestConnectionLifecycleDelegation:
    def test_is_connected_reflects_the_contained_socket_handler(self) -> None:
        client = TransactingSocketHandlerClient(_logger("is-connected"), JsonTransactionCodec())
        assert client.is_connected is False

        with ThreadedLoopbackListener() as listener:
            client.connect(*listener.address, timeout=TEST_TIMEOUT)
            assert listener.accepted.wait(TEST_TIMEOUT)
            assert client.is_connected is True

            client.disconnect()
            assert client.is_connected is False
            listener.release.set()

    def test_connect_default_timeout_and_invalid_timeout_error_are_preserved(self) -> None:
        client = TransactingSocketHandlerClient(_logger("connect-errors"), JsonTransactionCodec())
        with pytest.raises(ValueError):
            client.connect("127.0.0.1", 1, timeout=0.0)
        assert client.is_connected is False

        with ThreadedLoopbackListener() as listener:
            client.connect(*listener.address)  # default timeout=1.0
            assert listener.accepted.wait(TEST_TIMEOUT)
            assert client.is_connected is True
            client.disconnect()
            listener.release.set()

    def test_disconnect_is_idempotent_like_the_contained_socket_handler(self) -> None:
        client = TransactingSocketHandlerClient(
            _logger("disconnect-idempotent"), JsonTransactionCodec()
        )
        client.disconnect()
        client.disconnect()
        assert client.is_connected is False


class TestOddTransactionIdSequence:
    def test_disconnected_calls_still_consume_sequential_odd_ids(self) -> None:
        client = TransactingSocketHandlerClient(_logger("disconnected-ids"), JsonTransactionCodec())

        outcomes = [client.send_transaction("cmd", 1) for _ in range(3)]

        assert [outcome.tx_id for outcome in outcomes] == [1, 3, 5]
        for outcome in outcomes:
            assert outcome.send_status is SendStatus.NOT_CONNECTED
            assert outcome.ack_status is AckStatus.CONNECTION_CLOSED
            assert outcome.completion_status is CompletionStatus.NOT_REQUESTED

    def test_ids_do_not_reset_across_disconnect_and_reconnect(self) -> None:
        client = TransactingSocketHandlerClient(_logger("no-reset"), JsonTransactionCodec())

        first_disconnected = client.send_transaction("cmd", 1)
        assert first_disconnected.tx_id == 1

        with ThreadedLoopbackListener() as listener_a:
            client.connect(*listener_a.address, timeout=TEST_TIMEOUT)
            assert listener_a.accepted.wait(TEST_TIMEOUT)

            connected_outcome = client.send_transaction(
                "cmd", 1, wait_ack=False, wait_result=False, timeout=TEST_TIMEOUT
            )
            assert connected_outcome.tx_id == 3
            assert connected_outcome.send_status is SendStatus.SENT

            client.disconnect()
            listener_a.release.set()

        second_disconnected = client.send_transaction("cmd", 1)
        assert second_disconnected.tx_id == 5

        with ThreadedLoopbackListener() as listener_b:
            client.connect(*listener_b.address, timeout=TEST_TIMEOUT)
            assert listener_b.accepted.wait(TEST_TIMEOUT)

            reconnected_outcome = client.send_transaction(
                "cmd", 1, wait_ack=False, wait_result=False, timeout=TEST_TIMEOUT
            )
            assert reconnected_outcome.tx_id == 7
            assert reconnected_outcome.send_status is SendStatus.SENT

            client.disconnect()
            listener_b.release.set()


class TestCloseWakesPendingClientOperations:
    def test_disconnect_wakes_a_blocked_ack_wait_as_connection_closed(self) -> None:
        client = TransactingSocketHandlerClient(_logger("wake-disconnect"), JsonTransactionCodec())

        waiting = threading.Event()
        original_wait_ack = client._core.wait_ack

        def _wait_ack_and_signal(tx_id: int, timeout: float | None = None) -> AckStatus | None:
            waiting.set()
            return original_wait_ack(tx_id, timeout)

        client._core.wait_ack = _wait_ack_and_signal  # type: ignore[method-assign]

        outcome_box: dict[str, TransactionOutcome] = {}

        def _send() -> None:
            outcome_box["outcome"] = client.send_transaction(
                "cmd", 1, wait_ack=True, wait_result=False, timeout=TEST_TIMEOUT
            )

        with ThreadedLoopbackListener() as listener:
            client.connect(*listener.address, timeout=TEST_TIMEOUT)
            assert listener.accepted.wait(TEST_TIMEOUT)

            with start_worker("pending-send-transaction", _send):
                assert waiting.wait(TEST_TIMEOUT)
                client.disconnect()

            listener.release.set()

        outcome = outcome_box["outcome"]
        assert outcome.send_status is SendStatus.SENT
        assert outcome.ack_status is AckStatus.CONNECTION_CLOSED
        assert outcome.completion_status is CompletionStatus.NOT_REQUESTED
        assert len(client._core._pending) == 0

    def test_reconnect_wakes_the_old_epochs_pending_op_and_new_calls_use_the_new_epoch(
        self,
    ) -> None:
        client = TransactingSocketHandlerClient(_logger("wake-reconnect"), JsonTransactionCodec())

        waiting = threading.Event()
        original_wait_ack = client._core.wait_ack

        def _wait_ack_and_signal(tx_id: int, timeout: float | None = None) -> AckStatus | None:
            waiting.set()
            return original_wait_ack(tx_id, timeout)

        client._core.wait_ack = _wait_ack_and_signal  # type: ignore[method-assign]

        outcome_box: dict[str, TransactionOutcome] = {}

        def _send() -> None:
            outcome_box["outcome"] = client.send_transaction(
                "cmd", 1, wait_ack=True, wait_result=False, timeout=TEST_TIMEOUT
            )

        with ThreadedLoopbackListener() as listener_a, ThreadedLoopbackListener() as listener_b:
            client.connect(*listener_a.address, timeout=TEST_TIMEOUT)
            assert listener_a.accepted.wait(TEST_TIMEOUT)

            with start_worker("pending-send-transaction", _send):
                assert waiting.wait(TEST_TIMEOUT)
                # A fresh connect disconnects the incumbent (listener_a's
                # epoch) before attaching the new one, waking the pending op
                # above exactly like an explicit disconnect would.
                client.connect(*listener_b.address, timeout=TEST_TIMEOUT)
                assert listener_b.accepted.wait(TEST_TIMEOUT)

            listener_a.release.set()

            new_outcome = client.send_transaction(
                "cmd", 2, wait_ack=False, wait_result=False, timeout=TEST_TIMEOUT
            )
            client.disconnect()
            listener_b.release.set()

        old_outcome = outcome_box["outcome"]
        assert old_outcome.send_status is SendStatus.SENT
        assert old_outcome.ack_status is AckStatus.CONNECTION_CLOSED

        assert new_outcome.send_status is SendStatus.SENT
        assert new_outcome.tx_id == old_outcome.tx_id + 2
