"""Common interface implemented by both printer backends."""

from typing import Protocol

from PIL import Image

from fmcafe.receipts.base import Receipt


class Printer(Protocol):
    def print_receipt(self, receipt: Receipt) -> None: ...
    def print_photo(self, image: Image.Image) -> None: ...
