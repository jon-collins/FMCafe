"""Combined production entry point for the Pi.

Runs the GPIO buttons and the kiosk web app together, sharing one UsbPrinter
and one Throttle so neither path can overrun the physical printer.
"""

from fmcafe.gpio.buttons import BUTTON_PINS, make_handler
from fmcafe.kiosk.app import create_app
from fmcafe.printer.driver import UsbPrinter
from fmcafe.printer.throttle import PRINT_COOLDOWN_SECONDS, Throttle


def main() -> None:
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

    app = create_app(printer, throttle)
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
