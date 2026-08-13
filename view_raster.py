# ------------------------------------------------------------------------------
# Simple raster viewer using rasterio
# ------------------------------------------------------------------------------

import matplotlib.pyplot as plt
import rasterio
from rasterio.plot import show


def view_raster(raster_path, title=None):
    with rasterio.open(raster_path) as src:
        data = src.read(1)
        nodata = src.nodata

    if nodata is not None:
        data = data.astype("float64")
        data[data == nodata] = float("nan")

    fig, ax = plt.subplots()
    show(data, ax=ax, cmap="terrain")

    if title is None:
        title = f"Raster: {raster_path}"
    ax.set_title(title)
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    raster_path1 = "./tests/serial_mwd.tif"
    raster_path2 = "./tests/serial_wd.tif"
    raster_path3 = "./tests/serial_wl.tif"
    view_raster(raster_path3)
