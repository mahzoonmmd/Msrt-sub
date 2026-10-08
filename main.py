"""
main.py
-------
MSRT entry point. Run with `python main.py` during development.

To build a distributable package:
  - Windows: `python build_windows.py` -> dist/MSRT.exe (see installer/setup.iss
    for the Inno Setup installer)
  - macOS:   `python build_macos.py`   -> dist/MSRT.app + dist/MSRT.dmg
    (must run on macOS; see .github/workflows/build-macos.yml for a
    ready-made macOS build/test pipeline that needs no local Mac)
"""
import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase

from app.config import get_resource_path
from ui.main_window import MainWindow


def _load_bundled_fonts() -> None:
    """Register the bundled Vazirmatn (Persian) font family if present."""
    fonts_dir = get_resource_path("resources/fonts")
    if fonts_dir.exists():
        for font_file in fonts_dir.glob("*.ttf"):
            QFontDatabase.addApplicationFont(str(font_file))


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("MSRT")
    app.setOrganizationName("MSRT")
    _load_bundled_fonts()

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
