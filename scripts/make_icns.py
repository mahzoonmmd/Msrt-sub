"""
make_icns.py
------------
Generates resources/icon.icns (macOS app icon) from the existing
resources/logo_rounded.png, the same rounded-corner artwork already
used for the Windows .ico. Run once (or whenever the logo changes);
the output is committed like icon.ico so the macOS build doesn't
need Pillow at build time.

Usage:
    python scripts/make_icns.py
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "resources" / "logo_rounded.png"
OUT = ROOT / "resources" / "icon.icns"

# macOS icon sizes (standard + @2x retina variants up to 1024).
ICNS_SIZES = [(16, 16), (32, 32), (64, 64), (128, 128), (256, 256), (512, 512), (1024, 1024)]


def main() -> int:
    if not SRC.exists():
        print(f"Missing source artwork: {SRC}")
        return 1

    base = Image.open(SRC).convert("RGBA")
    # Source art is 256x256; upscale with high-quality resampling so the
    # 512/1024 variants (used for the Dock icon and Retina displays)
    # aren't visibly soft. Replace logo_rounded.png with a larger master
    # (512 or 1024px) later for a sharper result if desired.
    upscaled = base.resize((1024, 1024), Image.LANCZOS)
    upscaled.save(OUT, sizes=ICNS_SIZES)
    print(f"Wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
