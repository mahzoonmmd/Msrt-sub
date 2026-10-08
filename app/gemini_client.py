"""
gemini_client.py
-----------------
Thin wrapper around the Google Gemini API (generateContent):
  - Audio in -> transcription + translation + timestamps, in a single
    multimodal call, using a JSON schema-constrained response so the
    output structure is guaranteed (no more hand-parsing loosely-typed
    JSON like the old Groq/gpt-oss integration needed).
  - Text in -> translation only, for the "translate an existing SRT"
    feature (same schema-constrained approach, batched for very long
    files).

No SDK dependency — plain `requests` calls against the REST API, same
approach as the rest of the app, so the whole thing still packs into a
single PyInstaller exe without extra native wheels.
"""
from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Callable, List, Optional, Tuple

import requests

from app.srt_utils import Segment

API_BASE = "https://generativelanguage.googleapis.com/v1beta"
# gemini-3.5-flash-lite: GA, cheapest/fastest model in the current Gemini 3
# line, still fully multimodal (audio/text) — a good fit for a mechanical
# transcribe+translate task that doesn't need heavy reasoning.
MODEL = "gemini-3.5-flash-lite"

TIMEOUT = 180
# Cues per request for pure-text (SRT) translation. Gemini's JSON-schema
# mode is much more reliable than the old free-form JSON prompting, so a
# large batch is safe; the halving retry below is just a safety net.
BATCH_SIZE = 200
MIN_RETRY_BATCH = 8

LANG_NAMES = {"en": "English", "fa": "Persian (Farsi)"}

AUDIO_MIME_TYPES = {
    ".mp3": "audio/mp3",
    ".wav": "audio/wav",
    ".m4a": "audio/m4a",
    ".flac": "audio/flac",
    ".ogg": "audio/ogg",
}

PERSIAN_TRANSLATION_GUIDELINES = """
When translating into Persian (Farsi), follow these rules strictly:
- Write natural, fluent, contemporary spoken Persian — the way an educated native speaker would actually say it out loud. Never produce a stiff, literal word-for-word calque of the English sentence structure.
- Match the register of the source: casual conversation stays casual and colloquial (natural contractions like "می‌خوام", "نمی‌دونم" are fine for informal speech); formal, technical, or news content stays precise and properly formal.
- Prefer everyday, natural Persian vocabulary over unnecessarily formal Arabic-origin words when a common Persian equivalent exists — but keep standard formal terminology where the content itself is formal or technical.
- Use correct Persian punctuation and sentence structure: «،» for commas, «؟» for questions, verb typically at the end of the clause.
- Persian pronouns are gender-neutral ("او"/"ایشان") — never guess or inject a gender the Persian language doesn't require, even if the English pronoun was "he" or "she".
- Translate idioms and figures of speech to their natural Persian equivalent meaning — never a literal translation that would sound foreign or confusing to a Persian speaker.
- Keep proper nouns, numbers, and technical/brand terms accurate. Transliterate personal and place names into Persian script using standard conventions; leave well-known brand/product names in Latin script if that's how Persian speakers normally write them.
- Keep sentences concise enough to be read comfortably as a subtitle — don't pad with extra formal phrasing that makes the line longer than the spoken original needed to be.
- The result should read like something a native Persian speaker would naturally say, never like something obviously translated.
""".strip()


class GeminiError(RuntimeError):
    """Base error. Not retried at a smaller batch — retrying won't fix a
    bad API key, a blocked region, or a rate limit."""


class GeminiRetryableError(GeminiError):
    """The model's JSON response was malformed or got cut off. Worth
    retrying with a smaller batch (more headroom to finish cleanly)."""


