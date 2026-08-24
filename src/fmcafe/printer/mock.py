"""Mock printer backend: renders a receipt as an HTML fragment for local preview."""

import base64
from html import escape
from io import BytesIO

from fmcafe.receipts.base import EMPTY_SECTION_LABEL, Receipt, format_price, load_full_width_logo


def _logo_img_tag(receipt: Receipt) -> str:
    if receipt.logo is None:
        return ""
    buffer = BytesIO()
    load_full_width_logo(receipt.logo).save(buffer, format="PNG")
    data = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f'<img class="logo" src="data:image/png;base64,{data}" alt="">'


def _section_html(section: str, items: list) -> str:
    body = (
        "\n".join(
            f'<div class="row"><span>{escape(item.name)}</span>'
            f'<span>{format_price(item.price)}</span></div>'
            for item in items
        )
        if items
        else f'<div class="row empty-section">{escape(EMPTY_SECTION_LABEL)}</div>'
    )
    return f'<div class="section">{escape(section)}</div>\n{body}'


def render_html(receipt: Receipt) -> str:
    sections_html = "\n".join(
        _section_html(section, items) for section, items in receipt.sections
    )
    return f"""
<div class="receipt">
  {_logo_img_tag(receipt)}
  <div class="title">{escape(receipt.title)}</div>
  <div class="timestamp">{receipt.timestamp:%Y-%m-%d %H:%M}</div>
  <div class="divider"></div>
  {sections_html}
  <div class="divider"></div>
  <div class="row total"><span>TOTAL</span><span>{format_price(receipt.total)}</span></div>
  <div class="footer">{escape(receipt.footer)}</div>
</div>
"""


class MockPrinter:
    """Stands in for a real printer; keeps the last rendered receipt as HTML."""

    def __init__(self) -> None:
        self.last_html: str | None = None

    def print_receipt(self, receipt: Receipt) -> None:
        self.last_html = render_html(receipt)
