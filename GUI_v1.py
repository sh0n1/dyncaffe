import numpy as np
import sys
sys.path.append("./src")
import os
import traceback

import numpy as np
import rasterio
from rasterio.plot import plotting_extent
from rasterio.windows import Window, from_bounds  # for the crop feature, if/when you build it

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QFileDialog, QMessageBox,
    QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem,
    QProgressBar, QStatusBar,
    QStackedWidget, QTabWidget, QGroupBox,
    QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
)

from PyQt6.QtCore import Qt, QThread, pyqtSignal  # note: pyqtSignal, not Signal
from PyQt6.QtGui import QIcon, QDoubleValidator, QIntValidator

from caffe import caffe

app = QApplication(sys.argv)

window = QWidget()
window.show()

app.exec()