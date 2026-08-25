"""Receipt themes.

Each theme module exposes a ``generate() -> Receipt`` function.
"""

from . import cafe, ice_cream, restaurant, supermarket
from .base import LineItem, Receipt

THEMES = {
    "cafe": cafe.generate,
    "ice_cream": ice_cream.generate,
    "restaurant": restaurant.generate,
    "supermarket": supermarket.generate,
}

__all__ = ["LineItem", "Receipt", "THEMES"]
