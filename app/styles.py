"""
styles.py
---------
MSRT design system.

Redesigned as a restrained, professional desktop palette rather than a
generic "AI app" purple/blue gradient wash: neutral surfaces, a single
disciplined accent color, small consistent radii, subtle borders, and
a clear typographic scale. The accent (a muted indigo, echoing the
logo) is used sparingly — primary actions, the active nav item, focus
rings — not as a background wash.

Both themes are separately tuned (dark is NOT just an inverted light
theme): light uses a soft neutral background with white panels; dark
uses a deep neutral background with slightly-elevated panel surfaces,
tuned for readability rather than pure black.
"""
from __future__ import annotations

DARK = {
    "bg": "#17171B",
    "surface": "#1E1E23",
    "surface_alt": "#26262C",
    "surface_hover": "#2C2C33",
    "border": "#313138",
    "border_strong": "#3D3D46",
    "text": "#F2F2F5",
    "text_secondary": "#A3A3AD",
    "text_tertiary": "#77777F",
    "accent": "#7C7CF0",
    "accent_hover": "#8F8FFA",
    "accent_soft": "#26264A",
    "accent_text": "#FFFFFF",
    "success": "#3DD68C",
    "success_soft": "#173226",
    "danger": "#F97066",
    "danger_soft": "#3A1F1E",
    "warning": "#FDB022",
}

LIGHT = {
    "bg": "#F7F7F8",
    "surface": "#FFFFFF",
    "surface_alt": "#F1F1F3",
    "surface_hover": "#EAEAEE",
    "border": "#E3E3E7",
    "border_strong": "#D2D2D8",
    "text": "#1A1A1F",
    "text_secondary": "#6B6B76",
    "text_tertiary": "#9494A0",
    "accent": "#5457D5",
    "accent_hover": "#4547BE",
    "accent_soft": "#EEEEFB",
    "accent_text": "#FFFFFF",
    "success": "#1A9D5C",
    "success_soft": "#E7F8EF",
    "danger": "#D8342A",
    "danger_soft": "#FBEAE9",
    "warning": "#B4680A",
}

FONT_STACK = '"Segoe UI Variable Text", "Segoe UI", "Vazirmatn", "Tahoma", sans-serif'


