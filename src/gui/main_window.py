# import sys
# sys.path.append("./src")
# from caffe import caffe  # NOQA

"""Main Application Window"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from .tabs import InputDEMTab, SatelliteTab, MaxWaterDepthTab, WaterLevelTab, WaterDepthTab
from .sidebar import Sidebar


class MainWindow(QMainWindow):
    """Main application window for the Dynamic CA-ffe GUI"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CAFFE — Cellular Automaton Flood Flow Emulator")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        # No stylesheet applied yet. A theme.py (GLOBAL_STYLE / DARK_STYLE)
        # can be added later and applied here via self.setStyleSheet(...),
        # following the same pattern CorroSim uses.

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

        layout = QVBoxLayout(self.sidebar)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(6)

        self.logo_label = QLabel("CAFFE")
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
        """Called by the sidebar's Preview button: draw the DEM and its satellite view."""
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)  # tile download can take a moment
        try:
            dem_warning = self.input_dem_tab.show_dem(dem_path, basemap=satellite)
        except Exception as e:
            QApplication.restoreOverrideCursor()
            self.statusBar().showMessage(f"Could not preview DEM: {e}")
            QMessageBox.critical(self, "DEM Preview Error", str(e))
            return

        # A satellite failure (e.g. offline) is non-fatal, so no error dialog
        try:
            sat_warning = self.satellite_tab.show_satellite(dem_path)
        except Exception as e:
            sat_warning = f"Satellite view failed: {e}"
        QApplication.restoreOverrideCursor()

        self.tabs.setCurrentIndex(0)
        warnings = [w for w in (dem_warning, sat_warning) if w]
        self.statusBar().showMessage(" | ".join(warnings) if warnings else f"Previewing DEM: {dem_path}")

    def _run_simulation(self, config):
        """
        Called by the sidebar's Run Simulation button.
        `config` is a dict of validated inputs the sidebar collects
        (DEM path, output dir/name, parameters, EV/BC arrays).
        Actual backend execution belongs in a separate QThread worker,
        not here — see the multithreading pattern from earlier.
        """
        import numpy as np
        from caffe import caffe

        self.statusBar().showMessage("Running simulation...")
        # TODO: hand off `config` to a SimulationWorker(QThread), connect
        # its signals to update statusBar() and refresh the tabs once
        # outputs are written.

        try:
            sim = caffe(config["dem_path"])
            sim.setConstants(
                config["hf"],
                config["increment_constant"],
                config["ev_threshold"],
            )

            ev_array = np.array(
                [[int(r), int(c), float(v)] for r, c, v in config["ev_sources"]]
            )
            sim.ExcessVolumeArray(ev_array)

            bc_array = np.array(
                [[int(r), int(c)] for r, c in config["boundaries"]]
            )
            sim.OpenBCArray(bc_array)

            sim.RunSimulation()
            sim.setOutputPath(config["output_dir"])
            sim.setOutputName(config["output_name"])
            sim.CloseSimulation()

            self.statusBar().showMessage("Simulation completed successfully.")

        except Exception as e:
            self.statusBar().showMessage(f"Simulation failed: {e}")
            QMessageBox.critical(self, "Simulation Error", str(e))
 

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

    def _show_about(self):
        QMessageBox.about(
            self,
            "About CAFFE GUI",
            "<h3>CAFFE — Cellular Automaton Flood Flow Emulator</h3>"
            "<p>GUI front-end for the Dynamic CA-ffé flood modelling framework.</p>",
        )

    def closeEvent(self, event):
        event.accept()