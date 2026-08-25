from unittest.mock import MagicMock, patch

from fmcafe.printer import driver, mock
from fmcafe.printer.malfunction import GLITCH_CHARS, garbled_lines
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
