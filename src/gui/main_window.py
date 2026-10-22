# import sys
# sys.path.append("./src")
# from caffe import caffe  # NOQA

"""Main Application Window"""

import os

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from .tabs import InputDEMTab, SatelliteTab, MaxWaterDepthTab, WaterLevelTab, WaterDepthTab
from .sidebar import Sidebar
from .worker import SimulationWorker
from .theme import GLOBAL_STYLE, SIDEBAR_STYLE


class MainWindow(QMainWindow):
    """Main application window for the Dynamic CA-ffe GUI"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CAFFE — Cellular Automaton Flood Flow Emulator")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        self.setStyleSheet(GLOBAL_STYLE)

        self.last_outputs = None     # paths of the most recent run's rasters
        self._satellite_on = False   # current state of the sidebar's satellite toggle

        self._setup_ui()
        self._setup_menu()
        self.statusBar().showMessage("Not connected — configure and export")

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._create_sidebar()
        self._create_tabs()

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.tabs, 1)

    def _create_sidebar(self):
        # Persistent configuration panel — not a tab switcher.
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(350)

        self.sidebar.setStyleSheet(SIDEBAR_STYLE)

        layout = QVBoxLayout(self.sidebar)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(6)

        self.logo_label = QLabel("CAFFE")
        self.logo_label.setObjectName("logo")
        layout.addWidget(self.logo_label)
        layout.addSpacing(12)

        # Sidebar content (file pickers, parameter fields, EV/BC tables,
        # Run button) is built by a dedicated controller populating this
        # container — same pattern as CorroSim's per-tab .setup() calls.
        
        self.sidebar_controller = Sidebar()
        self.sidebar_controller.setup(
            parent=self.sidebar,
            layout=layout,
            run_callback=self._run_simulation,
            preview_callback=self._preview_dem,
        )

    def _create_tabs(self):
        # Visible tab bar. Unlike CorroSim, these are independent raster
        # views, not app sections driven by the sidebar.
        self.tabs = QTabWidget()

        self.input_dem_widget = QWidget()
        self.satellite_widget = QWidget()
        self.mwd_widget = QWidget()
        self.wl_widget = QWidget()
        self.wd_widget = QWidget()

        self.tabs.addTab(self.input_dem_widget, "Input DEM")
        self.tabs.addTab(self.satellite_widget, "Satellite")
        self.tabs.addTab(self.mwd_widget, "Max Water Depth")
        self.tabs.addTab(self.wl_widget, "Water Level")
        self.tabs.addTab(self.wd_widget, "Water Depth")

        self.input_dem_tab = InputDEMTab()
        self.input_dem_tab.setup(parent=self.input_dem_widget)

        self.satellite_tab = SatelliteTab()
        self.satellite_tab.setup(parent=self.satellite_widget)

        self.mwd_tab = MaxWaterDepthTab()
        self.mwd_tab.setup(parent=self.mwd_widget)

        self.wl_tab = WaterLevelTab()
        self.wl_tab.setup(parent=self.wl_widget)

        self.wd_tab = WaterDepthTab()
        self.wd_tab.setup(parent=self.wd_widget)

    def _preview_dem(self, dem_path, satellite=False):
        """Called by the sidebar when the DEM/output folder is set or the satellite toggle changes."""
        new_dem = dem_path != getattr(self, "_previewed_dem", None)
        self._satellite_on = satellite

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)  # tile download can take a moment
        try:
            dem_warning = self.input_dem_tab.show_dem(dem_path, basemap=satellite)
        except Exception as e:
            QApplication.restoreOverrideCursor()
            self.statusBar().showMessage(f"Could not preview DEM: {e}")
            QMessageBox.critical(self, "DEM Preview Error", str(e))
            return False

        sat_warning = None
        if satellite:
            # A satellite failure (e.g. offline) is non-fatal, so no error dialog
            try:
                sat_warning = self.satellite_tab.show_satellite(dem_path)
            except Exception as e:
                sat_warning = f"Satellite view failed: {e}"
        else:
            self.satellite_tab.clear()

        # Keep the result tabs in step with the toggle. Skipped when a new DEM was just
        # loaded, since the old outputs don't belong to it.
        output_warnings = []
        if not new_dem and self.last_outputs:
            output_warnings = self._show_outputs(self.last_outputs, satellite)
        QApplication.restoreOverrideCursor()

        self._previewed_dem = dem_path
        if new_dem:
            self.tabs.setCurrentIndex(0)  # jump to Input DEM only when a new DEM is loaded

        warnings = [w for w in (dem_warning, sat_warning, *output_warnings) if w]
        self.statusBar().showMessage(" | ".join(warnings) if warnings else f"Previewing DEM: {dem_path}")
        return True

    def _run_simulation(self, config):
        """Called by the sidebar's Run button: start the simulation on a worker thread."""
        self.sidebar_controller.set_running(True)
        self.statusBar().showMessage("Running simulation...")

        # Keep a reference on self, otherwise the thread can be garbage-collected mid-run
        self.worker = SimulationWorker(config, self)
        self.worker.succeeded.connect(self._on_run_succeeded)
        self.worker.failed.connect(self._on_run_failed)
        self.worker.start()

    def _on_run_succeeded(self, outputs):
        self.sidebar_controller.set_running(False)
        self.last_outputs = outputs

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)  # tiles may need downloading
        warnings = self._show_outputs(outputs, self._satellite_on)
        QApplication.restoreOverrideCursor()

        self.tabs.setCurrentWidget(self.mwd_widget)  # jump to the headline result

        message = "Simulation completed successfully."
        if warnings:
            message += " " + " | ".join(warnings)
        self.statusBar().showMessage(message)

    def _on_run_failed(self, message):
        self.sidebar_controller.set_running(False)
        self.statusBar().showMessage(f"Simulation failed: {message}")
        QMessageBox.critical(self, "Simulation Error", message)
 

    def _setup_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _show_outputs(self, outputs, satellite):
        """Draw the three result tabs (with or without the satellite basemap). Returns warnings."""
        warnings = []
        for tab, key in ((self.mwd_tab, "mwd"), (self.wl_tab, "wl"), (self.wd_tab, "wd")):
            try:
                warning = tab.show_output(outputs[key], basemap=satellite)
                if warning:
                    warnings.append(warning)
            except Exception as e:
                warnings.append(f"Could not display {key}: {e}")
        return warnings
    
    def _show_about(self):
        QMessageBox.about(
            self,
            "About CAFFE GUI",
            "<h3>CAFFE — Cellular Automaton Flood Flow Emulator</h3>"
            "<p>GUI front-end for the Dynamic CA-ffé flood modelling framework.</p>",
        )

    def closeEvent(self, event):
        # Closing mid-run: stop the model process instead of leaving it running
        worker = getattr(self, "worker", None)
        if worker is not None and worker.isRunning():
            worker.cancel()
        event.accept()