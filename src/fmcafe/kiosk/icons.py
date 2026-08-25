"""Icons for menu items.

Looks for real artwork in kiosk/imgs/<slug>.png (lower-case, hyphenated item
name), falling back to a generated colored tile with initials when no image
has been made for that item yet.
"""

import colorsys
import re
from hashlib import md5
from pathlib import Path

IMAGE_DIR = Path(__file__).parent / "imgs"


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def icon_path(name: str) -> Path | None:
    """Look up a real icon image for an item, if one has been generated."""
    path = IMAGE_DIR / f"{slugify(name)}.png"
    return path if path.is_file() else None


def tile_color(name: str) -> str:
    digest = md5(name.encode()).digest()
    hue = digest[0] / 255
    r, g, b = colorsys.hsv_to_rgb(hue, 0.55, 0.85)
    return f"rgb({int(r * 255)}, {int(g * 255)}, {int(b * 255)})"


def initials(name: str) -> str:
    words = [word for word in name.replace("'", "").replace("(", "").split() if word]
    letters = "".join(word[0] for word in words[:2])
    return letters.upper() or "?"
