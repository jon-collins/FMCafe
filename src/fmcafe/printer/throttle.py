"""Shared print-rate limiting.

Used by both the GPIO buttons and the kiosk web app so neither path can
overrun the single physical printer between the two.
"""

import time
from threading import Lock

# Minimum time between prints, shared across every way of triggering a print.
PRINT_COOLDOWN_SECONDS = 10.0


class Throttle:
    """Tracks whether enough time has passed since the last allowed call."""

    def __init__(self, cooldown_seconds: float, clock=time.monotonic):
        self._cooldown_seconds = cooldown_seconds
        self._clock = clock
        self._lock = Lock()
        self._last_allowed_at: float | None = None

    def ready(self) -> bool:
        """Returns True at most once per cooldown window, and marks that window used."""
        with self._lock:
            now = self._clock()
            if self._last_allowed_at is not None and now - self._last_allowed_at < self._cooldown_seconds:
                return False
            self._last_allowed_at = now
            return True
