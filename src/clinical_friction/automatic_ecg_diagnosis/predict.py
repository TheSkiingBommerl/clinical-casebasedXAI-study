"""
Uses the model: https://github.com/antonior92/automatic-ecg-diagnosis to make predictions for Code-test and the filtered PTB-XL dataset

This file was based on: https://github.com/antonior92/automatic-ecg-diagnosis/blob/master/predict.py
"""

import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")
from tensorflow.keras.models import load_model
from tensorflow.keras.optimizers import Adam
from datasets import ECGSequence
from helpers.h5py_handling import load_h5py
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

def in_pop_prediction():
    input_path = "data/ecg_tracings.hdf5"
    data_name = "tracings"
    output_path = "dnn_predicts/model"

    y_score = predict(input_path, data_name)

    np.save(f"{output_path}.npy", y_score)


def out_pop_prediction():
    input_path = "ptb.hdf5"
    data_name = "signals"
    output_path = "ptb_predictions"

    ids, _ = load_h5py(input_path)

    y_score = predict(input_path, data_name)
   
    df = pd.DataFrame({
        "id": ids,
        "y_score": list(y_score)
    })

    df.to_csv(f"{output_path}.csv", index=False)

    
if __name__ == '__main__':

    out_pop_prediction()
    print("Output predictions saved")

    