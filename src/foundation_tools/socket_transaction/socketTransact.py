"""
SocketTransact — Layer 4 (public facade) of the socket-transaction stack.

The only class socket end users touch: mirrors the ``CLITransact`` ethos of a
minimal surface, result objects, and total containment on the transaction
methods. Wires the default stack (``SocketByteTransport`` -> codec ->
``TransactionRouter``); an alternative ``PeripheralByteTransport`` may be
injected. See ``.claude/specs/socketTransact.md`` (Layer 4) for the full
contract.
"""

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Generic, TypeVar

from foundation_abc.peripheralByteTransport import PeripheralByteTransport
from foundation_tools.socket_transaction._lifecycle import (
    LifecycleState,
    require_min,
    require_positive,
)
from foundation_tools.socket_transaction.framing_codecs import DelimiterCodec, FramingCodec
from foundation_tools.socket_transaction.socket_byte_transport import SocketByteTransport
from foundation_tools.socket_transaction.transaction_router import (
    DEFAULT_POLL_TIMEOUT,
    DEFAULT_READ_SIZE,
    DEFAULT_UNSOLICITED_MAXSIZE,
    TransactionRouter,
    TxIdExtractor,
    TxIdGenerator,
    TxIdInjector,
)
from foundationTypes.data_model_helper import DataModelHelper

T = TypeVar("T", bound=DataModelHelper)


@dataclass
class SocketTransactResult:
    """Result container for one correlated socket request.

    Attributes:
        payload: The reply frame's raw bytes, or None on failure.
        error: Diagnostic message on failure (timeout, connection loss, codec
            error, or contained exception); None on success.
        success: Whether a correlated reply was received.
    """

    payload: bytes | None = None
    error: str | None = None
    success: bool = False


@dataclass
class SocketTransactResultModel(SocketTransactResult, Generic[T]):
    """Extended result container that includes a parsed data model.

    Attributes:
        model: Parsed data model instance created from the reply payload via
            ``Model.from_wire``. None if the request failed, the reply payload
            was empty, or the parser raised.
    """

    model: T | None = None


