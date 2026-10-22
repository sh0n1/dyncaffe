"""Backend execution layer: runs Dynamic CA-ffé from a config dict. No Qt imports."""

import os
import numpy as np


def run_simulation(config):
    """Run the serial CA-ffé workflow and return the paths of the output rasters."""
    from caffe import caffe  # imported here so the GUI still opens if the backend import fails

    sim = caffe(config["dem_path"])
    sim.setConstants(
        config["hf"],
        config["increment_constant"],
        config["ev_threshold"],
    )

    ev_array = np.array(
        [[int(r), int(c), float(v)] for r, c, v in config["ev_sources"]]
    )
    sim.ExcessVolumeArray(ev_array)

    bc_array = np.array(
        [[int(r), int(c)] for r, c in config["boundaries"]]
    )
    sim.OpenBCArray(bc_array)

    sim.RunSimulation()
    sim.setOutputPath(os.path.join(config["output_dir"], ""))  # backend needs a trailing separator
    sim.setOutputName(config["output_name"])
    sim.CloseSimulation()

    outputs = {
        key: os.path.join(config["output_dir"], f"{config['output_name']}_{key}.tif")
        for key in ("wd", "wl", "mwd")
    }
    missing = [os.path.basename(p) for p in outputs.values() if not os.path.exists(p)]
    if missing:
        raise FileNotFoundError(
            "Run finished but outputs were not found in the output directory: "
            + ", ".join(missing)
        )
    return outputs

if __name__ == "__main__":
    import json
    import sys

    with open(sys.argv[1]) as f:
        cfg = json.load(f)
    result = run_simulation(cfg)
    print("CAFFE_GUI_OUTPUTS:" + json.dumps(result), flush=True)