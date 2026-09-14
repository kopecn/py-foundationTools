"""
Tests for the threaded transaction codec protocol and JSON codec
(Action Plan 25, chunk 03): ``TransactionCodec`` and ``JsonTransactionCodec``.

Contract: ``.claude/specs/threadedTransactionProtocol.md`` ("Codec protocol"
and "JSON codec" sections). This module intentionally has no socket,
threading, transaction-core, or angle-bracket codec behavior — those are out
of scope for this chunk.
"""

import ast
import inspect
import json
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

import pytest

from foundation_tools.socket_transaction import transaction_codecs
from foundation_tools.socket_transaction.transaction_codecs import (
    AngleBracketTransactionCodec,
    JsonTransactionCodec,
    TransactionCodec,
)
from foundation_tools.socket_transaction.transaction_models import TransactionFrame
from foundationTypes.data_model_helper import DataModelHelper


@dataclass
class _Greeting(DataModelHelper):
    """Minimal DataModelHelper payload model used only by these tests."""

    text: str
    count: int

    @classmethod
    def from_dict(cls, obj: object) -> "_Greeting":
        assert isinstance(obj, dict)
        return cls(text=obj["text"], count=obj["count"])

    def to_dict(self) -> dict[str, object]:
        return {"text": self.text, "count": self.count}


def test_transaction_codecs_has_no_transport_or_threading_import() -> None:
    """Acceptance: no transport, threading, or socket import in this module."""
    source = inspect.getsource(transaction_codecs)
    tree = ast.parse(source)
    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_modules.add(node.module.split(".")[0])

    assert "socket" not in imported_modules
    assert "asyncio" not in imported_modules
    assert "threading" not in imported_modules


class TestTransactionCodecProtocolShape:
    def test_is_a_protocol(self) -> None:
        assert getattr(TransactionCodec, "_is_protocol", False) is True

    def test_is_not_runtime_checkable(self) -> None:
        # A structural, non-runtime-checkable Protocol raises on isinstance().
        with pytest.raises(TypeError):
            isinstance(JsonTransactionCodec(), TransactionCodec)  # type: ignore[misc]

    def test_declares_delimiter_encode_decode(self) -> None:
        members = set(dir(TransactionCodec))
        assert {"delimiter", "encode", "decode"} <= members

    def test_json_codec_satisfies_protocol_structurally(self) -> None:
        @runtime_checkable
        class _CheckableCodec(Protocol):
            @property
            def delimiter(self) -> str: ...

            def encode(
                self, tx_id: int, msg_type: str, code: int, payload: object = None
            ) -> bytes: ...

            def decode(self, raw: bytes | str) -> TransactionFrame: ...

        assert isinstance(JsonTransactionCodec(), _CheckableCodec)


class TestJsonTransactionCodecDelimiter:
    def test_delimiter_is_newline(self) -> None:
        assert JsonTransactionCodec().delimiter == "\n"


class TestJsonTransactionCodecEncode:
    def test_encode_returns_utf8_bytes_ending_in_one_newline(self) -> None:
        encoded = JsonTransactionCodec().encode(1, "req", 0)
        assert isinstance(encoded, bytes)
        assert encoded.endswith(b"\n")
        assert not encoded.endswith(b"\n\n")
        decoded_text = encoded.decode("utf-8")
        assert decoded_text.count("\n") == 1

    def test_encode_no_payload_omits_payload_field(self) -> None:
        encoded = JsonTransactionCodec().encode(1, "req", 0)
        obj = json.loads(encoded.decode("utf-8"))
        assert obj == {"tx_id": 1, "msg_type": "req", "code": 0}
        assert "payload" not in obj

    def test_encode_string_payload(self) -> None:
        encoded = JsonTransactionCodec().encode(1, "req", 0, payload="hello")
        obj = json.loads(encoded.decode("utf-8"))
        assert obj["payload"] == "hello"

    def test_encode_bytes_payload_decodes_utf8(self) -> None:
        encoded = JsonTransactionCodec().encode(1, "req", 0, payload=b"hello")
        obj = json.loads(encoded.decode("utf-8"))
        assert obj["payload"] == "hello"

    def test_encode_bytes_payload_uses_replacement_for_invalid_utf8(self) -> None:
        encoded = JsonTransactionCodec().encode(1, "req", 0, payload=b"\xff\xfe")
        obj = json.loads(encoded.decode("utf-8"))
        assert "�" in obj["payload"]

    def test_encode_data_model_helper_payload_calls_to_dict(self) -> None:
        encoded = JsonTransactionCodec().encode(
            1, "req", 0, payload=_Greeting(text="hi", count=2)
        )
        obj = json.loads(encoded.decode("utf-8"))
        assert obj["payload"] == {"text": "hi", "count": 2}


