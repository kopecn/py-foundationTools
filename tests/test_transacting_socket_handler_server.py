"""
Tests for ``TransactingSocketHandlerServer`` (Action Plan 25, chunk 15): the
thin public composition of ``SocketHandlerServer``, the shared
``TransactingSocketHandler`` engine, and an even-sequence ``TransactionCore``.

Contract: ``.claude/specs/transactingSocketHandlers.md`` ("Composition and
roles" section, server facade).

Construction/wiring assertions use a distinctive fake codec (spy) so the
delimiter/logger/core wiring can be checked without depending on a specific
codec implementation. Listener/active-client lifecycle uses real loopback
sockets via ``tests/threaded_socket_helpers.py`` with
``threading.Event``/``wait_for_connection`` polling only; no test in this
file uses a sleep or random delay. Real bidirectional transaction behavior
over the wire is covered separately by
``tests/test_threaded_socket_transaction_integration.py``.
"""

from __future__ import annotations

import inspect
import logging
import socket
import threading
from typing import Any

import pytest

from foundation_tools.socket_transaction.socket_handler_server import SocketHandlerServer
from foundation_tools.socket_transaction.transacting_socket_handler import (
    TransactingSocketHandler,
)
from foundation_tools.socket_transaction.transacting_socket_handler_server import (
    TransactingSocketHandlerServer,
)
from foundation_tools.socket_transaction.transaction_codecs import JsonTransactionCodec
from foundation_tools.socket_transaction.transaction_core import TransactionCore
from foundation_tools.socket_transaction.transaction_models import (
    AckStatus,
    CompletionStatus,
    SendStatus,
)
from tests.threaded_socket_helpers import TEST_TIMEOUT

_LOOPBACK = "127.0.0.1"


def _logger(name: str) -> logging.Logger:
    return logging.getLogger(f"test.transacting_socket_handler_server.{name}")


