"""
Real bidirectional end-to-end tests for the threaded transacting socket stack
(Action Plan 25, chunk 15): ``TransactingSocketHandlerClient`` (chunk 14) and
``TransactingSocketHandlerServer`` (this chunk) proven over real loopback TCP
sockets, not fakes.

Contract: ``.claude/specs/transactingSocketHandlers.md`` (composition,
receive pipeline, synchronous transaction operation, and lifecycle-coupling
sections), and this chunk's "E2E coordination recipe".

All coordination uses ``threading.Event``/``threading.Barrier``, real socket
teardown propagation, and bounded ``WorkerHandle.join`` -- no test in this
file uses a sleep or randomized delay. Simultaneous bidirectional and
replacement tests use explicit "entered"/"release" gates per the chunk's
recipe so the wire-level race is deterministic rather than incidental.
"""

from __future__ import annotations

import logging
import queue
import socket
import threading

from foundation_tools.socket_transaction.transacting_socket_handler import InboundTransaction
from foundation_tools.socket_transaction.transacting_socket_handler_client import (
    TransactingSocketHandlerClient,
)
from foundation_tools.socket_transaction.transacting_socket_handler_server import (
    TransactingSocketHandlerServer,
)
from foundation_tools.socket_transaction.transaction_codecs import JsonTransactionCodec
from foundation_tools.socket_transaction.transaction_models import (
    AckStatus,
    CompletionStatus,
    SendStatus,
    TransactionFrame,
    TransactionOutcome,
)
from tests.threaded_socket_helpers import TEST_TIMEOUT, start_worker


def _logger(name: str) -> logging.Logger:
    return logging.getLogger(f"test.threaded_socket_transaction_integration.{name}")


class TestClientInitiatedRequest:
    def test_client_request_gets_server_ack_and_result(self) -> None:
        server = TransactingSocketHandlerServer(_logger("client-initiated"), JsonTransactionCodec())

        def server_inbound_handler(inbound: InboundTransaction) -> None:
            assert inbound.frame.payload == "from-client"
            assert inbound.reply("ack", 0) is True
            assert inbound.reply("res", 0, payload="from-server") is True

        server.set_inbound_transaction_handler(server_inbound_handler)
        server.listen(0)
        try:
            address = server.listening_address
            assert address is not None

            client = TransactingSocketHandlerClient(
                _logger("client-initiated"), JsonTransactionCodec()
            )
            try:
                client.connect(*address, timeout=TEST_TIMEOUT)
                assert server.wait_for_connection(TEST_TIMEOUT) is True

                outcome = client.send_transaction(
                    "request",
                    0,
                    "from-client",
                    wait_ack=True,
                    wait_result=True,
                    timeout=TEST_TIMEOUT,
                )
            finally:
                client.disconnect()
        finally:
            server.stop()

        assert outcome.tx_id % 2 == 1
        assert outcome.send_status is SendStatus.SENT
        assert outcome.ack_status is AckStatus.ACKNOWLEDGED
        assert outcome.completion_status is CompletionStatus.RESULT
        assert outcome.result is not None
        assert outcome.result.payload == "from-server"


class TestServerInitiatedRequest:
    def test_server_request_gets_client_ack_and_result(self) -> None:
        server = TransactingSocketHandlerServer(_logger("server-initiated"), JsonTransactionCodec())
        client = TransactingSocketHandlerClient(_logger("server-initiated"), JsonTransactionCodec())

        def client_inbound_handler(inbound: InboundTransaction) -> None:
            assert inbound.frame.payload == "from-server"
            assert inbound.reply("ack", 0) is True
            assert inbound.reply("res", 0, payload="from-client") is True

        client.set_inbound_transaction_handler(client_inbound_handler)
        server.listen(0)
        try:
            address = server.listening_address
            assert address is not None
            client.connect(*address, timeout=TEST_TIMEOUT)
            try:
                assert server.wait_for_connection(TEST_TIMEOUT) is True

                outcome = server.send_transaction(
                    "request",
                    0,
                    "from-server",
                    wait_ack=True,
                    wait_result=True,
                    timeout=TEST_TIMEOUT,
                )
            finally:
                client.disconnect()
        finally:
            server.stop()

        assert outcome.tx_id % 2 == 0
        assert outcome.send_status is SendStatus.SENT
        assert outcome.ack_status is AckStatus.ACKNOWLEDGED
        assert outcome.completion_status is CompletionStatus.RESULT
        assert outcome.result is not None
        assert outcome.result.payload == "from-client"


