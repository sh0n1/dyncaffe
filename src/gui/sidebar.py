"""Sidebar controller — configuration panel for the CAFFE GUI"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

import math
import os

import numpy as np
import rasterio
from rasterio.windows import Window

class Sidebar:
    """Builds and manages the configuration sidebar: file I/O, model
    parameters, EV sources, open boundaries, and run controls."""

    DEFAULTS = {
        "output_name": "serial",
        "hf": "0.09",
        "increment_constant": "1e-4",
        "ev_threshold": "1e-5",
        "ev_sources": [["499", "499", "2000"]],
        "boundaries": [["300", "300"]],
    }

    def setup(self, parent, layout, run_callback, preview_callback):
        self.parent = parent
        self.layout = layout
        self.run_callback = run_callback
        self.preview_callback = preview_callback

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
        self._last_preview = None  # (dem_path, satellite_on) of the last drawn preview

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

        self.output_name_edit = QLineEdit(self.DEFAULTS["output_name"])
        form.addRow("Output Name", self.output_name_edit)

        self.satellite_btn = QPushButton("Show satellite")
        self.satellite_btn.setCheckable(True)
        self.satellite_btn.setToolTip("Select an input DEM and an output directory first (needs internet)")
        self.satellite_btn.toggled.connect(self._on_satellite_toggled)
        form.addRow(self.satellite_btn)

        # The DEM preview now draws automatically once both fields are set
        self.dem_path_edit.textChanged.connect(self._update_satellite_enabled)
        self.output_dir_edit.textChanged.connect(self._update_satellite_enabled)
        self.dem_path_edit.editingFinished.connect(self._refresh_preview)
        self.output_dir_edit.editingFinished.connect(self._refresh_preview)
        self._update_satellite_enabled()

        self.layout.addWidget(group)

    def _browse_dem(self):
        path, _ = QFileDialog.getOpenFileName(
            self.parent, "Select DEM file", "", "GeoTIFF Files (*.tif *.tiff)"
        )
        if path:
            self.dem_path_edit.setText(path)
            self._refresh_preview()
            # TODO: DEM size warning (large rasters should be cropped)

    def _browse_output_dir(self):
        path = QFileDialog.getExistingDirectory(self.parent, "Select Output Directory")
        if path:
            self.output_dir_edit.setText(path)
            self._refresh_preview()

    def _update_satellite_enabled(self):
        """The toggle (and the auto-preview) need both a DEM and an output directory."""
        ready = bool(self.dem_path_edit.text().strip()) and bool(self.output_dir_edit.text().strip())
        self.satellite_btn.setEnabled(ready)

    def _on_satellite_toggled(self, checked):
        self.satellite_btn.setText("Hide satellite" if checked else "Show satellite")
        self._refresh_preview()

    def _refresh_preview(self):
        """Redraw the preview, but only if the DEM or the satellite state actually changed."""
        dem = self.dem_path_edit.text().strip()
        out = self.output_dir_edit.text().strip()
        if not dem or not out:
            return
        key = (dem, self.satellite_btn.isChecked())
        if key == self._last_preview:
            return
        self._last_preview = key
        if self.preview_callback(*key) is False:  # failed to draw, so allow a retry
            self._last_preview = None

    # ------------------------------------------------------------------
    # Model parameters
    # ------------------------------------------------------------------
    def _build_parameters_section(self):
        group = QGroupBox("Model Parameters")
        form = QFormLayout(group)

        self.hf_edit = QLineEdit(self.DEFAULTS["hf"])
        self.hf_edit.setValidator(QDoubleValidator())
        form.addRow("hf — Friction Factor", self.hf_edit)

        self.increment_constant_edit = QLineEdit(self.DEFAULTS["increment_constant"])
        self.increment_constant_edit.setValidator(QDoubleValidator())
        form.addRow("Increment Constant (Δ)", self.increment_constant_edit)

        self.ev_threshold_edit = QLineEdit(self.DEFAULTS["ev_threshold"])
        self.ev_threshold_edit.setValidator(QDoubleValidator())
        form.addRow("EV Convergence Threshold", self.ev_threshold_edit)

        self.layout.addWidget(group)

    # ------------------------------------------------------------------
    # Excess volume sources
    # ------------------------------------------------------------------
    def _make_table(self, headers):
        """Table with the data columns plus one dedicated column for the remove button."""
        table = QTableWidget(0, len(headers) + 1)
        table.setHorizontalHeaderLabels(headers + [""])
        table.verticalHeader().setVisible(False)

        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(len(headers), QHeaderView.ResizeMode.ResizeToContents)
        return table
    
    def _build_ev_sources_section(self):
        group = QGroupBox("Excess Volume Sources")
        vbox = QVBoxLayout(group)

        self.ev_table = self._make_table(["Row", "Col", "Vol (m³)"])
        vbox.addWidget(self.ev_table)

        add_btn = QPushButton("+ add source")
        add_btn.setFlat(True)
        add_btn.clicked.connect(lambda: self._add_table_row(self.ev_table, ["", "", ""]))
        vbox.addWidget(add_btn)

        # default EV sources
        for values in self.DEFAULTS["ev_sources"]:
            self._add_table_row(self.ev_table, list(values))

        self.layout.addWidget(group)

    # ------------------------------------------------------------------
    # Open boundaries
    # ------------------------------------------------------------------
    def _build_boundaries_section(self):
        group = QGroupBox("Open Boundaries")
        vbox = QVBoxLayout(group)

        self.bc_table = self._make_table(["Row", "Col"])
        vbox.addWidget(self.bc_table)

        add_btn = QPushButton("+ add boundary")
        add_btn.setFlat(True)
        add_btn.clicked.connect(lambda: self._add_table_row(self.bc_table, ["", ""]))
        vbox.addWidget(add_btn)

        for values in self.DEFAULTS["boundaries"]:
            self._add_table_row(self.bc_table, list(values))

        self.layout.addWidget(group)

    # ------------------------------------------------------------------
    # Shared table helper
    # ------------------------------------------------------------------
    def _add_table_row(self, table, values):
        row = table.rowCount()
        table.insertRow(row)
        for col, value in enumerate(values):
            table.setItem(row, col, QTableWidgetItem(str(value)))

        remove_btn = QPushButton("X")
        remove_btn.setObjectName("removeButton")

        remove_btn.setFlat(True)
        remove_btn.setToolTip("Remove this row")
        remove_btn.clicked.connect(lambda: self._remove_table_row(table, remove_btn))
        table.setCellWidget(row, table.columnCount() - 1, remove_btn)

        self._update_remove_buttons(table)

    def _remove_table_row(self, table, button):
        if table.rowCount() <= 1:  # safety guard: always keep at least one row
            return
        last_col = table.columnCount() - 1
        for row in range(table.rowCount()):
            if table.cellWidget(row, last_col) is button:
                table.removeRow(row)
                break
        self._update_remove_buttons(table)

    def _update_remove_buttons(self, table):
        """Remove buttons only appear when there is more than one row."""
        last_col = table.columnCount() - 1
        show = table.rowCount() > 1
        for row in range(table.rowCount()):
            btn = table.cellWidget(row, last_col)
            if btn is not None:
                btn.setVisible(show)

    # ------------------------------------------------------------------
    # Run controls
    # ------------------------------------------------------------------
    def _build_run_controls(self):
        row = QHBoxLayout()

        self.run_btn = QPushButton("▶ Run Simulation")
        self.run_btn.setObjectName("runButton")
        self.run_btn.clicked.connect(self._on_run_clicked)
        row.addWidget(self.run_btn, 1)

        self.reset_btn = QPushButton("⟲")
        self.reset_btn.setToolTip("Reset parameters to defaults")
        self.reset_btn.clicked.connect(self._reset)
        row.addWidget(self.reset_btn)

        self.layout.addLayout(row)

    def validate(self):
        import os
        """Return a list of problems with the current inputs (empty list = OK)."""
        problems = []

        if not os.path.isfile(self.dem_path_edit.text().strip()):
            problems.append("Input DEM: file not found.")

        if not os.path.isdir(self.output_dir_edit.text().strip()):
            problems.append("Output directory: folder not found.")

        try:
            float(self.hf_edit.text())
        except ValueError:
            problems.append("hf: must be a number.")

        return problems
    
    def _on_run_clicked(self):
        problems = self.validate()
        if problems:
            shown = problems[:10]
            text = "\n".join(f"• {p}" for p in shown)
            if len(problems) > len(shown):
                text += f"\n…and {len(problems) - len(shown)} more."
            QMessageBox.warning(self.parent.window(), "Check your inputs", text)
            return

        config = self.get_config() 
        self.run_callback(config)

    def _reset(self):
        """Restore model parameters, EV sources, boundaries and output name to defaults.
        The input DEM and output directory are left alone."""
        d = self.DEFAULTS
        self.output_name_edit.setText(d["output_name"])
        self.hf_edit.setText(d["hf"])
        self.increment_constant_edit.setText(d["increment_constant"])
        self.ev_threshold_edit.setText(d["ev_threshold"])

        for table, rows in ((self.ev_table, d["ev_sources"]),
                            (self.bc_table, d["boundaries"])):
            table.setRowCount(0)
            for values in rows:
                self._add_table_row(table, list(values))

    def set_running(self, running):
        """Disable the Run button while a simulation is in progress."""
        self.run_btn.setEnabled(not running)
        self.run_btn.setText("Running..." if running else "▶ Run Simulation")

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    def validate(self):
        """Check every input before a run. Returns a list of problems (empty list = OK)."""
        problems = []
        dem_path = self.dem_path_edit.text().strip()

        src = self._open_dem(dem_path, problems)
        try:
            self._check_output_settings(problems)
            self._check_parameters(problems)
            self._check_cells(problems, "EV source", self._read_table(self.ev_table, 3), src, has_volume=True)
            self._check_cells(problems, "Open boundary", self._read_table(self.bc_table, 2), src, has_volume=False)
        finally:
            if src is not None:
                src.close()
        return problems

    def _open_dem(self, dem_path, problems):
        """Open the DEM for the cell checks. Returns the dataset, or None (with a problem recorded)."""
        if not dem_path:
            problems.append("Input DEM: no file selected.")
            return None
        if not os.path.isfile(dem_path):
            problems.append("Input DEM: file not found.")
            return None
        try:
            return rasterio.open(dem_path)
        except Exception as e:
            problems.append(f"Input DEM: could not be opened as a raster ({e}).")
            return None

    def _check_output_settings(self, problems):
        out_dir = self.output_dir_edit.text().strip()
        if not out_dir:
            problems.append("Output directory: no folder selected.")
        elif not os.path.isdir(out_dir):
            problems.append("Output directory: folder not found.")
        elif not os.access(out_dir, os.W_OK):
            problems.append("Output directory: folder is not writable.")

        name = self.output_name_edit.text().strip()
        if not name:
            problems.append("Output name: cannot be blank.")
        elif any(ch in name for ch in '<>:"/\\|?*'):
            problems.append('Output name: cannot contain any of < > : " / \\ | ? *')

    def _check_parameters(self, problems):
        params = (
            ("hf", self.hf_edit),
            ("Increment constant", self.increment_constant_edit),
            ("EV convergence threshold", self.ev_threshold_edit),
        )
        for label, edit in params:
            try:
                value = float(edit.text())
                if not math.isfinite(value) or value <= 0:
                    raise ValueError
            except ValueError:
                problems.append(f"{label}: must be a number greater than 0.")

    def _check_cells(self, problems, label, rows, src, has_volume):
        """Check each EV source / boundary row: whole-number cell, inside the DEM, not nodata."""
        if not rows:
            problems.append(f"{label}s: at least one is required.")
            return

        for i, vals in enumerate(rows, start=1):
            name = f"{label} {i}"

            cell = None
            try:
                cell = (int(vals[0]), int(vals[1]))
            except ValueError:
                problems.append(f"{name}: row and column must be whole numbers.")

            if has_volume:
                try:
                    volume = float(vals[2])
                    if not math.isfinite(volume) or volume <= 0:
                        raise ValueError
                except ValueError:
                    problems.append(f"{name}: volume must be a number greater than 0.")

            if cell is None or src is None:
                continue  # nothing more to check without a valid cell and a readable DEM

            r, c = cell
            if not (0 <= r < src.height and 0 <= c < src.width):
                problems.append(
                    f"{name}: cell ({r}, {c}) is outside the DEM "
                    f"(rows 0-{src.height - 1}, columns 0-{src.width - 1})."
                )
                continue

            pixel = np.ma.masked_invalid(src.read(1, window=Window(c, r, 1, 1), masked=True))
            if np.ma.is_masked(pixel):
                problems.append(f"{name}: cell ({r}, {c}) has no elevation data (nodata).")
    
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
    
