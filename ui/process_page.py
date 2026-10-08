"""
process_page.py
----------------
Main "Process Video" page.

Before processing: drop/select a video (shown at a fixed 16:9 preview),
pick its spoken language, hit Start.

After processing: the language/start controls disappear (no longer
relevant) and the layout switches to a two-column view — video on the
left, the Original/Translation tabs on the right (highlighting the
currently-spoken line in sync with playback) — with the words-per-line/
reapply/download/copy controls in one row underneath both columns.

The whole page scrolls, so nothing is ever pushed out of reach.
"""
from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QTabWidget, QSpinBox, QFileDialog, QProgressBar, QApplication,
    QScrollArea, QFrame,
)

from app.i18n import t
from app.config import Settings, UsageTracker
from app.history import HistoryStore
from app.styles import DARK, LIGHT
from app.srt_utils import strip_timestamps, rechunk_by_words, find_active_segment_index
from app.workers import VideoPipelineWorker, RechunkWorker
from ui.widgets import Card, DropArea, BidiTextEdit, SuccessBanner
from ui.video_player import VideoPreviewPlayer
from ui.icons import icon as get_icon


class ProcessPage(QWidget):
    def __init__(self, settings: Settings, usage: UsageTracker, history: HistoryStore, banner: SuccessBanner,
                 on_show_info=None, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.usage = usage
        self.history = history
        self.banner = banner
        self.on_show_info = on_show_info

        self.video_path: str | None = None
        self.worker: VideoPipelineWorker | None = None
        self.result: dict | None = None
        self._flowed_src_segments = None
        self._flowed_tr_segments = None

        self._build_ui()
        self.retranslate()

    # ------------------------------------------------------------------ #
    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)

        root = QVBoxLayout(container)
        root.setContentsMargins(32, 28, 32, 28)
        root.setSpacing(18)

        title_row = QHBoxLayout()
        self.title = QLabel()
        self.title.setObjectName("PageTitle")
        self.info_btn = QPushButton()
        self.info_btn.setObjectName("IconButton")
        self.info_btn.setFixedSize(28, 28)
        self.info_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.info_btn.clicked.connect(self._show_info)
        title_row.addWidget(self.title)
        title_row.addWidget(self.info_btn)
        title_row.addStretch()
        root.addLayout(title_row)

        # --- Drop area (shown when no video is selected) ---
        self.drop_area = DropArea("", "")
        self.drop_area.clicked.connect(self._browse_file)
        self.drop_area.file_dropped.connect(self._set_video)
        root.addWidget(self.drop_area)

        # --- Selected-video card: header (filename + remove), then a
        #     video | subtitles split row, then an actions row. The
        #     subtitle column and actions row only appear once results
        #     exist. ---
        self.selected_card = Card()
        selected_layout = QVBoxLayout(self.selected_card)
        selected_layout.setContentsMargins(20, 18, 20, 18)
        selected_layout.setSpacing(14)

        header_row = QHBoxLayout()
        header_row.setSpacing(8)
        self.file_icon_label = QLabel()
        self.file_icon_label.setFixedSize(18, 18)
        self.selected_name_label = QLabel()
        self.selected_name_label.setStyleSheet("font-size: 14px; font-weight: 600;")
        self.selected_name_label.setWordWrap(True)
        self.remove_video_btn = QPushButton()
        self.remove_video_btn.setObjectName("DangerButton")
        self.remove_video_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.remove_video_btn.clicked.connect(self._clear_video)
        header_row.addWidget(self.file_icon_label)
        header_row.addWidget(self.selected_name_label, stretch=1)
        header_row.addWidget(self.remove_video_btn)
        selected_layout.addLayout(header_row)

        split_row = QHBoxLayout()
        split_row.setSpacing(14)

        self.video_player = VideoPreviewPlayer()
        self.video_player.player.positionChanged.connect(self._on_playback_position)
        split_row.addWidget(self.video_player, stretch=5)

        self.tabs = QTabWidget()
        self.original_view = BidiTextEdit()
        self.translation_view = BidiTextEdit()
        self.tabs.addTab(self.original_view, "")
        self.tabs.addTab(self.translation_view, "")
        self.tabs.hide()  # only shown once there are results
        split_row.addWidget(self.tabs, stretch=6)

        selected_layout.addLayout(split_row)

        # words-per-line + reapply + download/copy — one row, below both
        # columns, visible only once there are results.
        self.actions_container = QWidget()
        actions_v = QVBoxLayout(self.actions_container)
        actions_v.setContentsMargins(0, 0, 0, 0)
        actions_v.setSpacing(10)

        wpl_row = QHBoxLayout()
        self.wpl_label = QLabel()
        self.wpl_spin = QSpinBox()
        self.wpl_spin.setRange(1, 10)
        self.wpl_spin.setValue(self.settings.words_per_line)
        self.reapply_btn = QPushButton()
        self.reapply_btn.setObjectName("SecondaryButton")
        self.reapply_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.reapply_btn.clicked.connect(self._reapply_words_per_line)
        wpl_row.addWidget(self.wpl_label)
        wpl_row.addWidget(self.wpl_spin)
        wpl_row.addWidget(self.reapply_btn)

        self.download_en_btn = QPushButton()
        self.download_fa_btn = QPushButton()
        self.copy_btn = QPushButton()
        for b in (self.download_en_btn, self.download_fa_btn, self.copy_btn):
            b.setObjectName("SecondaryButton")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
        self.download_en_btn.clicked.connect(lambda: self._download("en"))
        self.download_fa_btn.clicked.connect(lambda: self._download("fa"))
        self.copy_btn.clicked.connect(self._copy_plain)
        wpl_row.addWidget(self.download_en_btn)
        wpl_row.addWidget(self.download_fa_btn)
        wpl_row.addWidget(self.copy_btn)
        wpl_row.addStretch()
        actions_v.addLayout(wpl_row)

        self.actions_container.hide()  # only shown once there are results
        selected_layout.addWidget(self.actions_container)

        self.selected_card.hide()
        root.addWidget(self.selected_card)

        # --- Options: source language + start/cancel. Hidden once a
        #     video has been successfully processed — no longer relevant. ---
        self.options_container = QWidget()
        options_row = QHBoxLayout(self.options_container)
        options_row.setContentsMargins(0, 0, 0, 0)
        options_row.setSpacing(14)

        self.lang_label = QLabel()
        self.lang_combo = QComboBox()
        options_row.addWidget(self.lang_label)
        options_row.addWidget(self.lang_combo)
        options_row.addStretch()

        self.start_btn = QPushButton()
        self.start_btn.setObjectName("PrimaryButton")
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_btn.clicked.connect(self._start_processing)
        options_row.addWidget(self.start_btn)

        # Only visible while a job is actually running — a quick safety
        # net in case the wrong video/language got started by mistake.
        self.cancel_btn = QPushButton()
        self.cancel_btn.setObjectName("DangerButton")
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.clicked.connect(self._cancel_processing)
        self.cancel_btn.hide()
        options_row.addWidget(self.cancel_btn)

        root.addWidget(self.options_container)

        # --- Progress ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.hide()
        root.addWidget(self.progress_bar)

        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #9a9aad;")
        self.status_label.setWordWrap(True)
        self.status_label.hide()
        root.addWidget(self.status_label)

        root.addStretch()

    # ------------------------------------------------------------------ #
    def retranslate(self) -> None:
        lang = self.settings.language
        self.title.setText(t("nav.process", lang))
        self.drop_area.set_texts(t("process.drop_title", lang), t("process.drop_subtitle", lang))
        self.remove_video_btn.setText(t("process.remove_video", lang))
        self.lang_label.setText(t("process.source_lang", lang))
        cur = self.lang_combo.currentIndex()
        self.lang_combo.clear()
        self.lang_combo.addItem(t("process.lang_en", lang), "en")
        self.lang_combo.addItem(t("process.lang_fa", lang), "fa")
        self.lang_combo.setCurrentIndex(max(cur, 0))
        self.start_btn.setText(t("process.start", lang))
        self.cancel_btn.setText(t("process.cancel", lang))
        self.info_btn.setToolTip(t("process.info_tooltip", lang))
        self.tabs.setTabText(0, t("process.tab_original", lang))
        self.tabs.setTabText(1, t("process.tab_translation", lang))
        self.wpl_label.setText(t("process.words_per_line", lang))
        self.reapply_btn.setText(t("process.reapply", lang))
        self.download_en_btn.setText(t("process.download_en", lang))
        self.download_fa_btn.setText(t("process.download_fa", lang))
        self.copy_btn.setText(t("process.copy_plain", lang))
        self._apply_icon_colors()
        if self.video_path:
            self.selected_name_label.setText(Path(self.video_path).name)

    def _show_info(self) -> None:
        if self.on_show_info:
            self.on_show_info()

    def _apply_icon_colors(self) -> None:
        c = DARK if self.settings.theme == "dark" else LIGHT
        self.info_btn.setIcon(get_icon("info", color=c["text_secondary"], size=15))
        self.drop_area.set_icon("upload", color=c["text_tertiary"], size=26)
        self.file_icon_label.setPixmap(get_icon("film", color=c["text_secondary"], size=16).pixmap(16, 16))
        self.remove_video_btn.setIcon(get_icon("trash", color=c["danger"], size=13))
        self.reapply_btn.setIcon(get_icon("refresh", color=c["text"], size=13))
        self.download_en_btn.setIcon(get_icon("download", color=c["text"], size=13))
        self.download_fa_btn.setIcon(get_icon("download", color=c["text"], size=13))
        self.copy_btn.setIcon(get_icon("copy", color=c["text"], size=13))
        self.cancel_btn.setIcon(get_icon("close", color=c["danger"], size=12))

    def apply_theme(self) -> None:
        """Called by MainWindow whenever the theme changes — procedurally
        drawn icons carry a baked-in color, so (unlike QSS colors) they
        need an explicit refresh instead of picking the new theme up
        automatically."""
        self._apply_icon_colors()

    # ------------------------------------------------------------------ #
    def _browse_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "", "", "Video Files (*.mp4 *.mov *.mkv *.avi *.webm)"
        )
        if path:
            self._set_video(path)

    def _set_video(self, path: str) -> None:
        if not path.lower().endswith((".mp4", ".mov", ".mkv", ".avi", ".webm")):
            return
        self._clear_status()
        self.video_path = path
        self.selected_name_label.setText(Path(path).name)
        self.drop_area.hide()
        self.selected_card.show()
        self.options_container.show()
        self.video_player.load(path)

    def _clear_video(self) -> None:
        self._clear_status()
        self.video_path = None
        self.video_player.clear()
        self.selected_card.hide()
        self.drop_area.show()
        self.options_container.show()
        self.tabs.hide()
        self.actions_container.hide()
        self.result = None
        self._flowed_src_segments = None
        self._flowed_tr_segments = None

    def _clear_status(self) -> None:
        """Hide any leftover error/progress text from a previous run —
        otherwise an old error message could stay stuck on screen even
        after removing the video and starting fresh."""
        self.status_label.hide()
        self.status_label.setText("")
        self.progress_bar.hide()
        self.cancel_btn.hide()

    def _start_processing(self) -> None:
        lang = self.settings.language
        self._clear_status()
        if not self.settings.api_key:
            self.status_label.setText(t("process.no_api_key", lang))
            self.status_label.show()
            return
        if not self.video_path:
            self.status_label.setText(t("process.no_file", lang))
            self.status_label.show()
            return

        self.start_btn.setEnabled(False)
        self.cancel_btn.show()
        self.progress_bar.show()
        self.status_label.show()
        self.tabs.hide()
        self.actions_container.hide()

        source_lang = self.lang_combo.currentData()
        self.worker = VideoPipelineWorker(
            api_key=self.settings.api_key,
            video_path=self.video_path,
            source_lang=source_lang,
            words_per_line=self.wpl_spin.value(),
            on_tokens=self.usage.add,
        )
        self.worker.progress.connect(self._on_progress)
        self.worker.finished_ok.connect(self._on_finished)
        self.worker.failed.connect(self._on_failed)
        self.worker.start()

    def _cancel_processing(self) -> None:
        if self.worker:
            # Cooperative cancel: the worker checks this between chunks
            # and stops without emitting finished/failed. The current
            # in-flight request (if any) still has to return first, but
            # the UI resets immediately either way.
            self.worker.cancel()
        self._clear_status()
        self.start_btn.setEnabled(True)

    def _on_progress(self, key: str) -> None:
        self.status_label.setText(t(key, self.settings.language))

    def _apply_flowed_display(self) -> tuple[str, str]:
        """
        Rebuild the Original/Translation views (one paragraph per cue,
        line-broken every `words_per_line` words) from the raw segments,
        and keep the flowed segment lists around for sync-highlighting
        during playback. Returns (original_text, translated_text) for
        history storage / plain-text copy.
        """
        wpl = self.wpl_spin.value()
        self._flowed_src_segments = rechunk_by_words(self.result["segments_src"], wpl)
        self._flowed_tr_segments = rechunk_by_words(self.result["segments_translated"], wpl)

        self.original_view.set_segments(self._flowed_src_segments, self.result["source_lang"])
        self.translation_view.set_segments(self._flowed_tr_segments, self.result["target_lang"])

        original_text = "\n".join(seg.text for seg in self._flowed_src_segments)
        translated_text = "\n".join(seg.text for seg in self._flowed_tr_segments)
        return original_text, translated_text

    def _on_finished(self, result: dict) -> None:
        self.result = result
        self._clear_status()
        self.start_btn.setEnabled(True)
        # Language/start are no longer relevant once a video has been
        # successfully processed.
        self.options_container.hide()

        src_lang = result["source_lang"]
        original_text, translated_text = self._apply_flowed_display()

        self.tabs.show()
        self.actions_container.show()
        self.banner.show_message(t("process.success", self.settings.language))

        self.history.add(
            kind="video",
            filename=Path(self.video_path).name if self.video_path else "video",
            source_lang=src_lang,
            words_per_line=self.wpl_spin.value(),
            original_text=original_text,
            translated_text=translated_text,
            srt_source=result["srt_src"],
            srt_translated=result["srt_translated"],
        )

    def _on_failed(self, message: str) -> None:
        self.progress_bar.hide()
        self.cancel_btn.hide()
        self.start_btn.setEnabled(True)
        self.status_label.setText(f"{t('process.error', self.settings.language)} {message}")
        self.status_label.show()

    def _reapply_words_per_line(self) -> None:
        if not self.result:
            self.banner.show_message(t("process.no_result_yet", self.settings.language), 1800)
            return
        srt_src, srt_tr = RechunkWorker.rebuild(
            self.result["segments_src"], self.result["segments_translated"], self.wpl_spin.value()
        )
        self.result["srt_src"] = srt_src
        self.result["srt_translated"] = srt_tr

        self._apply_flowed_display()

        self.settings.words_per_line = self.wpl_spin.value()
        self.settings.save()
        self.banner.show_message(t("process.reapplied", self.settings.language), 1800)

    def _on_playback_position(self, position_ms: int) -> None:
        """Highlight whichever cue is being spoken right now in both the
        Original and Translation views, as the video plays."""
        t_seconds = position_ms / 1000.0
        if self._flowed_src_segments:
            idx = find_active_segment_index(self._flowed_src_segments, t_seconds)
            self.original_view.highlight_index(idx)
        if self._flowed_tr_segments:
            idx_tr = find_active_segment_index(self._flowed_tr_segments, t_seconds)
            self.translation_view.highlight_index(idx_tr)

    def _download(self, which: str) -> None:
        if not self.result:
            return
        content = self.result["srt_src"] if which == self.result["source_lang"] else self.result["srt_translated"]
        default_name = f"subtitles_{which}.srt"
        path, _ = QFileDialog.getSaveFileName(self, "", default_name, "SubRip Subtitle (*.srt)")
        if path:
            Path(path).write_text(content, encoding="utf-8-sig")

    def _copy_plain(self) -> None:
        if not self.result:
            return
        text = strip_timestamps(self.result["segments_src"])
        QApplication.clipboard().setText(text)
        self.banner.show_message(t("process.copied", self.settings.language), 1600)
