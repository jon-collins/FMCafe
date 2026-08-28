"""Ice cream shop ticket theme."""

import random

from .base import SILLY_WEIGHT, LineItem, MenuItem, Receipt, logo_path, weighted_sample

ICE_CREAM = [
    MenuItem("Vanilla Scoop", 2.50),
    MenuItem("Chocolate Scoop", 2.50),
    MenuItem("Strawberry Scoop", 2.50),
    MenuItem("Mint Choc Chip Scoop", 2.75),
    MenuItem("Cookie Dough Scoop", 2.75),
    MenuItem("Mango Scoop", 2.75),
    MenuItem("Bubblegum Scoop", 2.75),
    MenuItem("Salted Caramel Scoop", 2.75),

]

EXTRAS = [
    MenuItem("Sprinkles", 0.50),
    MenuItem("Waffle Cone", 1.00),
    MenuItem("Whipped Cream", 0.50),
    MenuItem("Cherry", 0.25),
    MenuItem("Marshmallows", 0.50),
    MenuItem("Caramel Sauce", 0.75),
    MenuItem("Chocolate Chips", 0.50),
    MenuItem("Crushed Nuts", 0.60),
]


TITLE = "F&M Ice Cream Shop"
FOOTER = "Enjoy your treat!"
SECTIONS = {"Ice Cream": ICE_CREAM, "Extras": EXTRAS}
SECTION_ORDER = ["Ice Cream", "Extras"]


def generate() -> Receipt:
    scoops = [
        LineItem(name=item.name, price=item.price, category="Ice Cream")
        for item in weighted_sample(ICE_CREAM, k=random.randint(1, 3))
    ]
    extras = [
        LineItem(name=item.name, price=item.price, category="Extras")
        for item in weighted_sample(EXTRAS, k=random.randint(0, 5))
    ]
    return Receipt(
        theme="ice_cream",
        title=TITLE,
        items=scoops + extras,
        footer=FOOTER,
        logo=logo_path("ice_cream"),
        section_order=SECTION_ORDER,
    )
