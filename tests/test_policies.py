"""
Tests for the execution-policy layer (Action Plan 03): BackoffPolicy + RetryPolicy.
"""

import subprocess
import sys
from typing import Any
from unittest.mock import MagicMock

import pytest

from foundation_tools.cli_transaction import CLITransactResult, CLITransactResultModel
from foundation_tools.policies import BackoffPolicy, RetryPolicy


class TestBackoffPolicy:
    def test_exponential_growth(self) -> None:
        policy = BackoffPolicy(base_delay=1.0, max_delay=100.0)
        assert policy.compute_delay(0) == 1.0
        assert policy.compute_delay(1) == 2.0
        assert policy.compute_delay(2) == 4.0
        assert policy.compute_delay(3) == 8.0

    def test_cap_applied(self) -> None:
        policy = BackoffPolicy(base_delay=1.0, max_delay=5.0)
        assert policy.compute_delay(10) == 5.0

    def test_no_sleeping_pure_computation(self) -> None:
        policy = BackoffPolicy(base_delay=0.001, max_delay=0.001)
        # Calling repeatedly must be instant — no time.sleep inside.
        for attempt in range(5):
            assert policy.compute_delay(attempt) == 0.001

    def test_jitter_within_bounds(self) -> None:
        policy = BackoffPolicy(base_delay=1.0, max_delay=100.0, jitter=True)
        for attempt in range(5):
            capped = min(100.0, 1.0 * 2**attempt)
            for _ in range(20):
                delay = policy.compute_delay(attempt)
                assert 0.0 <= delay <= capped

    def test_no_jitter_deterministic(self) -> None:
        policy = BackoffPolicy(base_delay=2.0, max_delay=100.0, jitter=False)
        assert policy.compute_delay(1) == policy.compute_delay(1) == 4.0


def _result(return_code: int, success: bool) -> CLITransactResult:
    return CLITransactResult(return_code=return_code, success=success)