class GeminiClient:
    def __init__(self, api_key: str, on_tokens: Optional[Callable[[int], None]] = None):
        if not api_key:
            raise GeminiError("Missing Gemini API key")
        self.api_key = api_key
        self.on_tokens = on_tokens

    @staticmethod
    def _post(url: str, headers: dict, body: dict):
        try:
            return requests.post(url, headers=headers, json=body, timeout=TIMEOUT)
        except requests.exceptions.RequestException as exc:
            raise GeminiError(
                f"Could not reach Google's servers: {exc}\n"
                "اتصال به سرور Google برقرار نشد. اتصال اینترنت یا VPN خود را بررسی کنید."
            ) from exc

    def _headers(self) -> dict:
        return {"x-goog-api-key": self.api_key, "Content-Type": "application/json"}

    # ------------------------------------------------------------------ #
    # Audio -> transcription + translation (one call per chunk)
    # ------------------------------------------------------------------ #
    def transcribe_translate_chunk(
        self, audio_path: Path, source_lang: str, target_lang: str, time_offset: float = 0.0
    ) -> Tuple[List[Segment], List[Segment]]:
        """
        Send one audio chunk to Gemini and get back both the original-
        language transcript AND its translation, as two timestamp-aligned
        Segment lists (timestamps already shifted by `time_offset` so
        multi-chunk results line up on one continuous timeline).
        """
        mime_type = AUDIO_MIME_TYPES.get(audio_path.suffix.lower(), "audio/mp3")
        audio_b64 = base64.b64encode(audio_path.read_bytes()).decode("ascii")

        source_name = LANG_NAMES.get(source_lang, source_lang)
        target_name = LANG_NAMES.get(target_lang, target_lang)
        guidelines = f"\n\n{PERSIAN_TRANSLATION_GUIDELINES}" if target_lang == "fa" else ""

        system_prompt = f"""You are a professional subtitle transcriber and translator.

You will receive an audio clip spoken in {source_name}. Do both of the following for the WHOLE clip:
1. Transcribe the speech into short subtitle-style cues — natural phrase boundaries, the way a professional subtitler breaks lines (roughly 2-8 seconds each), not one giant block and not one cue per single word.
2. Translate each cue into {target_name}, preserving tone, register and meaning precisely — prefer natural phrasing over literal word-for-word translation.{guidelines}

For each cue report:
- start: the cue's start time in seconds from the beginning of THIS audio clip (a decimal number, e.g. 12.4)
- end: the cue's end time in seconds (decimal)
- original: the transcribed text in {source_name}
- translated: the translated text in {target_name}

Rules:
- Cues must be in chronological order, non-overlapping, and together cover all speech in the clip.
- Skip silence and non-speech audio — don't invent cues for silence.
- Do not merge unrelated sentences into one cue.
- Output only the structured data — no commentary, no markdown."""

        response_schema = {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "start": {"type": "NUMBER"},
                    "end": {"type": "NUMBER"},
                    "original": {"type": "STRING"},
                    "translated": {"type": "STRING"},
                },
                "required": ["start", "end", "original", "translated"],
            },
        }

        body = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [{
                "parts": [
                    {"text": "Transcribe and translate this audio clip as instructed."},
                    {"inline_data": {"mime_type": mime_type, "data": audio_b64}},
                ],
            }],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": response_schema,
                # Gemini 3.x flash-lite can't fully disable thinking, but
                # "low" keeps it minimal for a mechanical task like this
                # (in practice, audio-containing requests barely think at
                # all regardless — this is just a safety cap on latency).
                "thinkingConfig": {"thinkingLevel": "low"},
                "maxOutputTokens": 8192,
            },
        }

        items = self._generate(body)

        original_segments: List[Segment] = []
        translated_segments: List[Segment] = []
        for entry in items:
            try:
                start = float(entry["start"]) + time_offset
                end = float(entry["end"]) + time_offset
                original_text = str(entry["original"]).strip()
                translated_text = str(entry["translated"]).strip()
            except (KeyError, ValueError, TypeError):
                continue
            if not original_text:
                continue
            original_segments.append(Segment(start=start, end=end, text=original_text))
            translated_segments.append(Segment(start=start, end=end, text=translated_text))

        return original_segments, translated_segments

    # ------------------------------------------------------------------ #
    # Text-only translation (existing SRT file, no audio involved)
    # ------------------------------------------------------------------ #
    def translate_segments(self, segments: List[Segment], source_lang: str, target_lang: str) -> List[Segment]:
        if not segments:
            return []
        result: List[Segment] = []
        for start in range(0, len(segments), BATCH_SIZE):
            batch = segments[start:start + BATCH_SIZE]
            result.extend(self._translate_batch(batch, source_lang, target_lang))
        return result

    def _translate_batch(self, batch: List[Segment], source_lang: str, target_lang: str) -> List[Segment]:
        try:
            translations = self._translate_batch_call(batch, source_lang, target_lang)
        except GeminiRetryableError:
            if len(batch) <= MIN_RETRY_BATCH:
                raise
            mid = len(batch) // 2
            first_half = self._translate_batch(batch[:mid], source_lang, target_lang)
            second_half = self._translate_batch(batch[mid:], source_lang, target_lang)
            return first_half + second_half
        # Network errors, invalid API key, blocked region, rate limits
        # etc. are NOT caught here — a smaller batch won't fix any of
        # those, so they propagate immediately as one clear error.

        return [
            Segment(start=seg.start, end=seg.end, text=translations.get(i, seg.text))
            for i, seg in enumerate(batch)
        ]

    def _translate_batch_call(self, batch: List[Segment], source_lang: str, target_lang: str) -> dict:
        source_name = LANG_NAMES.get(source_lang, source_lang)
        target_name = LANG_NAMES.get(target_lang, target_lang)
        guidelines = f"\n\n{PERSIAN_TRANSLATION_GUIDELINES}" if target_lang == "fa" else ""

        system_prompt = f"""You are a professional subtitle translator. Translate from {source_name} into {target_name}.
Preserve tone, register and meaning precisely; prefer natural phrasing over literal word-for-word translation. Keep names, numbers and technical terms accurate. Do not add explanations or extra commentary.{guidelines}

You will receive a JSON array of cues, each {{"i": index, "text": string}}. Translate each "text" independently, keeping every index and the exact same number of items."""

        numbered = [{"i": i, "text": s.text} for i, s in enumerate(batch)]
        response_schema = {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {"i": {"type": "INTEGER"}, "text": {"type": "STRING"}},
                "required": ["i", "text"],
            },
        }
        body = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"parts": [{"text": json.dumps(numbered, ensure_ascii=False)}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": response_schema,
                "thinkingConfig": {"thinkingLevel": "low"},
                "maxOutputTokens": 8192,
            },
        }

        items = self._generate(body, retryable_on_parse_failure=True)
        out = {}
        for entry in items:
            try:
                out[int(entry["i"])] = str(entry["text"])
            except (KeyError, ValueError, TypeError):
                continue
        return out

    # ------------------------------------------------------------------ #
    # Internals
    # ------------------------------------------------------------------ #
    def _generate(self, body: dict, retryable_on_parse_failure: bool = False) -> list:
        """POST to generateContent and return the parsed JSON array from
        the model's response. Raises GeminiRetryableError for malformed/
        truncated JSON (only if retryable_on_parse_failure — the audio
        transcription path isn't batched, so there's nothing smaller to
        retry with there; the caller just sees the plain error)."""
        url = f"{API_BASE}/models/{MODEL}:generateContent"
        resp = self._post(url, self._headers(), body)
        if resp.status_code != 200:
            raise GeminiError(self._friendly_error(resp))

        payload = resp.json()
        self._track_usage(payload)

        candidates = payload.get("candidates") or []
        if not candidates:
            block_reason = (payload.get("promptFeedback") or {}).get("blockReason")
            if block_reason:
                raise GeminiError(
                    f"Gemini blocked this request (reason: {block_reason}).\n"
                    "درخواست توسط فیلترهای ایمنی Gemini مسدود شد."
                )
            err = GeminiRetryableError if retryable_on_parse_failure else GeminiError
            raise err("Gemini returned no candidates in its response.")

        parts = (candidates[0].get("content") or {}).get("parts") or []
        text = "".join(p.get("text", "") for p in parts)

        parsed = self._parse_json_loosely(text)
        if parsed is None:
            err = GeminiRetryableError if retryable_on_parse_failure else GeminiError
            raise err("Gemini returned invalid or empty JSON.")
        if not isinstance(parsed, list):
            err = GeminiRetryableError if retryable_on_parse_failure else GeminiError
            raise err("Gemini's response wasn't the expected JSON array.")
        return parsed

    @staticmethod
    def _parse_json_loosely(content: str):
        if not content:
            return None
        content = content.strip()
        if content.startswith("```"):
            content = content.strip("`")
            if content.lower().startswith("json"):
                content = content[4:]
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        start = content.find("[")
        end = content.rfind("]")
        if start == -1 or end == -1 or end <= start:
            return None
        try:
            return json.loads(content[start:end + 1])
        except json.JSONDecodeError:
            return None

    def _track_usage(self, payload: dict) -> None:
        usage = payload.get("usageMetadata") or {}
        total = usage.get("totalTokenCount")
        if total and self.on_tokens:
            self.on_tokens(int(total))

    @staticmethod
    def _friendly_error(resp: "requests.Response") -> str:
        body = resp.text[:600]
        if "User location is not supported" in body:
            return (
                f"Gemini rejected the request — region not supported ({resp.status_code}): {body}\n"
                "Google blocks Gemini API access from certain countries (including "
                "Iran) under US export-control rules. Try a different VPN server/"
                "location and try again.\n"
                "این خطا یعنی Google دسترسی از این منطقه (از جمله ایران) را به‌خاطر "
                "قوانین تحریم صادراتی آمریکا مسدود کرده — نه اشکالی در MSRT. یک "
                "سرور یا لوکیشن دیگر برای VPN امتحان کنید."
            )
        if resp.status_code in (401, 403):
            return (
                f"Gemini rejected the API key ({resp.status_code}): {body}\n"
                "کلید Gemini API نامعتبر است یا دسترسی لازم را ندارد. آن را در "
                "تنظیمات دوباره بررسی کنید (از Google AI Studio بگیرید)."
            )
        if resp.status_code == 429:
            return (
                f"Rate limited by Gemini (429): {body}\n"
                "به سقف مصرف رایگان/نرخ درخواست Gemini رسیده‌اید؛ کمی صبر کنید و "
                "دوباره تلاش کنید."
            )
        return f"Gemini request failed ({resp.status_code}): {body}"
