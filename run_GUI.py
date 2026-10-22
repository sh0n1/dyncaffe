import numpy as np
import sys
sys.path.append("./src")

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from src.gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.styleHints().setColorScheme(Qt.ColorScheme.Light)   # needs PyQt6 6.8 or newer | change app theme to light mode

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()