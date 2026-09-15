---
human_ask: >
  I want you to take top level spec: /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/.claude/plans/25-threaded-socket-transaction.md and reduce it to a plural set of bite sized tasks that will rip and tear /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/src/foundation_tools/socket_transaction/...   I do not want to use asyncio for the socket handling and want it reduced to threading and sockets.
goal: >
  Close the source-authorized gaps found after execution, then make Plan 25 ready for a clean re-audit and final archival.
last_updated: 2026-09-14
semver: 0.3.1
author: Nicholas Bergantz
status: archived
---

# Plan 25 corrective actions

## Summary goal

Correct the confirmed lifecycle, framing, and protocol defects left after chunks 01-16; close the confirmed regression-coverage and documentation drift; preserve the completed historical chunks in the archive; and finish with `make fullCheck` green. This corrective set does not decide unsupported detailed contract changes.

## Original ask

The complete initiating request and planning clarifications remain preserved in the [archived original-ask record](00-original-ask.md). The human explicitly designated the [top-level socket specification](25-threaded-socket-transaction.md) as the source to decompose, so requirements stated there support corrective work. Requirements introduced only by later specs or plan prose remain open unless independently authorized.

## Audit verdict

The ask-to-result objective is substantially satisfied: the socket family is synchronous, uses `socket` and `threading`, covers client and server roles, and contains no asyncio compatibility facade. Spec conformance is incomplete because seven source-authorized defects were reproduced firsthand. `make fullCheck` remains green with 895 tests, demonstrating that the current gate does not cover these failures.

## Usability north star

A synchronous caller can connect or listen, send concurrent transactions, replace or stop connections safely, and receive only data from the connection that produced it. Public failures remain truthful and contained, and cleanup releases owned sockets without requiring an event loop.

## Corrective actions - 2026-09-13

```text
17 serialize client lifecycle --------┐
18 close listener startup race -------┤
19 suppress stale binary frames ------┤
20 make connection waits broadcast ---┤
21 make GC socket cleanup reachable --┼──> 24 regression coverage ──> 25 docs/convention sweep
22 normalize JSON numeric failures ---┤
23 route late failed ACK completion ---┘
```

| # | corrective chunk | finding | depends on |
| --- | --- | --- | --- |
| 17 | [Serialize client connection lifecycle](17-serialize-client-lifecycle.md) | PA25-01 | - |
| 18 | [Close listener startup/stop race](18-listener-start-stop-race.md) | PA25-02 | - |
| 19 | [Suppress stale binary frames](19-binary-epoch-revalidation.md) | PA25-03 | - |
| 20 | [Broadcast connection-state changes](20-connection-waiters.md) | PA25-04 | - |
| 21 | [Make garbage-collection cleanup reachable](21-gc-socket-cleanup.md) | PA25-05 | - |
| 22 | [Normalize JSON numeric failures](22-json-numeric-error-boundary.md) | PA25-06 | - |
| 23 | [Route failed ACK after ACK timeout](23-late-failed-ack-completion.md) | PA25-07 | - |
| 24 | [Close regression coverage gaps](24-regression-coverage-closure.md) | PA25-08 | 17-23 |
| 25 | [Repair documentation and archive navigation](25-docs-convention-sweep.md) | PA25-09 | 24 |

## Findings traceability

| finding | confirmed evidence | disposition |
| --- | --- | --- |
| PA25-01 | Concurrent `SocketHandlerClient.connect()` calls publish two receive workers and leave one socket open after `disconnect`; `socket_handler_client.py:33-57`, `socket_handler.py:239-270`. | Chunk 17 |
| PA25-02 | `listen()` publishes an unstarted accept thread; concurrent `stop()` raises `RuntimeError`, then the worker starts on a closed listener; `socket_handler_server.py:149-178,226-280`. | Chunk 18 |
| PA25-03 | A decoder blocked on epoch 1 can dispatch its frame after epoch 2 is attached; `binary_framed_socket_handler_client.py:74-129`. | Chunk 19 |
| PA25-04 | One connection waiter can clear the shared Event before another enters `wait()`, leaving the second blocked while connected; `socket_handler_server.py:180-205`. | Chunk 20 |
| PA25-05 | The bound atexit callback and bound receive-thread target retain an active handler, so `weakref.finalize` cannot run during ordinary garbage collection; `socket_handler.py:148-149,255-267`. | Chunk 21 |
| PA25-06 | JSON `Infinity` reaches `int()` and raises uncaught `OverflowError` instead of the required `ValueError`; `transaction_codecs.py:56-65`. | Chunk 22 |
| PA25-07 | A failed ACK arriving after ACK timeout is dropped before it can settle the independently requested completion stage; `transaction_core.py:236-268`. | Chunk 23 |
| PA25-08 | Existing tests omit the reproduced races and several source-authorized behavior boundaries, including fresh-process cutover verification. | Chunk 24 |
| PA25-09 | Active/archive links, historical statuses, serialization documentation, examples, and source docstrings contain confirmed stale statements. | Chunk 25 |

## Recorded, no action

| claim | disposition |
| --- | --- |
| The immutable `TransactionOutcome` fields can contradict detailed status/diagnostic invariants. | Recorded, no action: the typed outcome model and exact invariants are not entailed by the designated top-level specification; human contract decision required. |
| Encoders accept Boolean IDs/codes and JSON accepts an empty message type despite the later strict protocol spec. | Recorded, no action: encode-time rejection is a later contract addition without independent authorization. |
| A discarded transaction ID can be re-registered while an old internal waiter remains, and timeout settlement does not signal other internal waiters. | Recorded, no action: the public facades allocate monotonically and use one owner wait; reusable IDs and multiple waiters per transaction are not authorized requirements. |
| Byte payload diagnostics decode bytes rather than using Python's `str(bytes)` representation. | Recorded, no action: "converted to string" does not independently decide the desired bytes rendering. |
| Later specs differ from the top-level scaffold on missing JSON fields, duplicate registration, orphan control frames, odd/even IDs, and epoch-bound responders. | Recorded, no action: these are contract-provenance questions, not implementation corrections authorized by this audit. |

## Conventions inherited by every corrective chunk

1. TDD: add the deterministic failing regression first, confirm the focused failure, implement only the chunk, then run focused tests and `make fullCheck`.
2. Gate: `make fullCheck` is the completion gate.
3. Dependencies: keep `[project].dependencies` empty; production code uses only the standard library and existing project types.
4. Thread tests: use Events, Barriers, Conditions, or bounded queues/joins; no correctness assertion may depend on sleeps, random delays, or unbounded joins.
5. Errors: preserve the established public error boundary; do not broaden exception propagation while fixing lifecycle races.
6. Scope: do not add TLS, UDP, automatic reconnect, multiple active server clients, compatibility shims, or changes to `foundation_abc.PeripheralByteTransport`.
7. Authority: do not change an unsupported/open contract claim to make implementation and spec agree; return it for human decision.
8. Tracking: keep chunk frontmatter current and record ask-to-result evidence before marking a chunk completed.
9. Naming: new Python tests use snake_case files and `test*` names.
10. Ownership: preserve unrelated dirty-worktree changes and do not commit unless asked.

## Execution handoff

Run chunks 17-23 independently where convenient, then 24, then 25. Final archival remains blocked until these chunks execute and a fresh post-audit confirms closure.
