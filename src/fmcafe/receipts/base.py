"""Shared data model and helpers for building receipts."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime
from importlib import resources
from pathlib import Path

from PIL import Image

from fmcafe.printer.imaging import PRINTER_WIDTH_PX, resize_to_printer_width

SILLY_WEIGHT = 0.1
"""Relative pick weight for silly/funny menu items vs. a normal item's weight of 1.0."""

CURRENCY_SYMBOL = "£"

EMPTY_SECTION_LABEL = "---- None ----"


def format_price(amount: float) -> str:
    return f"{CURRENCY_SYMBOL}{amount:.2f}"


@dataclass(frozen=True)
class MenuItem:
    name: str
    price: float
    weight: float = 1.0


@dataclass
class LineItem:
    name: str
    price: float
    category: str


def weighted_sample(menu: list[MenuItem], k: int) -> list[MenuItem]:
    """Pick up to k items from menu without replacement, favoring higher-weight items.

    Uses the Efraimidis-Spirakis method: give each item a random key scaled by
    its weight, then take the top k keys.
    """
    k = min(k, len(menu))
    keyed = [(random.random() ** (1 / item.weight), item) for item in menu]
    keyed.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in keyed[:k]]


@dataclass
class Receipt:
    theme: str
    title: str
    items: list[LineItem]
    footer: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    logo: Path | None = None
    section_order: list[str] = field(default_factory=list)

    @property
    def total(self) -> float:
        return sum(item.price for item in self.items)

    @property
    def sections(self) -> list[tuple[str, list[LineItem]]]:
        """Items grouped by category, in section_order. Every section in section_order
        is included even if empty, so an empty section can still be shown on the receipt."""
        groups: dict[str, list[LineItem]] = {}
        for item in self.items:
            groups.setdefault(item.category, []).append(item)
        order = self.section_order or list(groups.keys())
        return [(category, groups.get(category, [])) for category in order]


def logo_path(theme: str) -> Path | None:
    """Look up the logos/<theme>.png shipped alongside the receipt themes."""
    path = resources.files("fmcafe.receipts") / "logos" / f"{theme}.png"
    return Path(path) if path.is_file() else None


def load_full_width_logo(logo: Path, width: int = PRINTER_WIDTH_PX) -> Image.Image:
    """Load a logo and resize it to span the full receipt width, keeping aspect ratio."""
    return resize_to_printer_width(Image.open(logo), width)
