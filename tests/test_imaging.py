from PIL import Image

from fmcafe.printer.imaging import MAX_PRINT_HEIGHT_PX, PRINTER_WIDTH_PX, resize_to_printer_width


def test_resize_to_printer_width_scales_to_target_width_keeping_aspect_ratio():
    image = Image.new("RGB", (1000, 500), "red")

    resized = resize_to_printer_width(image, width=PRINTER_WIDTH_PX)

    assert resized.width == PRINTER_WIDTH_PX
    assert resized.height == PRINTER_WIDTH_PX // 2


def test_resize_to_printer_width_leaves_already_correct_width_alone():
    image = Image.new("RGB", (PRINTER_WIDTH_PX, 300), "blue")

    resized = resize_to_printer_width(image)

    assert resized.width == PRINTER_WIDTH_PX
    assert resized.height == 300


def test_resize_to_printer_width_crops_extremely_tall_images():
    # A very tall, narrow image (e.g. a panorama rotated or a long screenshot).
    image = Image.new("RGB", (100, 100_000), "green")

    resized = resize_to_printer_width(image, width=PRINTER_WIDTH_PX)

    assert resized.width == PRINTER_WIDTH_PX
    assert resized.height == MAX_PRINT_HEIGHT_PX
