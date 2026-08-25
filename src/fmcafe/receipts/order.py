"""Build a Receipt from an explicit cart of item -> quantity.

Used by the kiosk order-builder UI, as opposed to each theme's random,
weighted ``generate()``.
"""

from . import cafe, ice_cream, restaurant, supermarket
from .base import LineItem, MenuItem, Receipt, logo_path

THEME_MODULES = {
    "cafe": cafe,
    "ice_cream": ice_cream,
    "restaurant": restaurant,
    "supermarket": supermarket,
}


def menu_for(theme: str) -> dict[str, list[MenuItem]]:
    return THEME_MODULES[theme].SECTIONS


def build_receipt_from_cart(theme: str, item_counts: dict[str, int]) -> Receipt:
    module = THEME_MODULES[theme]
    items: list[LineItem] = []
    for section, menu_items in module.SECTIONS.items():
        for menu_item in menu_items:
            count = item_counts.get(menu_item.name, 0)
            items.extend(
                LineItem(name=menu_item.name, price=menu_item.price, category=section)
                for _ in range(count)
            )

    return Receipt(
        theme=theme,
        title=module.TITLE,
        items=items,
        footer=module.FOOTER,
        logo=logo_path(theme),
        section_order=module.SECTION_ORDER,
    )
