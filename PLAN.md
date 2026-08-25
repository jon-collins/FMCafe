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

## Status (as of this phase)
Phases 1–4 above are done: four themes (cafe, ice cream, restaurant, supermarket)
with randomized, weighted item selection (including low-probability silly/funny
items), grouped sections with a trailing category and an "empty section" label,
full-width theme logos, a configurable currency symbol, a rare simulated printer
malfunction (garbled output), and a shared print throttle (10s cooldown across
all buttons) in the GPIO listener. Not yet done: GPIO pins are still placeholders
(decide when wiring the Pi), and a supermarket logo image.

**Hardware confirmed working (2026-08-25)**: the physical Epson TM-T20II
arrived and was tested over USB from a Windows PC. Its real USB IDs are
`VID_04B8&PID_0E15` (Device Manager) — `driver.py`'s hardcoded default was
wrong (`0x0202`, from unverified web research) and has been corrected. A raw
ESC/POS test print (align/bold/width/height/cut — the same primitives
`UsbPrinter` uses) was sent via Windows' print spooler (`Win32Raw` backend,
a temporary "Generic / Text Only" printer queue) and printed correctly.

Note for next time we touch USB printing on Windows: `python-escpos`'s `Usb`
backend (`pyusb`) needs the `usb` extra to even import (`python-escpos[usb]`,
now in `pyproject.toml`) — without it you get a confusing "usb library not
installed" error. Beyond that, pyusb needs a **libusb** backend, and on
Windows the printer is normally claimed by the stock `usbprint.sys` class
driver, which blocks libusb from opening it — pyusb raises `NoBackendError`.
Fixing that for real USB access requires Zadig to rebind the device's
interface to WinUSB (admin, and the device stops working as a normal Windows
printer until reverted) — we deliberately skipped that and used the Windows
spooler instead, since it isn't relevant on the Pi anyway: Linux's libusb
opens the device directly once a udev rule grants permission, no
Zadig-equivalent needed. This means `UsbPrinter`/`fmcafe-kiosk` still hasn't
been run for real — that first real test will happen directly on the Pi.

## Phase 2: Order-builder web app (iPad kiosk)

### Goal
Instead of only pressing a button for a random receipt, let a kid build an
actual order by tapping pictures of items (an apple, a coffee, etc.) on an
iPad, then print the receipt that matches exactly what they picked. Runs as a
small web app hosted on the Pi's local network — no internet required, just
the Pi and the iPad on the same Wi-Fi.

### Key decisions
- **Runs alongside the GPIO buttons**, not instead of them — both stay
  available, and both must share one `UsbPrinter` + one `Throttle` instance so
  they can't overrun the physical printer between them. This means combining
  the GPIO listener and the new Flask app into a single process/entry point
  (`fmcafe-kiosk`) rather than two independent scripts.
- **Item pictures**: simple icons rather than raw emoji text (consistent look
  across devices) or real photos (too much asset work for 60+ items across 4
  themes). Plan is to start with generated placeholder icon tiles so every
  item has *something* immediately, then swap in nicer icons for the common
  items over time without blocking the rest.
- **Ordering interaction**: tap-to-add cart. Tapping an item's tile adds one
  to the order (tap again for more), a running list + total is shown, with
  "Clear" and "Print Receipt" actions. Cart state lives client-side in the
  browser and is only sent to the server on print — no server-side session
  needed for a single shared iPad.
- **Open question**: whether the low-probability silly/funny menu items (e.g.
  "Sock Puppet Sandwich") should be tappable in the manual order UI too, or
  whether manual ordering only shows the normal menu and silly items stay
  exclusive to the random button-press flow.

### New pieces
- `receipts/order.py` — `build_receipt_from_cart(theme, item_counts) -> Receipt`,
  reusing the existing `Receipt`/`LineItem`/`section_order` model so mock
  rendering, real printing, the malfunction easter egg, and the throttle all
  keep working unchanged for manually-built orders.
- `kiosk/app.py` (+ templates/static) — Flask app: a theme-picker landing page,
  one order page per theme (grid of item tiles grouped by section, cart panel,
  print button), sized for touch on an iPad.
