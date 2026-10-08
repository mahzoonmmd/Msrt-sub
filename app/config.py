"""
config.py
---------
Application paths, persisted settings (theme, language, API key,
words-per-line) and the rolling 24h token-usage counter.

All data lives under the user's AppData/Local folder on Windows
(falls back to ~/.msrt on other platforms during development).
"""
from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path

APP_NAME = "MSRT"


def get_app_dir() -> Path:
    """Return (and create) the per-user data directory for the app."""
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        root = Path(base) / APP_NAME
    elif sys.platform == "darwin":
        # Standard macOS per-user application support location.
        root = Path.home() / "Library" / "Application Support" / APP_NAME
    else:
        root = Path.home() / f".{APP_NAME.lower()}"
    root.mkdir(parents=True, exist_ok=True)
    return root


def get_resource_path(relative: str) -> Path:
    """
    Resolve a bundled resource (e.g. ffmpeg.exe, icons) whether running
    from source or from a PyInstaller-frozen executable.
    """
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        base = Path(__file__).resolve().parent.parent
    return base / relative


SETTINGS_FILE = get_app_dir() / "settings.json"
HISTORY_FILE = get_app_dir() / "history.json"
USAGE_FILE = get_app_dir() / "usage.json"

DEFAULT_SETTINGS = {
    "api_key": "",
    "theme": "light",       # "dark" | "light"
    "language": "en",       # "fa" | "en"
    "words_per_line": 6,
    "onboarding_done": False,
}


@dataclass
class Settings:
    api_key: str = ""
    theme: str = "light"
    language: str = "en"
    words_per_line: int = 6
    onboarding_done: bool = False

    @classmethod
    def load(cls) -> "Settings":
        if SETTINGS_FILE.exists():
            try:
                data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
                merged = {**DEFAULT_SETTINGS, **data}
                return cls(**merged)
            except Exception:
                pass
        return cls(**DEFAULT_SETTINGS)

    def save(self) -> None:
        SETTINGS_FILE.write_text(
            json.dumps(asdict(self), ensure_ascii=False, indent=2), encoding="utf-8"
        )


class UsageTracker:
    """Tracks approximate daily token consumption with a 24h rolling reset."""

    def __init__(self) -> None:
        self._data = {"tokens_used": 0, "window_start": time.time()}
        self._load()

    def _load(self) -> None:
        if USAGE_FILE.exists():
            try:
                self._data = json.loads(USAGE_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass
        self._maybe_reset()

    def _save(self) -> None:
        USAGE_FILE.write_text(json.dumps(self._data), encoding="utf-8")

    def _maybe_reset(self) -> None:
        if time.time() - self._data.get("window_start", 0) >= 24 * 3600:
            self._data = {"tokens_used": 0, "window_start": time.time()}
            self._save()

    def refresh(self) -> None:
        """Reload usage data from disk (e.g. for a manual refresh action)."""
        self._load()

    def add(self, tokens: int) -> None:
        self._maybe_reset()
        self._data["tokens_used"] = int(self._data.get("tokens_used", 0)) + int(tokens)
        self._save()

    @property
    def tokens_used(self) -> int:
        self._maybe_reset()
        return int(self._data.get("tokens_used", 0))

    @property
    def seconds_until_reset(self) -> int:
        elapsed = time.time() - self._data.get("window_start", 0)
        return max(0, int(24 * 3600 - elapsed))
