def main() -> None:
    """Entry point for running on the Pi: listens for button presses and prints."""
    from fmcafe.gpio.buttons import run

    run()
