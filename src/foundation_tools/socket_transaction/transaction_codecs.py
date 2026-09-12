"""
Threaded transaction codec protocol and JSON codec (Action Plan 25, chunk 03).

Defines ``TransactionCodec``, a structural (non-runtime-checkable) protocol
for encoding/decoding one complete delimiter-terminated wire message, and
``JsonTransactionCodec``, its newline-delimited JSON implementation.

Contract: ``.claude/specs/threadedTransactionProtocol.md`` ("Codec protocol"
and "JSON codec" sections). This module intentionally has no transport,
threading, or socket behavior, no angle-bracket codec, and no transaction
routing or payload model decoding.
"""

import json
from typing import Any, Protocol

from foundation_tools.socket_transaction.transaction_models import TransactionFrame
from foundationTypes.data_model_helper import DataModelHelper


class TransactionCodec(Protocol):
    """Structural typing protocol for one wire codec.

    Deliberately not ``@runtime_checkable``: conformance is judged by
    structure at the type-checker level, not by ``isinstance()``.
    """

    @property
    def delimiter(self) -> str: ...

    def encode(
        self,
        tx_id: int,
        msg_type: str,
        code: int,
        payload: DataModelHelper | bytes | str | None = None,
    ) -> bytes: ...

    def decode(self, raw: bytes | str) -> TransactionFrame: ...


def _encode_payload(payload: DataModelHelper | bytes | str | None) -> str | dict[str, Any] | None:
    """Convert an ``encode`` payload argument into its JSON-native form."""
    if payload is None:
        return None
    if isinstance(payload, DataModelHelper):
        return payload.to_dict()
    if isinstance(payload, bytes):
        return payload.decode("utf-8", errors="replace")
    if isinstance(payload, str):
        return payload
    raise TypeError(f"Unsupported payload type for encoding: {type(payload).__name__}")


def _decode_numeric_field(value: Any, field_name: str) -> int:
    """Convert a required numeric field with ``int()``, rejecting booleans."""
    if isinstance(value, bool):
        raise ValueError(f"'{field_name}' must not be a boolean")
    if not isinstance(value, int | float | str):
        raise ValueError(f"'{field_name}' must be an int, float, or numeric string")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"'{field_name}' could not be converted to int: {exc}") from exc


def _decode_payload_field(obj: dict[str, Any]) -> str | dict[str, Any] | None:
    """Extract and validate the optional ``payload`` field of a decoded object."""
    raw_payload = obj.get("payload")
    if raw_payload is None:
        return None
    if isinstance(raw_payload, str | dict):
        return raw_payload
    raise ValueError("'payload' must be a string, object, or null")


class JsonTransactionCodec:
    """Newline-delimited JSON ``TransactionCodec`` implementation."""

    @property
    def delimiter(self) -> str:
        return "\n"

    def encode(
        self,
        tx_id: int,
        msg_type: str,
        code: int,
        payload: DataModelHelper | bytes | str | None = None,
    ) -> bytes:
        obj: dict[str, Any] = {"tx_id": tx_id, "msg_type": msg_type, "code": code}
        encoded_payload = _encode_payload(payload)
        if encoded_payload is not None:
            obj["payload"] = encoded_payload
        return (json.dumps(obj) + self.delimiter).encode("utf-8")

    def decode(self, raw: bytes | str) -> TransactionFrame:
        try:
            text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
            parsed: Any = json.loads(text)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"malformed JSON transaction message: {exc}") from exc

        if not isinstance(parsed, dict):
            raise ValueError("JSON transaction message must be an object")

        for required_field in ("tx_id", "msg_type", "code"):
            if required_field not in parsed:
                raise ValueError(
                    f"JSON transaction message missing required field '{required_field}'"
                )

        msg_type = parsed["msg_type"]
        if not isinstance(msg_type, str) or msg_type == "":
            raise ValueError("'msg_type' must be a non-empty string")

        return TransactionFrame(
            tx_id=_decode_numeric_field(parsed["tx_id"], "tx_id"),
            msg_type=msg_type,
            code=_decode_numeric_field(parsed["code"], "code"),
            payload=_decode_payload_field(parsed),
        )
