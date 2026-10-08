"""
build_macos.py
---------------
Builds the standalone macOS app bundle (MSRT.app) with PyInstaller,
then packages it into a distributable .dmg.

This mirrors build_windows.py exactly in spirit — same PyInstaller
options, same bundled-resources approach — just swapping the
Windows-only pieces (icon.ico, .exe binaries, Inno Setup) for their
macOS equivalents (icon.icns, ffmpeg/ffprobe Mach-O binaries, a .dmg).
Nothing about the app's actual logic changes; this is packaging only.

Prerequisites (place these before running):
  resources/ffmpeg    - static macOS ffmpeg binary (no extension)
  resources/ffprobe   - static macOS ffprobe binary, same source
                         e.g. https://evermeet.cc/ffmpeg/ (universal
                         binaries), or `brew install ffmpeg` and copy
                         the binaries out of the Homebrew prefix.
                         Must be executable (chmod +x) and, ideally,
                         codesigned/notarized-compatible (see README).

  resources/icon.icns already ships in this repo, generated from the
  same rounded logo as icon.ico via `python scripts/make_icns.py`.

This script only runs meaningfully on macOS (PyInstaller cross-builds
are not supported — a macOS build must run on macOS, which is exactly
what the project's GitHub Actions workflow
(.github/workflows/build-macos.yml) does on a hosted macOS runner).

Usage:
    python build_macos.py

Output:
    dist/MSRT.app
    dist/MSRT.dmg
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESOURCES = ROOT / "resources"
DIST = ROOT / "dist"


def ensure_prereqs() -> bool:
    if sys.platform != "darwin":
        print(
            "build_macos.py must be run on macOS (PyInstaller cannot cross-build "
            "a macOS app from Linux/Windows). Use the GitHub Actions workflow "
            "'build-macos' instead if you don't have a Mac available."
        )
        return False

    missing = []
    for name in ("ffmpeg", "ffprobe"):
        path = RESOURCES / name
        if not path.exists():
            missing.append(name)
        elif not (path.stat().st_mode & 0o111):
            print(f"resources/{name} exists but isn't executable — run: chmod +x resources/{name}")
            return False

    if missing:
        print("Missing required files before building:")
        for m in missing:
            print(f"  - resources/{m}")
        print("\nSee the docstring at the top of build_macos.py for how to obtain them.")
        return False

    if not (RESOURCES / "icon.icns").exists():
        print("resources/icon.icns is missing. Generate it with: python scripts/make_icns.py")
        return False

    return True


def build_app() -> int:
    args = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--windowed",
        "--name", "MSRT",
        "--icon", str(RESOURCES / "icon.icns"),
        "--add-data", f"{RESOURCES}:resources",
        # macOS apps are always codesigned at least ad-hoc so Gatekeeper/
        # QtMultimedia's media backend don't choke on an unsigned bundle.
        "--codesign-identity", "-",
        "--osx-bundle-identifier", "com.msrt.app",
        str(ROOT / "main.py"),
    ]
    print("Running:", " ".join(args))
    result = subprocess.run(args, cwd=str(ROOT))
    return result.returncode


def build_dmg() -> int:
    app_path = DIST / "MSRT.app"
    dmg_path = DIST / "MSRT.dmg"
    if not app_path.exists():
        print(f"Expected {app_path} to exist after the PyInstaller build, but it's missing.")
        return 1
    if dmg_path.exists():
        dmg_path.unlink()

    if shutil.which("create-dmg"):
        # create-dmg (brew install create-dmg) gives a nicer drag-to-Applications
        # window; fall back to plain hdiutil if it isn't installed.
        result = subprocess.run([
            "create-dmg",
            "--volname", "MSRT",
            "--window-size", "600", "400",
            "--icon-size", "100",
            "--icon", "MSRT.app", "150", "180",
            "--app-drop-link", "450", "180",
            str(dmg_path), str(app_path),
        ])
        return result.returncode

    result = subprocess.run([
        "hdiutil", "create",
        "-volname", "MSRT",
        "-srcfolder", str(app_path),
        "-ov", "-format", "UDZO",
        str(dmg_path),
    ])
    return result.returncode


def main() -> int:
    if not ensure_prereqs():
        return 1

    rc = build_app()
    if rc != 0:
        return rc

    rc = build_dmg()
    if rc != 0:
        return rc

    print("\nBuild complete: dist/MSRT.app and dist/MSRT.dmg")
    print(
        "Note: this build is only ad-hoc signed (--codesign-identity -), which is "
        "enough to run locally but will still trigger Gatekeeper's 'unidentified "
        "developer' warning on another Mac. See README.md for notarizing with a "
        "real Apple Developer ID if you plan to distribute this build publicly."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
