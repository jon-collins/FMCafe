"""Maps physical buttons to receipt themes and runs the main event loop.

Update BUTTON_PINS with the actual GPIO pin each button is wired to.
"""

import time
from threading import Lock

from gpiozero import Button

from fmcafe.printer.driver import UsbPrinter
from fmcafe.receipts import THEMES

BUTTON_PINS = {
    "cafe": 2,
    "ice_cream": 3,
    "restaurant": 4,
    "supermarket": 5,
}

# Minimum time between prints, shared across all buttons, so an excited kid
# mashing buttons can't overrun the printer.
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


def make_handler(theme: str, printer: UsbPrinter, throttle: Throttle):
    generate = THEMES[theme]

    def handler() -> None:
        if not throttle.ready():
            return
        receipt = generate()
        printer.print_receipt(receipt)

    return handler


def run() -> None:
    from signal import pause  # not available on Windows; only needed on the Pi

    printer = UsbPrinter()
    throttle = Throttle(PRINT_COOLDOWN_SECONDS)
    buttons = []
    for theme, pin in BUTTON_PINS.items():
        button = Button(pin)
        button.when_pressed = make_handler(theme, printer, throttle)
        buttons.append(button)

    pause()
