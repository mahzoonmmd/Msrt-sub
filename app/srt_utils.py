"""
srt_utils.py
------------
Segment model + SRT read/write + word-count re-chunking.

Re-chunking lets the user pick "words per line" (1-10) and re-flow an
already-transcribed segment list into new subtitle cues *without*
re-calling the API — each new cue's time span is interpolated
proportionally to how many of the original words it contains, so timing
stays tightly in sync with speech.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List


@dataclass
class Segment:
    start: float  # seconds
    end: float    # seconds
    text: str


def _format_timestamp(seconds: float) -> str:
    if seconds < 0:
        seconds = 0
    ms = int(round(seconds * 1000))
    hours, ms = divmod(ms, 3_600_000)
    minutes, ms = divmod(ms, 60_000)
    secs, ms = divmod(ms, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"


def _parse_timestamp(ts: str) -> float:
    ts = ts.strip().replace(".", ",")
    match = re.match(r"(\d+):(\d+):(\d+),(\d+)", ts)
    if not match:
        return 0.0
    h, m, s, ms = (int(x) for x in match.groups())
    return h * 3600 + m * 60 + s + ms / 1000.0


def segments_to_srt(segments: List[Segment]) -> str:
    lines = []
    for idx, seg in enumerate(segments, start=1):
        lines.append(str(idx))
        lines.append(f"{_format_timestamp(seg.start)} --> {_format_timestamp(seg.end)}")
        lines.append(seg.text.strip())
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def parse_srt(content: str) -> List[Segment]:
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    blocks = re.split(r"\n\s*\n", content.strip())
    segments: List[Segment] = []
    for block in blocks:
        lines = [ln for ln in block.split("\n") if ln.strip() != ""]
        if len(lines) < 2:
            continue
        time_line_idx = 1 if re.match(r"^\d+$", lines[0].strip()) else 0
        time_line = lines[time_line_idx]
        m = re.match(r"(.+?)-->(.+)", time_line)
        if not m:
            continue
        start = _parse_timestamp(m.group(1))
        end = _parse_timestamp(m.group(2))
        text = " ".join(lines[time_line_idx + 1:]).strip()
        segments.append(Segment(start=start, end=end, text=text))
    return segments


def strip_timestamps(segments: List[Segment]) -> str:
    """Plain running text with no cue numbers or timing — for copy/paste."""
    return "\n".join(seg.text.strip() for seg in segments if seg.text.strip())


def rechunk_by_words(segments: List[Segment], words_per_line: int) -> List[Segment]:
    """
    Flatten all segments into a single word stream (each word carrying an
    interpolated timestamp based on its position within its source
    segment), then regroup into new cues of up to `words_per_line` words.
    """
    words_per_line = max(1, min(10, words_per_line))

    timed_words = []  # (word, start, end)
    for seg in segments:
        words = seg.text.split()
        if not words:
            continue
        span = max(seg.end - seg.start, 0.01)
        step = span / len(words)
        for i, w in enumerate(words):
            w_start = seg.start + i * step
            w_end = seg.start + (i + 1) * step
            timed_words.append((w, w_start, w_end))

    if not timed_words:
        return []

    new_segments: List[Segment] = []
    for i in range(0, len(timed_words), words_per_line):
        chunk = timed_words[i:i + words_per_line]
        text = " ".join(w for w, _, _ in chunk)
        start = chunk[0][1]
        end = chunk[-1][2]
        new_segments.append(Segment(start=start, end=end, text=text))

    return new_segments


def find_active_segment_index(segments: List[Segment], t: float) -> int:
    """
    Return the index of the segment spoken at time `t` (seconds), or -1
    if `t` falls in a gap before/between/after cues. Used to highlight
    the subtitle line matching the video's current playback position.
    """
    for i, seg in enumerate(segments):
        if seg.start <= t < seg.end:
            return i
        if t < seg.start:
            return -1
    return -1
