"""Compute Chamfer distance errors for predicted trajectories."""

from __future__ import annotations

import csv
import glob
import json
import os
import pickle
from typing import Dict, Iterable

import numpy as np
import torch
from pytorch3d.loss import chamfer_distance

prediction_dir: str = "./experiments"
base_path: str = "./data/different_types"
output_file: str = "results/final_results.csv"

if not os.path.exists("results"):
    os.makedirs("results")

def evaluate_prediction(
    start_frame: int,
    end_frame: int,
    vertices: Iterable[np.ndarray | torch.Tensor],
    object_points: Iterable[np.ndarray | torch.Tensor],
    object_visibilities: Iterable[np.ndarray | torch.Tensor],
    object_motions_valid: Iterable[np.ndarray | torch.Tensor],
    num_original_points: int,
    num_surface_points: int,
) -> Dict[str, float]:
    """Compute Chamfer distance statistics for a frame range."""

    chamfer_errors: list[float] = []

    if not isinstance(vertices, torch.Tensor):
        vertices = torch.tensor(vertices, dtype=torch.float32)
    if not isinstance(object_points, torch.Tensor):
        object_points = torch.tensor(object_points, dtype=torch.float32)
    if not isinstance(object_visibilities, torch.Tensor):
        object_visibilities = torch.tensor(object_visibilities, dtype=torch.bool)
    if not isinstance(object_motions_valid, torch.Tensor):
        object_motions_valid = torch.tensor(object_motions_valid, dtype=torch.bool)

    for frame_idx in range(start_frame, end_frame):
        x = vertices[frame_idx]
        current_object_points = object_points[frame_idx]
        current_object_visibilities = object_visibilities[frame_idx]

        # Whether the tracking between frames is valid.
        current_object_motions_valid = object_motions_valid[frame_idx - 1]

        # Compute the one-way Chamfer loss between predicted and ground-truth
        # points visible in this frame.
        chamfer_object_points = current_object_points[current_object_visibilities]
        chamfer_x = x[:num_surface_points]
        chamfer_error = chamfer_distance(
            chamfer_object_points.unsqueeze(0),
            chamfer_x.unsqueeze(0),
            single_directional=True,
            norm=1,
        )[0]

        chamfer_errors.append(chamfer_error.item())

    chamfer_errors = np.array(chamfer_errors)

    results = {
        "frame_len": len(chamfer_errors),
        "chamfer_error": np.mean(chamfer_errors),
    }

    return results


if __name__ == "__main__":
    # Open the output CSV file for writing.
    file = open(output_file, mode="w", newline="", encoding="utf-8")
    writer = csv.writer(file)

    writer.writerow(
        [
            "Case Name",
            "Train Frame Num",
            "Train Chamfer Error",
            "Test Frame Num",
            "Test Chamfer Error",
        ]
    )

    dir_names = glob.glob(f"{prediction_dir}/*")
    for dir_name in dir_names:
        case_name = dir_name.split("/")[-1]
        print(f"Processing {case_name}")

        # Load predicted vertices produced by inference.
        with open(f"{dir_name}/inference.pkl", "rb") as f:
            vertices = pickle.load(f)

        # Load ground truth point clouds and visibilities.
        with open(f"{base_path}/{case_name}/final_data.pkl", "rb") as f:
            data = pickle.load(f)

        object_points = data["object_points"]
        object_visibilities = data["object_visibilities"]
        object_motions_valid = data["object_motions_valid"]
        num_original_points = object_points.shape[1]
        num_surface_points = num_original_points + data["surface_points"].shape[0]

        # read the train/test split
        # Frame split for training and testing.
        with open(f"{base_path}/{case_name}/split.json", "r") as f:
            split = json.load(f)
        train_frame = split["train"][1]
        test_frame = split["test"][1]

        assert (
            test_frame == vertices.shape[0]
        ), f"Test frame {test_frame} != {vertices.shape[0]}"

        # Do the statistics on train split, only evalaute from the 2nd frame
        results_train = evaluate_prediction(
            1,
            train_frame,
            vertices,
            object_points,
            object_visibilities,
            object_motions_valid,
            num_original_points,
            num_surface_points,
        )
        results_test = evaluate_prediction(
            train_frame,
            test_frame,
            vertices,
            object_points,
            object_visibilities,
            object_motions_valid,
            num_original_points,
            num_surface_points,
        )

        writer.writerow(
            [
                case_name,
                results_train["frame_len"],
                results_train["chamfer_error"],
                results_test["frame_len"],
                results_test["chamfer_error"],
            ]
        )
    file.close()
