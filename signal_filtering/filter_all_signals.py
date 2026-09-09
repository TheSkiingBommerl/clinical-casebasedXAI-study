"""
Filter ECG signals. This code filters the ECG signals from the filtered PTB-XL dataset.
When adjusted, it can also be used for Code-test but keep in mind to also adjust the sampling frequancy in filters.py and the powerline interferance Hz in pipeline.py
"""

from signal_filtering.pipeline import filter_pipeline
from database.useful_queries import get_ecg_signals
from database.db_connection import store_data
from helpers.h5py_handling import write_h5py
from helpers.remove_padding import remove_zero_padding, get_middle_segment
import numpy as np
import pandas as pd

query = """
        INSERT INTO "ptb-xl".filtered_ecgs
        (id, DI, DII, DIII, AVR, AVL, AVF, V1, V2, V3, V4, V5, V6)   
        VALUES %s

        """

def filter_signal(signal):
    signal = remove_zero_padding(signal)
    signal = filter_pipeline(signal)
    signal = get_middle_segment(signal, fs=500)
    return signal

def save_db(ids, signals):

    rows = []
    for signal_id, signal in zip(ids, signals):
        
        filtered_signal = filter_signal(signal)

        row = [int(signal_id)] + [lead.tolist() for lead in filtered_signal]
        rows.append(row)

    print("Saving to DB")
    store_data(query, rows)


def save_h5py(ids, signals):

    rows = []
    for idx, signal in enumerate(signals):
        print(ids[idx])
        filtered_signal = filter_signal(signal)
        
        row = [lead.tolist() for lead in filtered_signal]
        rows.append(row)
    
    print("Saving to H5PY")
    write_h5py("signal_filtering/filtered_signals", rows, ids)


if __name__ == '__main__':
    #database\transform_and_load\ptb\datasets\filtered_ecg.csv
    ids = pd.read_csv("database/transform_and_load/ptb/datasets/filtered_ecg_experiment_2.csv")["ecg_id"].tolist()
    signals = get_ecg_signals(dataset="ptb-xl", patient_ids=ids)


    ids = signals["id"].to_list()
    signals = np.stack(signals["signal"])

    
    print("Starting ...")
    #save_h5py(ids, signals)
    save_db(ids, signals)

    

       
