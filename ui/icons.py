"""
icons.py
--------
A small offline icon set drawn directly with QPainter on a 24x24 grid —
no SVG files, no icon fonts, nothing to bundle or that could go missing
in a PyInstaller build. Every icon shares the same stroke weight, cap
style and join style so the set reads as one consistent family.

Usage:
    from ui.icons import icon
    button.setIcon(icon("film", color="#5B5BD6", size=18))
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPen, QColor, QPainterPath

GRID = 24


def _new_painter(size: int, color: str, stroke: float) -> tuple[QPixmap, QPainter]:
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(QColor(color))
    pen.setWidthF(stroke)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.scale(size / GRID, size / GRID)
    return pix, p


def _line(p, x1, y1, x2, y2):
    p.drawLine(QPointF(x1, y1), QPointF(x2, y2))


def _rect(p, x, y, w, h, radius=2.5):
    p.drawRoundedRect(QRectF(x, y, w, h), radius, radius)


def _ellipse(p, cx, cy, rx, ry):
    p.drawEllipse(QPointF(cx, cy), rx, ry)


def _path(p, points, close=False):
    path = QPainterPath()
    path.moveTo(*points[0])
    for pt in points[1:]:
        path.lineTo(*pt)
    if close:
        path.closeSubpath()
    p.drawPath(path)


# --------------------------------------------------------------------- #
# Icon drawers — each receives a QPainter already scaled to a 24x24 grid.
# --------------------------------------------------------------------- #

def _draw_film(p):
    _rect(p, 2.5, 4.5, 19, 15, 3)
    for x in (7.7, 16.3):
        _line(p, x, 4.5, x, 19.5)
    p.save()
    p.setBrush(QColor(p.pen().color()))
    for x in (5.1, 12, 18.9):
        for y in (7.2, 12, 16.8):
            p.drawEllipse(QPointF(x, y), 0.55, 0.55)
    p.restore()


def _draw_file_text(p):
    _path(p, [(6, 2.5), (15, 2.5), (18.5, 6), (18.5, 21.5), (6, 21.5)], close=True)
    _path(p, [(15, 2.5), (15, 6), (18.5, 6)])
    for y in (11, 14.2, 17.4):
        _line(p, 8.7, y, 15.8, y)


def _draw_clock(p):
    _ellipse(p, 12, 12, 9, 9)
    _line(p, 12, 12, 12, 6.7)
    _line(p, 12, 12, 16.2, 14)


def _draw_settings(p):
    for y, kx in ((7, 9), (12, 15), (17, 7)):
        _line(p, 3.5, y, 20.5, y)
        p.save()
        p.setBrush(QColor(p.pen().color()))
        p.drawEllipse(QPointF(kx, y), 2.1, 2.1)
        p.restore()


def _draw_info(p):
    _ellipse(p, 12, 12, 9, 9)
    p.drawPoint(QPointF(12, 8.3))
    _line(p, 12, 8.1, 12, 8.5)
    _line(p, 12, 11, 12, 16.3)
    _line(p, 10.3, 11, 12, 11)


def _draw_play(p):
    p.setBrush(QColor(p.pen().color()))
    _path(p, [(8, 5.5), (18.5, 12), (8, 18.5)], close=True)
    p.setBrush(Qt.BrushStyle.NoBrush)


def _draw_pause(p):
    _rect(p, 7.5, 5.5, 3.4, 13, 1.2)
    _rect(p, 13.1, 5.5, 3.4, 13, 1.2)


def _draw_upload(p):
    _line(p, 12, 16, 12, 4.2)
    _path(p, [(7.2, 8.6), (12, 3.8), (16.8, 8.6)])
    _line(p, 4.5, 19.2, 19.5, 19.2)


def _draw_download(p):
    _line(p, 12, 3.8, 12, 15.6)
    _path(p, [(7.2, 11), (12, 15.8), (16.8, 11)])
    _line(p, 4.5, 19.2, 19.5, 19.2)


def _draw_copy(p):
    _rect(p, 8.5, 2.5, 12, 12, 2.4)
    _path(p, [(6, 8.5), (3.5, 8.5), (3.5, 21.5), (15.5, 21.5), (15.5, 19)])


def _draw_close(p):
    _line(p, 6, 6, 18, 18)
    _line(p, 18, 6, 6, 18)


def _draw_chevron_down(p):
    _path(p, [(6.5, 9.5), (12, 15), (17.5, 9.5)])


def _draw_check(p):
    _path(p, [(5, 12.5), (10, 17.5), (19.5, 6.5)])


def _draw_alert(p):
    _path(p, [(12, 3), (21.5, 20), (2.5, 20)], close=True)
    _line(p, 12, 9.3, 12, 14.3)
    _line(p, 12, 16.9, 12, 17.1)


def _draw_refresh(p):
    p.drawArc(QRectF(4, 4, 16, 16), 20 * 16, 320 * 16)
    _path(p, [(16.4, 3.6), (20.2, 4.4), (19.4, 8.2)], close=True)


def _draw_trash(p):
    _line(p, 4.5, 7, 19.5, 7)
    _path(p, [(8.5, 7), (8.5, 4.3), (15.5, 4.3), (15.5, 7)])
    _path(p, [(6.3, 7), (7.2, 20.5), (16.8, 20.5), (17.7, 7)])
    _line(p, 10.2, 10.5, 10.2, 17)
    _line(p, 13.8, 10.5, 13.8, 17)


def _draw_eye(p):
    _path(p, [(2.5, 12), (12, 5.3), (21.5, 12), (12, 18.7)], close=True)
    _ellipse(p, 12, 12, 2.6, 2.6)


def _draw_video_off_slot(p):
    _rect(p, 2.5, 6, 13, 12, 2.5)
    _path(p, [(15.5, 10.5), (21, 7.3), (21, 16.7), (15.5, 13.5)], close=True)


def _draw_language(p):
    _ellipse(p, 12, 12, 9, 9)
    p.drawArc(QRectF(3, 3, 18, 18), 0, 360 * 16)
    _line(p, 3, 12, 21, 12)
    p.save()
    path = QPainterPath()
    path.addEllipse(QRectF(8.2, 3, 7.6, 18))
    p.drawPath(path)
    p.restore()


def _draw_star(p):
    pts = []
    import math
    for i in range(10):
        r = 9.2 if i % 2 == 0 else 4.0
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((12 + r * math.cos(a), 12 + r * math.sin(a)))
    _path(p, pts, close=True)


def _draw_github(p):
    _ellipse(p, 12, 12, 8.6, 8.6)
    _path(p, [(9, 18.5), (9, 15.6), (15, 15.6), (15, 18.5)])


ICONS = {
    "film": _draw_film,
    "file-text": _draw_file_text,
    "clock": _draw_clock,
    "settings": _draw_settings,
    "info": _draw_info,
    "play": _draw_play,
    "pause": _draw_pause,
    "upload": _draw_upload,
    "download": _draw_download,
    "copy": _draw_copy,
    "close": _draw_close,
    "chevron-down": _draw_chevron_down,
    "check": _draw_check,
    "alert": _draw_alert,
    "refresh": _draw_refresh,
    "trash": _draw_trash,
    "eye": _draw_eye,
    "video-off": _draw_video_off_slot,
    "language": _draw_language,
    "star": _draw_star,
    "github": _draw_github,
}

_cache: dict[tuple, QIcon] = {}


def icon(name: str, color: str = "#1A1A1F", size: int = 20, stroke: float = 1.7) -> QIcon:
    key = (name, color, size, stroke)
    if key in _cache:
        return _cache[key]
    draw = ICONS.get(name)
    if draw is None:
        return QIcon()
    pix, p = _new_painter(size, color, stroke)
    draw(p)
    p.end()
    result = QIcon(pix)
    _cache[key] = result
    return result


def pixmap(name: str, color: str = "#1A1A1F", size: int = 20, stroke: float = 1.7) -> QPixmap:
    draw = ICONS.get(name)
    pix, p = _new_painter(size, color, stroke)
    if draw:
        draw(p)
    p.end()
    return pix
