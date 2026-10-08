"""
video_player.py
----------------
A compact, styled video preview player used on the Process Video page.
Shows the picked video with play/pause + seek controls. ProcessPage
listens to `player.positionChanged` and looks up the matching subtitle
cue (via app.srt_utils.find_active_segment_index) to highlight it live
in the Original/Translation text views as the video plays.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QWidget

from ui.widgets import Card
from ui.icons import icon as get_icon


def _format_time(ms: int) -> str:
    total_seconds = max(0, ms) // 1000
    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


class _AspectRatioBox(QWidget):
    """A container that keeps a fixed width:height ratio (16:9 by
    default) no matter how the surrounding layout resizes it — avoids
    the big empty black bars a plain min-height video widget leaves
    around non-matching window sizes."""

    def __init__(self, ratio: float = 9 / 16, parent=None):
        super().__init__(parent)
        self._ratio = ratio
        self._inner_layout = QVBoxLayout(self)
        self._inner_layout.setContentsMargins(0, 0, 0, 0)

    def resizeEvent(self, event) -> None:  # noqa: N802
        target_h = max(120, int(self.width() * self._ratio))
        if self.height() != target_h:
            self.setFixedHeight(target_h)
        super().resizeEvent(event)

    def content_layout(self) -> QVBoxLayout:
        return self._inner_layout


class VideoPreviewPlayer(Card):
    """Rounded video preview card with play/pause and a seek bar."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._seeking = False
        # Media controls (play button, seek bar, elapsed/duration) follow
        # the universal left-to-right playback convention regardless of
        # the app's current UI language — mirroring them under Persian's
        # RTL layout direction would scramble their positions.
        self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.video_widget = QVideoWidget()
        self.video_widget.setObjectName("VideoSurface")
        self._aspect_box = _AspectRatioBox(ratio=9 / 16)
        self._aspect_box.content_layout().addWidget(self.video_widget)
        layout.addWidget(self._aspect_box)

        controls = QHBoxLayout()
        controls.setSpacing(10)

        self.play_btn = QPushButton()
        self.play_btn.setIcon(get_icon("play", color="#FFFFFF", size=14))
        self.play_btn.setIconSize(self.play_btn.iconSize())
        self.play_btn.setObjectName("PlayButton")
        self.play_btn.setFixedSize(34, 34)
        self.play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.play_btn.clicked.connect(self.toggle_play)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setObjectName("SeekSlider")
        self.slider.setRange(0, 0)
        self.slider.sliderPressed.connect(self._on_slider_pressed)
        self.slider.sliderReleased.connect(self._on_slider_released)
        self.slider.sliderMoved.connect(self._on_slider_moved)

        self.time_label = QLabel("0:00 / 0:00")
        self.time_label.setObjectName("MetaText")
        self.time_label.setMinimumWidth(84)

        controls.addWidget(self.play_btn)
        controls.addWidget(self.slider, 1)
        controls.addWidget(self.time_label)
        layout.addLayout(controls)

        self.player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_output)
        self.player.setVideoOutput(self.video_widget)

        self.player.positionChanged.connect(self._on_position_changed)
        self.player.durationChanged.connect(self._on_duration_changed)
        self.player.playbackStateChanged.connect(self._on_playback_state_changed)

    # ------------------------------------------------------------------ #
    def load(self, path: str) -> None:
        self.player.stop()
        self.player.setSource(QUrl.fromLocalFile(path))

    def clear(self) -> None:
        self.player.stop()
        self.player.setSource(QUrl())
        self.slider.setRange(0, 0)
        self.time_label.setText("0:00 / 0:00")
        self.play_btn.setIcon(get_icon("play", color="#FFFFFF", size=14))

    def toggle_play(self) -> None:
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    # ------------------------------------------------------------------ #
    def _on_playback_state_changed(self, state) -> None:
        playing = state == QMediaPlayer.PlaybackState.PlayingState
        self.play_btn.setIcon(get_icon("pause" if playing else "play", color="#FFFFFF", size=14))

    def _on_duration_changed(self, duration_ms: int) -> None:
        self.slider.setRange(0, duration_ms)
        self._refresh_time_label(self.player.position())

    def _on_position_changed(self, position_ms: int) -> None:
        if not self._seeking:
            self.slider.setValue(position_ms)
        self._refresh_time_label(position_ms)

    def _refresh_time_label(self, position_ms: int) -> None:
        self.time_label.setText(f"{_format_time(position_ms)} / {_format_time(self.player.duration())}")

    def _on_slider_pressed(self) -> None:
        self._seeking = True

    def _on_slider_released(self) -> None:
        self._seeking = False
        self.player.setPosition(self.slider.value())

    def _on_slider_moved(self, value: int) -> None:
        self._refresh_time_label(value)
