"""
srt_page.py
-----------
Standalone SRT -> SRT translation, no video/audio required. Timing from
the source file is preserved exactly (the LLM only rewrites cue text).
"""
from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QFileDialog, QProgressBar,
)

from app.i18n import t
from app.config import Settings, UsageTracker
from app.styles import DARK, LIGHT
from app.workers import SrtTranslateWorker
from ui.widgets import Card, DropArea, BidiTextEdit, SuccessBanner
from ui.icons import icon as get_icon


class SrtPage(QWidget):
    def __init__(self, settings: Settings, usage: UsageTracker, banner: SuccessBanner, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.usage = usage
        self.banner = banner
        self.srt_path: str | None = None
        self.worker: SrtTranslateWorker | None = None
        self.translated_srt: str | None = None

        self._build_ui()
        self.retranslate()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 28, 32, 28)
        root.setSpacing(18)

        self.title = QLabel()
        self.title.setObjectName("PageTitle")
        root.addWidget(self.title)

        # --- Drop area (shown when no SRT file is selected) ---
        self.drop_area = DropArea("", "")
        self.drop_area.clicked.connect(self._browse_file)
        self.drop_area.file_dropped.connect(self._set_srt)
        root.addWidget(self.drop_area)

        # --- Selected-file row (shown once an SRT is chosen) ---
        self.selected_card = Card()
        selected_layout = QHBoxLayout(self.selected_card)
        selected_layout.setContentsMargins(16, 14, 16, 14)
        selected_layout.setSpacing(10)

        self.file_icon_label = QLabel()
        self.file_icon_label.setFixedSize(18, 18)
        self.selected_name_label = QLabel()
        self.selected_name_label.setStyleSheet("font-size: 14px; font-weight: 600;")
        self.selected_name_label.setWordWrap(True)

        self.remove_srt_btn = QPushButton()
        self.remove_srt_btn.setObjectName("DangerButton")
        self.remove_srt_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.remove_srt_btn.clicked.connect(self._clear_srt)

        selected_layout.addWidget(self.file_icon_label)
        selected_layout.addWidget(self.selected_name_label, stretch=1)
        selected_layout.addWidget(self.remove_srt_btn)

        self.selected_card.hide()
        root.addWidget(self.selected_card)

        # --- Direction + start ---
        options_row = QHBoxLayout()
        options_row.setSpacing(14)
        self.dir_label = QLabel()
        self.dir_label.setObjectName("FieldLabel")
        self.dir_combo = QComboBox()
        options_row.addWidget(self.dir_label)
        options_row.addWidget(self.dir_combo)
        options_row.addStretch()
        self.start_btn = QPushButton()
        self.start_btn.setObjectName("PrimaryButton")
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_btn.clicked.connect(self._start)
        options_row.addWidget(self.start_btn)
        root.addLayout(options_row)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.hide()
        root.addWidget(self.progress_bar)

        self.status_label = QLabel()
        self.status_label.setObjectName("HelperText")
        self.status_label.setWordWrap(True)
        self.status_label.hide()
        root.addWidget(self.status_label)

        # --- Result ---
        self.result_card = Card()
        result_layout = QVBoxLayout(self.result_card)
        result_layout.setContentsMargins(4, 4, 4, 4)
        result_layout.setSpacing(10)
        self.result_view = BidiTextEdit()
        result_layout.addWidget(self.result_view)
        self.download_btn = QPushButton()
        self.download_btn.setObjectName("SecondaryButton")
        self.download_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.download_btn.clicked.connect(self._download)
        dl_row = QHBoxLayout()
        dl_row.setContentsMargins(12, 0, 12, 10)
        dl_row.addWidget(self.download_btn)
        dl_row.addStretch()
        result_layout.addLayout(dl_row)
        self.result_card.hide()
        root.addWidget(self.result_card)
        root.addStretch()

    def retranslate(self) -> None:
        lang = self.settings.language
        self.title.setText(t("srt.title", lang))
        self.drop_area.set_texts(t("srt.drop_title", lang), t("srt.drop_subtitle", lang))
        self.remove_srt_btn.setText(t("srt.remove_file", lang))
        self.dir_label.setText(t("srt.direction", lang))
        cur = self.dir_combo.currentIndex()
        self.dir_combo.clear()
        self.dir_combo.addItem(t("srt.dir_en_fa", lang), ("en", "fa"))
        self.dir_combo.addItem(t("srt.dir_fa_en", lang), ("fa", "en"))
        self.dir_combo.setCurrentIndex(max(cur, 0))
        self.start_btn.setText(t("srt.start", lang))
        self.download_btn.setText(t("srt.download", lang))
        self._apply_icon_colors()
        if self.srt_path:
            self.selected_name_label.setText(Path(self.srt_path).name)

    def _apply_icon_colors(self) -> None:
        c = DARK if self.settings.theme == "dark" else LIGHT
        self.drop_area.set_icon("file-text", color=c["text_tertiary"], size=26)
        self.file_icon_label.setPixmap(get_icon("file-text", color=c["text_secondary"], size=16).pixmap(16, 16))
        self.remove_srt_btn.setIcon(get_icon("trash", color=c["danger"], size=13))
        self.download_btn.setIcon(get_icon("download", color=c["text"], size=13))

    def apply_theme(self) -> None:
        self._apply_icon_colors()

    def _browse_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "", "", "SubRip Subtitle (*.srt)")
        if path:
            self._set_srt(path)

    def _set_srt(self, path: str) -> None:
        if not path.lower().endswith(".srt"):
            return
        self.srt_path = path
        self.selected_name_label.setText(Path(path).name)
        self.drop_area.hide()
        self.selected_card.show()

    def _clear_srt(self) -> None:
        self.srt_path = None
        self.selected_card.hide()
        self.drop_area.show()
        self.result_card.hide()
        self.translated_srt = None

    def _start(self) -> None:
        lang = self.settings.language
        if not self.settings.api_key:
            self.status_label.setText(t("process.no_api_key", lang))
            self.status_label.show()
            return
        if not self.srt_path:
            self.status_label.setText(t("process.no_file", lang))
            self.status_label.show()
            return

        self.start_btn.setEnabled(False)
        self.progress_bar.show()
        self.status_label.show()
        self.result_card.hide()

        src, tgt = self.dir_combo.currentData()
        srt_text = Path(self.srt_path).read_text(encoding="utf-8-sig")

        self.worker = SrtTranslateWorker(
            api_key=self.settings.api_key, srt_text=srt_text,
            source_lang=src, target_lang=tgt, on_tokens=self.usage.add,
        )
        self.worker.progress.connect(lambda k: self.status_label.setText(t(k, self.settings.language)))
        self.worker.finished_ok.connect(self._on_finished)
        self.worker.failed.connect(self._on_failed)
        self.worker.start()

    def _on_finished(self, srt_text: str) -> None:
        self.translated_srt = srt_text
        self.progress_bar.hide()
        self.start_btn.setEnabled(True)
        self.status_label.hide()
        _, tgt = self.dir_combo.currentData()
        self.result_view.set_bidi_text(srt_text, tgt)
        self.result_card.show()
        self.banner.show_message(t("process.success", self.settings.language))

    def _on_failed(self, message: str) -> None:
        self.progress_bar.hide()
        self.start_btn.setEnabled(True)
        self.status_label.setText(f"{t('process.error', self.settings.language)} {message}")
        self.status_label.show()

    def _download(self) -> None:
        if not self.translated_srt:
            return
        path, _ = QFileDialog.getSaveFileName(self, "", "translated.srt", "SubRip Subtitle (*.srt)")
        if path:
            Path(path).write_text(self.translated_srt, encoding="utf-8-sig")
