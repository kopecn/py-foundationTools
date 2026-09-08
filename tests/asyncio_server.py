"""Shared asyncio test-server helper.

Exists to centralize one non-obvious teardown requirement. On Python 3.12,
``asyncio.Server.wait_closed()`` blocks until every accepted connection's
transport is closed, and ``StreamReaderProtocol.eof_received()`` returns True —
which keeps the server-side transport open after the client goes away. A handler
that returns without closing its writer therefore deadlocks server teardown
forever. Python 3.11 and 3.13 do not exhibit this, so the failure is 3.12-only.

Every test that needs a real socket endpoint should go through
:func:`running_server` so no individual handler has to remember this.
"""

import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

ServerHandler = Callable[[asyncio.StreamReader, asyncio.StreamWriter], Awaitable[None]]


@asynccontextmanager
async def running_server(handler: ServerHandler) -> AsyncIterator[tuple[str, int]]:
    """Run ``handler`` on an ephemeral 127.0.0.1 port, yielding ``(host, port)``.

    ``asyncio.start_server`` begins accepting connections in the background as
    soon as it returns, so no explicit ``serve_forever()`` task is needed. On
    exit the listening socket is closed and all connection handlers are awaited;
    each connection's writer is closed for the handler, guaranteeing teardown
    completes (see module docstring).
    """

    async def _closing_handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            await handler(reader, writer)
        finally:
            writer.close()

    server = await asyncio.start_server(_closing_handler, host="127.0.0.1", port=0)
    host, port = server.sockets[0].getsockname()[:2]
    try:
        yield host, port
    finally:
        server.close()
        await server.wait_closed()
