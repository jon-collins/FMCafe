"""Diagnostic tool: prints which GPIO (BCM) pin was pressed/released.

Useful for figuring out which physical buttons on an add-on HAT are wired to
which GPIO pins when that isn't documented. Run it on the Pi, press each
button in turn, and note which pin number gets printed for each one.
"""

from datetime import datetime

# Commonly usable BCM GPIO pins on the 40-pin header. Excludes power/ground
# pins and GPIO0/1, which are reserved for HAT ID EEPROM detection.
CANDIDATE_PINS = [
    2, 3, 4, 17, 27, 22, 10, 9, 11, 5, 6, 13, 19, 26,
    14, 15, 18, 23, 24, 25, 8, 7, 12, 16, 20, 21,
]


def main() -> None:
    from signal import pause

    from gpiozero import Button

    buttons = []
    for pin in CANDIDATE_PINS:
        try:
            button = Button(pin, pull_up=True, bounce_time=0.05)
        except Exception as exc:
            print(f"GPIO{pin}: skipped ({exc})")
            continue

        button.when_pressed = lambda pin=pin: print(f"[{datetime.now():%H:%M:%S}] GPIO{pin} pressed")
        button.when_released = lambda pin=pin: print(f"[{datetime.now():%H:%M:%S}] GPIO{pin} released")
        buttons.append(button)

    watched = ", ".join(str(pin) for pin in CANDIDATE_PINS)
    print(f"Watching GPIO pins: {watched}")
    print("Press each button on the HAT and note which GPIO number prints. Ctrl+C to quit.")

    pause()


if __name__ == "__main__":
    main()
