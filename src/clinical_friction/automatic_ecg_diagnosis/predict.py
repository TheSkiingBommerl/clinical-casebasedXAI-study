"""
Uses the model: https://github.com/antonior92/automatic-ecg-diagnosis to make predictions for Code-test and the filtered PTB-XL dataset

This file was based on: https://github.com/antonior92/automatic-ecg-diagnosis/blob/master/predict.py
"""

from pathlib import Path
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")
from tensorflow.keras.models import load_model
from tensorflow.keras.optimizers import Adam
from clinical_friction.helpers.h5py_handling import load_h5py

from clinical_friction.automatic_ecg_diagnosis.datasets import ECGSequence
# import h5py

# def load_h5py(path_to_hdf5):

#     file = h5py.File(path_to_hdf5, "r")
#     ids = file["ids"][:]
#     data = file["signals"][:]

#     return ids, data


def predict(input_path, data_name):
    seq = ECGSequence(input_path, data_name, batch_size=1)
    model = load_model("model/model.hdf5", compile=False)
    model.compile(loss='binary_crossentropy', optimizer=Adam())
    return model.predict(seq,  verbose=1)

def in_pop_prediction(hdf5_path: Path, filename: str, dst_dir: Path):

    y_score = predict(hdf5_path, "signals")

    np.save(dst_dir / f"{filename}.npy", y_score)


def out_pop_prediction(hdf5_path: Path,dst_dir: Path,  filename: str="ptb_predictions"):
    data_name = "signals"

    ids, _ = load_h5py(hdf5_path)

    y_score = predict(hdf5_path, data_name)

    df = pd.DataFrame({
        "id": ids,
        "y_score": list(y_score)
    })

    df.to_csv(dst_dir / f"{filename}.csv", index=False)


if __name__ == '__main__':

    out_pop_prediction()
    print("Output predictions saved")
