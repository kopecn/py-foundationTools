"""Typed launch outcome for a synchronous CLI process."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from foundation_tools.cli_transaction.cliTransact import CLITransactResult

if TYPE_CHECKING:
    from foundation_tools.cli_transaction.cli_process import CLIProcess


@dataclass(frozen=True)
class CLIProcessStartResult:
    """Contain either a live process owner or a launch error, never both."""

    process: CLIProcess | None = None
    error: CLITransactResult | None = None

    def __post_init__(self) -> None:
        if (self.process is None) == (self.error is None):
            raise ValueError("Exactly one of process and error must be supplied")

    @property
    def success(self) -> bool:
        """Indicate successful launch, independently of the child's eventual exit."""
        return self.process is not None
