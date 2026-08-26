from unittest.mock import MagicMock, patch

from fmcafe.printer import driver, mock
from fmcafe.printer.malfunction import GLITCH_CHARS, garbled_lines
from fmcafe.printer.throttle import Throttle
from fmcafe.receipts import THEMES


def test_garbled_lines_uses_only_glitch_chars():
    for line in garbled_lines(num_lines=5, width=10):
        assert len(line) == 10
        assert all(ch in GLITCH_CHARS for ch in line)


def test_mock_renders_glitch_when_malfunctioning():
    receipt = THEMES["cafe"]()
    with patch.object(mock, "is_malfunctioning", return_value=True):
        html = mock.render_html(receipt)
    assert "glitch-line" in html
    assert receipt.title not in html


def test_usb_driver_prints_garbled_lines_when_malfunctioning():
    with patch.object(driver, "Usb", return_value=MagicMock()):
        printer = driver.UsbPrinter()
        with patch.object(driver, "is_malfunctioning", return_value=True):
            printer.print_receipt(THEMES["cafe"]())

    printer._printer.cut.assert_called_once()
    assert printer._printer.image.call_count == 0


def test_print_ready_prints_and_cuts():
    with patch.object(driver, "Usb", return_value=MagicMock()):
        printer = driver.UsbPrinter()
        with patch.object(driver, "is_malfunctioning", return_value=False):
            printer.print_ready()

    printer._printer.cut.assert_called_once()
    assert any("READY" in call.args[0] for call in printer._printer.text.call_args_list)


def test_print_ready_can_also_glitch():
    with patch.object(driver, "Usb", return_value=MagicMock()):
        printer = driver.UsbPrinter()
        with patch.object(driver, "is_malfunctioning", return_value=True):
            printer.print_ready()

    printer._printer.cut.assert_called_once()
    assert not any("READY" in call.args[0] for call in printer._printer.text.call_args_list)


def test_announce_ready_does_not_raise_when_printer_unreachable():
    printer = MagicMock()
    printer.print_ready.side_effect = RuntimeError("no backend")
    throttle = Throttle(cooldown_seconds=10.0)

    driver.announce_ready(printer, throttle)  # must not raise

    assert throttle.ready() is True  # cooldown window was not reserved


def test_announce_ready_reserves_the_cooldown_window_on_success():
    printer = MagicMock()
    throttle = Throttle(cooldown_seconds=10.0)

    driver.announce_ready(printer, throttle)

    printer.print_ready.assert_called_once()
    assert throttle.ready() is False  # already reserved by the ready print
