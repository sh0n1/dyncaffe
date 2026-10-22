from .base_tab import BaseRasterTab


class WaterDepthTab(BaseRasterTab):
    def __init__(self):
        super().__init__(title="Water Depth", subtitle="Choose a wd file to preview")

    def show_output(self, path, basemap=False):
        return self.show_raster(path, cmap="Blues", cbar_label="Water depth (m)",
                                title="Water Depth", mask_below=0.0, basemap=basemap)