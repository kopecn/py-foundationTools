---
human_ask: >
  I want you to take top level spec: /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/.claude/plans/25-threaded-socket-transaction.md and reduce it to a plural set of bite sized tasks that will rip and tear /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/src/foundation_tools/socket_transaction/...   I do not want to use asyncio for the socket handling and want it reduced to threading and sockets.
goal: >
  Implement the synchronous IPv4 threaded socket client connection lifecycle.
last_updated: 2026-09-12
semver: 0.0.1
author: Nicholas Bergantz
status: completed
---

# 09 — Threaded socket client

Scope: [summary goal](00-overview.md#summary-goal) · [original ask](00-original-ask.md) · Contract: [client](../../specs/threadedSocketTransport.md#client)

## Deliverable

Create `SocketHandlerClient` with synchronous IPv4 connect, incumbent disconnect, connection timeout validation, blocking-mode restoration, and attachment to the base receive lifecycle.

## Depends on

08 raw and delimiter-text receive dispatch.

## Files

- Create `src/foundation_tools/socket_transaction/socket_handler_client.py`.
- Create `tests/test_socket_handler_client.py`.

## Design constraints

- Constructor accepts logger, delimiter, and join timeout only; host/port/timeout belong to each `connect` call.
- Validate timeout (`None` or finite positive) before disconnecting an incumbent.
- Create `AF_INET`/`SOCK_STREAM`, apply timeout, connect, call `settimeout(None)`, then attach.
- Failed connect closes the candidate and propagates the original `OSError`; it does not leave a receive thread or attached socket.
- A valid reconnect disconnects the incumbent first even if the replacement connect later fails.

## TDD steps

1. Add failing socket-double tests for constructor forwarding, timeout validation order, socket family/type, connect call, blocking restoration, and candidate cleanup.
2. Add real loopback tests for connect/send/receive/disconnect and successful reconnect with fresh epoch state.
3. Implement `SocketHandlerClient` without compatibility with `PeripheralByteTransport`.
4. Run `pytest tests/test_socket_handler_client.py` and `make fullCheck`.

## Acceptance criteria

- [x] Invalid timeout leaves an incumbent connected because validation precedes disconnect.
- [x] Valid reconnect closes the incumbent and attaches a fresh blocking socket.
- [x] Failed replacement leaves the handler disconnected and the candidate closed.
- [x] `isinstance(client, PeripheralByteTransport)` is not asserted or supported.
- [x] `make fullCheck` passes.

## Out of scope

- Automatic reconnect, keepalive, TLS, UDP, IPv6.
- Transaction codecs/facades.
- Synchronous context-manager additions not specified by the contract.

## Ask ↔ result

- **Objective (human_ask + goal):** the recorded `human_ask` is the top-level directive to replace the asyncio socket stack in `src/foundation_tools/socket_transaction/` with threading/sockets. This chunk's `goal` narrows that to: implement the synchronous IPv4 threaded socket client connection lifecycle. No conflict between `human_ask` and `goal`.
- **Live authorization:** `/execute-plan .claude/plans/25-threaded-socket-transaction` — the user explicitly authorized executing chunk 09 now.
- **Delivered:** `src/foundation_tools/socket_transaction/socket_handler_client.py` — `SocketHandlerClient(SocketHandler)` with no constructor override (inherits `logger`, `string_delimiter`, `join_timeout` unchanged from `SocketHandler.__init__`) and one added method, `connect(self, host, port, timeout=1.0)`. `connect` validates the timeout (`None` or finite and strictly positive, via `_validate_connect_timeout`) before calling `self.disconnect()` on any incumbent; creates `socket.socket(socket.AF_INET, socket.SOCK_STREAM)`; applies the requested timeout with `settimeout`; calls `connect((host, port))`; on `OSError` closes the candidate and re-raises the original exception unchanged; on success calls `settimeout(None)` to restore blocking mode, then `self._attach(candidate)`. Not a `foundation_abc.PeripheralByteTransport` — no import, no inheritance, no async methods; `rg -n "asyncio|PeripheralByteTransport|async def"` against the new file matches only an explanatory docstring line.
- `tests/test_socket_handler_client.py` — 22 tests, all synchronized with `threading.Event`/bounded `queue.Queue.get(timeout=...)` or real loopback accept/recv, no sleeps or randomness:
  - `TestConstructorForwarding` (5): logger/delimiter/join_timeout forwarding, defaults, empty-delimiter and non-finite/non-positive join_timeout still raise via the inherited base validation.
  - `TestTimeoutValidationOrder` (5, parametrized `0.0, -1.0, inf, -inf, nan`): a real loopback incumbent connection survives an invalid `connect` timeout — asserted both behaviorally (`is_connected` stays `True`, epoch unchanged) and via a `socket.socket` replacement that raises `AssertionError` if called, proving no candidate socket is even created before the `ValueError`.
  - `TestConnectSocketDouble` (7), using a `_FakeConnectSocket` double that monkeypatches `socket.socket`: `AF_INET`/`SOCK_STREAM` construction args; the `connect((host, port))` call; the `settimeout` call sequence (`[timeout, None]` and `[None, None]` for a `None` timeout) proving blocking-mode restoration; a successful connect attaching and starting the receive thread; a failed connect closing the candidate and re-raising the exact original `OSError` instance with no receive thread or attached socket left; a failed replacement candidate leaving the handler disconnected (incumbent already torn down) with the failed candidate closed.
  - `TestConnectRealLoopback` (2), using `tests/threaded_socket_helpers.ThreadedLoopbackListener`: full real connect/send/receive/disconnect round trip; and a successful reconnect to a second listener that observes the first listener's peer socket hit EOF (incumbent disconnected first) while the new epoch (`> ` the old one) sends/receives correctly.
- **Verification:** ran the new test file before creating the implementation — collection failed with `ModuleNotFoundError` for `socket_handler_client`, confirming the tests were genuinely failing pre-implementation. After implementing, `pytest tests/test_socket_handler_client.py -v` — 22/22 passed. `rg -n "asyncio|PeripheralByteTransport|async def" src/foundation_tools/socket_transaction/socket_handler_client.py` — only the explanatory docstring line matches. `make fullCheck` — flake8, strict mypy (`src` + `tests`), and the full pytest suite (893 tests, up from 871 before this chunk) all passed.
- **Gap:** none against this chunk's in-scope deliverable. `git status --short` confirms only `src/foundation_tools/socket_transaction/socket_handler_client.py` and `tests/test_socket_handler_client.py` were added; no package export, automatic reconnect, keepalive, TLS, UDP, IPv6, transaction codec/facade, or context-manager addition was made.
