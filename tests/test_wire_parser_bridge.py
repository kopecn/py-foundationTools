"""
Tests for the Wire-Parser Bridge (Action Plan 11).

Proves `DataModelHelper` is the canonical parser for `CLITransact.run_*_with_model`:
`from_wire` / `from_bytes` / a `from_dict`-based method are all directly usable as
`output_parser` against real generated models and real subprocess output — no
ad-hoc parser classes, no adapter shim.

Ergonomics conclusion (step 2 of the chunk): no adapter helper is needed.
`Model.from_wire` is already a classmethod of signature `(str) -> T`, which is
exactly `output_parser: Callable[[str], T]` — it can be passed as a bound method
with zero glue. `Model.from_bytes` takes `bytes`, so the one-line
`lambda s: Model.from_bytes(s.encode())` adapter is the minimal glue a caller
ever needs, and it is a wrapper the *caller* writes at the call site, not
something this library should abstract further.
"""

import pytest

from foundation_tools.cli_transaction.cliTransact import CLITransact
from foundationTypes.commonTypes.DiskUsage import DiskUsage
from foundationTypes.commonTypes.GeoCoordinate import GeoCoordinate


@pytest.fixture
def wired_geo_coordinate(monkeypatch: pytest.MonkeyPatch) -> None:
    """Configure GeoCoordinate's wire hooks as a JSON encoding — mirrors the
    chunk-08 wire-bridge test pattern (no wire_config.py wiring exists yet)."""
    import json

    monkeypatch.setattr(
        GeoCoordinate, "wire_encode", lambda instance, **_kwargs: json.dumps(instance.to_dict())
    )
    monkeypatch.setattr(
        GeoCoordinate, "wire_decode", lambda cls, wire_str: cls.from_dict(json.loads(wire_str))
    )


class TestFromWireRoundTrip:
    def test_run_sync_with_model_from_wire_round_trip_on_real_output(
        self, wired_geo_coordinate: None
    ) -> None:
        model = GeoCoordinate(latitude=37.7749, longitude=-122.4194)
        wire_str = model.to_wire()

        result = CLITransact.run_sync_with_model(["echo", wire_str], GeoCoordinate.from_wire)

        assert result.success is True
        assert result.model == model

    @pytest.mark.asyncio
    async def test_run_async_with_model_from_wire_round_trip_on_real_output(
        self, wired_geo_coordinate: None
    ) -> None:
        model = GeoCoordinate(latitude=51.5074, longitude=-0.1278)
        wire_str = model.to_wire()

        result = await CLITransact.run_async_with_model(
            ["echo", wire_str], GeoCoordinate.from_wire
        )

        assert result.success is True
        assert result.model == model


class TestFromBytesRoundTrip:
    def test_run_sync_with_model_from_bytes_parses_real_json_output(self) -> None:
        # No wire_encode/wire_decode configuration needed: to_bytes/from_bytes
        # compose on to_dict/from_dict, which every DataModelHelper subclass
        # already implements.
        model = GeoCoordinate(latitude=40.7128, longitude=-74.0060)
        json_output = model.to_bytes().decode("utf-8")

        result = CLITransact.run_sync_with_model(
            ["echo", json_output], lambda output: GeoCoordinate.from_bytes(output.encode("utf-8"))
        )

        assert result.success is True
        assert result.model == model


class TestUnconfiguredWireDecodeIsContained:
    def test_unconfigured_wire_decode_is_advisory_and_does_not_flip_success(self) -> None:
        # GeoCoordinate.wire_decode is None by default (never configured in this
        # repo — see data_model_helper.py) unless a test monkeypatches it, and
        # monkeypatch reverts automatically, so this test is independent of
        # execution order.
        result = CLITransact.run_sync_with_model(
            ["echo", "irrelevant output"], GeoCoordinate.from_wire
        )

        assert result.success is True
        assert result.model is None
        assert result.stderr is not None
        assert "Model parsing failed" in result.stderr
        assert "NotImplementedError" in result.stderr or "not configured" in result.stderr


class TestGeneratedModelWithDomainSpecificParser:
    def test_run_sync_with_model_with_disk_usage_from_df_output(self) -> None:
        # DiskUsage.from_df_output is itself a from_dict-adjacent, hand-written
        # CLI-output parser on a schema-generated DataModelHelper subclass — the
        # canonical shape for a real command whose output isn't wire-encoded JSON.
        result = CLITransact.run_sync_with_model(["df", "-h"], DiskUsage.from_df_output)

        assert result.success is True
        assert result.model is not None
        assert isinstance(result.model, DiskUsage)
        assert len(result.model.entries) > 0