class TestSimultaneousBidirectionalTransactions:
    def test_disjoint_ids_resolve_independently_out_of_wire_order(self) -> None:
        server = TransactingSocketHandlerServer(_logger("simultaneous"), JsonTransactionCodec())
        client = TransactingSocketHandlerClient(_logger("simultaneous"), JsonTransactionCodec())

        client_request_entered = threading.Event()
        client_release = threading.Event()
        server_request_entered = threading.Event()
        server_release = threading.Event()

        def server_inbound_handler(inbound: InboundTransaction) -> None:
            # Answers the request the client initiated.
            assert inbound.reply("ack", 0) is True
            client_request_entered.set()
            assert client_release.wait(TEST_TIMEOUT)
            assert inbound.reply("res", 0, payload="server-answers-client") is True

        def client_inbound_handler(inbound: InboundTransaction) -> None:
            # Answers the request the server initiated.
            assert inbound.reply("ack", 0) is True
            server_request_entered.set()
            assert server_release.wait(TEST_TIMEOUT)
            assert inbound.reply("res", 0, payload="client-answers-server") is True

        server.set_inbound_transaction_handler(server_inbound_handler)
        client.set_inbound_transaction_handler(client_inbound_handler)

        server.listen(0)
        try:
            address = server.listening_address
            assert address is not None
            client.connect(*address, timeout=TEST_TIMEOUT)
            try:
                assert server.wait_for_connection(TEST_TIMEOUT) is True

                both_registered = threading.Barrier(3)
                outcomes: queue.Queue[tuple[str, TransactionOutcome]] = queue.Queue()

                def _initiate_from_client() -> None:
                    both_registered.wait(TEST_TIMEOUT)
                    outcome = client.send_transaction(
                        "request", 0, "from-client", wait_result=True, timeout=TEST_TIMEOUT
                    )
                    outcomes.put(("client", outcome))

                def _initiate_from_server() -> None:
                    both_registered.wait(TEST_TIMEOUT)
                    outcome = server.send_transaction(
                        "request", 0, "from-server", wait_result=True, timeout=TEST_TIMEOUT
                    )
                    outcomes.put(("server", outcome))

                with start_worker("initiate-client", _initiate_from_client), start_worker(
                    "initiate-server", _initiate_from_server
                ):
                    both_registered.wait(TEST_TIMEOUT)

                    assert client_request_entered.wait(TEST_TIMEOUT)
                    assert server_request_entered.wait(TEST_TIMEOUT)

                    # Release in the opposite order from initiation: the
                    # responder answering the server-initiated request
                    # (running on the client) finishes first, even though
                    # the client's own request was registered first.
                    server_release.set()
                    client_release.set()
            finally:
                client.disconnect()
        finally:
            server.stop()

        collected = dict(outcomes.get_nowait() for _ in range(2))
        client_outcome = collected["client"]
        server_outcome = collected["server"]

        assert client_outcome.tx_id % 2 == 1
        assert server_outcome.tx_id % 2 == 0
        assert client_outcome.send_status is SendStatus.SENT
        assert server_outcome.send_status is SendStatus.SENT
        assert client_outcome.completion_status is CompletionStatus.RESULT
        assert server_outcome.completion_status is CompletionStatus.RESULT
        assert client_outcome.result is not None
        assert server_outcome.result is not None
        assert client_outcome.result.payload == "server-answers-client"
        assert server_outcome.result.payload == "client-answers-server"


