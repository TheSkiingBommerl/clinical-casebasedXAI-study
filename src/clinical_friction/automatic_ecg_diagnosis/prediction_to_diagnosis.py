"""
Maps models predictions to a diagnosis
"""

import pandas as pd
from clinical_friction.database.db_connection import store_data
import numpy as np
from pathlib import Path
from loguru import logger
from tqdm import tqdm

BASE = Path(__file__).parent.parent

# thresholds from: https://github.com/antonior92/automatic-ecg-diagnosis/blob/master/generate_figures_and_tables.py
TRESHOLDS = np.array([0.124, 0.07, 0.05, 0.278, 0.390, 0.174])




def add_ptbxl_dnn(pred_csv_path: Path):
    df = pd.read_csv(pred_csv_path)

    result = []

    for i in tqdm(range(len(df)), total=len(df)):

        _id = int(df.iloc[i]["id"])

        pred = np.fromstring(df.iloc[i]["y_score"].strip("[]"), sep=" ")

        result.append([_id] + [1 if v > TRESHOLDS[j] else 0 for j, v in enumerate(pred)])

    data = [tuple(int(x) for x in row) for row in result]
    logger.debug("Inserting tresholded diagnoses into ptb-xl.dnn_annotations")
    query = """
    INSERT INTO "ptb-xl".dnn_annotations (id, "1dAVb", rbbb, lbbb, sb, af, st)
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
