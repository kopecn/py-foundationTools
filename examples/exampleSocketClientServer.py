"""Usage examples for the threaded socket-transaction stack: server + client over a
loopback TCP connection, correlating replies by transaction id."""

import logging
import queue
import threading

from foundation_tools.socket_transaction import (
    InboundTransaction,
    JsonTransactionCodec,
    TransactingSocketHandlerClient,
    TransactingSocketHandlerServer,
)

_LOGGER = logging.getLogger("examples.socket_client_server")
_TIMEOUT = 5.0


def echo_handler(inbound: InboundTransaction) -> None:
    """Server side: ack, then echo the request payload back as the result."""
    inbound.reply("ack", 0)
    inbound.reply("res", 0, payload=inbound.frame.payload)


print("---- single request/reply round trip ----")
server = TransactingSocketHandlerServer(_LOGGER, JsonTransactionCodec())
server.set_inbound_transaction_handler(echo_handler)
server.listen(0)
host, port = server.listening_address
client = TransactingSocketHandlerClient(_LOGGER, JsonTransactionCodec())
client.connect(host, port, timeout=_TIMEOUT)
server.wait_for_connection(_TIMEOUT)
outcome = client.send_transaction(
    "request", 0, "hello-server", wait_ack=True, wait_result=True, timeout=_TIMEOUT
)
payload = outcome.result.payload if outcome.result else None
print(f"success={outcome.success} payload={payload!r}")

print("\n---- concurrent requests, correlated by transaction id ----")
outcomes: queue.Queue = queue.Queue()


def send(i: int) -> None:
    result = client.send_transaction(
        "request", 0, f"payload-{i}", wait_ack=True, wait_result=True, timeout=_TIMEOUT
    )
    outcomes.put((i, result))


workers = [threading.Thread(target=send, args=(i,)) for i in range(5)]
for worker in workers:
    worker.start()
for worker in workers:
    worker.join(timeout=_TIMEOUT)
for i, result in sorted(outcomes.get_nowait() for _ in range(5)):
    payload = result.result.payload if result.result else None
    print(f"  request {i}: success={result.success} payload={payload!r}")

print("\n---- server push (unsolicited channel) ----")
pushes: queue.Queue = queue.Queue()
client.set_broadcast_event_handler(pushes.put)
server.send_broadcast(payload="server-announcement")
frame = pushes.get(timeout=_TIMEOUT)
print(f"received unsolicited push: {frame.payload!r}")

client.disconnect()
server.stop()
