"""
Get the header information of a specific ECG from the filtered PTB-XL dataset
"""

import pandas as pd
from pathlib import Path
import wfdb

df = pd.read_csv("database/transform_and_load/ptb/datasets/filtered_ecg_experiment_2.csv")

filename = df.iloc[0]["filename_hr"]

rec = wfdb.rdrecord(Path("C:/Users/flo_o/Desktop/records/" + filename), sampfrom=0, sampto=None, smooth_frames=False)

for (name, units, data) in zip(rec.sig_name,
                               rec.units,
                               rec.e_p_signal):
    print('{} (units {}):'.format(name, units))
    print(data)