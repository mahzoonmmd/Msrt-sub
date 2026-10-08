"""
build_windows.py
-----------------
Builds the standalone Windows executable with PyInstaller.
(Formerly build.py — renamed when macOS support was added; see
build_macos.py for the macOS .app/.dmg build.)

Prerequisites (place these before running):
  resources/ffmpeg.exe   - static ffmpeg build (e.g. from gyan.dev)
  resources/ffprobe.exe  - static ffprobe build, same source

  resources/logo.png and resources/icon.ico already ship in this repo
  (the app's real logo, pre-rendered with rounded corners as a
  multi-size Windows .ico). Only replace them if you want new branding.

Note: the video preview player uses QtMultimedia. PyInstaller's PyQt6
hook normally bundles the required Qt multimedia plugins automatically,
but it's worth actually playing a video in the built dist/MSRT.exe once
before shipping, in case a plugin needs to be added manually via
--add-binary for your PyInstaller/PyQt6 version.

Usage:
    python build.py

Output:
    dist/MSRT.exe
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESOURCES = ROOT / "resources"


def ensure_prereqs() -> bool:
    missing = []
    for name in ("ffmpeg.exe", "ffprobe.exe"):
        if not (RESOURCES / name).exists():
            missing.append(name)

    if missing:
        print("Missing required files before building:")
        for m in missing:
            print(f"  - resources/{m}")
        print("\nSee the docstring at the top of build.py for how to obtain them.")
        return False
    return True


def main() -> int:
    if not ensure_prereqs():
        return 1

    sep = ";" if sys.platform == "win32" else ":"
    add_data = [
        f"resources{sep}resources",
    ]

    args = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name", "MSRT",
        "--icon", str(RESOURCES / "icon.ico"),
    ]
    for entry in add_data:
        args += ["--add-data", entry]
    args.append(str(ROOT / "main.py"))

    print("Running:", " ".join(args))
    result = subprocess.run(args, cwd=str(ROOT))
    if result.returncode != 0:
        return result.returncode

    print("\nBuild complete: dist/MSRT.exe")
    print("Next: run Inno Setup on installer/setup.iss to produce the installer.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
