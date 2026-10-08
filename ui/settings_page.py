"""
settings_page.py
-----------------
API key entry, live daily token-usage meter (24h auto-reset), theme
toggle and interface language toggle — grouped into clear labeled
sections rather than a stack of look-alike cards.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QProgressBar,
)

from app.i18n import t
from app.config import Settings, UsageTracker
from app.styles import DARK, LIGHT
from ui.widgets import SuccessBanner, Divider
from ui.icons import icon as get_icon

DAILY_TOKEN_ESTIMATE = 400_000  # soft visual reference for the usage bar


def _section_label(text_key: str = "") -> QLabel:
    lbl = QLabel()
    lbl.setObjectName("SectionLabel")
    return lbl


class SettingsPage(QWidget):
    def __init__(self, settings: Settings, usage: UsageTracker, banner: SuccessBanner,
                 on_theme_change, on_language_change, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.usage = usage
        self.banner = banner
        self.on_theme_change = on_theme_change
        self.on_language_change = on_language_change

        self._build_ui()
        self.retranslate()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh_usage)
        self._timer.start(15_000)
        self._refresh_usage()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 28, 32, 28)
        root.setSpacing(22)
        root.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.title = QLabel()
        self.title.setObjectName("PageTitle")
        root.addWidget(self.title)

        # ---------------- AI / API section ----------------
        self.api_section_label = _section_label()
        root.addWidget(self.api_section_label)

        self.api_label = QLabel()
        self.api_label.setObjectName("FieldLabel")
        self.api_helper = QLabel()
        self.api_helper.setObjectName("HelperText")
        self.api_helper.setWordWrap(True)

        api_row = QHBoxLayout()
        api_row.setSpacing(10)
        self.api_input = QLineEdit()
        self.api_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_input.setText(self.settings.api_key)
        self.save_btn = QPushButton()
        self.save_btn.setObjectName("PrimaryButton")
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self._save_api_key)
        api_row.addWidget(self.api_input, stretch=1)
        api_row.addWidget(self.save_btn)

        root.addWidget(self.api_label)
        root.addLayout(api_row)
        root.addWidget(self.api_helper)

        root.addWidget(Divider())

        # ---------------- Usage section ----------------
        self.usage_section_label = _section_label()
        root.addWidget(self.usage_section_label)

        usage_title_row = QHBoxLayout()
        self.usage_title = QLabel()
        self.usage_title.setObjectName("FieldLabel")
        self.refresh_usage_btn = QPushButton()
        self.refresh_usage_btn.setObjectName("SecondaryButton")
        self.refresh_usage_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_usage_btn.clicked.connect(self._refresh_usage)
        usage_title_row.addWidget(self.usage_title)
        usage_title_row.addStretch()
        usage_title_row.addWidget(self.refresh_usage_btn)
        root.addLayout(usage_title_row)

        self.usage_bar = QProgressBar()
        self.usage_bar.setRange(0, DAILY_TOKEN_ESTIMATE)
        self.usage_bar.setTextVisible(False)
        root.addWidget(self.usage_bar)

        self.usage_detail = QLabel()
        self.usage_detail.setObjectName("HelperText")
        root.addWidget(self.usage_detail)

        root.addWidget(Divider())

        # ---------------- Appearance section ----------------
        self.appearance_section_label = _section_label()
        root.addWidget(self.appearance_section_label)

        theme_row = QHBoxLayout()
        self.theme_label = QLabel()
        self.theme_label.setObjectName("FieldLabel")
        self.theme_combo = QComboBox()
        theme_row.addWidget(self.theme_label)
        theme_row.addStretch()
        theme_row.addWidget(self.theme_combo)
        self.theme_combo.currentIndexChanged.connect(self._theme_changed)
        root.addLayout(theme_row)

        root.addWidget(Divider())

        # ---------------- Language section ----------------
        self.language_section_label = _section_label()
        root.addWidget(self.language_section_label)

        lang_row = QHBoxLayout()
        self.lang_pref_label = QLabel()
        self.lang_pref_label.setObjectName("FieldLabel")
        self.lang_combo = QComboBox()
        lang_row.addWidget(self.lang_pref_label)
        lang_row.addStretch()
        lang_row.addWidget(self.lang_combo)
        self.lang_combo.currentIndexChanged.connect(self._language_changed)
        root.addLayout(lang_row)

        root.addStretch()

    def retranslate(self) -> None:
        lang = self.settings.language
        self.title.setText(t("nav.settings", lang))
        self.api_section_label.setText(t("settings.section_api", lang))
        self.api_label.setText(t("settings.api_key", lang))
        self.api_input.setPlaceholderText(t("settings.api_key_placeholder", lang))
        self.api_helper.setText(t("settings.api_key_helper", lang))
        self.save_btn.setText(t("settings.save", lang))
        self.usage_section_label.setText(t("settings.section_usage", lang))
        self.usage_title.setText(t("settings.usage", lang))
        self.refresh_usage_btn.setText(t("settings.refresh", lang))
        self.appearance_section_label.setText(t("settings.section_appearance", lang))
        self.theme_label.setText(t("settings.theme", lang))
        self.language_section_label.setText(t("settings.section_language", lang))
        self.lang_pref_label.setText(t("settings.language", lang))

        self.theme_combo.blockSignals(True)
        self.theme_combo.clear()
        self.theme_combo.addItem(t("settings.theme_dark", lang), "dark")
        self.theme_combo.addItem(t("settings.theme_light", lang), "light")
        self.theme_combo.setCurrentIndex(0 if self.settings.theme == "dark" else 1)
        self.theme_combo.blockSignals(False)

        self.lang_combo.blockSignals(True)
        self.lang_combo.clear()
        self.lang_combo.addItem("فارسی", "fa")
        self.lang_combo.addItem("English", "en")
        self.lang_combo.setCurrentIndex(0 if self.settings.language == "fa" else 1)
        self.lang_combo.blockSignals(False)

        self._apply_icon_colors()
        self._refresh_usage()

    def _apply_icon_colors(self) -> None:
        c = DARK if self.settings.theme == "dark" else LIGHT
        self.refresh_usage_btn.setIcon(get_icon("refresh", color=c["text"], size=12))

    def apply_theme(self) -> None:
        self._apply_icon_colors()

    def _save_api_key(self) -> None:
        self.settings.api_key = self.api_input.text().strip()
        self.settings.save()
        self.banner.show_message(t("settings.saved", self.settings.language), 1800)

    def _theme_changed(self, _index: int) -> None:
        theme = self.theme_combo.currentData()
        self.settings.theme = theme
        self.settings.save()
        self.on_theme_change(theme)

    def _language_changed(self, _index: int) -> None:
        language = self.lang_combo.currentData()
        self.settings.language = language
        self.settings.save()
        self.on_language_change(language)

    def _refresh_usage(self) -> None:
        self.usage.refresh()
        used = min(self.usage.tokens_used, DAILY_TOKEN_ESTIMATE)
        self.usage_bar.setValue(used)
        hours = self.usage.seconds_until_reset // 3600
        minutes = (self.usage.seconds_until_reset % 3600) // 60
        lang = self.settings.language
        self.usage_detail.setText(
            f"{self.usage.tokens_used:,} tokens  ·  {t('settings.usage_reset', lang)} {hours}h {minutes}m"
        )
