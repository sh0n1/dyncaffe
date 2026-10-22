from .base_tab import BaseRasterTab


class MaxWaterDepthTab(BaseRasterTab):
    def __init__(self):
        super().__init__(title="Max Water Depth", subtitle="Choose a mwd file to preview")

    def show_output(self, path, basemap=False):
        return self.show_raster(path, cmap="Blues", cbar_label="Max water depth (m)",
                                title="Max Water Depth", mask_below=0.0, basemap=basemap)