class SocketTransact:
    """Public facade for the socket-transaction stack.

    Construction wires the default stack: ``SocketByteTransport`` (or an
    injected ``PeripheralByteTransport``) -> ``codec`` -> ``TransactionRouter``.
    The tx_id correlation pair is required — there is no default because the
    wire format is protocol-specific and this stack defines none of its own.

    Example:
        async with SocketTransact(
            host, port,
            tx_id_injector=my_injector,
            tx_id_extractor=my_extractor,
        ) as st:
            result = await st.request_with_model(model, ModelType)
    """

    def __init__(
        self,
        host: str,
        port: int,
        *,
        tx_id_injector: TxIdInjector,
        tx_id_extractor: TxIdExtractor,
        codec: FramingCodec | None = None,
        tx_id_generator: TxIdGenerator | None = None,
        transport: PeripheralByteTransport | None = None,
        connect_timeout: float = 5.0,
        read_size: int = DEFAULT_READ_SIZE,
        poll_timeout: float = DEFAULT_POLL_TIMEOUT,
        unsolicited_maxsize: int = DEFAULT_UNSOLICITED_MAXSIZE,
    ) -> None:
        require_positive("connect_timeout", connect_timeout)
        require_positive("read_size", read_size)
        require_positive("poll_timeout", poll_timeout)
        require_min("unsolicited_maxsize", unsolicited_maxsize, 1)
        self._state = LifecycleState.IDLE
        self._codec = codec if codec is not None else DelimiterCodec()
        self._transport = (
            transport
            if transport is not None
            else SocketByteTransport(host, port, connect_timeout=connect_timeout)
        )
        self._router = TransactionRouter(
            self._transport,
            self._codec,
            tx_id_injector=tx_id_injector,
            tx_id_extractor=tx_id_extractor,
            tx_id_generator=tx_id_generator,
            read_size=read_size,
            poll_timeout=poll_timeout,
            unsolicited_maxsize=unsolicited_maxsize,
        )

    # -----------------------------------------------------------------------
    # MARK: - Lifecycle
    # -----------------------------------------------------------------------

    async def connect(self) -> None:
        """Open the transport and start the router's reader task.

        Raises ``RuntimeError`` if already connected — a live connection is never
        silently replaced. The instance may be reconnected after ``disconnect()``.
        """
        if self._state is LifecycleState.ACTIVE:
            raise RuntimeError("Cannot connect: already connected")
        await self._transport.connect()
        self._router.start()
        self._state = LifecycleState.ACTIVE

    async def disconnect(self) -> None:
        """Stop the router and close the transport. A no-op if not connected;
        clears in-flight state while retaining construction configuration."""
        if self._state is LifecycleState.IDLE:
            return
        await self._router.stop()
        await self._transport.disconnect()
        self._state = LifecycleState.IDLE

    async def __aenter__(self) -> "SocketTransact":
        await self.connect()
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        await self.disconnect()

    # -----------------------------------------------------------------------
    # MARK: - Public — request/reply
    # -----------------------------------------------------------------------

    async def request(
        self, payload: bytes, *, tx_id: str | None = None, timeout: float | None = None
    ) -> SocketTransactResult:
        """Send ``payload``, awaiting the correlated reply.

        Never raises: timeout, connection loss, and codec errors are captured
        into the result (``success=False``, diagnostic in ``error``).
        """
        try:
            reply = await self._router.request(payload, tx_id=tx_id, timeout=timeout)
        except Exception as error:  # pylint: disable=broad-exception-caught
            return SocketTransactResult(success=False, error=str(error))
        return SocketTransactResult(payload=reply, success=True)

    async def request_with_model(
        self,
        model_or_payload: DataModelHelper | bytes,
        model_type: type[T],
        *,
        tx_id: str | None = None,
        timeout: float | None = None,
    ) -> SocketTransactResultModel[T]:
        """Send a model (via ``to_wire``) or raw payload, parsing the reply via
        ``model_type.from_wire``.

        Parsing runs only on success with a non-empty reply payload, and never
        changes ``success`` — a parser failure is appended to ``error``.
        """
        try:
            payload = self._encode_outbound(model_or_payload)
        except Exception as error:  # pylint: disable=broad-exception-caught
            return SocketTransactResultModel[T](
                success=False, error=f"Outbound model serialization failed: {error}"
            )

        base_result = await self.request(payload, tx_id=tx_id, timeout=timeout)
        return self._attach_model(base_result, model_type)

    async def send(self, payload: bytes) -> None:
        """Send an uncorrelated, fire-and-forget frame.

        Raises on transport failure — a transport-level operation, not a
        transaction result.
        """
        await self._transport.send(self._codec.encode(payload))

    def unsolicited(self) -> AsyncIterator[bytes]:
        """Async iterator of frames with no matching pending request (server
        pushes, broadcasts)."""
        return self._router.unsolicited()

    # -----------------------------------------------------------------------
    # MARK: - Private — implementation
    # -----------------------------------------------------------------------

    def _encode_outbound(self, model_or_payload: DataModelHelper | bytes) -> bytes:
        if isinstance(model_or_payload, DataModelHelper):
            return model_or_payload.to_wire().encode("utf-8")
        return model_or_payload

    def _attach_model(
        self, base_result: SocketTransactResult, model_type: type[T]
    ) -> SocketTransactResultModel[T]:
        extended_result = SocketTransactResultModel[T](
            payload=base_result.payload,
            error=base_result.error,
            success=base_result.success,
            model=None,
        )

        if base_result.success and base_result.payload:
            try:
                extended_result.model = model_type.from_wire(base_result.payload.decode("utf-8"))
            except Exception as parse_error:  # pylint: disable=broad-exception-caught
                extended_result.error = (
                    f"{base_result.error or ''}\nModel parsing failed: {parse_error}"
                ).strip()

        return extended_result
