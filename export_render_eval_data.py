"""Export a subset of the dataset for rendering and evaluation."""

from __future__ import annotations

import os
import csv
import json

base_path: str = "./data/different_types"
output_path: str = "./data/render_eval_data"
CONTROLLER_NAME: str = "hand"


def existDir(dir_path: str) -> None:
    """Create directory ``dir_path`` if needed."""

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


# Ensure base output directory exists
existDir(output_path)

# Parse scene information from the configuration CSV and copy the corresponding
# images and masks into ``output_path`` for easier visualization.
with open("data_config.csv", newline="", encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        case_name = row[0]
        category = row[1]
        shape_prior = row[2]
        
        if not os.path.exists(f"{base_path}/{case_name}"):
            continue
        print(f"Processing {case_name}!!!!!!!!!!!!!!!")
    
        # Create the directory for the case
        existDir(f"{output_path}/{case_name}")
        existDir(f"{output_path}/{case_name}/mask")
        for i in range(3):
            # Copy the original RGB image
            os.system(
                f"cp -r {base_path}/{case_name}/color {output_path}/{case_name}/"
            )
            # Copy only the object mask image
            # Get the mask path for the image
            with open(f"{base_path}/{case_name}/mask/mask_info_{i}.json", "r") as f:
                data = json.load(f)
            obj_idx = None
            for key, value in data.items():
                if value != CONTROLLER_NAME:
                    if obj_idx is not None:
                        raise ValueError("More than one object detected.")
                    obj_idx = int(key)
            existDir(f"{output_path}/{case_name}/mask/{i}")
            os.system(f"cp -r {base_path}/{case_name}/mask/{i}/{obj_idx}/* {output_path}/{case_name}/mask/{i}/")
        
        # Copy the split.json
        os.system(f"cp {base_path}/{case_name}/split.json {output_path}/{case_name}/")