class TestJsonTransactionCodecRoundTrip:
    def test_round_trip_no_payload(self) -> None:
        codec = JsonTransactionCodec()
        frame = codec.decode(codec.encode(1, "req", 0))
        assert frame == TransactionFrame(tx_id=1, msg_type="req", code=0, payload=None)

    def test_round_trip_model_payload(self) -> None:
        codec = JsonTransactionCodec()
        frame = codec.decode(codec.encode(2, "req", 0, payload=_Greeting(text="hi", count=2)))
        assert frame == TransactionFrame(
            tx_id=2, msg_type="req", code=0, payload={"text": "hi", "count": 2}
        )

    def test_round_trip_bytes_payload(self) -> None:
        codec = JsonTransactionCodec()
        frame = codec.decode(codec.encode(3, "req", 0, payload=b"hello"))
        assert frame == TransactionFrame(tx_id=3, msg_type="req", code=0, payload="hello")

    def test_round_trip_string_payload(self) -> None:
        codec = JsonTransactionCodec()
        frame = codec.decode(codec.encode(4, "req", 0, payload="hello"))
        assert frame == TransactionFrame(tx_id=4, msg_type="req", code=0, payload="hello")

    def test_decode_dictionary_payload_from_raw_json(self) -> None:
        codec = JsonTransactionCodec()
        raw = json.dumps({"tx_id": 5, "msg_type": "res", "code": 0, "payload": {"a": 1}}) + "\n"
        frame = codec.decode(raw)
        assert frame == TransactionFrame(tx_id=5, msg_type="res", code=0, payload={"a": 1})

    def test_decode_accepts_str_without_trailing_newline(self) -> None:
        codec = JsonTransactionCodec()
        raw = json.dumps({"tx_id": 1, "msg_type": "req", "code": 0})
        frame = codec.decode(raw)
        assert frame == TransactionFrame(tx_id=1, msg_type="req", code=0, payload=None)

    def test_decode_accepts_bytes_with_trailing_newline(self) -> None:
        codec = JsonTransactionCodec()
        raw = (json.dumps({"tx_id": 1, "msg_type": "req", "code": 0}) + "\n").encode("utf-8")
        frame = codec.decode(raw)
        assert frame == TransactionFrame(tx_id=1, msg_type="req", code=0, payload=None)

    def test_decode_does_not_strip_meaningful_string_content(self) -> None:
        codec = JsonTransactionCodec()
        raw = json.dumps({"tx_id": 1, "msg_type": "req", "code": 0, "payload": "a\nb "}) + "\n"
        frame = codec.decode(raw)
        assert frame.payload == "a\nb "


class TestJsonTransactionCodecMalformed:
    def test_decode_rejects_invalid_json_syntax(self) -> None:
        with pytest.raises(ValueError):
            JsonTransactionCodec().decode("{not json")

    def test_decode_rejects_invalid_utf8_bytes(self) -> None:
        with pytest.raises(ValueError):
            JsonTransactionCodec().decode(b"\xff\xfe\x00\x01")

    @pytest.mark.parametrize("root", ["[]", '"a string"', "1", "true", "null"])
    def test_decode_rejects_non_object_root(self, root: str) -> None:
        with pytest.raises(ValueError):
            JsonTransactionCodec().decode(root)

    @pytest.mark.parametrize("missing", ["tx_id", "msg_type", "code"])
    def test_decode_rejects_missing_required_field(self, missing: str) -> None:
        obj = {"tx_id": 1, "msg_type": "req", "code": 0}
        del obj[missing]
        with pytest.raises(ValueError):
            JsonTransactionCodec().decode(json.dumps(obj))

    def test_decode_rejects_boolean_tx_id(self) -> None:
        obj = {"tx_id": True, "msg_type": "req", "code": 0}
        with pytest.raises(ValueError):
            JsonTransactionCodec().decode(json.dumps(obj))

    def test_decode_rejects_boolean_code(self) -> None:
        obj = {"tx_id": 1, "msg_type": "req", "code": False}
        with pytest.raises(ValueError):
            JsonTransactionCodec().decode(json.dumps(obj))

    def test_decode_rejects_nonnumeric_tx_id(self) -> None:
        obj = {"tx_id": "abc", "msg_type": "req", "code": 0}
        with pytest.raises(ValueError):
            JsonTransactionCodec().decode(json.dumps(obj))

    def test_decode_rejects_nonnumeric_code(self) -> None:
        obj = {"tx_id": 1, "msg_type": "req", "code": "abc"}
        with pytest.raises(ValueError):
            JsonTransactionCodec().decode(json.dumps(obj))

    def test_decode_rejects_empty_msg_type(self) -> None:
        obj = {"tx_id": 1, "msg_type": "", "code": 0}
        with pytest.raises(ValueError):
            JsonTransactionCodec().decode(json.dumps(obj))

    def test_decode_rejects_non_string_msg_type(self) -> None:
        obj = {"tx_id": 1, "msg_type": 5, "code": 0}
        with pytest.raises(ValueError):
            JsonTransactionCodec().decode(json.dumps(obj))

    @pytest.mark.parametrize("bad_payload", [1, 1.5, True, ["x"]])
    def test_decode_rejects_invalid_payload_shape(self, bad_payload: object) -> None:
        obj = {"tx_id": 1, "msg_type": "req", "code": 0, "payload": bad_payload}
        with pytest.raises(ValueError):
            JsonTransactionCodec().decode(json.dumps(obj))

    def test_decode_rejects_positive_infinity_tx_id(self) -> None:
        obj = {"tx_id": float("inf"), "msg_type": "req", "code": 0}
        with pytest.raises(ValueError):
            JsonTransactionCodec().decode(json.dumps(obj))

    def test_decode_rejects_negative_infinity_tx_id(self) -> None:
        obj = {"tx_id": float("-inf"), "msg_type": "req", "code": 0}
        with pytest.raises(ValueError):
            JsonTransactionCodec().decode(json.dumps(obj))

    def test_decode_rejects_positive_infinity_code(self) -> None:
        obj = {"tx_id": 1, "msg_type": "req", "code": float("inf")}
        with pytest.raises(ValueError):
            JsonTransactionCodec().decode(json.dumps(obj))

    def test_decode_rejects_negative_infinity_code(self) -> None:
        obj = {"tx_id": 1, "msg_type": "req", "code": float("-inf")}
        with pytest.raises(ValueError):
            JsonTransactionCodec().decode(json.dumps(obj))


