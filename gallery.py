from PIL import Image, ImageEnhance, ImageFilter
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
import os
import random
import readchar

console = Console()

PROJECT_NAME = "MatriCanvas Terminal Museum"
SUBTITLE = "A private terminal gallery of my mother's artworks"

ARTWORK_FOLDER = "artworks"

# Display mode:
# "blocks" = smoother, more image-like
# "ascii" = classic character-art look
DISPLAY_MODE = "blocks"


def load_artworks():
    valid_extensions = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tiff", ".tif"}
    files = []

    for filename in os.listdir(ARTWORK_FOLDER):
        full_path = os.path.join(ARTWORK_FOLDER, filename)

        if os.path.isfile(full_path):
            extension = os.path.splitext(filename)[1].lower()
            if extension in valid_extensions:
                files.append(full_path)

    files.sort()
    return files


def get_display_width():
    width = console.size.width
    return max(60, min(width - 4, 160))


def enhance_image(image):
    image = image.convert("RGB")

    # Slightly improve dull scans/photos.
    image = ImageEnhance.Color(image).enhance(1.25)
    image = ImageEnhance.Contrast(image).enhance(1.18)
    image = ImageEnhance.Sharpness(image).enhance(1.35)

    return image


def image_to_blocks(path, width=None):
    if width is None:
        width = get_display_width()

    image = Image.open(path)
    image = enhance_image(image)

    original_width, original_height = image.size
    aspect_ratio = original_height / original_width

    # The block mode uses two image pixels per terminal row.
    height = int(width * aspect_ratio)
    if height < 20:
        height = 20

    # Make height even because we process two rows at a time.
    if height % 2 != 0:
        height += 1

    image = image.resize((width, height), Image.Resampling.LANCZOS)

    output = Text()

    for y in range(0, image.height, 2):
        for x in range(image.width):
            top_r, top_g, top_b = image.getpixel((x, y))
            bottom_r, bottom_g, bottom_b = image.getpixel((x, y + 1))

            output.append(
                "▀",
                style=(
                    f"rgb({top_r},{top_g},{top_b}) "
                    f"on rgb({bottom_r},{bottom_g},{bottom_b})"
                ),
            )
        output.append("\n")

    return output


def image_to_ascii(path, width=None):
    if width is None:
        width = get_display_width()

    chars = " .,:;irsXA253hMHGS#9B&@"

    image = Image.open(path)
    image = enhance_image(image)

    original_width, original_height = image.size
    aspect_ratio = original_height / original_width

    height = int(width * aspect_ratio * 0.45)
    if height < 10:
        height = 10

    image = image.resize((width, height), Image.Resampling.LANCZOS)

    output = Text()

    for y in range(image.height):
        for x in range(image.width):
            r, g, b = image.getpixel((x, y))

            brightness = (0.2126 * r) + (0.7152 * g) + (0.0722 * b)
            char_index = int(brightness / 255 * (len(chars) - 1))
            char = chars[char_index]

            output.append(char, style=f"rgb({r},{g},{b})")

        output.append("\n")

    return output


def render_artwork(path):
    if DISPLAY_MODE == "blocks":
        return image_to_blocks(path)
    return image_to_ascii(path)


def intro_screen():
    console.clear()

    title = Text()
    title.append("\n")
    title.append("MATRICANVAS\n", style="bold")
    title.append(PROJECT_NAME + "\n", style="bold")
    title.append(SUBTITLE + "\n\n", style="dim")
    title.append("n / →  next     p / ←  previous     r  random     m  switch mode     q  quit\n", style="bold")
    title.append("\nPress any key to enter the museum...", style="dim")

    console.print(Align.center(title))
    readchar.readkey()


def show_artwork(path, index, total):
    console.clear()

    filename = os.path.basename(path)
    artwork_name = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ").title()

    header = Text()
    header.append(f"{PROJECT_NAME}\n", style="bold")
    header.append("Mother's Collection — Terminal Paintings\n", style="dim")
    header.append(f"{index + 1} / {total}  |  {artwork_name}  |  mode: {DISPLAY_MODE}\n", style="dim")

    console.print(Align.center(header))

    console.print(Align.center(render_artwork(path)))

    footer = Text()
    footer.append("\n")
    footer.append("n / → next   ", style="bold")
    footer.append("p / ← previous   ", style="bold")
    footer.append("r random   ", style="bold")
    footer.append("m switch mode   ", style="bold")
    footer.append("q quit", style="bold")

    console.print(Align.center(footer))


def missing_folder_screen():
    console.clear()

    message = f"""
The folder '{ARTWORK_FOLDER}' does not exist yet.

Create this structure:

{PROJECT_NAME}/
├── gallery.py
└── artworks/
    ├── artwork1.jpg
    ├── artwork2.png
    └── artwork3.jpeg

Then run:

python gallery.py
"""

    console.print(
        Panel(
            message,
            title="No artworks folder found",
            border_style="red",
        )
    )


def empty_folder_screen():
    console.clear()

    message = f"""
No image files were found inside the '{ARTWORK_FOLDER}' folder.

Supported formats:
.jpg, .jpeg, .png, .webp, .bmp, .gif, .tiff, .tif

Put your mother's artwork images inside:

{ARTWORK_FOLDER}/

Then run:

python gallery.py
"""

    console.print(
        Panel(
            message,
            title="No artworks found",
            border_style="yellow",
        )
    )


def main():
    global DISPLAY_MODE

    if not os.path.exists(ARTWORK_FOLDER):
        missing_folder_screen()
        return

    artworks = load_artworks()

    if not artworks:
        empty_folder_screen()
        return

    intro_screen()

    index = 0

    while True:
        show_artwork(artworks[index], index, len(artworks))

        key = readchar.readkey()

        if key.lower() == "q":
            console.clear()
            console.print(
                Align.center(
                    Text("Thank you for visiting MatriCanvas Terminal Museum.", style="bold")
                )
            )
            break

        elif key.lower() == "n" or key == readchar.key.RIGHT:
            index = (index + 1) % len(artworks)

        elif key.lower() == "p" or key == readchar.key.LEFT:
            index = (index - 1) % len(artworks)

        elif key.lower() == "r":
            index = random.randint(0, len(artworks) - 1)

        elif key.lower() == "m":
            DISPLAY_MODE = "ascii" if DISPLAY_MODE == "blocks" else "blocks"


if __name__ == "__main__":
    main()