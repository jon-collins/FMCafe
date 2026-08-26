"""Image prep shared by anything sent to the thermal printer (logos, photos).

Resizing happens here, up front, so the expensive part -- ESC/POS's
black-and-white dithering (``PIL.Image.convert("1")``, done in ``python-escpos``'s
``EscposImage``) -- runs on an already-print-sized image instead of a full
multi-megapixel photo. Both the resize and the dithering are implemented in
Pillow's C code rather than pixel-by-pixel Python loops, so neither step is
heavy even on a Raspberry Pi -- as long as we don't feed it a huge image.
"""

from PIL import Image, ImageOps

# Epson TM-T20II printable width at 203 dpi (72mm / 576px), per its
# escpos-printer-db capability profile.
PRINTER_WIDTH_PX = 576

# Safety cap so an extreme aspect-ratio upload (e.g. a panorama or a long
# screenshot) can't demand an unreasonable amount of paper; taller images
# get center-cropped to this height after resizing to width.
MAX_PRINT_HEIGHT_PX = PRINTER_WIDTH_PX * 3


def resize_to_printer_width(image: Image.Image, width: int = PRINTER_WIDTH_PX) -> Image.Image:
    """Resize an image to span the full printer width, keeping aspect ratio."""
    image = ImageOps.exif_transpose(image)  # respect phone camera orientation

    if image.width != width:
        height = round(image.height * (width / image.width))
        image = image.resize((width, height))

    if image.height > MAX_PRINT_HEIGHT_PX:
        top = (image.height - MAX_PRINT_HEIGHT_PX) // 2
        image = image.crop((0, top, image.width, top + MAX_PRINT_HEIGHT_PX))

    return image
