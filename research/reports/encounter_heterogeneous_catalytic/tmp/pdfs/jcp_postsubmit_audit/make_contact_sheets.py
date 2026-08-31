from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont


def main() -> None:
    source = Path(sys.argv[1])
    output = Path(sys.argv[2])
    output.mkdir(parents=True, exist_ok=True)
    pages = sorted(source.glob("page-*.png"))
    font = ImageFont.load_default()
    for sheet_index in range(0, len(pages), 4):
        batch = pages[sheet_index : sheet_index + 4]
        opened = [Image.open(path).convert("RGB") for path in batch]
        max_w = max(image.width for image in opened)
        max_h = max(image.height for image in opened)
        canvas = Image.new("RGB", (2 * max_w, 2 * (max_h + 28)), "white")
        draw = ImageDraw.Draw(canvas)
        for slot, (path, page) in enumerate(zip(batch, opened)):
            x = (slot % 2) * max_w
            y = (slot // 2) * (max_h + 28)
            canvas.paste(page, (x, y + 28))
            draw.text((x + 8, y + 7), path.stem, fill="black", font=font)
        canvas.save(output / f"sheet-{sheet_index // 4 + 1:02d}.jpg", quality=88)


if __name__ == "__main__":
    main()
