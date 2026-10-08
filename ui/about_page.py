"""about_page.py — App info, description and GitHub links."""
from __future__ import annotations

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

from app.i18n import t
from app.config import Settings, get_resource_path
from app.styles import DARK, LIGHT
from ui.widgets import Divider, LogoWidget
from ui.icons import icon as get_icon

REPO_URL = "https://github.com/mahzoonmmd/Msrt-sub"
APP_VERSION = "v1.0"


class AboutPage(QWidget):
    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self._build_ui()
        self.retranslate()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 28, 32, 28)
        root.setSpacing(20)
        root.setAlignment(Qt.AlignmentFlag.AlignTop)

        # ---------------- Brand header ----------------
        brand_row = QHBoxLayout()
        brand_row.setSpacing(14)
        logo_path = get_resource_path("resources/logo.png")
        self.logo_widget = LogoWidget(logo_path, size=48, radius=12)
        brand_row.addWidget(self.logo_widget)

        brand_text = QVBoxLayout()
        brand_text.setSpacing(2)
        self.app_name = QLabel("MSRT")
        self.app_name.setStyleSheet("font-size: 20px; font-weight: 700;")
        self.app_subtitle = QLabel()
        self.app_subtitle.setObjectName("HelperText")
        brand_text.addWidget(self.app_name)
        brand_text.addWidget(self.app_subtitle)
        brand_row.addLayout(brand_text)
        brand_row.addStretch()

        self.version_label = QLabel(APP_VERSION)
        self.version_label.setObjectName("MetaText")
        brand_row.addWidget(self.version_label, alignment=Qt.AlignmentFlag.AlignTop)
        root.addLayout(brand_row)

        self.tagline = QLabel()
        self.tagline.setWordWrap(True)
        self.tagline.setObjectName("FieldLabel")
        root.addWidget(self.tagline)

        root.addWidget(Divider())

        # ---------------- Technical info ----------------
        self.tech_section_label = QLabel()
        self.tech_section_label.setObjectName("SectionLabel")
        root.addWidget(self.tech_section_label)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)
        rows = [
            ("AI Engine", "Google Gemini (gemini-3.5-flash-lite)"),
            ("Platform", "Windows 10 / 11"),
        ]
        for key, value in rows:
            row = QHBoxLayout()
            k = QLabel(key)
            k.setObjectName("HelperText")
            v = QLabel(value)
            v.setObjectName("FieldLabel")
            row.addWidget(k)
            row.addStretch()
            row.addWidget(v)
            info_layout.addLayout(row)
        root.addLayout(info_layout)

        root.addWidget(Divider())

        # ---------------- Links ----------------
        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(10)
        self.github_btn = QPushButton()
        self.github_btn.setObjectName("PrimaryButton")
        self.github_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.github_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(REPO_URL)))

        self.star_btn = QPushButton()
        self.star_btn.setObjectName("SecondaryButton")
        self.star_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.star_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(REPO_URL)))

        buttons_row.addWidget(self.github_btn)
        buttons_row.addWidget(self.star_btn)
        buttons_row.addStretch()
        root.addLayout(buttons_row)
        root.addStretch()

    def retranslate(self) -> None:
        lang = self.settings.language
        self.app_subtitle.setText(t("about.subtitle", lang))
        self.tagline.setText(t("about.description", lang))
        self.tech_section_label.setText(t("about.section_tech", lang))
        self.github_btn.setText(t("about.github", lang))
        self.star_btn.setText(t("about.star", lang))
        self._apply_icon_colors()

    def _apply_icon_colors(self) -> None:
        c = DARK if self.settings.theme == "dark" else LIGHT
        self.github_btn.setIcon(get_icon("github", color=c["accent_text"], size=14))
        self.star_btn.setIcon(get_icon("star", color=c["text"], size=14))

    def apply_theme(self) -> None:
        self._apply_icon_colors()
