"""
Maps models predictions to a diagnosis
"""

import pandas as pd
from database.db_connection import store_data
import numpy as np
from pathlib import Path

BASE = Path(__file__).parent.parent

# thresholds from: https://github.com/antonior92/automatic-ecg-diagnosis/blob/master/generate_figures_and_tables.py
thresholds = np.array([0.124, 0.07, 0.05, 0.278, 0.390, 0.174])

file = pd.read_csv(BASE / "automatic-ecg-diagnosis" / "ptb_predictions.csv")
    
result = []

for i in range(len(file)):
        
    _id = int(file.iloc[i]["id"])

    pred = np.fromstring(file.iloc[i]["y_score"].strip("[]"), sep=" ")
    
    result.append([_id] + [1 if v > thresholds[j] else 0 for j, v in enumerate(pred)])

data = [tuple(int(x) for x in row) for row in result]

query = """
INSERT INTO "ptb-xl".dnn_annotations (id, "1dAVb", rbbb, lbbb, sb, af, st)
VALUES %s
"""

store_data(query, data)