class _SpyCodec:
    """A distinctive ``TransactionCodec``-shaped spy (not the real JSON codec).

    Its odd delimiter lets construction tests prove the contained
    ``SocketHandlerServer`` was configured from *this* codec's delimiter, not
    a hardcoded default.
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
        server = TransactingSocketHandlerServer(_logger("delimiter"), _SpyCodec())
        assert isinstance(server._socket, SocketHandlerServer)
        assert server._socket.string_delimiter == "|"

    def test_logger_identity_reaches_transport_core_and_engine_unchanged(self) -> None:
        logger = _logger("identity")
        server = TransactingSocketHandlerServer(logger, JsonTransactionCodec())
        assert server._socket._logger is logger
        assert server._core._logger is logger
        assert server._engine._logger is logger

    def test_core_is_configured_with_the_standard_even_server_sequence(self) -> None:
        server = TransactingSocketHandlerServer(_logger("sequence"), JsonTransactionCodec())
        assert isinstance(server._core, TransactionCore)
        assert server._core._next_tx_id == 2
        assert server._core._tx_id_step == 2

    def test_engine_is_built_over_the_same_socket_and_core(self) -> None:
        server = TransactingSocketHandlerServer(_logger("engine-wiring"), JsonTransactionCodec())
        assert isinstance(server._engine, TransactingSocketHandler)
        assert server._engine._transport is server._socket
        assert server._engine._core is server._core

    def test_join_timeout_forwards_to_the_contained_socket_handler(self) -> None:
        server = TransactingSocketHandlerServer(
            _logger("join-timeout"), JsonTransactionCodec(), join_timeout=2.5
        )
        assert server._socket._join_timeout == 2.5

    def test_accept_poll_interval_forwards_to_the_contained_socket_handler(self) -> None:
        server = TransactingSocketHandlerServer(
            _logger("accept-poll"), JsonTransactionCodec(), accept_poll_interval=0.05
        )
        assert server._socket._accept_poll_interval == 0.05

    def test_admission_handler_forwards_to_the_contained_socket_handler(self) -> None:
        def _handler(peer: tuple[str, int]) -> bool:
            return True

        server = TransactingSocketHandlerServer(
            _logger("admission"), JsonTransactionCodec(), connection_admission_handler=_handler
        )
        assert server._socket._connection_admission_handler is _handler

    def test_no_coroutine_or_async_context_manager_method_exists(self) -> None:
        server = TransactingSocketHandlerServer(_logger("no-async"), JsonTransactionCodec())
        assert not hasattr(server, "__aenter__")
        assert not hasattr(server, "__aexit__")
        for name in dir(server):
            if name.startswith("__"):
                continue
            attribute = getattr(type(server), name, None)
            assert not inspect.iscoroutinefunction(
                attribute
            ), f"{name!r} must not be a coroutine function"


class TestListenerLifecycleDelegation:
    def test_is_listening_and_listening_address_reflect_the_contained_server(self) -> None:
        server = TransactingSocketHandlerServer(_logger("listening"), JsonTransactionCodec())
        assert server.is_listening is False
        assert server.listening_address is None

        server.listen(0)
        try:
            assert server.is_listening is True
            assert server.listening_address == server._socket.listening_address
            assert server.listening_address is not None
            assert server.listening_address[1] != 0
        finally:
            server.stop()

        assert server.is_listening is False

    def test_stop_delegates_to_contained_server_and_is_idempotent(self) -> None:
        server = TransactingSocketHandlerServer(_logger("stop"), JsonTransactionCodec())
        server.listen(0)
        server.stop()
        assert server.is_listening is False
        server.stop()
        assert server.is_listening is False


class TestActivePeerAndConnectionDelegation:
    def test_active_peer_and_is_connected_reflect_a_real_admitted_client(self) -> None:
        server = TransactingSocketHandlerServer(_logger("active-peer"), JsonTransactionCodec())
        assert server.active_peer is None
        assert server.is_connected is False

        server.listen(0)
        try:
            address = server.listening_address
            assert address is not None
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                client_socket.connect(address)
                assert server.wait_for_connection(TEST_TIMEOUT) is True
                assert server.is_connected is True
                assert server.active_peer == client_socket.getsockname()
            finally:
                client_socket.close()
        finally:
            server.stop()

    def test_wait_for_connection_invalid_timeout_raises(self) -> None:
        server = TransactingSocketHandlerServer(_logger("wait-invalid"), JsonTransactionCodec())
        with pytest.raises(ValueError):
            server.wait_for_connection(-1.0)

    def test_wait_for_connection_zero_timeout_is_an_immediate_check(self) -> None:
        server = TransactingSocketHandlerServer(_logger("wait-zero"), JsonTransactionCodec())
        assert server.wait_for_connection(0) is False

    def test_kick_disconnects_active_client_and_leaves_listener_running(self) -> None:
        server = TransactingSocketHandlerServer(_logger("kick"), JsonTransactionCodec())
        received = threading.Event()
        server.set_string_message_handler(lambda token: received.set())
        server.listen(0)
        try:
            address = server.listening_address
            assert address is not None
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(TEST_TIMEOUT)
            try:
                client_socket.connect(address)
                assert server.wait_for_connection(TEST_TIMEOUT) is True
                # A round-tripped token proves the server's receive worker is
                # already running (not merely that the connection state was
                # published), so the deterministic `kick()` below cannot race
                # `_start_receive_worker`'s not-yet-started thread.
                client_socket.sendall(b'{"tx_id": -1, "msg_type": "evt", "code": 0}\n')
                assert received.wait(TEST_TIMEOUT)

                server.kick()

                assert server.is_connected is False
                assert server.active_peer is None
                assert server.is_listening is True
                assert client_socket.recv(1) == b""
            finally:
                client_socket.close()
        finally:
            server.stop()

    def test_disconnect_has_the_same_active_client_effect_as_kick(self) -> None:
        server = TransactingSocketHandlerServer(_logger("disconnect"), JsonTransactionCodec())
        received = threading.Event()
        server.set_string_message_handler(lambda token: received.set())
        server.listen(0)
        try:
            address = server.listening_address
            assert address is not None
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(TEST_TIMEOUT)
            try:
                client_socket.connect(address)
                assert server.wait_for_connection(TEST_TIMEOUT) is True
                client_socket.sendall(b'{"tx_id": -1, "msg_type": "evt", "code": 0}\n')
                assert received.wait(TEST_TIMEOUT)

                server.disconnect()

                assert server.is_connected is False
                assert server.active_peer is None
                assert server.is_listening is True
            finally:
                client_socket.close()
        finally:
            server.stop()


class TestEvenTransactionIdSequence:
    def test_disconnected_calls_still_consume_sequential_even_ids(self) -> None:
        server = TransactingSocketHandlerServer(_logger("disconnected-ids"), JsonTransactionCodec())

        outcomes = [server.send_transaction("cmd", 1) for _ in range(3)]

        assert [outcome.tx_id for outcome in outcomes] == [2, 4, 6]
        for outcome in outcomes:
            assert outcome.send_status is SendStatus.NOT_CONNECTED
            assert outcome.ack_status is AckStatus.CONNECTION_CLOSED
            assert outcome.completion_status is CompletionStatus.NOT_REQUESTED
