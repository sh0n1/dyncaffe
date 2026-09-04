from .base_tab import BaseRasterTab


class InputDEMTab(BaseRasterTab):
    def __init__(self):
        super().__init__(title="Input DEM", subtitle="Load a DEM file to preview")