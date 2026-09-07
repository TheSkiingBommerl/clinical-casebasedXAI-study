"""
Find most similar ECG signals using DTW
Article explaining DTW: https://medium.com/walmartglobaltech/time-series-similarity-using-dynamic-time-warping-explained-9d09119e48ec
"""

import time
import os
from pathlib import Path
import csv
import numpy as np
from tslearn.metrics import dtw_path
import time
from clinical_friction.helpers.h5py_handling import load_h5py

RESULTS = "similarity_measure/results/dtw"

def get_most_similar(ids, data, id):

    target_idx = np.where(ids == id)[0][0]
    target_signal = data[target_idx]
    R = np.ascontiguousarray(target_signal.T)

    mask = np.arange(len(ids)) != target_idx

    filtered_data = data[mask]
    filtered_ids = ids[mask]

    results = []

    print("Started Loop")

    for idx, signal in enumerate(filtered_data):

        signal = np.asarray(signal)

        Q = np.ascontiguousarray(signal.T)

        path, dist = dtw_path(R, Q)

        norm_c = dist / len(path)

        sim = 1 / (1 + norm_c)

        results.append((filtered_ids[idx], sim))

    best_id, best_score = max(results, key=lambda x: x[1])

    return best_id, best_score, results

def process_sample(ids, data, sample):

    best_id, best_score, _ = get_most_similar(ids, data, sample)

    with open(os.path.join(RESULTS, f"{sample}.csv"), "w", newline="") as f:
            writer = csv.writer(f)
            results = (sample, best_id, best_score)
            writer.writerow(results)
    print(f"Sample {sample} is done")
    return (sample, best_id, best_score)


if __name__ == '__main__':

    results_dir = Path(RESULTS)
    results_dir.mkdir(exist_ok=True)
    path_to_hdf5 = "signal_filtering/filtered_signals.hdf5"
    ids, data = load_h5py(path_to_hdf5)

    # ids used for experiment 1 - produced by get_test_split.py
    # 10 Normal, 10 1dAVb and 10 LBBB
    samples = [...]
    print("Start")

    for sample in samples:
        print("Sample: ", sample)
        tick = time.time()
        process_sample(ids, data, sample)
        tock = time.time()
        print(f"Took {round((tock - tick) / 60, ndigits=1)} minutes")
