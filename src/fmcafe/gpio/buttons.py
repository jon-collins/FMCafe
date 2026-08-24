"""Maps physical buttons to receipt themes and runs the main event loop.

Update BUTTON_PINS with the actual GPIO pin each button is wired to.
"""

from signal import pause

from gpiozero import Button

from fmcafe.printer.driver import UsbPrinter
from fmcafe.receipts import THEMES

BUTTON_PINS = {
    "cafe": 2,
    "ice_cream": 3,
    "restaurant": 4,
}


def make_handler(theme: str, printer: UsbPrinter):
    generate = THEMES[theme]

    def handler() -> None:
        receipt = generate()
        printer.print_receipt(receipt)

    return handler


def run() -> None:
    printer = UsbPrinter()
    buttons = []
    for theme, pin in BUTTON_PINS.items():
        button = Button(pin)
        button.when_pressed = make_handler(theme, printer)
        buttons.append(button)

    pause()
