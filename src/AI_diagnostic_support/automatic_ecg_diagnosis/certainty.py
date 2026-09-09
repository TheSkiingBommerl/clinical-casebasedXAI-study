"""
Calculate the certainty for each prediction
"""
from pathlib import Path
import numpy as np
import warnings

warnings.filterwarnings("ignore")
from tensorflow.keras.models import load_model
from tensorflow.keras.optimizers import Adam
from AI_diagnostic_support.automatic_ecg_diagnosis.datasets import ECGSequence
import tensorflow as tf
from AI_diagnostic_support.database.db_connection import store_data
from AI_diagnostic_support.helpers.h5py_handling import load_h5py
from tqdm import tqdm
from loguru import logger
# import h5py


# import h5py

# def load_h5py(path_to_hdf5):

#     file = h5py.File(path_to_hdf5, "r")
#     ids = file["ids"][:]
#     data = file["signals"][:]

#     return ids, data

def get_certainty(hdf5_path: Path, model_path: Path, data_name: str, pred_rep):
    """
    Returns the prediction variance of 5 drop out runs
    """

    model = load_model(model_path, compile=False)

    for layer in model.layers:
        if isinstance(layer, tf.keras.layers.BatchNormalization):
            layer.trainable = False

    model.compile(loss='binary_crossentropy', optimizer=Adam())
    seq = ECGSequence(hdf5_path, data_name, batch_size=1)

    logger.debug(f"Computing uncertainty for {hdf5_path.name} with {pred_rep} rollouts...")
    scores = []
    n = len(seq)
    for i in tqdm(range(n), total=n):
        run_scores = []
        for _ in range(pred_rep):
            X = seq[i]
            y_score = model(X, training=True).numpy()
            run_scores.append(y_score[0])

        scores.append(np.var(run_scores, axis=0))

    return scores

def aed_certainty(hdf5_path: Path, model_path: Path, pred_rep: int):
    data_name = "signals"
    ids, _ = load_h5py(hdf5_path)
    certainty = get_certainty(hdf5_path, model_path, data_name, pred_rep)
    data = [[int(i)] + [float(v) for v in certainty[i]] for i in range(len(ids))]

    logger.debug(f"Inserting uncertainty values into code-test.prediction_certainties")
    query = """
    INSERT INTO "code-test".prediction_certanties (id, "1dAVb", rbbb, lbbb, sb, af, st)
    VALUES %s
    ON CONFLICT (id) DO UPDATE SET
        "1dAVb" = EXCLUDED."1dAVb",
        rbbb = EXCLUDED.rbbb,
        lbbb = EXCLUDED.lbbb,
        sb = EXCLUDED.sb,
        af = EXCLUDED.af,
        st = EXCLUDED.st;
    """

    store_data(query, data)

def fm_certainty(hdf5_path: Path, model_path: Path, pred_rep: int):

    data_name = "signals"

    ids, _ = load_h5py(hdf5_path)

    certainty = get_certainty(hdf5_path, model_path, data_name, pred_rep)

    data = [[int(ids[i])] + [float(v) for v in certainty[i]] for i in range(len(ids))]
    logger.debug(f"Inserting uncertainty values into ptb-xl.prediction_certainties")
    query = """
    INSERT INTO "ptb-xl".prediction_certanties (id, "1dAVb", rbbb, lbbb, sb, af, st)
    VALUES %s
    ON CONFLICT (id) DO UPDATE SET
        "1dAVb" = EXCLUDED."1dAVb",
        rbbb = EXCLUDED.rbbb,
        lbbb = EXCLUDED.lbbb,
        sb = EXCLUDED.sb,
        af = EXCLUDED.af,
        st = EXCLUDED.st;
    """

    store_data(query, data)

if __name__ == '__main__':
    # nr. of predictions done using the drop outs
    pred_rep = 5
    fm_certainty(pred_rep)
