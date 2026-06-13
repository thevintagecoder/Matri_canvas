from PIL import Image
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
import os
import glob
import random
import readchar

console = Console()

PROJECT_NAME = "MatriCanvas Terminal Museum"
SUBTITLE = "A private terminal gallery of my mother's artworks"

ARTWORK_FOLDER = "artworks"

ASCII_CHARS = " .,:;irsXA253hMHGS#9B&@"


def get_terminal_width():
    width = console.size.width
    return max(60, min(width - 4, 140))


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


def image_to_ascii(path, width=None):
    if width is None:
        width = get_terminal_width()

    image = Image.open(path).convert("RGB")

    original_width, original_height = image.size
    aspect_ratio = original_height / original_width

    # Terminal characters are taller than they are wide,
    # so this correction keeps the artwork from looking stretched.
    height = int(width * aspect_ratio * 0.45)

    if height < 10:
        height = 10

    image = image.resize((width, height))

    ascii_image = Text()

    for y in range(image.height):
        for x in range(image.width):
            r, g, b = image.getpixel((x, y))

            brightness = (r + g + b) / 3
            char_index = int(brightness / 255 * (len(ASCII_CHARS) - 1))
            char = ASCII_CHARS[char_index]

            ascii_image.append(char, style=f"rgb({r},{g},{b})")

        ascii_image.append("\n")

    return ascii_image


def center_text(text):
    return Align.center(text)


def intro_screen():
    console.clear()

    title = Text()
    title.append("\n")
    title.append("███╗   ███╗ █████╗ ████████╗██████╗ ██╗ ██████╗ █████╗ ███╗   ██╗██╗   ██╗ █████╗ ███████╗\n", style="bold")
    title.append("████╗ ████║██╔══██╗╚══██╔══╝██╔══██╗██║██╔════╝██╔══██╗████╗  ██║██║   ██║██╔══██╗██╔════╝\n", style="bold")
    title.append("██╔████╔██║███████║   ██║   ██████╔╝██║██║     ███████║██╔██╗ ██║██║   ██║███████║███████╗\n", style="bold")
    title.append("██║╚██╔╝██║██╔══██║   ██║   ██╔══██╗██║██║     ██╔══██║██║╚██╗██║╚██╗ ██╔╝██╔══██║╚════██║\n", style="bold")
    title.append("██║ ╚═╝ ██║██║  ██║   ██║   ██║  ██║██║╚██████╗██║  ██║██║ ╚████║ ╚████╔╝ ██║  ██║███████║\n", style="bold")
    title.append("╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝  ╚═══╝  ╚═╝  ╚═╝╚══════╝\n", style="bold")
    title.append("\n")
    title.append(PROJECT_NAME + "\n", style="bold")
    title.append(SUBTITLE + "\n", style="dim")
    title.append("\n")
    title.append("n / →  next     p / ←  previous     r  random     q  quit\n", style="bold")
    title.append("\n")
    title.append("Press any key to enter the museum...", style="dim")

    console.print(Align.center(title))
    readchar.readkey()


def show_artwork(path, index, total):
    console.clear()

    filename = os.path.basename(path)
    artwork_name = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ").title()

    header = Text()
    header.append(f"{PROJECT_NAME}\n", style="bold")
    header.append("Mother's Collection — Terminal Paintings\n", style="dim")
    header.append(f"{index + 1} / {total}  |  {artwork_name}\n", style="dim")

    console.print(Align.center(header))

    ascii_art = image_to_ascii(path)
    console.print(Align.center(ascii_art))

    footer = Text()
    footer.append("\n")
    footer.append("n / → next   ", style="bold")
    footer.append("p / ← previous   ", style="bold")
    footer.append("r random   ", style="bold")
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
.jpg, .jpeg, .png, .webp, .bmp

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
            console.print(Align.center(Text("Thank you for visiting MatriCanvas Terminal Museum.", style="bold")))
            break

        elif key.lower() == "n" or key == readchar.key.RIGHT:
            index = (index + 1) % len(artworks)

        elif key.lower() == "p" or key == readchar.key.LEFT:
            index = (index - 1) % len(artworks)

        elif key.lower() == "r":
            index = random.randint(0, len(artworks) - 1)


if __name__ == "__main__":
    main()