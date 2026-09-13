"""
This example shows the threaded socket-transaction stack end to end:
TransactingSocketHandlerServer (server role) and TransactingSocketHandlerClient
(client role) over a real loopback TCP connection. Unlike CLITransact, this is
a long-lived, synchronous threaded connection -- one process fork/exec per CLI
call vs. many request/reply round trips over one already-open socket (see
exampleBenchmarkPerformance.py for the throughput difference this makes).

The stack correlates replies by an internal transaction id assigned when
``send_transaction`` is called, so no tx_id wiring is needed by the caller.

Three things are demonstrated:
1. A single request/reply round trip.
2. Several concurrent requests (each fired from its own thread) resolving
   correctly out of order (the transaction core correlates replies to
   requests by transaction id, not by send order).
3. The unsolicited channel: a server-initiated broadcast that the client
   reads through its broadcast-event handler, independent of the correlated
   request/reply channel.
"""

import logging
import queue
import random
import threading
import time

from foundation_tools.socket_transaction import (
    InboundTransaction,
    JsonTransactionCodec,
    TransactingSocketHandlerClient,
    TransactingSocketHandlerServer,
    TransactionFrame,
    TransactionOutcome,
)

_LOGGER = logging.getLogger("examples.socket_client_server")
_TIMEOUT = 5.0


def _echo_handler(inbound: InboundTransaction) -> None:
    """Server-side handler: acks then echoes the request payload back as the result."""
    inbound.reply("ack", 0)
    inbound.reply("res", 0, payload=inbound.frame.payload)


def example_single_round_trip() -> None:
    print("=== Single Request/Reply Round Trip ===")
    server = TransactingSocketHandlerServer(_LOGGER, JsonTransactionCodec())
    server.set_inbound_transaction_handler(_echo_handler)
    server.listen(0)
    try:
        address = server.listening_address
        assert address is not None
        client = TransactingSocketHandlerClient(_LOGGER, JsonTransactionCodec())
        try:
            client.connect(*address, timeout=_TIMEOUT)
            server.wait_for_connection(_TIMEOUT)
            outcome = client.send_transaction(
                "request", 0, "hello-server", wait_ack=True, wait_result=True, timeout=_TIMEOUT
            )
            payload = outcome.result.payload if outcome.result is not None else None
            print(f"success={outcome.success} payload={payload!r}")
        finally:
            client.disconnect()
    finally:
        server.stop()
    print()


def example_concurrent_out_of_order() -> None:
    print("=== Concurrent Requests, Resolved Out of Order ===")

    def randomized_delay_echo(inbound: InboundTransaction) -> None:
        inbound.reply("ack", 0)
        time.sleep(random.uniform(0, 0.03))  # noqa: S311 - demo jitter only
        inbound.reply("res", 0, payload=inbound.frame.payload)

    server = TransactingSocketHandlerServer(_LOGGER, JsonTransactionCodec())
    server.set_inbound_transaction_handler(randomized_delay_echo)
    server.listen(0)
    try:
        address = server.listening_address
        assert address is not None
        client = TransactingSocketHandlerClient(_LOGGER, JsonTransactionCodec())
        try:
            client.connect(*address, timeout=_TIMEOUT)
            server.wait_for_connection(_TIMEOUT)

            outcomes: queue.Queue[tuple[int, TransactionOutcome]] = queue.Queue()

            def _send(i: int) -> None:
                outcome = client.send_transaction(
                    "request",
                    0,
                    f"payload-{i}",
                    wait_ack=True,
                    wait_result=True,
                    timeout=_TIMEOUT,
                )
                outcomes.put((i, outcome))

            workers = [threading.Thread(target=_send, args=(i,)) for i in range(5)]
            for worker in workers:
                worker.start()
            for worker in workers:
                worker.join(timeout=_TIMEOUT)

            collected = sorted(outcomes.get_nowait() for _ in range(5))
        finally:
            client.disconnect()
    finally:
        server.stop()

    for i, outcome in collected:
        payload = outcome.result.payload if outcome.result is not None else None
        print(f"  request {i}: success={outcome.success} payload={payload!r}")
    print()


def example_server_push_unsolicited() -> None:
    print("=== Server Push (Unsolicited Channel) ===")

    def silent_handler(inbound: InboundTransaction) -> None:
        inbound.reply("ack", 0)  # never sends a result; all traffic here is server-pushed

    server = TransactingSocketHandlerServer(_LOGGER, JsonTransactionCodec())
    server.set_inbound_transaction_handler(silent_handler)
    server.listen(0)
    try:
        address = server.listening_address
        assert address is not None
        client = TransactingSocketHandlerClient(_LOGGER, JsonTransactionCodec())
        pushes: queue.Queue[TransactionFrame] = queue.Queue()
        client.set_broadcast_event_handler(pushes.put)
        try:
            client.connect(*address, timeout=_TIMEOUT)
            server.wait_for_connection(_TIMEOUT)

            server.send_broadcast(payload="server-announcement")
            frame = pushes.get(timeout=_TIMEOUT)
            print(f"received unsolicited push: {frame.payload!r}")
        finally:
            client.disconnect()
    finally:
        server.stop()
    print()


def main() -> None:
    example_single_round_trip()
    example_concurrent_out_of_order()
    example_server_push_unsolicited()


if __name__ == "__main__":
    main()
