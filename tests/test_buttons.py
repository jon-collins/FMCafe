from unittest.mock import MagicMock

from fmcafe.gpio.buttons import PRINT_COOLDOWN_SECONDS, Throttle, make_handler


def test_throttle_blocks_within_cooldown_and_allows_after():
    now = [0.0]
    throttle = Throttle(cooldown_seconds=10.0, clock=lambda: now[0])

    assert throttle.ready() is True
    assert throttle.ready() is False

    now[0] = 9.9
    assert throttle.ready() is False

    now[0] = 10.0
    assert throttle.ready() is True


def test_handler_does_not_print_when_throttle_blocks():
    printer = MagicMock()
    throttle = MagicMock()
    throttle.ready.return_value = False

    handler = make_handler("cafe", printer, throttle)
    handler()

    printer.print_receipt.assert_not_called()


def test_handler_prints_when_throttle_allows():
    printer = MagicMock()
    throttle = MagicMock()
    throttle.ready.return_value = True

    handler = make_handler("cafe", printer, throttle)
    handler()

    printer.print_receipt.assert_called_once()


def test_shared_throttle_blocks_a_different_button_too():
    now = [0.0]
    throttle = Throttle(cooldown_seconds=PRINT_COOLDOWN_SECONDS, clock=lambda: now[0])
    printer = MagicMock()

    make_handler("cafe", printer, throttle)()
    make_handler("ice_cream", printer, throttle)()

    printer.print_receipt.assert_called_once()