def build_stylesheet(theme: str) -> str:
    c = DARK if theme == "dark" else LIGHT
    return f"""
QWidget {{
    background: transparent;
    color: {c['text']};
    font-family: {FONT_STACK};
    font-size: 13px;
}}

QMainWindow {{
    background: {c['bg']};
}}

QDialog {{
    background: {c['surface']};
}}

/* ---------- Sidebar ---------- */
#Sidebar {{
    background: {c['bg']};
    border-right: 1px solid {c['border']};
}}

#SidebarBrand {{
    font-size: 15px;
    font-weight: 600;
    letter-spacing: 0.2px;
}}

#SidebarVersion {{
    color: {c['text_tertiary']};
    font-size: 11px;
}}

#SectionLabel {{
    color: {c['text_tertiary']};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.6px;
}}

QPushButton#NavButton {{
    text-align: left;
    padding: 9px 12px;
    border: none;
    border-radius: 7px;
    background: transparent;
    color: {c['text_secondary']};
    font-size: 13px;
    font-weight: 500;
}}
QPushButton#NavButton:hover {{
    background: {c['surface_hover']};
    color: {c['text']};
}}
QPushButton#NavButton:checked {{
    background: {c['accent_soft']};
    color: {c['accent']};
    font-weight: 600;
}}

/* ---------- Surfaces ---------- */
#Card {{
    background: {c['surface']};
    border: 1px solid {c['border']};
    border-radius: 10px;
}}

#SubtleCard {{
    background: {c['accent_soft']};
    border: 1px solid {c['accent']};
    border-radius: 10px;
}}
#SubtleCard QLabel {{ background: transparent; }}

#Divider {{
    background: {c['border']};
    max-height: 1px;
    min-height: 1px;
}}

#DropArea {{
    border: 1.5px dashed {c['border_strong']};
    border-radius: 12px;
    background: {c['surface']};
}}
#DropArea[dragActive="true"] {{
    border: 1.5px dashed {c['accent']};
    background: {c['accent_soft']};
}}

/* ---------- Buttons ---------- */
QPushButton#PrimaryButton {{
    border: none;
    border-radius: 7px;
    padding: 9px 18px;
    font-weight: 600;
    font-size: 13px;
    color: {c['accent_text']};
    background: {c['accent']};
}}
QPushButton#PrimaryButton:hover {{ background: {c['accent_hover']}; }}
QPushButton#PrimaryButton:disabled {{
    background: {c['surface_alt']};
    color: {c['text_tertiary']};
}}

QPushButton#SecondaryButton {{
    border: 1px solid {c['border_strong']};
    border-radius: 7px;
    padding: 8px 16px;
    font-weight: 500;
    background: {c['surface']};
    color: {c['text']};
}}
QPushButton#SecondaryButton:hover {{
    background: {c['surface_hover']};
    border: 1px solid {c['text_tertiary']};
}}
QPushButton#SecondaryButton:disabled {{
    color: {c['text_tertiary']};
    border: 1px solid {c['border']};
}}

QPushButton#IconButton {{
    border: 1px solid {c['border']};
    border-radius: 7px;
    background: {c['surface']};
    padding: 6px;
}}
QPushButton#IconButton:hover {{
    background: {c['surface_hover']};
    border: 1px solid {c['border_strong']};
}}

QPushButton#DangerButton {{
    border: 1px solid {c['danger']};
    border-radius: 7px;
    padding: 7px 14px;
    color: {c['danger']};
    background: transparent;
    font-weight: 600;
}}
QPushButton#DangerButton:hover {{
    background: {c['danger_soft']};
}}

QPushButton#TextButton {{
    border: none;
    background: transparent;
    color: {c['accent']};
    font-weight: 600;
    padding: 4px 2px;
}}
QPushButton#TextButton:hover {{ color: {c['accent_hover']}; text-decoration: underline; }}

/* ---------- Inputs ---------- */
QLineEdit, QSpinBox, QComboBox, QTextEdit {{
    background: {c['surface_alt']};
    border: 1px solid {c['border']};
    border-radius: 7px;
    padding: 8px 11px;
    selection-background-color: {c['accent']};
    selection-color: {c['accent_text']};
}}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus, QTextEdit:focus {{
    border: 1px solid {c['accent']};
}}
QComboBox::drop-down {{ border: none; width: 26px; }}
QComboBox QAbstractItemView {{
    background: {c['surface']};
    border: 1px solid {c['border']};
    selection-background-color: {c['accent_soft']};
    selection-color: {c['accent']};
    outline: none;
    padding: 4px;
}}
QSpinBox::up-button, QSpinBox::down-button {{ width: 18px; }}

/* ---------- Tabs (underline style, not filled pills) ---------- */
QTabWidget::pane {{
    border: 1px solid {c['border']};
    border-radius: 10px;
    top: 6px;
    background: {c['surface']};
}}
QTabBar::tab {{
    background: transparent;
    color: {c['text_secondary']};
    padding: 8px 4px;
    margin-right: 18px;
    border-bottom: 2px solid transparent;
    font-weight: 500;
}}
QTabBar::tab:selected {{
    color: {c['text']};
    border-bottom: 2px solid {c['accent']};
    font-weight: 600;
}}
QTabBar::tab:hover:!selected {{
    color: {c['text']};
}}

/* ---------- Progress bar ---------- */
QProgressBar {{
    border: none;
    border-radius: 3px;
    background: {c['surface_alt']};
    height: 5px;
    text-align: center;
    color: transparent;
}}
QProgressBar::chunk {{
    border-radius: 3px;
    background: {c['accent']};
}}

/* ---------- Video preview ---------- */
#VideoPreviewCard {{
    background: {c['surface']};
    border: 1px solid {c['border']};
    border-radius: 10px;
}}
#VideoSurfaceWrap {{
    background: #000000;
    border-radius: 7px;
}}
QPushButton#PlayButton {{
    border: none;
    border-radius: 17px;
    background: {c['accent']};
}}
QPushButton#PlayButton:hover {{ background: {c['accent_hover']}; }}
QSlider#SeekSlider::groove:horizontal {{
    height: 4px;
    border-radius: 2px;
    background: {c['border_strong']};
}}
QSlider#SeekSlider::sub-page:horizontal {{
    height: 4px;
    border-radius: 2px;
    background: {c['accent']};
}}
QSlider#SeekSlider::handle:horizontal {{
    width: 12px;
    height: 12px;
    margin: -4px 0;
    border-radius: 6px;
    background: {c['accent']};
    border: 2px solid {c['surface']};
}}

/* ---------- Synced subtitle highlighting ---------- */
#ActiveCue {{
    background: {c['accent_soft']};
    border-left: 2px solid {c['accent']};
}}

/* ---------- Scrollbars ---------- */
QScrollBar:vertical {{
    background: transparent;
    width: 9px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {c['border_strong']};
    border-radius: 4px;
    min-height: 28px;
}}
QScrollBar::handle:vertical:hover {{ background: {c['text_tertiary']}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{
    background: transparent;
    height: 9px;
    margin: 0;
}}
QScrollBar::handle:horizontal {{
    background: {c['border_strong']};
    border-radius: 4px;
    min-width: 28px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

/* ---------- Misc text ---------- */
#PageTitle {{ font-size: 18px; font-weight: 600; letter-spacing: -0.1px; }}
#PageSubtitle {{ color: {c['text_secondary']}; font-size: 12.5px; }}
#FieldLabel {{ font-size: 13px; font-weight: 500; }}
#HelperText {{ color: {c['text_tertiary']}; font-size: 12px; }}
#MetaText {{ color: {c['text_tertiary']}; font-size: 11.5px; }}

#StatusBanner {{
    border-radius: 8px;
    padding: 9px 14px;
    font-weight: 500;
    font-size: 12.5px;
}}
#StatusBanner[kind="success"] {{
    background: {c['success_soft']};
    color: {c['success']};
    border: 1px solid {c['success']};
}}
#StatusBanner[kind="error"] {{
    background: {c['danger_soft']};
    color: {c['danger']};
    border: 1px solid {c['danger']};
}}

#HistoryRow {{
    background: {c['surface']};
    border: 1px solid {c['border']};
    border-radius: 9px;
}}
#HistoryRow:hover {{ border: 1px solid {c['border_strong']}; background: {c['surface_hover']}; }}

QToolTip {{
    background: {c['surface_alt']};
    color: {c['text']};
    border: 1px solid {c['border']};
    border-radius: 6px;
    padding: 5px 9px;
    font-size: 12px;
}}

/* ---------- Message boxes (e.g. history delete confirmation) ---------- */
QMessageBox {{
    background: {c['surface']};
}}
QMessageBox QLabel {{
    color: {c['text']};
    background: transparent;
    font-size: 13.5px;
}}
QMessageBox QPushButton {{
    border: 1px solid {c['border_strong']};
    border-radius: 7px;
    padding: 7px 18px;
    background: {c['surface']};
    color: {c['text']};
    min-width: 64px;
}}
QMessageBox QPushButton:hover {{
    background: {c['surface_hover']};
}}
QMessageBox QPushButton:default {{
    border: none;
    color: {c['accent_text']};
    background: {c['accent']};
}}
"""
