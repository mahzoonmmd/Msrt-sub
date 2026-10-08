"""
widgets.py
----------
Small reusable widgets shared across pages.

BidiTextEdit is the key piece for readability: when Persian and English
share a line, we render the content as HTML with
`unicode-bidi: plaintext` so Qt's text engine applies the standard
Unicode Bidirectional Algorithm per line instead of forcing one global
direction — Persian stays right-to-left, embedded English/numbers stay
left-to-right and reading order never scrambles.
"""
from __future__ import annotations

import html as htmlmod

from PyQt6.QtCore import Qt, QPropertyAnimation, QTimer, pyqtSignal
from PyQt6.QtGui import (
    QDragEnterEvent, QDropEvent, QPixmap, QPainter, QPainterPath, QColor,
    QTextCursor, QTextCharFormat,
)
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QGraphicsOpacityEffect, QGraphicsDropShadowEffect, QTextEdit, QFrame,
)

from ui.icons import icon as get_icon

RTL_LANGS = {"fa", "ar", "he", "ur"}


def is_probably_rtl(text: str) -> bool:
    for ch in text:
        code = ord(ch)
        if 0x0590 <= code <= 0x08FF or 0xFB1D <= code <= 0xFDFF or 0xFE70 <= code <= 0xFEFF:
            return True
    return False


def bidi_html(text: str, lang_hint: str | None = None) -> str:
    """Wrap plain text as bidi-safe HTML for display in a QTextEdit."""
    base_dir = "rtl" if (lang_hint in RTL_LANGS or (lang_hint is None and is_probably_rtl(text))) else "ltr"
    align = "right" if base_dir == "rtl" else "left"
    escaped = htmlmod.escape(text).replace("\n", "<br/>")
    return (
        f'<div dir="{base_dir}" style="unicode-bidi:plaintext; direction:{base_dir}; '
        f'text-align:{align}; font-family:\'Vazirmatn\',\'Segoe UI\',sans-serif; '
        f'line-height:1.85; font-size:14px;">{escaped}</div>'
    )


def _bidi_paragraph(text: str, lang_hint: str | None) -> str:
    """One bidi-safe <p> — used so each cue becomes its own QTextBlock,
    which lets highlight_index() target it precisely."""
    base_dir = "rtl" if (lang_hint in RTL_LANGS or (lang_hint is None and is_probably_rtl(text))) else "ltr"
    align = "right" if base_dir == "rtl" else "left"
    escaped = htmlmod.escape(text) if text else "&nbsp;"
    return (
        f'<p dir="{base_dir}" style="unicode-bidi:plaintext; direction:{base_dir}; '
        f'text-align:{align}; font-family:\'Vazirmatn\',\'Segoe UI\',sans-serif; '
        f'line-height:1.85; font-size:14px; margin:2px 0; padding:5px 8px; '
        f'border-radius:6px;">{escaped}</p>'
    )


class BidiTextEdit(QTextEdit):
    """Read-only rich text viewer tuned for mixed Persian/English content.
    Can render as one flowing block (set_bidi_text) or as one paragraph
    per subtitle cue (set_segments) so a specific line can be highlighted
    in sync with video playback (highlight_index).

    NOTE: this is the same highlighting mechanism as before the visual
    redesign (QTextEdit.ExtraSelection targeting a specific QTextBlock)
    — only the tint color was tuned to the new accent palette.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self._segment_count = 0
        self._highlighted_index = -1

    def set_bidi_text(self, text: str, lang_hint: str | None = None) -> None:
        self.setHtml(bidi_html(text, lang_hint))
        self._segment_count = 0
        self._highlighted_index = -1

    def set_segments(self, segments, lang_hint: str | None = None) -> None:
        """Render one paragraph per segment (same order), enabling
        highlight_index() to target an exact cue as the video plays."""
        html = "".join(_bidi_paragraph(seg.text, lang_hint) for seg in segments) or _bidi_paragraph("", lang_hint)
        self.setHtml(html)
        self._segment_count = len(segments)
        self._highlighted_index = -1

    def highlight_index(self, index: int) -> None:
        """Highlight the paragraph at `index` (from the last set_segments
        call) and scroll it into view; pass -1 to clear the highlight."""
        if index == self._highlighted_index:
            return
        self._highlighted_index = index
        if index is None or index < 0 or index >= self._segment_count:
            self.setExtraSelections([])
            return

        block = self.document().findBlockByNumber(index)
        if not block.isValid():
            self.setExtraSelections([])
            return

        cursor = QTextCursor(block)
        cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
        fmt = QTextCharFormat()
        fmt.setBackground(QColor(124, 124, 240, 55))
        selection = QTextEdit.ExtraSelection()
        selection.cursor = cursor
        selection.format = fmt
        self.setExtraSelections([selection])

        scroll_cursor = QTextCursor(block)
        self.setTextCursor(scroll_cursor)
        self.ensureCursorVisible()


class NavButton(QPushButton):
    def __init__(self, text: str, icon_name: str | None = None, parent=None):
        super().__init__(text, parent)
        self.setObjectName("NavButton")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(38)
        self._icon_name = icon_name

    def set_icon_colors(self, normal: str, active: str) -> None:
        if not self._icon_name:
            return
        self.setIcon(get_icon(self._icon_name, color=active if self.isChecked() else normal, size=17))
        self.setIconSize(self.iconSize())


def rounded_pixmap(source_path, size: int, radius: int) -> QPixmap | None:
    """
    Load an image from disk and return a copy scaled to size x size and
    clipped to rounded corners. Returns None if the file can't be loaded
    (callers should fall back to a text logo in that case).
    """
    src = QPixmap(str(source_path))
    if src.isNull():
        return None
    src = src.scaled(
        size, size,
        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
        Qt.TransformationMode.SmoothTransformation,
    )
    x = max(0, (src.width() - size) // 2)
    y = max(0, (src.height() - size) // 2)
    src = src.copy(x, y, size, size)

    result = QPixmap(size, size)
    result.fill(Qt.GlobalColor.transparent)
    painter = QPainter(result)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    path = QPainterPath()
    path.addRoundedRect(0.0, 0.0, float(size), float(size), radius, radius)
    painter.setClipPath(path)
    painter.drawPixmap(0, 0, src)
    painter.end()
    return result


class LogoWidget(QLabel):
    """App logo: rounded corners, with a graceful text fallback ('MSRT')
    if the image asset is missing. Shadow kept minimal/off by default —
    a professional desktop app doesn't need a glowing logo."""

    def __init__(self, source_path, size: int = 30, radius: int = 8, parent=None):
        super().__init__(parent)
        pixmap = rounded_pixmap(source_path, size, radius)
        if pixmap is not None:
            self.setPixmap(pixmap)
        else:
            self.setText("M")
            self.setStyleSheet("font-weight: 800; font-size: 14px;")
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)


