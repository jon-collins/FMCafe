"""Maps physical buttons to receipt themes and runs the main event loop.

Update BUTTON_PINS with the actual GPIO pin each button is wired to.
"""

from fmcafe.printer.driver import UsbPrinter
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
        printer.print_receipt(receipt)

    return handler


def run() -> None:
    from signal import pause  # not available on Windows; only needed on the Pi

    from gpiozero import Button

    printer = UsbPrinter()
    throttle = Throttle(PRINT_COOLDOWN_SECONDS)
    printer.print_ready()
    throttle.ready()  # counts the ready print itself against the cooldown

    buttons = []
    for theme, pin in BUTTON_PINS.items():
        button = Button(pin)
        button.when_pressed = make_handler(theme, printer, throttle)
        buttons.append(button)

    pause()
