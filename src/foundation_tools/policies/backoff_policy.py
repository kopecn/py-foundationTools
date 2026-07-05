"""
BackoffPolicy — pure retry-delay computation.

Computes the delay before the next retry attempt. It never sleeps and never knows
about retries, transient codes, or execution — it is a pure function of attempt
number, wrapped in an immutable config object so it can be composed into
``RetryPolicy``.
"""

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class BackoffPolicy:
    """Exponential backoff with an optional full-jitter cap.

    Attributes:
        base_delay: Delay (seconds) for attempt 0, doubling each subsequent attempt.
        max_delay: Upper bound (seconds) on the computed delay, applied before jitter.
        jitter: When True, the returned delay is drawn uniformly from
            ``[0, capped_delay)`` instead of returning ``capped_delay`` directly —
            spreads out synchronized retry storms across callers.
    """

    base_delay: float
    max_delay: float
    jitter: bool = False

    def compute_delay(self, attempt: int) -> float:
        """Compute the delay before retrying after a failed ``attempt`` (0-indexed).

        ``delay = min(max_delay, base_delay * 2.0 ** attempt)``, optionally replaced by
        ``random.uniform(0, delay)`` when ``jitter`` is set.
        """
        delay = min(self.max_delay, self.base_delay * (2.0**attempt))
        if self.jitter:
            return float(random.uniform(0, delay))  # noqa: S311 - non-cryptographic jitter
        return delay