class TestAngleBracketTransactionCodecDelimiter:
    def test_delimiter_is_newline(self) -> None:
        assert AngleBracketTransactionCodec().delimiter == "\n"


class TestAngleBracketTransactionCodecEncode:
    def test_encode_no_payload_is_exact_wire_form(self) -> None:
        encoded = AngleBracketTransactionCodec().encode(1, "req", 0)
        assert encoded == b"<1,req,0>\n"

    def test_encode_returns_utf8_bytes_ending_in_one_newline(self) -> None:
        encoded = AngleBracketTransactionCodec().encode(1, "req", 0, payload="hi")
        assert isinstance(encoded, bytes)
        assert encoded.endswith(b"\n")
        assert not encoded.endswith(b"\n\n")
        assert encoded.decode("utf-8").count("\n") == 1

    def test_encode_string_payload(self) -> None:
        encoded = AngleBracketTransactionCodec().encode(1, "req", 0, payload="hello")
        assert encoded == b"<1,req,0,hello>\n"

    def test_encode_payload_commas_survive(self) -> None:
        encoded = AngleBracketTransactionCodec().encode(1, "req", 0, payload="a,b,c")
        assert encoded == b"<1,req,0,a,b,c>\n"

    def test_encode_payload_angle_brackets_survive(self) -> None:
        encoded = AngleBracketTransactionCodec().encode(1, "req", 0, payload="a>b")
        assert encoded == b"<1,req,0,a>b>\n"

    def test_encode_bytes_payload_decodes_utf8(self) -> None:
        encoded = AngleBracketTransactionCodec().encode(1, "req", 0, payload=b"hello")
        assert encoded == b"<1,req,0,hello>\n"

    def test_encode_bytes_payload_uses_replacement_for_invalid_utf8(self) -> None:
        encoded = AngleBracketTransactionCodec().encode(1, "req", 0, payload=b"\xff\xfe")
        assert "�" in encoded.decode("utf-8")

    def test_encode_data_model_helper_payload_uses_to_bytes(self) -> None:
        model = _Greeting(text="hi", count=2)
        encoded = AngleBracketTransactionCodec().encode(1, "req", 0, payload=model)
        expected_payload = model.to_bytes().decode("utf-8", errors="replace")
        assert encoded == f"<1,req,0,{expected_payload}>\n".encode()

    def test_encode_rejects_empty_msg_type(self) -> None:
        with pytest.raises(ValueError):
            AngleBracketTransactionCodec().encode(1, "", 0)

    def test_encode_rejects_comma_in_msg_type(self) -> None:
        with pytest.raises(ValueError):
            AngleBracketTransactionCodec().encode(1, "re,q", 0)

    def test_encode_rejects_cr_in_msg_type(self) -> None:
        with pytest.raises(ValueError):
            AngleBracketTransactionCodec().encode(1, "re\rq", 0)

    def test_encode_rejects_lf_in_msg_type(self) -> None:
        with pytest.raises(ValueError):
            AngleBracketTransactionCodec().encode(1, "re\nq", 0)

    def test_encode_rejects_cr_in_payload(self) -> None:
        with pytest.raises(ValueError):
            AngleBracketTransactionCodec().encode(1, "req", 0, payload="a\rb")

    def test_encode_rejects_lf_in_payload(self) -> None:
        with pytest.raises(ValueError):
            AngleBracketTransactionCodec().encode(1, "req", 0, payload="a\nb")

    def test_encode_rejects_lf_in_bytes_payload(self) -> None:
        with pytest.raises(ValueError):
            AngleBracketTransactionCodec().encode(1, "req", 0, payload=b"a\nb")

    def test_encode_no_bytes_emitted_on_rejected_msg_type(self) -> None:
        """No wire message escapes when the message type is ambiguous."""
        codec = AngleBracketTransactionCodec()
        try:
            codec.encode(1, "re,q", 0, payload="a\nb")
        except ValueError:
            pass
        else:
            pytest.fail("expected ValueError before any bytes were emitted")


