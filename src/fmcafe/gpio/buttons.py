"""Maps physical buttons to receipt themes and runs the main event loop.

Update BUTTON_PINS with the actual GPIO pin each button is wired to.
"""

from fmcafe.printer.driver import UsbPrinter, announce_ready
from fmcafe.printer.throttle import PRINT_COOLDOWN_SECONDS, Throttle
from fmcafe.receipts import THEMES

BUTTON_PINS = {
    "cafe": 5,
    "ice_cream": 6,
    "restaurant": 13,
    "supermarket": 19,
}


def make_handler(theme: str, printer: UsbPrinter, throttle: Throttle):
    generate = THEMES[theme]

    def handler() -> None:
        if not throttle.ready():
            return
        receipt = generate()
        try:
            printer.print_receipt(receipt)
        except Exception as exc:
            print(f"[fmcafe] printer error: {exc}")

    return handler


def setup_buttons(printer: UsbPrinter, throttle: Throttle) -> list:
    """Wire up all configured buttons; returns an empty list if GPIO isn't available.

    Lets the kiosk web app / this listener still run for local debugging on a
    machine without real GPIO hardware (e.g. a dev PC), instead of crashing.
    """
    try:
        from gpiozero import Button

        buttons = []
        for theme, pin in BUTTON_PINS.items():
            button = Button(pin)
            button.when_pressed = make_handler(theme, printer, throttle)
            buttons.append(button)
        return buttons
    except Exception as exc:
        print(f"[fmcafe] GPIO not available, buttons disabled: {exc}")
        return []


def run() -> None:
    from signal import pause  # not available on Windows; only needed on the Pi

    printer = UsbPrinter()
    throttle = Throttle(PRINT_COOLDOWN_SECONDS)
    announce_ready(printer, throttle)

    setup_buttons(printer, throttle)

    pause()
