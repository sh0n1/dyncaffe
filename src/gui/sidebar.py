"""Sidebar controller — configuration panel for the CAFFE GUI"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *


class Sidebar:
    """Builds and manages the configuration sidebar: file I/O, model
    parameters, EV sources, open boundaries, and run controls."""

    def setup(self, parent, layout, run_callback):
        self.parent = parent
        self.layout = layout
        self.run_callback = run_callback

        self._build_file_io_section()
        self._build_parameters_section()
        self._build_ev_sources_section()
        self._build_boundaries_section()
        self._build_run_controls()

    # ------------------------------------------------------------------
    # File I/O
    # ------------------------------------------------------------------
    def _build_file_io_section(self):
        group = QGroupBox("File I/O")
        form = QFormLayout(group)

        self.dem_path_edit = QLineEdit()
        dem_browse_btn = QPushButton("📁")
        dem_browse_btn.clicked.connect(self._browse_dem)
        dem_row = QHBoxLayout()
        dem_row.addWidget(self.dem_path_edit)
        dem_row.addWidget(dem_browse_btn)
        form.addRow("Input DEM", dem_row)

        self.output_dir_edit = QLineEdit()
        output_browse_btn = QPushButton("📁")
        output_browse_btn.clicked.connect(self._browse_output_dir)
        output_row = QHBoxLayout()
        output_row.addWidget(self.output_dir_edit)
        output_row.addWidget(output_browse_btn)
        form.addRow("Output Directory", output_row)

        self.output_name_edit = QLineEdit("serial")
        form.addRow("Output Name", self.output_name_edit)

        self.layout.addWidget(group)

    def _browse_dem(self):
        path, _ = QFileDialog.getOpenFileName(
            self.parent, "Select DEM file", "", "GeoTIFF Files (*.tif *.tiff)"
        )
        if path:
            self.dem_path_edit.setText(path)
            # TODO: trigger DEM preview load + validation (size warning, etc.)

    def _browse_output_dir(self):
        path = QFileDialog.getExistingDirectory(self.parent, "Select Output Directory")
        if path:
            self.output_dir_edit.setText(path)

    # ------------------------------------------------------------------
    # Model parameters
    # ------------------------------------------------------------------
    def _build_parameters_section(self):
        group = QGroupBox("Model Parameters")
        form = QFormLayout(group)

        self.hf_edit = QLineEdit("0.09")
        self.hf_edit.setValidator(QDoubleValidator())
        form.addRow("hf — Friction Factor", self.hf_edit)

        self.increment_constant_edit = QLineEdit("1e-4")
        self.increment_constant_edit.setValidator(QDoubleValidator())
        form.addRow("Increment Constant (Δ)", self.increment_constant_edit)

        self.ev_threshold_edit = QLineEdit("1e-5")
        self.ev_threshold_edit.setValidator(QDoubleValidator())
        form.addRow("EV Convergence Threshold", self.ev_threshold_edit)

        self.layout.addWidget(group)

    # ------------------------------------------------------------------
    # Excess volume sources
    # ------------------------------------------------------------------
    def _build_ev_sources_section(self):
        group = QGroupBox("Excess Volume Sources")
        vbox = QVBoxLayout(group)

        self.ev_table = QTableWidget(0, 3)
        self.ev_table.setHorizontalHeaderLabels(["Row", "Col", "Vol (m³)"])
        vbox.addWidget(self.ev_table)

        add_btn = QPushButton("+ add source")
        add_btn.setFlat(True)
        add_btn.clicked.connect(lambda: self._add_table_row(self.ev_table, ["", "", ""], removable=True))
        vbox.addWidget(add_btn)

        # Prefill with your known test case values
        self._add_table_row(self.ev_table, ["499", "499", "2000"])

        self.layout.addWidget(group)

    # ------------------------------------------------------------------
    # Open boundaries
    # ------------------------------------------------------------------
    def _build_boundaries_section(self):
        group = QGroupBox("Open Boundaries")
        vbox = QVBoxLayout(group)

        self.bc_table = QTableWidget(0, 2)
        self.bc_table.setHorizontalHeaderLabels(["Row", "Col", ""])
        vbox.addWidget(self.bc_table)

        add_btn = QPushButton("+ add boundary")
        add_btn.setFlat(True)
        add_btn.clicked.connect(lambda: self._add_table_row(self.bc_table, ["", ""], removable=True))
        vbox.addWidget(add_btn)

        self._add_table_row(self.bc_table, ["300", "300"], removable=True)

        self.layout.addWidget(group)

    # ------------------------------------------------------------------
    # Shared table helper
    # ------------------------------------------------------------------
    def _add_table_row(self, table, values, removable=False):
        row = table.rowCount()
        table.insertRow(row)
        for col, value in enumerate(values):
            table.setItem(row, col, QTableWidgetItem(str(value)))

        if removable:
            remove_btn = QPushButton("✕")
            remove_btn.setFlat(True)
            remove_btn.clicked.connect(lambda: self._remove_table_row(table, remove_btn))
            table.setCellWidget(row, len(values), remove_btn)

    def _remove_table_row(self, table, button):
        for row in range(table.rowCount()):
            if table.cellWidget(row, table.columnCount() - 1) is button:
                table.removeRow(row)
                break

    # ------------------------------------------------------------------
    # Run controls
    # ------------------------------------------------------------------
    def _build_run_controls(self):
        row = QHBoxLayout()

        self.run_btn = QPushButton("▶ Run Simulation")
        self.run_btn.clicked.connect(self._on_run_clicked)
        row.addWidget(self.run_btn, 1)

        reset_btn = QPushButton("⟲")
        reset_btn.clicked.connect(self._reset)
        row.addWidget(reset_btn)

        self.layout.addLayout(row)

    def _on_run_clicked(self):
        # TODO: run validate() here first and show a QMessageBox /
        # inline warnings before calling run_callback, per your
        # input-validation user stories.
        config = self.get_config()
        self.run_callback(config)

    def _reset(self):
        # TODO: clear/reset all fields to defaults
        pass

    # ------------------------------------------------------------------
    # Config collection
    # ------------------------------------------------------------------
    def get_config(self):
        """Collects all sidebar field values into a dict for the
        MainWindow's run callback / eventual SimulationWorker."""
        return {
            "dem_path": self.dem_path_edit.text(),
            "output_dir": self.output_dir_edit.text(),
            "output_name": self.output_name_edit.text(),
            "hf": float(self.hf_edit.text()),
            "increment_constant": float(self.increment_constant_edit.text()),
            "ev_threshold": float(self.ev_threshold_edit.text()),
            "ev_sources": self._read_table(self.ev_table, data_cols=3),
            "boundaries": self._read_table(self.bc_table, data_cols=2),
        }

    def _read_table(self, table, data_cols):
        """Reads back only the actual data columns — explicit, not inferred."""
        rows = []
        for r in range(table.rowCount()):
            row_vals = []
            for c in range(data_cols):
                item = table.item(r, c)
                row_vals.append(item.text() if item else "")
            rows.append(row_vals)
        return rows
    
