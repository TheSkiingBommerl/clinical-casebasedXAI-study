"""
Find most similar ECG signals using DTW
Article explaining DTW: https://medium.com/walmartglobaltech/time-series-similarity-using-dynamic-time-warping-explained-9d09119e48ec
"""
from pathlib import Path
from loguru import logger
import pandas as pd
import time
import os
from pathlib import Path
import csv
import numpy as np
from tslearn.metrics import dtw_path
import time
from clinical_friction.helpers.h5py_handling import load_h5py
from tqdm import tqdm

RESULTS = "similarity_measure/results/dtw"

def get_most_similar(ids, data, id):

    target_idx = np.where(ids == id)[0][0]
    target_signal = data[target_idx]
    R = np.ascontiguousarray(target_signal.T)

    mask = np.arange(len(ids)) != target_idx

    filtered_data = data[mask]
    filtered_ids = ids[mask]

    results = []

    for idx, signal in enumerate(filtered_data):

        signal = np.asarray(signal)

        Q = np.ascontiguousarray(signal.T)

        path, dist = dtw_path(R, Q)

        norm_c = dist / len(path)

        sim = 1 / (1 + norm_c)

        results.append((filtered_ids[idx], sim))

    best_id, best_score = max(results, key=lambda x: x[1])

    return best_id, best_score, results

def write_sample(sample, best_id,  best_score, dst_dir: Path):

    with open(dst_dir / f"{sample}.csv", "w", newline="") as f:
            writer = csv.writer(f)
            results = (sample, best_id, best_score)
            writer.writerow(results)


def process_all(samples: list[int], dst_dir: Path, hdf5_path: Path):
    """Find most similar samples to an ECG ID with Dynamic Time Warping"""
    dst_dir.mkdir(exist_ok=True)
    ids, data = load_h5py(hdf5_path)

    logger.debug(f"Applying DTW to {len(samples)} samples...")
    for sample in tqdm(samples):
        best_id, best_score, _ = get_most_similar(ids, data, sample)
        write_sample(sample, best_id, best_score, dst_dir)
