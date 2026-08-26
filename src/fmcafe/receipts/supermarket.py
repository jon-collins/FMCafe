"""Supermarket shopping receipt theme."""

import random

from .base import SILLY_WEIGHT, LineItem, MenuItem, Receipt, logo_path, weighted_sample

GROCERIES = [
    MenuItem("Bread", 1.20),
    MenuItem("Milk", 1.10),
    MenuItem("Eggs", 2.00),
    MenuItem("Cereal", 2.75),
    MenuItem("Apples", 1.80),
    MenuItem("Bananas", 1.00),
    MenuItem("Pasta", 1.50),
    MenuItem("Rice", 2.20),
    MenuItem("Cheese", 3.00),
    MenuItem("Chicken", 5.50),
    MenuItem("Tomatoes", 1.60),
    MenuItem("Orange Juice Carton", 2.30),
    MenuItem("Biscuits", 1.75),
    MenuItem("Crisps", 1.25),
    MenuItem("Baked Beans", 0.75),
    MenuItem("Ice Cream", 2.75),
    MenuItem("Custard", 2.00),
    MenuItem("Suspiciously Cheap Sushi", 1.00, weight=SILLY_WEIGHT),
]

HOUSEHOLD = [
    MenuItem("Toilet Paper", 3.00),
    MenuItem("Soap", 1.50),
    MenuItem("Sponges", 1.20),
    MenuItem("Laundry Detergent", 4.50),
    MenuItem("Washing Up Liquid", 2.50),
    MenuItem("Light Bulbs", 2.80),
    MenuItem("Bin Bags", 2.00),
    MenuItem("Kitchen Roll", 2.20),
    MenuItem("Nappies", 10.00),
    MenuItem("Rubber Chicken (Family Size)", 4.00, weight=SILLY_WEIGHT),
    MenuItem("Extra Squeaky Bath Duck", 1.90, weight=SILLY_WEIGHT),
]


TITLE = "F&M Bargains"
FOOTER = "Have a great day!"
SECTIONS = {"Groceries": GROCERIES, "Household": HOUSEHOLD}
SECTION_ORDER = ["Groceries", "Household"]


def generate() -> Receipt:
    groceries = [
        LineItem(name=item.name, price=item.price, category="Groceries")
        for item in weighted_sample(GROCERIES, k=random.randint(2, 5))
    ]
    household = [
        LineItem(name=item.name, price=item.price, category="Household")
        for item in weighted_sample(HOUSEHOLD, k=random.randint(1, 5))
    ]
    return Receipt(
        theme="supermarket",
        title=TITLE,
        items=groceries + household,
        footer=FOOTER,
        logo=logo_path("supermarket"),
        section_order=SECTION_ORDER,
    )