class TestRetryPolicySync:
    def test_stops_on_first_success(self) -> None:
        sleeper = MagicMock()
        policy = RetryPolicy(
            max_attempts=5,
            transient_return_codes=frozenset({-1}),
            backoff=BackoffPolicy(base_delay=0.0, max_delay=0.0),
            sync_sleeper=sleeper,
        )
        calls = {"n": 0}

        def execute() -> CLITransactResult:
            calls["n"] += 1
            return _result(0, True)

        result = policy.run_sync(execute)
        assert result.success is True
        assert calls["n"] == 1
        sleeper.assert_not_called()

    def test_retries_only_transient_codes(self) -> None:
        sleeper = MagicMock()
        policy = RetryPolicy(
            max_attempts=5,
            transient_return_codes=frozenset({-1}),
            backoff=BackoffPolicy(base_delay=0.0, max_delay=0.0),
            sync_sleeper=sleeper,
        )
        calls = {"n": 0}

        def execute() -> CLITransactResult:
            calls["n"] += 1
            return _result(2, False)  # non-transient failure

        result = policy.run_sync(execute)
        assert result.return_code == 2
        assert result.success is False
        assert calls["n"] == 1  # no retry on non-transient failure
        sleeper.assert_not_called()

    def test_exhaustion_returns_last_result_never_raises(self) -> None:
        sleeper = MagicMock()
        policy = RetryPolicy(
            max_attempts=3,
            transient_return_codes=frozenset({-1}),
            backoff=BackoffPolicy(base_delay=0.0, max_delay=0.0),
            sync_sleeper=sleeper,
        )
        calls = {"n": 0}

        def execute() -> CLITransactResult:
            calls["n"] += 1
            return _result(-1, False)  # always transient failure

        result = policy.run_sync(execute)
        assert result.return_code == -1
        assert result.success is False
        assert calls["n"] == 3  # exhausted all attempts
        assert sleeper.call_count == 2  # slept between attempts, not after the last

    def test_succeeds_on_a_later_attempt(self) -> None:
        sleeper = MagicMock()
        policy = RetryPolicy(
            max_attempts=5,
            transient_return_codes=frozenset({-1}),
            backoff=BackoffPolicy(base_delay=1.0, max_delay=10.0),
            sync_sleeper=sleeper,
        )
        calls = {"n": 0}

        def execute() -> CLITransactResult:
            calls["n"] += 1
            if calls["n"] < 3:
                return _result(-1, False)
            return _result(0, True)

        result = policy.run_sync(execute)
        assert result.success is True
        assert calls["n"] == 3
        assert sleeper.call_count == 2
        sleeper.assert_any_call(1.0)  # attempt 0 delay
        sleeper.assert_any_call(2.0)  # attempt 1 delay

    def test_zero_sleep_injection_runs_instantly(self) -> None:
        """Default real time.sleep is never invoked when a no-op sleeper is injected."""

        def noop_sleeper(_delay: float) -> None:
            return None

        policy = RetryPolicy(
            max_attempts=50,
            transient_return_codes=frozenset({-1}),
            backoff=BackoffPolicy(base_delay=10.0, max_delay=10.0),
            sync_sleeper=noop_sleeper,
        )

        def execute() -> CLITransactResult:
            return _result(-1, False)

        result = policy.run_sync(execute)  # would take 490s with real sleeping
        assert result.success is False

    def test_with_model_failed_parse_is_terminal_success_never_retried(self) -> None:
        """rc=0 with a failed parse is still success=True — terminal, not retried."""
        sleeper = MagicMock()
        policy = RetryPolicy(
            max_attempts=5,
            transient_return_codes=frozenset({-1}),
            backoff=BackoffPolicy(base_delay=0.0, max_delay=0.0),
            sync_sleeper=sleeper,
        )
        calls = {"n": 0}

        def execute() -> CLITransactResultModel[Any]:
            calls["n"] += 1
            return CLITransactResultModel(return_code=0, stdout="x", success=True, model=None)

        result = policy.run_sync(execute)
        assert result.success is True
        assert result.model is None
        assert calls["n"] == 1
        sleeper.assert_not_called()


