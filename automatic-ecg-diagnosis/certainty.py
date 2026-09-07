"""
Calculate the certainty for each prediction
"""

import numpy as np
import warnings
warnings.filterwarnings("ignore")
from tensorflow.keras.models import load_model
from tensorflow.keras.optimizers import Adam
from datasets import ECGSequence
import tensorflow as tf
from database.db_connection import store_data
from helpers.h5py_handling import load_h5py

# import h5py

# def load_h5py(path_to_hdf5):

#     file = h5py.File(path_to_hdf5, "r")
#     ids = file["ids"][:]
#     data = file["signals"][:]

#     return ids, data

def get_certainty(input_path, data_name, pred_rep):
    """
    Returns the prediction variance of 5 drop out runs 
    """
    
    model = load_model("model/model.hdf5", compile=False)
    
    for layer in model.layers:
        if isinstance(layer, tf.keras.layers.BatchNormalization):
            layer.trainable = False
       
    model.compile(loss='binary_crossentropy', optimizer=Adam())
    seq = ECGSequence(input_path, data_name, batch_size=1)

    scores = []
    
    for i in range(len(seq)):
        if i % 10 == 0:
            print(f"Predicting signal: {i}/{len(seq)}")
        run_scores = []
        for _ in range(pred_rep):
            X = seq[i]
            y_score = model(X, training=True).numpy()
            run_scores.append(y_score[0])

        scores.append(np.var(run_scores, axis=0))
    
    return scores

def in_pop_certainty(pred_rep):
    input_path = "data/ecg_tracings.hdf5"
    data_name = "tracings"

    certainty = get_certainty(input_path, data_name, pred_rep)
    data = [[int(i)] + [float(v) for v in certainty[i]] for i in range(len(ids))]

    query = """
    INSERT INTO "code-test".prediction_certainties (id, "1dAVb", rbbb, lbbb, sb, af, st)
    VALUES %s
    """

    store_data(query, data)

def out_pop_certainty(pred_rep):
    input_path = "ptb.hdf5"
    data_name = "signals"

    ids, _ = load_h5py(input_path)

    certainty = get_certainty(input_path, data_name, pred_rep)
   
    data = [[int(ids[i])] + [float(v) for v in certainty[i]] for i in range(len(ids))]

    query = """
    INSERT INTO "ptb-xl".prediction_certanties (id, "1dAVb", rbbb, lbbb, sb, af, st)
    VALUES %s
    """

    store_data(query, data)

if __name__ == '__main__':
    # nr. of predictions done using the drop outs
    pred_rep = 5 
    out_pop_certainty(pred_rep)