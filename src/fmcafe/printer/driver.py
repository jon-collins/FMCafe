"""Real printer backend, using python-escpos over USB.

Default USB IDs are for our Epson TM-T20II, confirmed via Windows Device
Manager (VID_04B8&PID_0E15). Override them if your unit enumerates
differently -- check with `lsusb` on the Pi, or Device Manager on Windows.
"""

from datetime import datetime

from escpos.printer import Usb

from fmcafe.printer.malfunction import garbled_lines, is_malfunctioning
from fmcafe.printer.throttle import Throttle
from fmcafe.receipts.base import EMPTY_SECTION_LABEL, Receipt, format_price, load_full_width_logo

DEFAULT_VENDOR_ID = 0x04B8
DEFAULT_PRODUCT_ID = 0x0E15
PROFILE = "TM-T20II"


class UsbPrinter:
    def __init__(
        self,
        vendor_id: int = DEFAULT_VENDOR_ID,
        product_id: int = DEFAULT_PRODUCT_ID,
        profile: str = PROFILE,
    ):
        self._printer = Usb(vendor_id, product_id, profile=profile)

    def print_receipt(self, receipt: Receipt) -> None:
        if is_malfunctioning():
            self._print_malfunction()
            return

        p = self._printer
        if receipt.logo is not None:
            p.set(align="center")
            p.image(load_full_width_logo(receipt.logo))

        p.set(align="center", bold=True, width=2, height=2)
        p.text(f"{receipt.title}\n")
        p.set(align="center", bold=False, width=1, height=1)
        p.text(f"{receipt.timestamp:%Y-%m-%d %H:%M}\n")
        p.text("-" * 32 + "\n")

        for section, items in receipt.sections:
            p.set(align="left", bold=True)
            p.text(f"{section}\n")
            p.set(align="left", bold=False)
            if items:
                for item in items:
                    p.text(f"{item.name:<24}{format_price(item.price):>8}\n")
            else:
                p.text(f"{EMPTY_SECTION_LABEL}\n")
        p.text("-" * 32 + "\n")

        p.set(align="right", bold=True)
        p.text(f"TOTAL: {format_price(receipt.total)}\n")

        if receipt.footer:
            p.set(align="center", bold=False)
            p.text(f"\n{receipt.footer}\n")

        p.text("\n\n")
        p.cut()

    def print_ready(self) -> None:
        """Print a short slip on startup so it's obvious the printer/service came up OK."""
        if is_malfunctioning():
            self._print_malfunction()
            return

        p = self._printer
        p.set(align="center", bold=True, width=2, height=2)
        p.text("F&M Cafe\n")
        p.set(align="center", bold=False, width=1, height=1)
        p.text(f"{datetime.now():%Y-%m-%d %H:%M}\n")
        p.text("-" * 32 + "\n")
        p.set(align="center", bold=True)
        p.text("READY TO SERVE!\n")
        p.set(align="center", bold=False)
        p.text("Buttons and the order app\nare both online.\n")
        p.text("\n\n")
        p.cut()

    def _print_malfunction(self) -> None:
        p = self._printer
        p.set(align="left")
        for line in garbled_lines():
            p.text(f"{line}\n")
        p.text("\n\n")
        p.cut()


def announce_ready(printer: UsbPrinter, throttle: Throttle) -> None:
    """Print the boot-time ready slip if the printer is reachable; never raises.

    Lets the GPIO listener / kiosk web server start up even when the printer
    is unplugged, powered off, or otherwise unreachable.
    """
    try:
        printer.print_ready()
        throttle.ready()  # only reserve the cooldown window if it actually printed
    except Exception as exc:
        print(f"[fmcafe] printer not available at startup: {exc}")
