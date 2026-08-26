"""Kiosk web app: build an order by tapping item tiles, then print the matching receipt.

``create_app`` takes a printer and a throttle so this can run against the
mock printer for local dev/testing, or against the real UsbPrinter (sharing
its throttle with the GPIO buttons) on the Pi.
"""

from flask import Flask, abort, jsonify, render_template, request, send_file

from fmcafe.printer.interface import Printer
from fmcafe.printer.mock import MockPrinter
from fmcafe.printer.throttle import Throttle
from fmcafe.receipts.base import format_price, logo_path
from fmcafe.receipts.order import THEME_MODULES, build_receipt_from_cart

from .icons import icon_path, initials, slugify, tile_color


def create_app(printer: Printer, throttle: Throttle) -> Flask:
    app = Flask(__name__)
    app.jinja_env.filters["tile_color"] = tile_color
    app.jinja_env.filters["initials"] = initials
    app.jinja_env.filters["format_price"] = format_price
    app.jinja_env.filters["slugify"] = slugify
    app.jinja_env.filters["has_icon"] = lambda name: icon_path(name) is not None

    @app.route("/")
    def index():
        themes = {
            name: {"title": module.TITLE, "has_logo": logo_path(name) is not None}
            for name, module in THEME_MODULES.items()
        }
        return render_template("index.html", themes=themes)

    @app.route("/assets/logo/<theme>.png")
    def theme_logo(theme: str):
        if theme not in THEME_MODULES:
            abort(404)
        path = logo_path(theme)
        if path is None:
            abort(404)
        return send_file(path, mimetype="image/png")

    @app.route("/assets/icon/<slug>.png")
    def item_icon(slug: str):
        path = icon_path(slug)  # slugify() is idempotent on an already-valid slug
        if path is None:
            abort(404)
        return send_file(path, mimetype="image/png")

    @app.route("/order/<theme>")
    def order(theme: str):
        module = THEME_MODULES.get(theme)
        if module is None:
            abort(404)
        return render_template(
            "order.html", theme=theme, title=module.TITLE, sections=module.SECTIONS
        )

    @app.route("/api/print/<theme>", methods=["POST"])
    def print_order(theme: str):
        if theme not in THEME_MODULES:
            abort(404)

        cart = request.get_json(silent=True) or {}
        item_counts = {name: int(qty) for name, qty in cart.items() if int(qty) > 0}
        if not item_counts:
            return jsonify(status="empty"), 400

        if not throttle.ready():
            return jsonify(status="cooling_down"), 429

        try:
            printer.print_receipt(build_receipt_from_cart(theme, item_counts))
        except Exception as exc:
            print(f"[kiosk] printer error: {exc}")
            return jsonify(status="printer_offline"), 503

        return jsonify(status="printed")

    return app


def main() -> None:
    """Local dev entry point: kiosk UI backed by the mock printer, no cooldown."""
    app = create_app(MockPrinter(), Throttle(cooldown_seconds=0))
    app.run(debug=True, port=5050)


if __name__ == "__main__":
    main()
