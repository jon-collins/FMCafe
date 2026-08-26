from io import BytesIO
from unittest.mock import patch

from markupsafe import escape
from PIL import Image

from fmcafe.kiosk import app as kiosk_app
from fmcafe.kiosk.app import create_app
from fmcafe.printer.mock import MockPrinter
from fmcafe.printer.throttle import Throttle
from fmcafe.receipts.order import THEME_MODULES


def make_test_png() -> BytesIO:
    buffer = BytesIO()
    Image.new("RGB", (200, 100), "red").save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def make_client(cooldown_seconds=0.0):
    app = create_app(MockPrinter(), Throttle(cooldown_seconds=cooldown_seconds))
    return app.test_client()


def test_index_lists_all_themes():
    client = make_client()
    response = client.get("/")
    assert response.status_code == 200
    for module in THEME_MODULES.values():
        assert str(escape(module.TITLE)).encode() in response.data


def test_index_shows_logo_image_when_theme_has_one():
    client = make_client()
    response = client.get("/")
    assert b'/assets/logo/cafe.png' in response.data


def test_index_falls_back_to_initials_tile_when_theme_has_no_logo():
    client = make_client()
    with patch.object(kiosk_app, "logo_path", return_value=None):
        response = client.get("/")
    assert b'/assets/logo/cafe.png' not in response.data
    assert b'class="initials"' in response.data


def test_theme_logo_route_404s_for_theme_with_no_logo_file():
    client = make_client()
    with patch.object(kiosk_app, "logo_path", return_value=None):
        response = client.get("/assets/logo/cafe.png")
    assert response.status_code == 404


def test_theme_logo_route_404s_for_unknown_theme():
    client = make_client()
    assert client.get("/assets/logo/not-a-theme.png").status_code == 404


def test_order_page_shows_theme_sections():
    client = make_client()
    response = client.get("/order/cafe")
    assert response.status_code == 200
    assert b"Food" in response.data
    assert b"Drinks" in response.data


def test_order_page_shows_item_icon_when_one_exists(tmp_path, monkeypatch):
    from fmcafe.kiosk import icons

    monkeypatch.setattr(icons, "IMAGE_DIR", tmp_path)
    (tmp_path / "muffin.png").write_bytes(b"fake png bytes")

    client = make_client()
    response = client.get("/order/cafe")
    assert b"/assets/icon/muffin.png" in response.data


def test_order_page_falls_back_to_initials_when_no_item_icon(tmp_path, monkeypatch):
    from fmcafe.kiosk import icons

    monkeypatch.setattr(icons, "IMAGE_DIR", tmp_path)

    client = make_client()
    response = client.get("/order/cafe")
    assert b"/assets/icon/" not in response.data


def test_item_icon_route_serves_existing_image(tmp_path, monkeypatch):
    from fmcafe.kiosk import icons

    monkeypatch.setattr(icons, "IMAGE_DIR", tmp_path)
    (tmp_path / "muffin.png").write_bytes(b"fake png bytes")

    client = make_client()
    response = client.get("/assets/icon/muffin.png")
    assert response.status_code == 200
    assert response.data == b"fake png bytes"


def test_item_icon_route_404s_for_missing_image(tmp_path, monkeypatch):
    from fmcafe.kiosk import icons

    monkeypatch.setattr(icons, "IMAGE_DIR", tmp_path)

    client = make_client()
    assert client.get("/assets/icon/muffin.png").status_code == 404


def test_order_page_unknown_theme_404s():
    client = make_client()
    assert client.get("/order/not-a-theme").status_code == 404


def test_print_endpoint_prints_and_returns_200():
    client = make_client()
    response = client.post("/api/print/cafe", json={"Muffin": 2, "Coffee": 1})
    assert response.status_code == 200
    assert response.get_json()["status"] == "printed"


def test_print_endpoint_rejects_empty_cart():
    client = make_client()
    response = client.post("/api/print/cafe", json={})
    assert response.status_code == 400


def test_print_endpoint_respects_shared_throttle():
    client = make_client(cooldown_seconds=10.0)
    first = client.post("/api/print/cafe", json={"Muffin": 1})
    second = client.post("/api/print/cafe", json={"Muffin": 1})
    assert first.status_code == 200
    assert second.status_code == 429
    assert second.get_json()["status"] == "cooling_down"


def test_print_endpoint_unknown_theme_404s():
    client = make_client()
    response = client.post("/api/print/not-a-theme", json={"x": 1})
    assert response.status_code == 404


def test_print_endpoint_reports_printer_offline_without_crashing():
    printer = MockPrinter()
    printer.print_receipt = lambda receipt: (_ for _ in ()).throw(RuntimeError("no backend"))
    app = create_app(printer, Throttle(cooldown_seconds=0))
    client = app.test_client()

    response = client.post("/api/print/cafe", json={"Muffin": 1})

    assert response.status_code == 503
    assert response.get_json()["status"] == "printer_offline"


def test_photo_page_renders():
    client = make_client()
    response = client.get("/photo")
    assert response.status_code == 200
    assert b"Print a Photo" in response.data


def test_print_photo_endpoint_prints_uploaded_image():
    client = make_client()
    response = client.post(
        "/api/print-photo",
        data={"photo": (make_test_png(), "test.png")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert response.get_json()["status"] == "printed"


def test_print_photo_endpoint_rejects_missing_file():
    client = make_client()
    response = client.post("/api/print-photo", data={}, content_type="multipart/form-data")
    assert response.status_code == 400
    assert response.get_json()["status"] == "empty"


def test_print_photo_endpoint_rejects_non_image_file():
    client = make_client()
    response = client.post(
        "/api/print-photo",
        data={"photo": (BytesIO(b"not an image"), "test.png")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert response.get_json()["status"] == "invalid_image"


def test_print_photo_endpoint_respects_shared_throttle():
    app = create_app(MockPrinter(), Throttle(cooldown_seconds=10.0))
    client = app.test_client()

    first = client.post(
        "/api/print-photo",
        data={"photo": (make_test_png(), "test.png")},
        content_type="multipart/form-data",
    )
    second = client.post(
        "/api/print-photo",
        data={"photo": (make_test_png(), "test.png")},
        content_type="multipart/form-data",
    )

    assert first.status_code == 200
    assert second.status_code == 429
    assert second.get_json()["status"] == "cooling_down"


def test_print_photo_endpoint_reports_printer_offline_without_crashing():
    printer = MockPrinter()
    printer.print_photo = lambda image: (_ for _ in ()).throw(RuntimeError("no backend"))
    app = create_app(printer, Throttle(cooldown_seconds=0))
    client = app.test_client()

    response = client.post(
        "/api/print-photo",
        data={"photo": (make_test_png(), "test.png")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 503
    assert response.get_json()["status"] == "printer_offline"