class Card(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")


class GradientCard(QFrame):
    """Kept as a distinct class for import compatibility; visually it's
    now a restrained accent-tinted panel (accent_soft bg + accent
    border) rather than a saturated full-bleed gradient block."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SubtleCard")


class Divider(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Divider")
        self.setFixedHeight(1)


class SuccessBanner(QLabel):
    """Fades in on show_message(), stays fully visible for a couple of
    seconds, then fades out slowly. `kind` controls the accent color
    ("success" or "error") via a QSS dynamic property."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StatusBanner")
        self.setProperty("kind", "success")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hide()
        self._effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._effect)
        self._anim = QPropertyAnimation(self._effect, b"opacity")

    def show_message(self, text: str, duration_ms: int = 2000, kind: str = "success") -> None:
        self.setText(text)
        self.setProperty("kind", kind)
        self.style().unpolish(self)
        self.style().polish(self)
        self.show()
        self._effect.setOpacity(0.0)
        self._anim.stop()
        self._anim.setDuration(200)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.start()
        QTimer.singleShot(duration_ms, self._fade_out)

    def _fade_out(self) -> None:
        self._anim.stop()
        self._anim.setDuration(900)  # slow, gentle fade-out
        self._anim.setStartValue(1.0)
        self._anim.setEndValue(0.0)
        self._anim.start()
        QTimer.singleShot(900, self.hide)


class DropArea(QFrame):
    """Drag & drop target that also opens a file dialog on click."""

    file_dropped = pyqtSignal(str)
    clicked = pyqtSignal()

    def __init__(self, title: str, subtitle: str, parent=None):
        super().__init__(parent)
        self.setObjectName("DropArea")
        self.setAcceptDrops(True)
        self.setMinimumHeight(168)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setProperty("dragActive", False)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)

        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("background: transparent;")
        layout.addWidget(self.icon_label)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("FieldLabel")
        self.title_label.setStyleSheet("background: transparent;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setObjectName("MetaText")
        self.subtitle_label.setStyleSheet("background: transparent;")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.title_label)
        layout.addWidget(self.subtitle_label)

    def set_icon(self, name: str, color: str, size: int = 26) -> None:
        self.icon_label.setPixmap(get_icon(name, color=color, size=size).pixmap(size, size))

    def set_texts(self, title: str, subtitle: str) -> None:
        self.title_label.setText(title)
        self.subtitle_label.setText(subtitle)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        self.clicked.emit()
        super().mousePressEvent(event)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:  # noqa: N802
        if event.mimeData().hasUrls():
            self.setProperty("dragActive", True)
            self.style().unpolish(self)
            self.style().polish(self)
            event.acceptProposedAction()

    def dragLeaveEvent(self, event) -> None:  # noqa: N802
        self.setProperty("dragActive", False)
        self.style().unpolish(self)
        self.style().polish(self)

    def dropEvent(self, event: QDropEvent) -> None:  # noqa: N802
        self.setProperty("dragActive", False)
        self.style().unpolish(self)
        self.style().polish(self)
        urls = event.mimeData().urls()
        if urls:
            self.file_dropped.emit(urls[0].toLocalFile())
