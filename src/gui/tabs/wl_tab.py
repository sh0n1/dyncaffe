from .base_tab import BaseRasterTab


class WaterLevelTab(BaseRasterTab):
    def __init__(self):
        super().__init__(title="Water Level", subtitle="Choose a water level file to preview")

    def show_output(self, path, basemap=False):
        return self.show_raster(path, cmap="terrain", cbar_label="Water level (m)",
                                title="Water Level", basemap=basemap)