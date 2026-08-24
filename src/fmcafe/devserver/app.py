"""Local dev preview server: renders receipt themes as HTML in the browser."""

from flask import Flask, abort, render_template

from fmcafe.printer.mock import render_html
from fmcafe.receipts import THEMES

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", themes=THEMES.keys(), receipt_html=None)


@app.route("/preview/<theme>")
def preview(theme: str):
    generate = THEMES.get(theme)
    if generate is None:
        abort(404)

    receipt = generate()
    return render_template(
        "index.html", themes=THEMES.keys(), receipt_html=render_html(receipt)
    )


def main() -> None:
    app.run(debug=True)


if __name__ == "__main__":
    main()
