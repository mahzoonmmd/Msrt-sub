"""
ffmpeg_utils.py
---------------
Wraps the bundled ffmpeg binary to:
  1. Extract mono 16kHz audio from any supported video container.
  2. Split audio into fixed ~10 minute chunks before sending to the
     Gemini API — this keeps each request's base64 audio payload well
     under Gemini's 20MB inline-data limit and keeps each response's
     JSON transcript short enough to avoid output-token truncation,
     regardless of how long the source video is.

ffmpeg is resolved in this order:
  1. resources/ffmpeg.exe next to the app (bundled by build.py into the exe)
  2. a system-wide "ffmpeg" already on PATH (useful for `python main.py` dev runs)
If neither is found, a clear, actionable FfmpegNotFoundError is raised
instead of letting a bare WinError bubble up to the UI.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

from app.config import get_resource_path

CHUNK_SECONDS = 10 * 60  # 10 minutes


class FfmpegNotFoundError(RuntimeError):
    pass


def _find_binary(name_base: str) -> Optional[str]:
    """Look for `name_base`(.exe) bundled next to the app, then on PATH."""
    exe_name = f"{name_base}.exe" if sys.platform == "win32" else name_base

    bundled = get_resource_path(f"resources/{exe_name}")
    if bundled.exists():
        return str(bundled)

    on_path = shutil.which(exe_name) or shutil.which(name_base)
    if on_path:
        return on_path

    if sys.platform == "darwin":
        # A GUI app launched from Finder/Dock doesn't inherit the shell's
        # PATH, so a Homebrew-installed ffmpeg can be invisible to
        # shutil.which() even though it's on disk. Check the two common
        # Homebrew prefixes directly as a last resort (Apple Silicon and
        # Intel installs use different default prefixes).
        for prefix in ("/opt/homebrew/bin", "/usr/local/bin"):
            candidate = Path(prefix) / name_base
            if candidate.exists():
                return str(candidate)

    return None


def _ffmpeg_bin() -> str:
    found = _find_binary("ffmpeg")
    if not found:
        raise FfmpegNotFoundError(
            "FFmpeg not found. ffmpeg.exe was not bundled with this build and is "
            "not on your system PATH. If running from source, install ffmpeg and "
            "add it to PATH, or place ffmpeg.exe/ffprobe.exe inside the 'resources' "
            "folder next to main.py.\n"
            "فایل ffmpeg.exe پیدا نشد. ffmpeg را نصب و به PATH اضافه کنید، یا "
            "فایل‌های ffmpeg.exe و ffprobe.exe را داخل پوشه‌ی resources قرار دهید."
        )
    return found


def _ffprobe_bin() -> Optional[str]:
    return _find_binary("ffprobe")


def _run(args: List[str]) -> None:
    creationflags = 0
    if sys.platform == "win32":
        creationflags = subprocess.CREATE_NO_WINDOW  # type: ignore[attr-defined]
    try:
        proc = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=creationflags,
        )
    except FileNotFoundError as exc:
        raise FfmpegNotFoundError(
            "FFmpeg could not be launched (file not found). Place ffmpeg.exe/"
            "ffprobe.exe in the 'resources' folder or add ffmpeg to PATH.\n"
            "اجرای ffmpeg ممکن نشد. فایل ffmpeg.exe را در پوشه‌ی resources "
            "قرار دهید یا آن را به PATH سیستم اضافه کنید."
        ) from exc

    if proc.returncode != 0:
        stderr = proc.stderr.decode("utf-8", errors="ignore")
        raise RuntimeError(f"ffmpeg failed: {stderr[-2000:]}")


def extract_audio(video_path: str, out_dir: Path) -> Path:
    """Extract mono 16kHz MP3 audio from a video file."""
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "audio.mp3"
    _run([
        _ffmpeg_bin(), "-y", "-i", video_path,
        "-vn", "-ac", "1", "-ar", "16000",
        "-b:a", "64k", str(out_path),
    ])
    return out_path


def get_audio_duration_seconds(audio_path: Path) -> float:
    ffprobe = _ffprobe_bin()
    if not ffprobe:
        return 0.0
    try:
        proc = subprocess.run(
            [ffprobe, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        return float(proc.stdout.decode().strip())
    except Exception:
        return 0.0


def split_audio_fixed_chunks(audio_path: Path, chunk_seconds: int = CHUNK_SECONDS) -> List[Path]:
    """
    Split audio_path into sequential fixed-length chunks. Returns a
    single-element list containing the original file untouched if it's
    already shorter than one chunk (the common case for short videos).
    """
    duration = get_audio_duration_seconds(audio_path)
    if duration <= 0 or duration <= chunk_seconds:
        return [audio_path]

    chunks: List[Path] = []
    chunk_dir = audio_path.parent / "chunks"
    chunk_dir.mkdir(exist_ok=True)

    start = 0.0
    index = 0
    while start < duration:
        chunk_path = chunk_dir / f"chunk_{index:03d}.mp3"
        _run([
            _ffmpeg_bin(), "-y", "-i", str(audio_path),
            "-ss", str(start), "-t", str(chunk_seconds),
            "-ac", "1", "-ar", "16000", "-b:a", "64k",
            str(chunk_path),
        ])
        chunks.append(chunk_path)
        start += chunk_seconds
        index += 1

    return chunks
