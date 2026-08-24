"""Restaurant bill theme."""

import random

from .base import SILLY_WEIGHT, LineItem, MenuItem, Receipt, logo_path, weighted_sample

FOOD = [
    MenuItem("Spaghetti", 8.00),
    MenuItem("Pizza Slice", 4.50),
    MenuItem("Salad", 5.00),
    MenuItem("Soup", 4.00),
    MenuItem("Grilled Cheese", 5.50),
    MenuItem("Burger", 7.50),
    MenuItem("Fish and Chips", 8.50),
    MenuItem("Chicken Nuggets", 6.00),
    MenuItem("Mac and Cheese", 6.50),
    MenuItem("Fries", 3.00),
    MenuItem("Tacos", 6.50),
    MenuItem("Cheese Sandwich", 5.00),
    MenuItem("Dragon Tail Stew", 9.50, weight=SILLY_WEIGHT),
    MenuItem("Spaghetti and Meatball Tower", 10.00, weight=SILLY_WEIGHT),
    MenuItem("Mystery Meat Surprise", 7.00, weight=SILLY_WEIGHT),
    MenuItem("Sock Puppet Sandwich", 5.50, weight=SILLY_WEIGHT),
    MenuItem("Triple Cheese Volcano", 8.50, weight=SILLY_WEIGHT),
]

DRINKS = [
    MenuItem("Juice", 2.00),
    MenuItem("Water", 1.00),
    MenuItem("Soda", 2.25),
    MenuItem("Lemonade", 2.50),
    MenuItem("Milkshake", 4.00),
    MenuItem("Iced Tea", 2.75),
    MenuItem("Swamp Water Slushie", 3.00, weight=SILLY_WEIGHT),
    MenuItem("Purple People Punch", 3.25, weight=SILLY_WEIGHT),
    MenuItem("Fizzy Frog Soda", 2.75, weight=SILLY_WEIGHT),
]


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
        theme="restaurant",
        title="Les Deux Frères",
        items=food + drinks,
        footer="Please come again!",
        logo=logo_path("restaurant"),
        section_order=["Food", "Drinks"],
    )
