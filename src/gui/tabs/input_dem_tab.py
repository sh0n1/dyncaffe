from .base_tab import BaseRasterTab


class InputDEMTab(BaseRasterTab):
    def __init__(self):
        super().__init__(title="Input DEM", subtitle="Load a DEM file to preview")

    def show_dem(self, path, basemap=False):
        return self.show_raster(path, cmap="terrain", cbar_label="Elevation (m)",
                                title="Input DEM", basemap=basemap)