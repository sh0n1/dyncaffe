"""Satellite imagery tab: shows the satellite view of the DEM's footprint by itself."""

import math
import rasterio
from .base_tab import BaseRasterTab


class SatelliteTab(BaseRasterTab):
    def __init__(self):
        super().__init__(title="Satellite", subtitle="Click 'Show satellite' to load imagery")

    def show_satellite(self, dem_path):
        """Draw satellite imagery covering the DEM's footprint (no DEM data drawn).

        Returns a warning string if the imagery could not be drawn, else None.
        """
        with rasterio.open(dem_path) as src:
            bounds = src.bounds
            crs = src.crs
            inverse_transform = ~src.transform

        if crs is None:
            self._show_message("DEM has no CRS, so satellite imagery can't be placed.")
            return "DEM has no CRS, so the satellite view was skipped."

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        # add_basemap fetches tiles for whatever extent the axes currently show
        ax.set_xlim(bounds.left, bounds.right)
        ax.set_ylim(bounds.bottom, bounds.top)

        try:
            import contextily as cx
            cx.add_basemap(ax, crs=crs, source=cx.providers.Esri.WorldImagery)
        except Exception as e:
            self._show_message(f"Satellite imagery unavailable.\n{e}")
            return f"Satellite imagery unavailable ({e})."

        def format_coord(x, y):
            col, row = inverse_transform * (x, y)
            return f"row={math.floor(row)}, col={math.floor(col)}"

        ax.format_coord = format_coord  # hover readout in DEM row/col
        ax.set_xlabel("Easting" if crs.is_projected else "Longitude")
        ax.set_ylabel("Northing" if crs.is_projected else "Latitude")
        ax.set_title("Satellite view")

        self._add_rowcol_axes(ax, inverse_transform)

        self.canvas.draw_idle()
        return None

    def _show_message(self, text):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.axis("off")
        ax.text(0.5, 0.5, text, ha="center", va="center", wrap=True,
                transform=ax.transAxes)
        self.canvas.draw_idle()