- A combined `fmcafe-kiosk` entry point that starts the GPIO listener thread
  and the Flask server together, bound to `0.0.0.0` so the iPad can reach it
  at the Pi's local address (e.g. `raspberrypi.local:5000`).

### Build order
1. `build_receipt_from_cart` — content layer only, unit-testable without any UI.
2. Kiosk Flask routes/templates, dev-tested against the mock printer first
   (same pattern as the existing preview server) so the flow is provable on a
   regular machine before touching the Pi.
3. Wire the shared `UsbPrinter` + `Throttle` singleton and combine the GPIO
   thread + Flask server into the single `fmcafe-kiosk` entry point.
4. Polish — bigger toddler-sized touch targets, a print confirmation
   animation, maybe a tap sound effect.

## Deployment: running on the Pi at boot

`UsbPrinter.print_ready()` prints a short "READY TO SERVE!" slip (subject to
the same rare malfunction easter egg as normal receipts) — call it once at
the start of `fmcafe.gpio.buttons.run()` and `fmcafe.kiosk.run.main()`, right
after creating the shared `Throttle`, so both boot paths confirm the
printer/service came up. It also consumes one throttle window itself, so an
eager button press right at boot still respects the cooldown.

To start `fmcafe-kiosk` automatically on boot via `systemd`:

1. One-time setup on the Pi:
   ```
   cd ~/FMCafe
   uv sync
   ```
   This creates `.venv/` with all dependencies and the `fmcafe-kiosk` console
   script installed inside it. Gotchas hit on our test Pi (Raspberry Pi OS
   with Python 3.13), all needing an `apt install` + re-run of `uv sync`
   since none of these packages have prebuilt wheels for that combo yet:
   - **Pillow needs image library headers to compile**: `sudo apt install -y
     libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libopenjp2-7-dev
     libtiff5-dev libwebp-dev` (try `libtiff-dev` if `libtiff5-dev` isn't found).
   - **`gpiozero` needs a real pin-access backend.** Without one it silently
     falls back to an experimental backend using the old `/sys/class/gpio`
     interface, which raises `OSError: [Errno 22] Invalid argument` on modern
     kernels. Fixed by adding `lgpio` (Linux-only) to `pyproject.toml`'s
     dependencies.
   - **`lgpio` itself needs `swig` and a C compiler to build**: `sudo apt
     install -y swig build-essential python3-dev`.

2. Grant the printer permission without root, via a udev rule (adjust the
   vendor/product IDs if `lsusb` shows different values for your unit):
   ```
sudo tee /etc/udev/rules.d/99-escpos.rules <<'EOF'
SUBSYSTEM=="usb", ATTR{idVendor}=="04b8", ATTR{idProduct}=="0e15", MODE="0666"
EOF
sudo udevadm control --reload-rules && sudo udevadm trigger
   ```
   Also make sure the user running the service is in the `gpio` group
   (`sudo usermod -aG gpio <your-username>`) — usually already the case on
   Raspberry Pi OS. **Substitute your actual username for `pi` everywhere
   below** (our test Pi's user is `jon`, so paths are `/home/jon/FMCafe`).

3. Create `/etc/systemd/system/fmcafe-kiosk.service`:
   ```ini
   [Unit]
   Description=F&M Cafe kiosk (GPIO buttons + order web app)
   After=network-online.target
   Wants=network-online.target

   [Service]
   Type=simple
   User=jon
   WorkingDirectory=/home/jon/FMCafe
   ExecStart=/home/jon/FMCafe/.venv/bin/fmcafe-kiosk
   Restart=on-failure
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
   ```
   Calling the venv's script directly (rather than `uv run fmcafe-kiosk`)
   avoids `uv` re-resolving the project on every boot.

4. Enable and start it:
   ```
   sudo systemctl daemon-reload
   sudo systemctl enable --now fmcafe-kiosk
   ```

5. Check it's alive / debug:
   ```
   sudo systemctl status fmcafe-kiosk
   sudo journalctl -u fmcafe-kiosk -f
   ```

After any code changes, `git pull && uv sync` (only needed if dependencies
changed) then `sudo systemctl restart fmcafe-kiosk`.
