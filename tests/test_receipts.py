from fmcafe.receipts import THEMES


def test_all_themes_generate_receipts_with_positive_total():
    for generate in THEMES.values():
        receipt = generate()
        assert receipt.items
        assert receipt.total > 0
