"""
Create hdf5 file, which is needed to make predictions with the model: https://github.com/antonior92/automatic-ecg-diagnosis
"""

import numpy as np
import pandas as pd
from scipy.signal import resample_poly

from clinical_friction.database.useful_queries import get_ecg_signals
from clinical_friction.helpers.h5py_handling import write_h5py


def convert_signals():
    """
    Convert signals from filtered PTB-XL dataset to fit requirements of automatic-ecg-diagnosis model and save as hdf5 file
    """

    df = pd.read_csv("database/transform_and_load/ptb/datasets/filtered_ecg_experiment_2.csv")
    ids = df["ecg_id"].tolist()

    df = get_ecg_signals(ids, "ptb-xl")

    signals = df["signal"]
    signals = np.stack(signals.to_numpy())

    # resample signals from 500Hz to 400Hz (automatic-ecg-diagnosis model was trained on 400Hz signals)
    x_resampled = resample_poly(signals, up=4, down=5, axis=2)

    # adjust the nr. of datapoints of signal (automatic-ecg-diagnosis expects a length of 4096)
    target_length = 4096
    current_length = x_resampled.shape[2]
    pad_width = target_length - current_length
    pad_left = pad_width // 2
    pad_right = pad_width - pad_left
    x_padded = np.pad(
        x_resampled,
        ((0, 0), (0, 0), (pad_left, pad_right)),
        mode="constant"
    )

    # model expects shape: (nr. of signals, nr. of datapoints = 4096, nr of leads = 12)
    x_padded = np.transpose(x_padded, (0, 2, 1))

    write_h5py("database/transform_and_load/ptb/datasets/ptb", x_padded, ids)


convert_signals()
