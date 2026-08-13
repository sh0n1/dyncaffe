# ------------------------------------------------------------------------------
# Simple raster viewer using rasterio
# ------------------------------------------------------------------------------

import matplotlib.pyplot as plt
import rasterio
from rasterio.plot import show


def view_raster(raster_path, base_map_path=None, title=None, alpha=0.7):
    with rasterio.open(raster_path) as src:
        data = src.read(1)
        nodata = src.nodata
        transform = src.transform

    if nodata is not None:
        data = data.astype("float64")
        data[data == nodata] = float("nan")

    fig, ax = plt.subplots()

    if base_map_path is not None:
        with rasterio.open(base_map_path) as base_src:
            base_data = base_src.read(1)
            base_nodata = base_src.nodata
            base_transform = base_src.transform

        if base_nodata is not None:
            base_data = base_data.astype("float64")
            base_data[base_data == base_nodata] = float("nan")

        show(base_data, transform=base_transform, ax=ax, cmap="terrain")
        show(data, transform=transform, ax=ax, cmap="inferno", alpha=alpha)
    else:
        show(data, transform=transform, ax=ax, cmap="terrain")

    if title is None:
        title = f"Raster: {raster_path}"
        if base_map_path is not None:
            title = f"Map + raster overlay: {raster_path}"
    ax.set_title(title)
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    raster_path = "./tests/serial_wl.tif"
    base_map_path = "./tests/csc_dem.tif"
    view_raster(raster_path, base_map_path=base_map_path)
