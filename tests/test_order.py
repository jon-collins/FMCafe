from fmcafe.receipts.order import THEME_MODULES, build_receipt_from_cart, menu_for


def test_build_receipt_from_cart_includes_only_requested_items_with_quantities():
    menu = menu_for("cafe")
    first_food = menu["Food"][0]
    first_drink = menu["Drinks"][0]

    receipt = build_receipt_from_cart(
        "cafe", {first_food.name: 2, first_drink.name: 1}
    )

    names = [item.name for item in receipt.items]
    assert names.count(first_food.name) == 2
    assert names.count(first_drink.name) == 1
    assert len(receipt.items) == 3
    assert receipt.total == first_food.price * 2 + first_drink.price


def test_build_receipt_from_cart_ignores_unknown_item_names():
    receipt = build_receipt_from_cart("cafe", {"Not On The Menu": 5})
    assert receipt.items == []
    assert receipt.total == 0


def test_build_receipt_from_cart_preserves_section_order_even_when_empty():
    receipt = build_receipt_from_cart("cafe", {})
    sections = [name for name, _ in receipt.sections]
    assert sections == ["Food", "Drinks"]


def test_every_theme_module_is_buildable_from_an_empty_cart():
    for theme in THEME_MODULES:
        receipt = build_receipt_from_cart(theme, {})
        assert receipt.theme == theme
        assert receipt.items == []
