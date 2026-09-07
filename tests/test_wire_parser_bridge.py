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

from typing import Any, ClassVar

import pytest

from foundation_tools.cli_transaction.cliTransact import CLITransact
from foundationTypes.commonTypes.disk_usage.DiskUsage import DiskUsage
from foundationTypes.commonTypes.GeoCoordinate import GeoCoordinate
from foundationTypes.data_model_helper import DataModelHelper


@pytest.fixture
def wired_geo_coordinate(monkeypatch: pytest.MonkeyPatch) -> None:
    """Configure GeoCoordinate's wire hooks as a JSON encoding for this test only.

    Unlike DiskUsage (see disk_usage/wire_config.py), GeoCoordinate has no
    permanent wire_config.py in this repo, so its hooks are monkeypatched here.
    """
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

        result = await CLITransact.run_async_with_model(["echo", wire_str], GeoCoordinate.from_wire)

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
    def test_run_sync_with_model_with_disk_usage_from_wire(self) -> None:
        # DiskUsage.wire_decode is a hand-written, domain-specific CLI-output
        # parser assigned externally in disk_usage/wire_config.py — the
        # generated DiskUsage.py itself carries none of this, only from_dict/
        # to_dict — so DiskUsage.from_wire is the canonical parser for a real
        # command whose output isn't wire-encoded JSON.
        result = CLITransact.run_sync_with_model(["df", "-h"], DiskUsage.from_wire)

        assert result.success is True
        assert result.model is not None
        assert isinstance(result.model, DiskUsage)
        assert len(result.model.entries) > 0


class TestDiskUsageWireConfigRoundTrip:
    """DiskUsage.wire_encode/wire_decode are permanently configured by
    disk_usage/wire_config.py (unlike GeoCoordinate, which is monkeypatched
    per-test above) — so to_wire()/from_wire() round-trip without any test
    setup."""

    def test_to_wire_from_wire_round_trip(self) -> None:
        model = DiskUsage.from_dict(
            {
                "entries": [
                    {
                        "filesystem": "/dev/disk3s5",
                        "size": "926Gi",
                        "used": "628Gi",
                        "available": "280Gi",
                        "use_percent": "70%",
                        "mounted_on": "/System/Volumes/Data",
                    },
                    {
                        "filesystem": "map auto_home",
                        "size": "0Bi",
                        "used": "0Bi",
                        "available": "0Bi",
                        "use_percent": "100%",
                        "mounted_on": "/System/Volumes/Data/home",
                    },
                ]
            }
        )

        wire_str = model.to_wire()
        reconstructed = DiskUsage.from_wire(wire_str)

        assert reconstructed == model


class TestModelClassAloneInvocation:
    """DiskUsage.wire_invoke exposes the request that produces its own wire
    input, so the model class alone is enough — no separate command or
    output_parser argument needed. Explicit (command, output_parser) overrides
    still work unchanged (parameterized invocations stay at the call site)."""

    def test_run_sync_with_model_with_disk_usage_class_alone(self) -> None:
        result = CLITransact.run_sync_with_model(DiskUsage)

        assert result.success is True
        assert result.model is not None
        assert isinstance(result.model, DiskUsage)
        assert len(result.model.entries) > 0

    @pytest.mark.asyncio
    async def test_run_async_with_model_with_disk_usage_class_alone(self) -> None:
        result = await CLITransact.run_async_with_model(DiskUsage)

        assert result.success is True
        assert result.model is not None
        assert isinstance(result.model, DiskUsage)
        assert len(result.model.entries) > 0

    def test_run_sync_with_model_class_alone_with_explicit_parser_override(self) -> None:
        # An explicit output_parser still wins over the model's own from_wire.
        calls: list[str] = []

        def tracking_parser(stdout: str) -> DiskUsage:
            calls.append(stdout)
            return DiskUsage.from_wire(stdout)

        result = CLITransact.run_sync_with_model(DiskUsage, tracking_parser)

        assert result.success is True
        assert len(calls) == 1


class _NoInvokeModel(DataModelHelper):
    """A DataModelHelper subclass that never configures wire_invoke."""

    @classmethod
    def from_dict(cls, obj: Any) -> "_NoInvokeModel":
        return cls()

    def to_dict(self) -> dict[str, Any]:
        return {}


class _TypeArmInvokeModel(DataModelHelper):
    """wire_invoke set to a type[DataModelHelper] — meaningful for other
    transports (e.g. a request/response pair over a socket transaction), but
    not for the CLI transport."""

    wire_invoke: ClassVar["str | list[str] | type[DataModelHelper] | None"] = GeoCoordinate

    @classmethod
    def from_dict(cls, obj: Any) -> "_TypeArmInvokeModel":
        return cls()

    def to_dict(self) -> dict[str, Any]:
        return {}


class TestUnsupportedModelInvocationArms:
    def test_model_class_alone_without_wire_invoke_raises(self) -> None:
        with pytest.raises(ValueError, match="wire_invoke"):
            CLITransact.run_sync_with_model(_NoInvokeModel)

    def test_model_class_alone_with_type_arm_wire_invoke_raises(self) -> None:
        with pytest.raises(ValueError, match="wire_invoke"):
            CLITransact.run_sync_with_model(_TypeArmInvokeModel)
