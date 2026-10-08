"""
workers.py
----------
QThread workers so the API/ffmpeg calls never block the UI thread.

VideoPipelineWorker:  video -> audio -> (split into chunks) -> Gemini
                       (transcribe + translate in one call per chunk) -> SRTs
SrtTranslateWorker:    existing .srt -> translated .srt (timing preserved)
"""
from __future__ import annotations

import tempfile
from pathlib import Path
from typing import List

from PyQt6.QtCore import QThread, pyqtSignal

from app.ffmpeg_utils import extract_audio, split_audio_fixed_chunks
from app.gemini_client import GeminiClient, GeminiError
from app.srt_utils import Segment, parse_srt, segments_to_srt, rechunk_by_words


class VideoPipelineWorker(QThread):
    progress = pyqtSignal(str)          # i18n key describing current step
    finished_ok = pyqtSignal(dict)      # {"segments_src", "segments_translated", ...}
    failed = pyqtSignal(str)

    def __init__(self, api_key: str, video_path: str, source_lang: str, words_per_line: int, on_tokens=None):
        super().__init__()
        self.api_key = api_key
        self.video_path = video_path
        self.source_lang = source_lang  # "en" or "fa"
        self.words_per_line = words_per_line
        self.on_tokens = on_tokens
        self._cancelled = False

    def cancel(self) -> None:
        """Cooperative cancel: checked between chunks. The in-flight
        request (if any) still has to finish/time out first — there's no
        safe way to abort a request mid-flight from another thread —
        but no finished/failed signal will fire after this is called."""
        self._cancelled = True

    def run(self) -> None:
        try:
            target_lang = "fa" if self.source_lang == "en" else "en"
            client = GeminiClient(self.api_key, on_tokens=self.on_tokens)

            with tempfile.TemporaryDirectory(prefix="msrt_") as tmp:
                tmp_dir = Path(tmp)

                self.progress.emit("process.step_audio")
                audio_path = extract_audio(self.video_path, tmp_dir)
                if self._cancelled:
                    return

                self.progress.emit("process.step_split")
                chunks = split_audio_fixed_chunks(audio_path)
                if self._cancelled:
                    return

                # Gemini transcribes + translates in one call per chunk,
                # so there's no separate "translate" pass — just one
                # step that produces both language tracks at once.
                self.progress.emit("process.step_transcribe")
                all_src: List[Segment] = []
                all_translated: List[Segment] = []
                offset = 0.0
                for chunk in chunks:
                    if self._cancelled:
                        return
                    src_segs, tr_segs = client.transcribe_translate_chunk(
                        chunk, self.source_lang, target_lang, time_offset=offset
                    )
                    if self._cancelled:
                        return
                    all_src.extend(src_segs)
                    all_translated.extend(tr_segs)
                    if src_segs:
                        offset = src_segs[-1].end
                    else:
                        offset += 600.0  # advance by chunk length as a fallback

                if self._cancelled:
                    return
                if not all_src:
                    raise GeminiError("No speech detected in this video.")

                self.progress.emit("process.step_build_srt")
                src_flowed = rechunk_by_words(all_src, self.words_per_line)
                tr_flowed = rechunk_by_words(all_translated, self.words_per_line)

                result = {
                    "source_lang": self.source_lang,
                    "target_lang": target_lang,
                    "segments_src": all_src,
                    "segments_translated": all_translated,
                    "srt_src": segments_to_srt(src_flowed),
                    "srt_translated": segments_to_srt(tr_flowed),
                }
                if not self._cancelled:
                    self.finished_ok.emit(result)

        except GeminiError as e:
            if not self._cancelled:
                self.failed.emit(str(e))
        except Exception as e:  # noqa: BLE001
            if not self._cancelled:
                self.failed.emit(str(e))


class RechunkWorker:
    """Not threaded — pure CPU-light re-flow, safe to call synchronously."""

    @staticmethod
    def rebuild(segments_src: List[Segment], segments_translated: List[Segment], words_per_line: int):
        src_flowed = rechunk_by_words(segments_src, words_per_line)
        tr_flowed = rechunk_by_words(segments_translated, words_per_line)
        return segments_to_srt(src_flowed), segments_to_srt(tr_flowed)


class SrtTranslateWorker(QThread):
    progress = pyqtSignal(str)
    finished_ok = pyqtSignal(str)   # translated SRT text
    failed = pyqtSignal(str)

    def __init__(self, api_key: str, srt_text: str, source_lang: str, target_lang: str, on_tokens=None):
        super().__init__()
        self.api_key = api_key
        self.srt_text = srt_text
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.on_tokens = on_tokens

    def run(self) -> None:
        try:
            self.progress.emit("process.step_translate")
            client = GeminiClient(self.api_key, on_tokens=self.on_tokens)
            segments = parse_srt(self.srt_text)
            if not segments:
                raise GeminiError("Could not parse any cues from this SRT file.")
            translated = client.translate_segments(segments, self.source_lang, self.target_lang)
            self.finished_ok.emit(segments_to_srt(translated))
        except GeminiError as e:
            self.failed.emit(str(e))
        except Exception as e:  # noqa: BLE001
            self.failed.emit(str(e))
