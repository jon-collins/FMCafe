"""Cafe order receipt theme."""

import random

from .base import SILLY_WEIGHT, LineItem, MenuItem, Receipt, logo_path, weighted_sample

FOOD = [
    MenuItem("Muffin", 2.75),
    MenuItem("Croissant", 3.25),
    MenuItem("Bagel", 2.50),
    MenuItem("Toast", 1.75),
    MenuItem("Scone", 2.25),
    MenuItem("Cookie", 1.50),
    MenuItem("Pancakes", 4.00),
    MenuItem("Waffle", 4.25),
    MenuItem("Cinnamon Roll", 3.00),
    MenuItem("Bacon Roll", 3.75),
    MenuItem("Avocado Toast", 4.50),
    MenuItem("Fruit Salad", 3.00),
    MenuItem("Unicorn Pancakes", 6.50, weight=SILLY_WEIGHT),
]

DRINKS = [
    MenuItem("Coffee", 3.50),
    MenuItem("Hot Chocolate", 3.00),
    MenuItem("Tea", 2.50),
    MenuItem("Latte", 3.75),
    MenuItem("Cappuccino", 3.75),
    MenuItem("Orange Juice", 2.25),
    MenuItem("Milkshake", 4.00),
    MenuItem("Lemonade", 2.50),
    MenuItem("Iced Tea", 2.75),

]


TITLE = "F&M Cafe"
FOOTER = "Thanks for visiting!"
SECTIONS = {"Food": FOOD, "Drinks": DRINKS}
SECTION_ORDER = ["Food", "Drinks"]


def generate() -> Receipt:
    food = [
        LineItem(name=item.name, price=item.price, category="Food")
        for item in weighted_sample(FOOD, k=random.randint(1, 3))
    ]
    drinks = [
        LineItem(name=item.name, price=item.price, category="Drinks")
        for item in weighted_sample(DRINKS, k=random.randint(0, 2))
    ]
    return Receipt(
        theme="cafe",
        title=TITLE,
        items=food + drinks,
        footer=FOOTER,
        logo=logo_path("cafe"),
        section_order=SECTION_ORDER,
    )
