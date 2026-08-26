"""Combined production entry point for the Pi.

Runs the GPIO buttons and the kiosk web app together, sharing one UsbPrinter
and one Throttle so neither path can overrun the physical printer.
"""

from fmcafe.gpio.buttons import setup_buttons
from fmcafe.kiosk.app import create_app
from fmcafe.printer.driver import UsbPrinter, announce_ready
from fmcafe.printer.throttle import PRINT_COOLDOWN_SECONDS, Throttle


def main() -> None:
    printer = UsbPrinter()
    throttle = Throttle(PRINT_COOLDOWN_SECONDS)
    announce_ready(printer, throttle)

    setup_buttons(printer, throttle)

    app = create_app(printer, throttle)
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
