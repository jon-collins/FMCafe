"""Common interface implemented by both printer backends."""

from typing import Protocol

from fmcafe.receipts.base import Receipt


class Printer(Protocol):
    def print_receipt(self, receipt: Receipt) -> None: ...
