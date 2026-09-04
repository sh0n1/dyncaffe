from .base_tab import BaseRasterTab


class WaterLevelTab(BaseRasterTab):
    def __init__(self):
        super().__init__(title="Water Level", subtitle="Choose a water level file to preview")