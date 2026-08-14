"""
Tests for the framing-codec layer (Action Plan 08): FramingCodec protocol,
DelimiterCodec, LengthPrefixedCodec.
"""

import json

import pytest

from foundation_tools.socket_transaction import DelimiterCodec, FramingCodec, LengthPrefixedCodec
from foundationTypes.commonTypes.GeoCoordinate import GeoCoordinate


class TestFramingCodecProtocol:
    def test_delimiter_codec_satisfies_protocol(self) -> None:
        assert isinstance(DelimiterCodec(), FramingCodec)

    def test_length_prefixed_codec_satisfies_protocol(self) -> None:
        assert isinstance(LengthPrefixedCodec(), FramingCodec)


class TestDelimiterCodec:
    def test_single_frame_round_trip(self) -> None:
        codec = DelimiterCodec()
        encoded = codec.encode(b"hello")
        assert codec.feed(encoded) == [b"hello"]

    def test_multi_frame_in_one_chunk(self) -> None:
        codec = DelimiterCodec()
        chunk = codec.encode(b"one") + codec.encode(b"two") + codec.encode(b"three")
        assert codec.feed(chunk) == [b"one", b"two", b"three"]

    def test_frame_split_across_many_chunks_byte_at_a_time(self) -> None:
        codec = DelimiterCodec()
        encoded = codec.encode(b"hello")
        frames: list[bytes] = []
        for byte in encoded:
            frames.extend(codec.feed(bytes([byte])))
        assert frames == [b"hello"]

    def test_empty_payload(self) -> None:
        codec = DelimiterCodec()
        encoded = codec.encode(b"")
        assert codec.feed(encoded) == [b""]

    def test_delimiter_in_payload_raises_at_encode_time(self) -> None:
        codec = DelimiterCodec()
        with pytest.raises(ValueError, match="delimiter"):
            codec.encode(b"line one\nline two")

    def test_buffer_survives_interleaved_calls(self) -> None:
        codec = DelimiterCodec()
        encoded_a = codec.encode(b"alpha")
        encoded_b = codec.encode(b"beta")
        assert codec.feed(encoded_a[:2]) == []
        assert codec.feed(encoded_a[2:] + encoded_b[:3]) == [b"alpha"]
        assert codec.feed(encoded_b[3:]) == [b"beta"]

    def test_custom_delimiter(self) -> None:
        codec = DelimiterCodec(delimiter=b"\r\n")
        encoded = codec.encode(b"hello") + codec.encode(b"world")
        assert codec.feed(encoded) == [b"hello", b"world"]


class TestLengthPrefixedCodec:
    def test_single_frame_round_trip(self) -> None:
        codec = LengthPrefixedCodec()
        encoded = codec.encode(b"hello")
        assert encoded == (5).to_bytes(4, "big") + b"hello"
        assert codec.feed(encoded) == [b"hello"]

    def test_multi_frame_in_one_chunk(self) -> None:
        codec = LengthPrefixedCodec()
        chunk = codec.encode(b"one") + codec.encode(b"two") + codec.encode(b"three")
        assert codec.feed(chunk) == [b"one", b"two", b"three"]

    def test_frame_split_across_many_chunks_byte_at_a_time(self) -> None:
        codec = LengthPrefixedCodec()
        encoded = codec.encode(b"hello world")
        frames: list[bytes] = []
        for byte in encoded:
            frames.extend(codec.feed(bytes([byte])))
        assert frames == [b"hello world"]

    def test_empty_payload(self) -> None:
        codec = LengthPrefixedCodec()
        encoded = codec.encode(b"")
        assert codec.feed(encoded) == [b""]

    def test_oversized_payload_raises_at_encode_time(self) -> None:
        codec = LengthPrefixedCodec(prefix_width=1)
        with pytest.raises(ValueError, match="exceeds"):
            codec.encode(b"x" * 256)

    def test_malformed_inbound_length_raises(self) -> None:
        codec = LengthPrefixedCodec(max_frame_size=10)
        corrupted = (999_999).to_bytes(4, "big")
        with pytest.raises(ValueError, match="malformed"):
            codec.feed(corrupted)

    def test_buffer_survives_interleaved_calls(self) -> None:
        codec = LengthPrefixedCodec()
        encoded_a = codec.encode(b"alpha")
        encoded_b = codec.encode(b"beta")
        assert codec.feed(encoded_a[:2]) == []
        assert codec.feed(encoded_a[2:] + encoded_b[:3]) == [b"alpha"]
        assert codec.feed(encoded_b[3:]) == [b"beta"]

    def test_little_endian(self) -> None:
        codec = LengthPrefixedCodec(byteorder="little")
        encoded = codec.encode(b"hi")
        assert encoded == (2).to_bytes(4, "little") + b"hi"
        assert codec.feed(encoded) == [b"hi"]

    def test_custom_prefix_width(self) -> None:
        codec = LengthPrefixedCodec(prefix_width=2)
        encoded = codec.encode(b"hi")
        assert encoded == (2).to_bytes(2, "big") + b"hi"
        assert codec.feed(encoded) == [b"hi"]


class TestWireBridgeRoundTrip:
    def test_delimiter_codec_round_trip_with_generated_model(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            GeoCoordinate,
            "wire_encode",
            lambda instance, **_kwargs: json.dumps(instance.to_dict()),
        )
        monkeypatch.setattr(
            GeoCoordinate,
            "wire_decode",
            lambda cls, wire_str: cls.from_dict(json.loads(wire_str)),
        )

        model = GeoCoordinate(latitude=37.7749, longitude=-122.4194)
        codec = DelimiterCodec()

        wire_bytes = model.to_wire().encode("utf-8")
        frames = codec.feed(codec.encode(wire_bytes))

        assert len(frames) == 1
        decoded_model = GeoCoordinate.from_wire(frames[0].decode("utf-8"))
        assert decoded_model == model

    def test_length_prefixed_codec_round_trip_with_generated_model(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            GeoCoordinate,
            "wire_encode",
            lambda instance, **_kwargs: json.dumps(instance.to_dict()),
        )
        monkeypatch.setattr(
            GeoCoordinate,
            "wire_decode",
            lambda cls, wire_str: cls.from_dict(json.loads(wire_str)),
        )

        model = GeoCoordinate(latitude=51.5074, longitude=-0.1278)
        codec = LengthPrefixedCodec()

        wire_bytes = model.to_wire().encode("utf-8")
        frames = codec.feed(codec.encode(wire_bytes))

        assert len(frames) == 1
        decoded_model = GeoCoordinate.from_wire(frames[0].decode("utf-8"))
        assert decoded_model == model
