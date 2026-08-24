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
    MenuItem("Dragon Fire Scoop", 3.00, weight=SILLY_WEIGHT),
    MenuItem("Alien Slime Scoop", 3.00, weight=SILLY_WEIGHT),
    MenuItem("Unicorn Sparkle Scoop", 3.25, weight=SILLY_WEIGHT),
    MenuItem("Stinky Cheese Scoop", 2.75, weight=SILLY_WEIGHT),
    MenuItem("Baked Bean Scoop", 2.75, weight=SILLY_WEIGHT),
]

EXTRAS = [
    MenuItem("Sprinkles", 0.50),
    MenuItem("Waffle Cone", 1.00),
    MenuItem("Hot Fudge", 0.75),
    MenuItem("Whipped Cream", 0.50),
    MenuItem("Cherry", 0.25),
    MenuItem("Marshmallows", 0.50),
    MenuItem("Caramel Sauce", 0.75),
    MenuItem("Chocolate Chips", 0.50),
    MenuItem("Crushed Nuts", 0.60),
    MenuItem("Gummy Worms", 0.60, weight=SILLY_WEIGHT),
    MenuItem("Popping Candy", 0.75, weight=SILLY_WEIGHT),
    MenuItem("Pickle Bits", 0.50, weight=SILLY_WEIGHT),
    MenuItem("Glitter Dust", 0.80, weight=SILLY_WEIGHT),
]


def generate() -> Receipt:
    scoops = [
        LineItem(name=item.name, price=item.price, category="Ice Cream")
        for item in weighted_sample(ICE_CREAM, k=random.randint(1, 2))
    ]
    extras = [
        LineItem(name=item.name, price=item.price, category="Extras")
        for item in weighted_sample(EXTRAS, k=random.randint(0, 2))
    ]
    return Receipt(
        theme="ice_cream",
        title="F&M Ice Cream Shop",
        items=scoops + extras,
        footer="Enjoy your treat!",
        logo=logo_path("ice_cream"),
        section_order=["Ice Cream", "Extras"],
    )
