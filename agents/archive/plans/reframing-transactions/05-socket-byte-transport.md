---
plan: ActionPlan05SocketByteTransport
scope: project
status: complete
last_updated: 2026-07-05
semver: 0.1.0
author: Nicholas Bergantz
---

# 05 — Socket Byte Transport

## Goal

Implement `SocketByteTransport`: an asyncio TCP client realizing the existing
`foundation_abc.PeripheralByteTransport` ABC. Raw bytes only — no framing.

Contract: Layer 1 of [socketTransact.md](../specs/socketTransact.md);
ABC: `src/foundation_abc/peripheralByteTransport.py`.

## Depends on

01 (package restructure). Independent of the CLI track.

## Files

- `src/foundation_tools/socket_transaction/socket_byte_transport.py`
- `src/foundation_tools/socket_transaction/__init__.py` (exports)
- `tests/test_socket_byte_transport.py` (pytest-asyncio)

## Design constraints

- `asyncio.open_connection` reader/writer pair; host/port/connect-timeout set at
  construction; no environment inspection.
- ABC raising semantics exactly: `ConnectionError` on failed connect,
  `RuntimeError` when sending/receiving while disconnected, `TimeoutError` when
  `receive` times out with no data; `timeout=0` non-blocking; short reads allowed
  at end-of-stream.
- **EOF signal:** when the peer has closed the connection and no buffered data
  remains, `receive` returns `b""` immediately — never `TimeoutError`. The empty
  read is the closed-connection signal the router (chunk 09) relies on.
- `disconnect()` closes the writer and awaits `wait_closed()`; double-disconnect
  is a no-op; async context manager comes from the ABC unchanged.
- Never blocks the event loop; no threads.

## Steps (TDD)

1. Test fixture: local `asyncio.start_server` echo/push server on an ephemeral port.
2. Tests first: connect/is_connected/disconnect lifecycle, `__aenter__`/`__aexit__`,
   send-receive round trip, receive timeout raises `TimeoutError`, disconnected use
   raises `RuntimeError`, refused connect raises `ConnectionError`,
   double-disconnect no-op, short read at EOF, peer-closed connection with no
   buffered data returns `b""` (not `TimeoutError`).
3. Implement the transport.
4. `make fullCheck`.

## Acceptance criteria

- [x] `isinstance(transport, PeripheralByteTransport)` and all abstract methods
      implemented per docstring contracts.
- [x] No framing/serialization knowledge in the module.
- [x] `make uv-fullCheck` passes (`make fullCheck` no longer exists).

## Out of scope

- Reconnect/keepalive logic (a future policy concern, not the transport's).
- TLS, UDP, server-side sockets.
- Codecs (chunk 08) and correlation (chunk 09).
