"""
history.py
----------
Lightweight JSON-file history store. Each entry captures everything
needed to redisplay a past run without re-calling the API:
original transcript, translation, both SRTs and the words-per-line
setting used to build them.
"""
from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, asdict, field
from typing import List, Optional

from app.config import HISTORY_FILE


@dataclass
class HistoryItem:
    id: str
    created_at: float
    kind: str              # "video" | "srt"
    filename: str
    source_lang: str
    words_per_line: int = 6
    original_text: str = ""
    translated_text: str = ""
    srt_source: str = ""     # SRT in the original transcription language
    srt_translated: str = ""  # SRT in the translated language

    @property
    def timestamp_display(self) -> str:
        return time.strftime("%Y-%m-%d %H:%M", time.localtime(self.created_at))


class HistoryStore:
    def __init__(self) -> None:
        self._items: List[HistoryItem] = []
        self._load()

    def _load(self) -> None:
        if HISTORY_FILE.exists():
            try:
                raw = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
                self._items = [HistoryItem(**item) for item in raw]
            except Exception:
                self._items = []

    def _save(self) -> None:
        HISTORY_FILE.write_text(
            json.dumps([asdict(i) for i in self._items], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def all(self) -> List[HistoryItem]:
        return sorted(self._items, key=lambda i: i.created_at, reverse=True)

    def add(self, **kwargs) -> HistoryItem:
        item = HistoryItem(id=str(uuid.uuid4()), created_at=time.time(), **kwargs)
        self._items.append(item)
        self._save()
        return item

    def update(self, item_id: str, **kwargs) -> None:
        for item in self._items:
            if item.id == item_id:
                for k, v in kwargs.items():
                    setattr(item, k, v)
                self._save()
                return

    def get(self, item_id: str) -> Optional[HistoryItem]:
        for item in self._items:
            if item.id == item_id:
                return item
        return None

    def delete(self, item_id: str) -> None:
        self._items = [i for i in self._items if i.id != item_id]
        self._save()
