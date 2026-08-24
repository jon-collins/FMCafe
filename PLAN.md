# F&M Cafe — Project Plan

## Goal
A fun receipt printer for kids' pretend play (cafe, ice cream shop, restaurant, etc).
Physical buttons on a Raspberry Pi trigger themed receipts to print on a real
thermal receipt printer. A local mock mode lets us develop receipt layouts on a
regular machine without the hardware attached.

## Hardware
- Raspberry Pi
- Epson TM-T20II thermal receipt printer, connected via **USB**
- GPIO buttons wired to the Pi, one button per theme

## Key decisions
- Language/tooling: Python, managed with `uv`
- Printer driver: `python-escpos` (USB connection)
- GPIO library: `gpiozero`
- Button mapping: one button per theme; each press prints a receipt for that theme
- Mock mode: renders receipt output as HTML for local dev preview only (not a
  kid-facing play mode — the real play mode is buttons + physical printer)
- Project layout: single `uv`-managed package

## Proposed structure
```
FMCafe/
  pyproject.toml
  src/fmcafe/
    __init__.py
    receipts/           # one module per theme, sharing common helpers
      cafe.py
      ice_cream.py
      restaurant.py
      base.py           # shared receipt-building helpers (header, line items, totals, footer)
    printer/
      interface.py      # common Printer protocol both backends implement
      driver.py         # wraps python-escpos, real USB printer backend
      mock.py           # renders receipt to HTML for local preview
    gpio/
      buttons.py        # button -> theme mapping, debouncing, main event loop (gpiozero)
    devserver/
      app.py            # tiny local web server showing mock output
  tests/
```

## Build order
1. **Receipt content layer** — theme modules producing structured receipt data,
   independent of any printer. Develop/test on a regular machine.
2. **Mock printer backend + dev preview page** — render structured data as HTML
   in a browser to check layouts before touching hardware.
3. **Real printer backend** — `python-escpos` wrapper (USB) implementing the
   same interface as the mock, tested against the actual Epson TM-T20II.
4. **GPIO button integration** — wire buttons via `gpiozero`, map presses to
   themes, call the shared receipt+printer pipeline. Runs on the Pi only.
5. **Polish** — add more themes, randomize content (fun order combos, silly
   prices), maybe sound/LED feedback on button press.

## Open items / future decisions
- Exact GPIO pin assignments per button/theme (decide when wiring the Pi)
- Whether receipts should have any randomization vs. fixed templates per theme
- Any physical enclosure / button labeling for the kids
