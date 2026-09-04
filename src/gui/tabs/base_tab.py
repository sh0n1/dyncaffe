"""Shared skeleton for raster-display tabs (Input DEM, MWD, WL, WD)."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt


class BaseRasterTab(QWidget):
    def __init__(self, title, subtitle):
        super().__init__()
        self._title = title
        self._subtitle = subtitle

    def setup(self, parent):
        layout = QVBoxLayout(parent)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel(self._title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        subtitle_label = QLabel(self._subtitle)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle_label)

        # TODO: replace placeholder with FigureCanvasQTAgg once raster
        # loading is wired up.