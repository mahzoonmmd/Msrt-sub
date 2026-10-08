"""
history_page.py
----------------
Lists every past processing run as compact rows. Clicking a row's
"view" action reopens it in a read-only detail panel (original /
translation) without touching the API; a close button on the panel
hides it again. "Delete" removes an item from disk after confirmation.
"""
from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QTabWidget, QMessageBox, QFileDialog,
)

from app.i18n import t
from app.config import Settings
from app.history import HistoryStore, HistoryItem
from app.styles import DARK, LIGHT
from ui.widgets import Card, BidiTextEdit
from ui.icons import icon as get_icon


class HistoryPage(QWidget):
    def __init__(self, settings: Settings, history: HistoryStore, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.history = history
        self.detail_item: HistoryItem | None = None
        self._build_ui()
        self.retranslate()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 28, 32, 28)
        root.setSpacing(16)

        self.title = QLabel()
        self.title.setObjectName("PageTitle")
        root.addWidget(self.title)

        # --- Empty state ---
        self.empty_wrap = QWidget()
        empty_layout = QVBoxLayout(self.empty_wrap)
        empty_layout.setContentsMargins(0, 40, 0, 40)
        empty_layout.setSpacing(8)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_icon_label = QLabel()
        self.empty_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label = QLabel()
        self.empty_label.setObjectName("HelperText")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(self.empty_icon_label)
        empty_layout.addWidget(self.empty_label)
        self.empty_wrap.hide()
        root.addWidget(self.empty_wrap)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(self.scroll.Shape.NoFrame)
        self.list_container = QWidget()
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setSpacing(8)
        self.list_layout.addStretch()
        self.scroll.setWidget(self.list_container)
        root.addWidget(self.scroll, stretch=1)

        # detail panel (shown when a row's "view" is clicked)
        self.detail_card = Card()
        detail_layout = QVBoxLayout(self.detail_card)
        detail_layout.setContentsMargins(18, 16, 18, 18)
        detail_layout.setSpacing(12)

        detail_header = QHBoxLayout()
        self.detail_title = QLabel()
        self.detail_title.setObjectName("FieldLabel")
        self.detail_close_btn = QPushButton()
        self.detail_close_btn.setObjectName("IconButton")
        self.detail_close_btn.setFixedSize(26, 26)
        self.detail_close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.detail_close_btn.clicked.connect(self._close_detail)
        detail_header.addWidget(self.detail_title)
        detail_header.addStretch()
        detail_header.addWidget(self.detail_close_btn)
        detail_layout.addLayout(detail_header)

        self.detail_tabs = QTabWidget()
        self.detail_original = BidiTextEdit()
        self.detail_translation = BidiTextEdit()
        self.detail_tabs.addTab(self.detail_original, "")
        self.detail_tabs.addTab(self.detail_translation, "")
        detail_layout.addWidget(self.detail_tabs)

        detail_actions = QHBoxLayout()
        self.detail_download_en_btn = QPushButton()
        self.detail_download_fa_btn = QPushButton()
        for b in (self.detail_download_en_btn, self.detail_download_fa_btn):
            b.setObjectName("SecondaryButton")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
        self.detail_download_en_btn.clicked.connect(lambda: self._download("en"))
        self.detail_download_fa_btn.clicked.connect(lambda: self._download("fa"))
        detail_actions.addWidget(self.detail_download_en_btn)
        detail_actions.addWidget(self.detail_download_fa_btn)
        detail_actions.addStretch()
        detail_layout.addLayout(detail_actions)

        self.detail_card.hide()
        root.addWidget(self.detail_card)

    def retranslate(self) -> None:
        lang = self.settings.language
        self.title.setText(t("nav.history", lang))
        self.empty_label.setText(t("history.empty", lang))
        self.detail_tabs.setTabText(0, t("process.tab_original", lang))
        self.detail_tabs.setTabText(1, t("process.tab_translation", lang))
        self.detail_download_en_btn.setText(t("process.download_en", lang))
        self.detail_download_fa_btn.setText(t("process.download_fa", lang))
        self._apply_icon_colors()
        if self.detail_item:
            self.detail_title.setText(self.detail_item.filename)
        self.refresh()

    def _apply_icon_colors(self) -> None:
        c = DARK if self.settings.theme == "dark" else LIGHT
        self.empty_icon_label.setPixmap(get_icon("clock", color=c["text_tertiary"], size=32).pixmap(32, 32))
        self.detail_close_btn.setIcon(get_icon("close", color=c["text_secondary"], size=13))
        self.detail_download_en_btn.setIcon(get_icon("download", color=c["text"], size=13))
        self.detail_download_fa_btn.setIcon(get_icon("download", color=c["text"], size=13))

    def apply_theme(self) -> None:
        self._apply_icon_colors()
        self.refresh()

    def refresh(self) -> None:
        lang = self.settings.language
        c = DARK if self.settings.theme == "dark" else LIGHT
        # clear existing rows (keep trailing stretch)
        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        items = self.history.all()
        self.empty_wrap.setVisible(len(items) == 0)
        self.scroll.setVisible(len(items) > 0)

        for item in items:
            row = Card()
            row.setObjectName("HistoryRow")
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(14, 10, 14, 10)
            row_layout.setSpacing(12)

            kind_icon = QLabel()
            kind_icon.setFixedSize(18, 18)
            kind_icon.setPixmap(
                get_icon("film" if item.kind == "video" else "file-text",
                         color=c["text_tertiary"], size=16).pixmap(16, 16)
            )
            row_layout.addWidget(kind_icon)

            info = QVBoxLayout()
            info.setSpacing(1)
            name_label = QLabel(item.filename)
            name_label.setObjectName("FieldLabel")
            meta_label = QLabel(f"{item.timestamp_display}  ·  {item.source_lang.upper()}")
            meta_label.setObjectName("MetaText")
            info.addWidget(name_label)
            info.addWidget(meta_label)
            row_layout.addLayout(info, stretch=1)

            view_btn = QPushButton()
            view_btn.setObjectName("IconButton")
            view_btn.setFixedSize(30, 30)
            view_btn.setToolTip(t("history.open", lang))
            view_btn.setIcon(get_icon("eye", color=c["text_secondary"], size=15))
            view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            view_btn.clicked.connect(lambda _, i=item: self._view(i))

            delete_btn = QPushButton()
            delete_btn.setObjectName("IconButton")
            delete_btn.setFixedSize(30, 30)
            delete_btn.setToolTip(t("history.delete", lang))
            delete_btn.setIcon(get_icon("trash", color=c["danger"], size=15))
            delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            delete_btn.clicked.connect(lambda _, i=item: self._delete(i))

            row_layout.addWidget(view_btn)
            row_layout.addWidget(delete_btn)

            self.list_layout.insertWidget(self.list_layout.count() - 1, row)

    def _view(self, item: HistoryItem) -> None:
        self.detail_item = item
        self.detail_title.setText(item.filename)
        self.detail_original.set_bidi_text(item.original_text, item.source_lang)
        target_lang = "fa" if item.source_lang == "en" else "en"
        self.detail_translation.set_bidi_text(item.translated_text, target_lang)
        self.detail_card.show()

    def _close_detail(self) -> None:
        self.detail_card.hide()
        self.detail_item = None

    def _download(self, which: str) -> None:
        if not self.detail_item:
            return
        item = self.detail_item
        content = item.srt_source if which == item.source_lang else item.srt_translated
        default_name = f"subtitles_{which}.srt"
        path, _ = QFileDialog.getSaveFileName(self, "", default_name, "SubRip Subtitle (*.srt)")
        if path:
            Path(path).write_text(content, encoding="utf-8-sig")

    def _delete(self, item: HistoryItem) -> None:
        lang = self.settings.language
        reply = QMessageBox.question(
            self, "", t("history.confirm_delete", lang),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.history.delete(item.id)
            if self.detail_item and self.detail_item.id == item.id:
                self.detail_card.hide()
                self.detail_item = None
            self.refresh()