class TestAngleBracketTransactionCodecRoundTrip:
    def test_round_trip_no_payload(self) -> None:
        codec = AngleBracketTransactionCodec()
        frame = codec.decode(codec.encode(1, "req", 0))
        assert frame == TransactionFrame(tx_id=1, msg_type="req", code=0, payload=None)

    def test_round_trip_string_payload(self) -> None:
        codec = AngleBracketTransactionCodec()
        frame = codec.decode(codec.encode(4, "req", 0, payload="hello"))
        assert frame == TransactionFrame(tx_id=4, msg_type="req", code=0, payload="hello")

    def test_round_trip_payload_with_commas(self) -> None:
        codec = AngleBracketTransactionCodec()
        frame = codec.decode(codec.encode(1, "req", 0, payload="a,b,c"))
        assert frame == TransactionFrame(tx_id=1, msg_type="req", code=0, payload="a,b,c")

    def test_round_trip_bytes_payload(self) -> None:
        codec = AngleBracketTransactionCodec()
        frame = codec.decode(codec.encode(3, "req", 0, payload=b"hello"))
        assert frame == TransactionFrame(tx_id=3, msg_type="req", code=0, payload="hello")

    def test_round_trip_model_payload(self) -> None:
        codec = AngleBracketTransactionCodec()
        model = _Greeting(text="hi", count=2)
        frame = codec.decode(codec.encode(2, "req", 0, payload=model))
        assert frame == TransactionFrame(
            tx_id=2,
            msg_type="req",
            code=0,
            payload=model.to_bytes().decode("utf-8", errors="replace"),
        )

    def test_decode_accepts_str_without_trailing_newline(self) -> None:
        codec = AngleBracketTransactionCodec()
        frame = codec.decode("<1,req,0>")
        assert frame == TransactionFrame(tx_id=1, msg_type="req", code=0, payload=None)

    def test_decode_accepts_bytes_with_trailing_newline(self) -> None:
        codec = AngleBracketTransactionCodec()
        frame = codec.decode(b"<1,req,0>\n")
        assert frame == TransactionFrame(tx_id=1, msg_type="req", code=0, payload=None)

    def test_decode_strips_surrounding_whitespace(self) -> None:
        codec = AngleBracketTransactionCodec()
        frame = codec.decode("  <1,req,0>\n  ")
        assert frame == TransactionFrame(tx_id=1, msg_type="req", code=0, payload=None)

    def test_decode_preserves_internal_angle_brackets_in_payload(self) -> None:
        codec = AngleBracketTransactionCodec()
        frame = codec.decode(codec.encode(1, "req", 0, payload="a>b<c"))
        assert frame.payload == "a>b<c"


class TestAngleBracketTransactionCodecMalformed:
    def test_decode_rejects_missing_opening_bracket(self) -> None:
        with pytest.raises(ValueError):
            AngleBracketTransactionCodec().decode("1,req,0>\n")

    def test_decode_rejects_missing_closing_bracket(self) -> None:
        with pytest.raises(ValueError):
            AngleBracketTransactionCodec().decode("<1,req,0\n")

    def test_decode_rejects_missing_fields(self) -> None:
        with pytest.raises(ValueError):
            AngleBracketTransactionCodec().decode("<1,req>\n")

    def test_decode_rejects_invalid_tx_id(self) -> None:
        with pytest.raises(ValueError):
            AngleBracketTransactionCodec().decode("<abc,req,0>\n")

    def test_decode_rejects_invalid_code(self) -> None:
        with pytest.raises(ValueError):
            AngleBracketTransactionCodec().decode("<1,req,abc>\n")

    def test_decode_rejects_empty_msg_type(self) -> None:
        with pytest.raises(ValueError):
            AngleBracketTransactionCodec().decode("<1,,0>\n")

    def test_decode_rejects_empty_string(self) -> None:
        with pytest.raises(ValueError):
            AngleBracketTransactionCodec().decode("")
