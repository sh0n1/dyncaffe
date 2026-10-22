"""Shared skeleton for raster-display tabs (Input DEM, MWD, WL, WD)."""

import math

import rasterio
import numpy as np

from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure

MAX_PREVIEW_PIXELS = 2000  # longest side of the displayed raster, in cells


class BaseRasterTab(QWidget):
    def __init__(self, title, subtitle):
        super().__init__()
        self._title = title
        self._subtitle = subtitle

    def setup(self, parent):
        layout = QVBoxLayout(parent)

        self.figure = Figure(layout="constrained")
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, parent)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self._show_placeholder()

    def _show_placeholder(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.axis("off")
        ax.text(0.5, 0.55, self._title, ha="center", va="center",
                fontsize=16, transform=ax.transAxes)
        ax.text(0.5, 0.45, self._subtitle, ha="center", va="center",
                fontsize=10, transform=ax.transAxes)
        self.canvas.draw_idle()

    def show_raster(self, path, cmap="viridis", cbar_label="", title=None,
                    basemap=False, mask_below=None):
        """Read band 1 of a GeoTIFF and draw it with a colourbar.

        Without a basemap, axes are full-resolution row/column indices.
        With a basemap, axes must be map coordinates so the satellite tiles
        line up, but the toolbar readout still shows row/col under the cursor.

        Returns a warning string if the basemap could not be drawn, else None.
        """
        with rasterio.open(path) as src:
            full_h, full_w = src.height, src.width
            scale = max(full_h, full_w) / MAX_PREVIEW_PIXELS
            if scale > 1:
                out_shape = (int(full_h / scale), int(full_w / scale))
            else:
                out_shape = (full_h, full_w)
            data = src.read(1, out_shape=out_shape, masked=True)  # nodata masked out
            bounds = src.bounds
            crs = src.crs
            inverse_transform = ~src.transform

        if mask_below is not None:
            # Hide dry cells so only flooded cells are coloured
            data = np.ma.masked_less_equal(data, mask_below)
            if data.count() == 0:
                self.figure.clear()
                ax = self.figure.add_subplot(111)
                ax.axis("off")
                ax.text(0.5, 0.5, "No water above the threshold in this output",
                        ha="center", va="center", transform=ax.transAxes)
                self.canvas.draw_idle()
                return None

        warning = None
        if basemap and crs is None:
            warning = "Raster has no CRS, so the satellite basemap was skipped."
            basemap = False

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if basemap:
            extent = (bounds.left, bounds.right, bounds.bottom, bounds.top)
            # zorder=2 keeps the DEM above the satellite tiles
            im = ax.imshow(data, cmap=cmap, extent=extent, alpha=0.65, zorder=2)
            try:
                import contextily as cx
                cx.add_basemap(ax, crs=crs, source=cx.providers.Esri.WorldImagery, attribution="Imagery © Esri", attribution_size=7)
            except Exception as e:
                im.set_alpha(1.0)
                warning = f"Satellite basemap unavailable ({e}). Showing DEM only."

            def format_coord(x, y):
                col, row = inverse_transform * (x, y)
                return f"row={math.floor(row)}, col={math.floor(col)}"

            ax.format_coord = format_coord
            ax.set_xlabel("Easting" if crs.is_projected else "Longitude")
            ax.set_ylabel("Northing" if crs.is_projected else "Latitude")
        else:
            im = ax.imshow(data, cmap=cmap, extent=(0, full_w, full_h, 0))
            ax.set_xlabel("Column")
            ax.set_ylabel("Row")

        cbar = self.figure.colorbar(im, ax=ax)
        cbar.set_label(cbar_label)
        ax.set_title(title or self._title)
        self.canvas.draw_idle()
        return warning

    def _add_rowcol_axes(self, ax, transform, grid=True):
        """Add Column (top) and Row (right) axes to a map drawn in CRS coordinates.
        Assumes a north-up raster (no rotation)."""
        a, c, e, f = transform.a, transform.c, transform.e, transform.f

        col_ax = ax.secondary_xaxis(
            "top", functions=(lambda x: (x - c) / a, lambda col: col * a + c))
        row_ax = ax.secondary_yaxis(
            "right", functions=(lambda y: (y - f) / e, lambda row: row * e + f))

        col_ax.set_xlabel("Column")
        row_ax.set_ylabel("Row")

        if grid:
            col_ax.grid(True, color="white", alpha=0.35, linewidth=0.6, linestyle="--")
            row_ax.grid(True, color="white", alpha=0.35, linewidth=0.6, linestyle="--")
            
    def clear(self):
        """Reset the tab to its placeholder text."""
        self._show_placeholder()