class TestTransactionEvent:
    def test_event_frame_is_retained_before_the_final_result(self) -> None:
        server = TransactingSocketHandlerServer(_logger("event"), JsonTransactionCodec())

        def server_inbound_handler(inbound: InboundTransaction) -> None:
            assert inbound.reply("ack", 0) is True
            assert inbound.reply("evt", 0, payload="progress") is True
            assert inbound.reply("res", 0, payload="done") is True

        server.set_inbound_transaction_handler(server_inbound_handler)
        server.listen(0)
        try:
            address = server.listening_address
            assert address is not None
            client = TransactingSocketHandlerClient(_logger("event"), JsonTransactionCodec())
            try:
                client.connect(*address, timeout=TEST_TIMEOUT)
                assert server.wait_for_connection(TEST_TIMEOUT) is True

                outcome = client.send_transaction(
                    "request", 0, wait_ack=True, wait_result=True, timeout=TEST_TIMEOUT
                )
            finally:
                client.disconnect()
        finally:
            server.stop()

        assert outcome.completion_status is CompletionStatus.RESULT
        assert outcome.result is not None
        assert outcome.result.payload == "done"
        assert len(outcome.events) == 1
        assert outcome.events[0].payload == "progress"


class TestBroadcast:
    def test_server_broadcast_reaches_the_active_client_only(self) -> None:
        server = TransactingSocketHandlerServer(_logger("broadcast"), JsonTransactionCodec())
        server.listen(0)
        try:
            address = server.listening_address
            assert address is not None
            client = TransactingSocketHandlerClient(_logger("broadcast"), JsonTransactionCodec())
            received: queue.Queue[TransactionFrame] = queue.Queue()
            client.set_broadcast_event_handler(received.put)
            try:
                client.connect(*address, timeout=TEST_TIMEOUT)
                assert server.wait_for_connection(TEST_TIMEOUT) is True

                assert server.send_broadcast(payload="announcement", code=7) is True

                frame = received.get(timeout=TEST_TIMEOUT)
            finally:
                client.disconnect()
        finally:
            server.stop()

        assert frame.tx_id == -1
        assert frame.msg_type == "evt"
        assert frame.code == 7
        assert frame.payload == "announcement"

    def test_disconnected_server_broadcast_is_a_no_op(self) -> None:
        server = TransactingSocketHandlerServer(
            _logger("broadcast-disconnected"), JsonTransactionCodec()
        )
        assert server.send_broadcast(payload="nobody-home") is False


class TestAdmittedReplacementWhileResponderRetained:
    def test_retained_responder_cannot_reach_the_replacement_and_a_waiter_closes(self) -> None:
        server = TransactingSocketHandlerServer(_logger("replacement"), JsonTransactionCodec())

        captured: dict[str, InboundTransaction] = {}
        responder_entered = threading.Event()

        def server_inbound_handler(inbound: InboundTransaction) -> None:
            # Deliberately retains the responder and never replies from
            # inside the handler: the test replies explicitly only after
            # client B has replaced client A, per the chunk's recipe.
            captured["inbound"] = inbound
            responder_entered.set()

        server.set_inbound_transaction_handler(server_inbound_handler)
        server.listen(0)

        address = server.listening_address
        assert address is not None

        client_a = TransactingSocketHandlerClient(_logger("replacement-a"), JsonTransactionCodec())
        client_b = TransactingSocketHandlerClient(_logger("replacement-b"), JsonTransactionCodec())
        b_tokens: queue.Queue[str] = queue.Queue()
        client_b.set_string_message_handler(b_tokens.put)

        outcome_box: dict[str, TransactionOutcome] = {}

        def _send_from_a() -> None:
            outcome_box["a"] = client_a.send_transaction(
                "request",
                0,
                "from-a",
                wait_ack=True,
                wait_result=True,
                timeout=TEST_TIMEOUT,
            )

        reply_reached_replacement = True
        try:
            client_a.connect(*address, timeout=TEST_TIMEOUT)
            assert server.wait_for_connection(TEST_TIMEOUT) is True

            handle = start_worker("client-a-send", _send_from_a)
            assert responder_entered.wait(TEST_TIMEOUT)

            client_b.connect(*address, timeout=TEST_TIMEOUT)
            assert server.wait_for_connection(TEST_TIMEOUT) is True

            # Wait for client A's own pending request to settle before
            # attempting the retained reply: A's outcome can only settle
            # once A's own socket has observed the server tear its
            # connection down for the replacement, so this join is the
            # deterministic proof that the replacement has fully happened
            # (not merely that client B's connect() call returned).
            handle.join(TEST_TIMEOUT)

            reply_reached_replacement = captured["inbound"].reply(
                "res", 0, payload="late-reply-for-a"
            )
        finally:
            client_a.disconnect()
            client_b.disconnect()
            server.stop()

        assert reply_reached_replacement is False
        assert b_tokens.empty()

        outcome_a = outcome_box["a"]
        assert outcome_a.send_status is SendStatus.SENT
        assert outcome_a.ack_status is AckStatus.CONNECTION_CLOSED
        assert outcome_a.completion_status is CompletionStatus.CONNECTION_CLOSED


