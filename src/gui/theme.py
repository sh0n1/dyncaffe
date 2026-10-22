"""Application stylesheet for the CAFFE GUI."""

# Colour palette: change these in one place to re-theme the app
NAVY = "#1F3864"
BLUE = "#2E75B6"
BLUE_DARK = "#255E91"
BG = "#F5F7FA"
PANEL = "#FFFFFF"
BORDER = "#CBD5E1"
TEXT = "#1E293B"
MUTED = "#64748B"
GREEN = "#16A34A"
RED = "#DC2626"

GLOBAL_STYLE = f"""
QMainWindow, QWidget {{
    background-color: {BG};
    color: {TEXT};
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 10pt;
}}

QLineEdit, QComboBox, QDoubleSpinBox {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 4px 6px;
}}
QLineEdit:focus {{ border: 1px solid {BLUE}; }}
QLineEdit:disabled {{ background: #E2E8F0; color: {MUTED}; }}

QPushButton {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 5px 10px;
}}
QPushButton:hover {{ border-color: {BLUE}; }}
QPushButton:pressed {{ background: #E2E8F0; }}
QPushButton:disabled {{ color: {MUTED}; background: #E2E8F0; }}

QPushButton#runButton {{
    background: {BLUE};
    color: white;
    border: none;
    font-weight: 600;
    padding: 8px 12px;
}}
QPushButton#runButton:hover {{ background: {BLUE_DARK}; }}
QPushButton#runButton:disabled {{ background: #94A3B8; }}

QPushButton#removeButton {{
    border: none;
    background: transparent;
    color: {RED};
    font-weight: 700;
}}

QTableWidget {{
    background: {PANEL};
    border: 1px solid {BORDER};
    gridline-color: #E2E8F0;
}}
QHeaderView::section {{
    background: #E2E8F0;
    border: none;
    border-right: 1px solid {BORDER};
    padding: 4px;
    font-weight: 600;
}}

QTabWidget::pane {{ border: 1px solid {BORDER}; background: {PANEL}; }}
QTabBar::tab {{
    background: #E2E8F0;
    padding: 8px 16px;
    border: 1px solid {BORDER};
    border-bottom: none;
}}
QTabBar::tab:selected {{ background: {PANEL}; color: {BLUE}; font-weight: 600; }}
QTabBar::tab:hover:!selected {{ background: #F1F5F9; }}

QStatusBar {{ background: {NAVY}; color: white; }}
QMenuBar {{ background: {PANEL}; }}
QMenuBar::item:selected {{ background: #E2E8F0; }}

QToolTip {{
    background: {NAVY}; color: white; border: none; padding: 4px;
}}

QMessageBox QLabel {{
    color: {TEXT};
    background: transparent;
}}
"""

SIDEBAR_STYLE = f"""
QWidget#sidebar {{
    background-color: {NAVY};
}}
QWidget#sidebar QLabel {{
    color: #E2E8F0;
    background: transparent;
}}
QWidget#sidebar QLabel#logo {{
    color: white;
    font-size: 18pt;
    font-weight: 700;
}}
QWidget#sidebar QGroupBox {{
    background: transparent;
    color: #E2E8F0;
    font-weight: 600;
    border: 1px solid #3B5280;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 8px;
}}
QWidget#sidebar QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}}
QWidget#sidebar QCheckBox {{
    color: #E2E8F0;
    background: transparent;
}}
QWidget#sidebar QPushButton[flat="true"] {{
    background: transparent;
    border: none;
    color: #93C5FD;
    text-align: left;
}}
QWidget#sidebar QPushButton[flat="true"]:hover {{
    color: white;
}}
QWidget#sidebar QLineEdit, QWidget#sidebar QTableWidget {{
    background: white;
    color: {TEXT};
}}
"""