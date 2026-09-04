from .base_tab import BaseRasterTab


class MaxWaterDepthTab(BaseRasterTab):
    def __init__(self):
        super().__init__(title="Max Water Depth", subtitle="Choose a mwd file to preview")