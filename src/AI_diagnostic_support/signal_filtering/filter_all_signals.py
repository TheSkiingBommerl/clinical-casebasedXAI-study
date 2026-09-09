"""
Filter ECG signals. This code filters the ECG signals from the filtered PTB-XL dataset.
When adjusted, it can also be used for Code-15 but keep in mind to also adjust the sampling frequancy in filters.py and the powerline interferance Hz in pipeline.py
"""
from typing import Literal
from pathlib import Path
from AI_diagnostic_support.signal_filtering.pipeline import filter_pipeline, FREQ_CODE_TEST, FREQ_PTB_XL
from AI_diagnostic_support.database.useful_queries import get_ecg_signals
import AI_diagnostic_support.database.db_connection as db
from AI_diagnostic_support.helpers.h5py_handling import write_h5py
from AI_diagnostic_support.database.transform_and_load.ptb.create_hdf5 import convert_signals
from AI_diagnostic_support.helpers.remove_padding import remove_zero_padding, get_middle_segment
import numpy as np
import pandas as pd
from tqdm import tqdm
from loguru import logger

query = """
        INSERT INTO "ptb-xl".filtered_ecgs
        (id, DI, DII, DIII, AVR, AVL, AVF, V1, V2, V3, V4, V5, V6)
        VALUES %s
        """

def filter_signal(signal, freq=FREQ_PTB_XL):
    signal = remove_zero_padding(signal)
    signal = filter_pipeline(signal, freq)
    signal = get_middle_segment(signal, fs=500)
    return signal

def save_db(ids, signals):
    rows = []
    for signal_id, signal in zip(ids, signals):
        signal = filter_signal(signal)
        row = [int(signal_id)] + [lead.tolist() for lead in signal]
        rows.append(row)

    print("Saving to DB")
    db.store_data(query, rows)


def save_h5py(ids, signals, dst: Path):


    rows = []
    for idx, signal in enumerate(signals):

        row = [lead.tolist() for lead in signals]
        rows.append(row)

    print("Saving to H5PY")
    write_h5py(dst, rows, ids)


def filter_ptbxl(ptbxl_entries_csv: Path, processed_dir: Path):
    ids = pd.read_csv(ptbxl_entries_csv)["ecg_id"].tolist()
    signals = get_ecg_signals(dataset="ptb-xl", patient_ids=ids)
    ids = signals["id"].to_list()
    signals = np.stack(signals["signal"])
    M, N, _ = signals.shape
    filtered = np.zeros(shape=(M, N, 2500))
    # Filter signals
    logger.debug("Filtering PTBXL signals and saving to DB...")
    for signal_id, signal in tqdm(zip(ids, signals), total=len(ids)):
        filtered = filter_signal(signal, FREQ_PTB_XL)
        row = [int(signal_id)] + [lead.tolist() for lead in filtered]
        db.store_data(query, [row])

    logger.debug("Converting PTBXL signals to .hdf5...")
    convert_signals(ptbxl_entries_csv, processed_dir)


def filter_from_db(dataset: Literal["ptb-xl", "code-test"], processed_dir: Path):
    signals = get_ecg_signals(dataset=dataset)
    ids = signals["id"].to_list()

    signals = np.stack(signals["signal"])
    M, N, _ = signals.shape
    filtered = np.zeros(shape=(M, N, 2500))
    # Filter signals


    query_store = (
        f'INSERT INTO "{dataset}".filtered_ecgs '
        '(id, DI, DII, DIII, AVR, AVL, AVF, V1, V2, V3, V4, V5, V6) '
        'VALUES %s'
    )
    frequency = FREQ_PTB_XL if dataset == "ptb-xl" else FREQ_CODE_TEST
    logger.debug(f"Filtering {frequency}hz signals in {dataset} and saving to DB...")
    for signal_id, signal in tqdm(zip(ids, signals), total=len(ids)):
        filtered = filter_signal(signal, frequency)
        row = [int(signal_id)] + [lead.tolist() for lead in filtered]
        db.store_data(query_store, [row])

    logger.debug(f"Converting {dataset} signals to .hdf5...")
    convert_signals(dataset, processed_dir)


if __name__ == '__main__':
    #database\transform_and_load\ptb\datasets\filtered_ecg.csv
    ids = pd.read_csv("database/transform_and_load/ptb/datasets/filtered_ptbxl.csv")["ecg_id"].tolist()
    signals = get_ecg_signals(dataset="ptb-xl", patient_ids=ids)
    #

    ids = signals["id"].to_list()
    signals = np.stack(signals["signal"])


    print("Starting ...")
    #save_h5py(ids, signals)
    save_db(ids, signals)
