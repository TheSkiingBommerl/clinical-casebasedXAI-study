"""
Create embedding using the model: https://github.com/antonior92/automatic-ecg-diagnosis

This file was based on: https://github.com/antonior92/automatic-ecg-diagnosis/blob/master/predict.py
"""

import warnings
warnings.filterwarnings("ignore")
from tensorflow.keras.models import load_model, Model
from tensorflow.keras.optimizers import Adam
from datasets import ECGSequence
from db_connection import store_data
from helpers.h5py_handling import load_h5py
# import h5py

# def load_h5py(path_to_hdf5):

#     file = h5py.File(path_to_hdf5, "r")
#     ids = file["ids"][:]
#     data = file["signals"][:]

#     return ids, data

def create_code15_emb():
    seq = ECGSequence("data/ecg_tracings.hdf5", "tracings", batch_size=1)
    model = load_model("model/model.hdf5", compile=False)
    
    # taking the output of the second to last layer as embeddings
    embedding_model = Model(
        inputs=model.input,
        outputs=model.get_layer("flatten_1").output
    )

    embedding_model.compile(loss='binary_crossentropy', optimizer=Adam())

    y_score = embedding_model.predict(seq,  verbose=1)

    rows = [
        (int(i), vec.astype(float).tolist())
        for i, vec in enumerate(y_score)
    ]

    query = """
    INSERT INTO "code-test".AED_model_embeddings
    (id, embedding)   
    VALUES %s
    """

    store_data(query, rows)


def create_ptb_emb():

    ids, _ = load_h5py("ptb.hdf5")

    seq = ECGSequence("ptb.hdf5", "signals", batch_size=1)
    model = load_model("model/model.hdf5", compile=False)
    
    embedding_model = Model(
        inputs=model.input,
        outputs=model.get_layer("flatten_1").output
    )

    embedding_model.compile(loss='binary_crossentropy', optimizer=Adam())

    y_score = embedding_model.predict(seq,  verbose=1)

    rows = [
        (int(ids[i]), vec.astype(float).tolist())
        for i, vec in enumerate(y_score)
    ]

    query = """
    INSERT INTO "ptb-xl".AED_model_embeddings
    (id, embedding)   
    VALUES %s
    """

    store_data(query, rows)

if __name__ == '__main__':
    create_ptb_emb()