from fmcafe.kiosk.icons import icon_path, slugify


def test_slugify_lowercases_and_hyphenates():
    assert slugify("Espresso Cup") == "espresso-cup"
    assert slugify("Rubber Chicken (Family Size)") == "rubber-chicken-family-size"
    assert slugify("Giant's Toenail Toast") == "giant-s-toenail-toast"


def test_icon_path_returns_none_when_no_image_exists():
    assert icon_path("Definitely Not A Real Menu Item") is None


def test_icon_path_finds_an_existing_image(tmp_path, monkeypatch):
    from fmcafe.kiosk import icons

    monkeypatch.setattr(icons, "IMAGE_DIR", tmp_path)
    (tmp_path / "espresso-cup.png").write_bytes(b"fake png bytes")

    assert icons.icon_path("Espresso Cup") == tmp_path / "espresso-cup.png"