class TestMalformedMessageAndCallbackExceptionRecovery:
    def test_server_role_survives_malformed_token_and_a_raising_inbound_handler(self) -> None:
        server = TransactingSocketHandlerServer(
            _logger("server-malformed"), JsonTransactionCodec()
        )
        tokens: queue.Queue[str] = queue.Queue()
        server.set_string_message_handler(tokens.put)
        server.listen(0)
        raw_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_client.settimeout(TEST_TIMEOUT)
        try:
            address = server.listening_address
            assert address is not None
            raw_client.connect(address)
            assert server.wait_for_connection(TEST_TIMEOUT) is True

            raw_client.sendall(b"not-json-at-all\n")
            assert tokens.get(timeout=TEST_TIMEOUT) == "not-json-at-all"

            raised = threading.Event()

            def failing_inbound_handler(inbound: InboundTransaction) -> None:
                raised.set()
                raise RuntimeError("boom")

            server.set_inbound_transaction_handler(failing_inbound_handler)
            raw_client.sendall(b'{"tx_id": 101, "msg_type": "request", "code": 0}\n')
            assert raised.wait(TEST_TIMEOUT)

            recovered = threading.Event()

            def working_inbound_handler(inbound: InboundTransaction) -> None:
                assert inbound.reply("ack", 0) is True
                recovered.set()

            server.set_inbound_transaction_handler(working_inbound_handler)
            raw_client.sendall(b'{"tx_id": 103, "msg_type": "request", "code": 0}\n')
            assert recovered.wait(TEST_TIMEOUT)
        finally:
            raw_client.close()
            server.stop()

    def test_client_role_survives_malformed_token_and_a_raising_inbound_handler(self) -> None:
        raw_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        raw_listener.bind(("127.0.0.1", 0))
        raw_listener.listen(1)
        address: tuple[str, int] = raw_listener.getsockname()

        client = TransactingSocketHandlerClient(_logger("client-malformed"), JsonTransactionCodec())
        tokens: queue.Queue[str] = queue.Queue()
        client.set_string_message_handler(tokens.put)

        accepted: queue.Queue[socket.socket] = queue.Queue()

        def _accept() -> None:
            connection, _ = raw_listener.accept()
            accepted.put(connection)

        try:
            with start_worker("raw-accept", _accept):
                client.connect(*address, timeout=TEST_TIMEOUT)
                raw_peer = accepted.get(timeout=TEST_TIMEOUT)

            raw_peer.settimeout(TEST_TIMEOUT)
            try:
                raw_peer.sendall(b"not-json-at-all\n")
                assert tokens.get(timeout=TEST_TIMEOUT) == "not-json-at-all"

                raised = threading.Event()

                def failing_inbound_handler(inbound: InboundTransaction) -> None:
                    raised.set()
                    raise RuntimeError("boom")

                client.set_inbound_transaction_handler(failing_inbound_handler)
                raw_peer.sendall(b'{"tx_id": 201, "msg_type": "request", "code": 0}\n')
                assert raised.wait(TEST_TIMEOUT)

                recovered = threading.Event()

                def working_inbound_handler(inbound: InboundTransaction) -> None:
                    assert inbound.reply("ack", 0) is True
                    recovered.set()

                client.set_inbound_transaction_handler(working_inbound_handler)
                raw_peer.sendall(b'{"tx_id": 203, "msg_type": "request", "code": 0}\n')
                assert recovered.wait(TEST_TIMEOUT)
            finally:
                raw_peer.close()
        finally:
            client.disconnect()
            raw_listener.close()