class TestRetryPolicyAsync:
    @pytest.mark.asyncio
    async def test_stops_on_first_success(self) -> None:
        sleeper_calls: list[float] = []

        async def sleeper(delay: float) -> None:
            sleeper_calls.append(delay)

        policy = RetryPolicy(
            max_attempts=5,
            transient_return_codes=frozenset({-1}),
            backoff=BackoffPolicy(base_delay=0.0, max_delay=0.0),
            async_sleeper=sleeper,
        )
        calls = {"n": 0}

        async def execute() -> CLITransactResult:
            calls["n"] += 1
            return _result(0, True)

        result = await policy.run_async(execute)
        assert result.success is True
        assert calls["n"] == 1
        assert sleeper_calls == []

    @pytest.mark.asyncio
    async def test_retries_only_transient_codes(self) -> None:
        async def sleeper(_delay: float) -> None:
            return None

        policy = RetryPolicy(
            max_attempts=5,
            transient_return_codes=frozenset({-1}),
            backoff=BackoffPolicy(base_delay=0.0, max_delay=0.0),
            async_sleeper=sleeper,
        )
        calls = {"n": 0}

        async def execute() -> CLITransactResult:
            calls["n"] += 1
            return _result(2, False)

        result = await policy.run_async(execute)
        assert result.return_code == 2
        assert calls["n"] == 1

    @pytest.mark.asyncio
    async def test_exhaustion_returns_last_result_never_raises(self) -> None:
        sleep_count = {"n": 0}

        async def sleeper(_delay: float) -> None:
            sleep_count["n"] += 1

        policy = RetryPolicy(
            max_attempts=3,
            transient_return_codes=frozenset({-1}),
            backoff=BackoffPolicy(base_delay=0.0, max_delay=0.0),
            async_sleeper=sleeper,
        )
        calls = {"n": 0}

        async def execute() -> CLITransactResult:
            calls["n"] += 1
            return _result(-1, False)

        result = await policy.run_async(execute)
        assert result.return_code == -1
        assert calls["n"] == 3
        assert sleep_count["n"] == 2

    @pytest.mark.asyncio
    async def test_sync_and_async_parity(self) -> None:
        """Sync and async policies applied to equivalent callables behave identically."""

        def sync_sleeper(_delay: float) -> None:
            return None

        async def async_sleeper(_delay: float) -> None:
            return None

        sync_policy = RetryPolicy(
            max_attempts=4,
            transient_return_codes=frozenset({-1}),
            backoff=BackoffPolicy(base_delay=0.0, max_delay=0.0),
            sync_sleeper=sync_sleeper,
        )
        async_policy = RetryPolicy(
            max_attempts=4,
            transient_return_codes=frozenset({-1}),
            backoff=BackoffPolicy(base_delay=0.0, max_delay=0.0),
            async_sleeper=async_sleeper,
        )

        sync_calls = {"n": 0}

        def sync_execute() -> CLITransactResult:
            sync_calls["n"] += 1
            return _result(-1, False) if sync_calls["n"] < 3 else _result(0, True)

        async_calls = {"n": 0}

        async def async_execute() -> CLITransactResult:
            async_calls["n"] += 1
            return _result(-1, False) if async_calls["n"] < 3 else _result(0, True)

        sync_result = sync_policy.run_sync(sync_execute)
        async_result = await async_policy.run_async(async_execute)

        assert sync_result.success == async_result.success
        assert sync_result.return_code == async_result.return_code
        assert sync_calls["n"] == async_calls["n"] == 3

    @pytest.mark.asyncio
    async def test_with_model_failed_parse_is_terminal_success_never_retried(self) -> None:
        async def sleeper(_delay: float) -> None:
            return None

        policy = RetryPolicy(
            max_attempts=5,
            transient_return_codes=frozenset({-1}),
            backoff=BackoffPolicy(base_delay=0.0, max_delay=0.0),
            async_sleeper=sleeper,
        )
        calls = {"n": 0}

        async def execute() -> CLITransactResultModel[Any]:
            calls["n"] += 1
            return CLITransactResultModel(return_code=0, stdout="x", success=True, model=None)

        result = await policy.run_async(execute)
        assert result.success is True
        assert result.model is None
        assert calls["n"] == 1


class TestFreshInterpreterImportHealth:
    """Regression for the Chunk 14 policy-layer import cycle.

    Each import MUST succeed as the *first* import in a brand-new interpreter, so
    an in-suite import order (e.g. importing ``foundation_tools.cli_transaction``
    before ``foundation_tools.policies`` elsewhere in the suite) can never mask a
    circular-import defect. Sweeps every internal-but-importable subpackage per
    the transport_transaction_architecture.md public-surface rule.
    """

    @pytest.mark.parametrize(
        "import_statement",
        [
            "from foundation_tools.policies import RetryPolicy",
            "from foundation_tools.builders import build_rsync_command",
            "import foundation_tools.socket_transaction",
        ],
    )
    def test_first_import_succeeds_in_fresh_interpreter(self, import_statement: str) -> None:
        result = subprocess.run(
            [sys.executable, "-c", import_statement],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert (
            result.returncode == 0
        ), f"{import_statement!r} failed as first import in a fresh interpreter:\n{result.stderr}"


class TestNoForbiddenImports:
    def test_policies_do_not_import_subprocess_or_builders(self) -> None:
        import inspect

        import foundation_tools.policies.backoff_policy as backoff_module
        import foundation_tools.policies.retry_policy as retry_module

        for module in (backoff_module, retry_module):
            source = inspect.getsource(module)
            assert "import subprocess" not in source
            assert "asyncio.subprocess" not in source
            assert "foundation_tools.builders" not in source
