"""
main_window.py
---------------
Top-level window: a flat, professional sidebar with icon-based
navigation, a stacked area for pages, and a floating status banner
shared by every page. Applies the QSS theme and reruns retranslate()
on every page when the user flips theme/language in Settings.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QStackedWidget,
    QApplication,
)

from app.config import Settings, UsageTracker, get_resource_path
from app.history import HistoryStore
from app.i18n import t
from app.styles import build_stylesheet, DARK, LIGHT

from ui.widgets import NavButton, SuccessBanner, LogoWidget, Divider
from ui.process_page import ProcessPage
from ui.srt_page import SrtPage
from ui.history_page import HistoryPage
from ui.settings_page import SettingsPage
from ui.about_page import AboutPage
from ui.onboarding import OnboardingDialog

PAGES = ["process", "srt", "history", "settings", "about"]
NAV_ICONS = {
    "process": "film",
    "srt": "file-text",
    "history": "clock",
    "settings": "settings",
    "about": "info",
}
APP_VERSION = "v1.0"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = Settings.load()
        self.usage = UsageTracker()
        self.history = HistoryStore()

        self.setWindowTitle(t("app.title", self.settings.language))
        self.resize(1180, 760)
        self.setMinimumSize(980, 640)

        logo_path = get_resource_path("resources/logo.png")
        if logo_path.exists():
            self.setWindowIcon(QIcon(str(logo_path)))

        self._build_ui()
        self._apply_theme()
        self._apply_layout_direction()

        if not self.settings.onboarding_done:
            QTimer.singleShot(150, self._show_onboarding)

    # ------------------------------------------------------------------ #
    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ---- Sidebar ----
        self.sidebar = QWidget()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(216)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 14)
        sidebar_layout.setSpacing(2)

        sidebar_header = QHBoxLayout()
        sidebar_header.setContentsMargins(16, 18, 16, 16)
        sidebar_header.setSpacing(9)
        logo_path = get_resource_path("resources/logo.png")
        self.logo_widget = LogoWidget(logo_path, size=26, radius=7)
        self.logo_text = QLabel("MSRT")
        self.logo_text.setObjectName("SidebarBrand")
        sidebar_header.addWidget(self.logo_widget)
        sidebar_header.addWidget(self.logo_text)
        sidebar_header.addStretch()
        sidebar_layout.addLayout(sidebar_header)

        nav_wrap = QVBoxLayout()
        nav_wrap.setContentsMargins(10, 0, 10, 0)
        nav_wrap.setSpacing(2)

        self.nav_buttons: dict[str, NavButton] = {}
        for key in PAGES:
            btn = NavButton("", icon_name=NAV_ICONS[key])
            btn.clicked.connect(lambda _, k=key: self._navigate(k))
            nav_wrap.addWidget(btn)
            self.nav_buttons[key] = btn
        sidebar_layout.addLayout(nav_wrap)

        sidebar_layout.addStretch()

        footer_divider = Divider()
        sidebar_layout.addWidget(footer_divider)

        self.version_label = QLabel(APP_VERSION)
        self.version_label.setObjectName("SidebarVersion")
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.version_label.setContentsMargins(0, 8, 0, 0)
        sidebar_layout.addWidget(self.version_label)

        root_layout.addWidget(self.sidebar)

        # ---- Main content area (stack + floating banner) ----
        content_wrap = QWidget()
        content_v = QVBoxLayout(content_wrap)
        content_v.setContentsMargins(0, 0, 0, 0)
        content_v.setSpacing(0)

        self.banner = SuccessBanner()
        banner_wrap = QHBoxLayout()
        banner_wrap.setContentsMargins(28, 14, 28, 0)
        banner_wrap.addWidget(self.banner)
        content_v.addLayout(banner_wrap)

        self.stack = QStackedWidget()
        content_v.addWidget(self.stack, stretch=1)
        root_layout.addWidget(content_wrap, stretch=1)

        # ---- Pages ----
        self.process_page = ProcessPage(
            self.settings, self.usage, self.history, self.banner,
            on_show_info=self._show_onboarding,
        )
        self.srt_page = SrtPage(self.settings, self.usage, self.banner)
        self.history_page = HistoryPage(self.settings, self.history)
        self.settings_page = SettingsPage(
            self.settings, self.usage, self.banner,
            on_theme_change=self._on_theme_change,
            on_language_change=self._on_language_change,
        )
        self.about_page = AboutPage(self.settings)

        self.stack.addWidget(self.process_page)
        self.stack.addWidget(self.srt_page)
        self.stack.addWidget(self.history_page)
        self.stack.addWidget(self.settings_page)
        self.stack.addWidget(self.about_page)

        self._retranslate_nav()
        self._navigate("process")

    def _navigate(self, key: str) -> None:
        index = PAGES.index(key)
        self.stack.setCurrentIndex(index)
        for k, btn in self.nav_buttons.items():
            btn.setChecked(k == key)
        self._refresh_nav_icons()
        if key == "history":
            self.history_page.refresh()

    def _refresh_nav_icons(self) -> None:
        c = DARK if self.settings.theme == "dark" else LIGHT
        for btn in self.nav_buttons.values():
            btn.set_icon_colors(normal=c["text_secondary"], active=c["accent"])

    def _retranslate_nav(self) -> None:
        lang = self.settings.language
        labels = {
            "process": t("nav.process", lang),
            "srt": t("nav.srt", lang),
            "history": t("nav.history", lang),
            "settings": t("nav.settings", lang),
            "about": t("nav.about", lang),
        }
        for key, btn in self.nav_buttons.items():
            btn.setText(labels[key])

    # ------------------------------------------------------------------ #
    def _apply_theme(self) -> None:
        app = QApplication.instance()
        app.setStyleSheet(build_stylesheet(self.settings.theme))
        self._refresh_nav_icons()

    def _apply_layout_direction(self) -> None:
        app = QApplication.instance()
        direction = Qt.LayoutDirection.RightToLeft if self.settings.language == "fa" else Qt.LayoutDirection.LeftToRight
        app.setLayoutDirection(direction)

    def _on_theme_change(self, theme: str) -> None:
        self.settings.theme = theme
        self._apply_theme()
        for page in (self.process_page, self.srt_page, self.history_page,
                     self.settings_page, self.about_page):
            if hasattr(page, "apply_theme"):
                page.apply_theme()

    def _on_language_change(self, language: str) -> None:
        self.settings.language = language
        self._apply_layout_direction()
        self.setWindowTitle(t("app.title", language))
        self._retranslate_nav()
        for page in (self.process_page, self.srt_page, self.history_page,
                     self.settings_page, self.about_page):
            page.retranslate()

    def _show_onboarding(self) -> None:
        dialog = OnboardingDialog(self.settings, self)
        dialog.exec()
