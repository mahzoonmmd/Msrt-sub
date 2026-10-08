"""onboarding.py — Three-step first-run guide shown as a modal dialog."""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

from app.i18n import t
from app.config import Settings
from app.styles import DARK, LIGHT
from ui.icons import icon as get_icon
from ui.widgets import GradientCard

STEPS = [
    ("onboarding.step1_title", "onboarding.step1_body", "settings"),
    ("onboarding.step2_title", "onboarding.step2_body", "film"),
    ("onboarding.step3_title", "onboarding.step3_body", "file-text"),
]


class OnboardingDialog(QDialog):
    finished_onboarding = pyqtSignal()

    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.step = 0
        self.setModal(True)
        self.setObjectName("OnboardingDialog")
        self.setWindowTitle("MSRT")
        self.setMinimumSize(420, 300)
        self.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft if settings.language == "fa" else Qt.LayoutDirection.LeftToRight
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(18)

        self.card = GradientCard()
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(28, 30, 28, 30)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.setSpacing(12)

        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("background: transparent;")

        self.step_title = QLabel()
        self.step_title.setStyleSheet("font-size: 16px; font-weight: 600; background: transparent;")
        self.step_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.step_title.setWordWrap(True)

        self.step_body = QLabel()
        self.step_body.setObjectName("PageSubtitle")
        self.step_body.setStyleSheet("background: transparent;")
        self.step_body.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.step_body.setWordWrap(True)

        card_layout.addWidget(self.icon_label)
        card_layout.addWidget(self.step_title)
        card_layout.addWidget(self.step_body)
        root.addWidget(self.card, stretch=1)

        dots_row = QHBoxLayout()
        dots_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dots_row.setSpacing(6)
        self.dots = []
        for _ in STEPS:
            dot = QLabel("●")
            dot.setStyleSheet("font-size: 8px;")
            self.dots.append(dot)
            dots_row.addWidget(dot)
        root.addLayout(dots_row)

        nav_row = QHBoxLayout()
        self.next_btn = QPushButton()
        self.next_btn.setObjectName("PrimaryButton")
        self.next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_btn.clicked.connect(self._next)
        nav_row.addStretch()
        nav_row.addWidget(self.next_btn)
        root.addLayout(nav_row)

        self._render_step()

    def _render_step(self) -> None:
        lang = self.settings.language
        title_key, body_key, icon_name = STEPS[self.step]
        c = DARK if self.settings.theme == "dark" else LIGHT
        self.icon_label.setPixmap(get_icon(icon_name, color=c["accent"], size=32).pixmap(32, 32))
        self.step_title.setText(t(title_key, lang))
        self.step_body.setText(t(body_key, lang))
        for i, dot in enumerate(self.dots):
            dot.setStyleSheet(f"font-size: 8px; color: {c['accent'] if i == self.step else c['border_strong']};")
        is_last = self.step == len(STEPS) - 1
        self.next_btn.setText(t("onboarding.done", lang) if is_last else t("onboarding.next", lang))

    def _next(self) -> None:
        if self.step < len(STEPS) - 1:
            self.step += 1
            self._render_step()
        else:
            self.settings.onboarding_done = True
            self.settings.save()
            self.finished_onboarding.emit()
            self.accept()
