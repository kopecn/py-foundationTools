"""Shared command preparation and structured logging for process owners."""

import os
import re
from collections.abc import Mapping, Sequence
from logging import DEBUG, Logger

DEFAULT_SHELL: tuple[str, ...] = ("bash", "-c")


class ProcessExecution:
    """Prepare commands and mask log fields without executing a process."""

    def __init__(
        self,
        *,
        shell: Sequence[str] | None = None,
        cwd: str | os.PathLike[str] | None = None,
        env: Mapping[str, str] | None = None,
    ) -> None:
        self._shell = tuple(shell) if shell is not None else DEFAULT_SHELL
        self._cwd = cwd
        self._env = dict(env) if env is not None else None

    @property
    def cwd(self) -> str | os.PathLike[str] | None:
        """Return the child working directory."""
        return self._cwd

    def build_argv(self, command: str | list[str]) -> list[str]:
        """Wrap string commands in the explicit shell or copy direct argv."""
        return [*self._shell, command] if isinstance(command, str) else list(command)

    def environment(self) -> dict[str, str] | None:
        """Overlay copied caller values on the current parent environment."""
        return None if self._env is None else {**os.environ, **self._env}

    def redact(self, text: str) -> str:
        """Mask exact non-empty overlay values, selecting longest matches first."""
        values = sorted(
            {value for value in (self._env or {}).values() if value}, key=len, reverse=True
        )
        if not values:
            return text
        pattern = "|".join(re.escape(value) for value in values)
        return re.sub(pattern, "[REDACTED]", text)

    def log_issued(self, logger: Logger, argv: list[str]) -> None:
        """Log the command immediately before a launch attempt."""
        logger.info("CLI command issued", extra={"argv": [self.redact(part) for part in argv]})

    def log_output(
        self, logger: Logger, return_code: int, stdout: str | None, stderr: str | None
    ) -> None:
        """Log output at DEBUG without changing execution results."""
        if logger.isEnabledFor(DEBUG):
            logger.debug(
                "CLI command output",
                extra={
                    "return_code": return_code,
                    "stdout": self.redact(stdout) if stdout is not None else None,
                    "stderr": self.redact(stderr) if stderr is not None else None,
                },
            )
