from .base_tab import BaseRasterTab


class WaterDepthTab(BaseRasterTab):
    def __init__(self):
        super().__init__(title="Water Depth", subtitle="Choose a wd file to preview")