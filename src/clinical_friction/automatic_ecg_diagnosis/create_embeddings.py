"""
Create embedding using the model: https://github.com/antonior92/automatic-ecg-diagnosis

This file was based on: https://github.com/antonior92/automatic-ecg-diagnosis/blob/master/predict.py
"""

import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
import math

import h5py
import numpy as np
import pandas as pd
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import Sequence

from clinical_friction.database.db_connection import store_data
from clinical_friction.helpers.h5py_handling import load_h5py


class ECGSequence(Sequence):
    @classmethod
    def get_train_and_val(cls, path_to_hdf5, hdf5_dset, path_to_csv, batch_size=8, val_split=0.02):
        n_samples = len(pd.read_csv(path_to_csv))
        n_train = math.ceil(n_samples*(1-val_split))
        train_seq = cls(path_to_hdf5, hdf5_dset, path_to_csv, batch_size, end_idx=n_train)
        valid_seq = cls(path_to_hdf5, hdf5_dset, path_to_csv, batch_size, start_idx=n_train)
        return train_seq, valid_seq

    def __init__(self, path_to_hdf5, hdf5_dset, path_to_csv=None, batch_size=8,
                 start_idx=0, end_idx=None):
        if path_to_csv is None:
            self.y = None
        else:
            self.y = pd.read_csv(path_to_csv).values
        # Get tracings
        self.f = h5py.File(path_to_hdf5, "r")
        self.x = self.f[hdf5_dset]
        self.batch_size = batch_size
        if end_idx is None:
            end_idx = len(self.x)
        self.start_idx = start_idx
        self.end_idx = end_idx

    @property
    def n_classes(self):
        return self.y.shape[1]

    def __getitem__(self, idx):
        start = self.start_idx + idx * self.batch_size
        end = min(start + self.batch_size, self.end_idx)
        if self.y is None:
            return np.array(self.x[start:end, :, :])
        else:
            return np.array(self.x[start:end, :, :]), np.array(self.y[start:end])

    def __len__(self):
        return math.ceil((self.end_idx - self.start_idx) / self.batch_size)

    def __del__(self):
        self.f.close()


def create_code15_emb(tracings_hdf5: Path, model_hdf5: Path):
    seq = ECGSequence(tracings_hdf5, "tracings", batch_size=1)
    model = load_model(model_hdf5, compile=False)

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
    (id, embedding)   tensorflow
    VALUES %s
    ON CONFLICT (id) DO UPDATE SET embedding = EXCLUDED.embedding;
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
