"""Occasionally makes the printer look like it's glitching out, for fun."""

import random

MALFUNCTION_PROBABILITY = 0.0

GLITCH_CHARS = "█▓▒░╪╫╬┼┴┬├┤═║╔╗╚╝#%&@!?$*^~<>{}[]|\\/¬¦§±"


def is_malfunctioning() -> bool:
    return random.random() < MALFUNCTION_PROBABILITY


def garbled_lines(num_lines: int = 14, width: int = 32) -> list[str]:
    return ["".join(random.choice(GLITCH_CHARS) for _ in range(width)) for _ in range(num_lines)]
