from pathlib import Path

import pandas as pd
import wfdb

from clinical_friction.database.db_connection import store_data

df = pd.read_csv("database/transform_and_load/ptb/datasets/filtered_ecg_experiment_2.csv")

gender_map = {
    0: "MALE",
    1: "FEMALE"
}

df["sex"] = df["sex"].map(gender_map)

rows = []

# be aware that the leads are odered in this way in the ptb-xl dataset: (I, II, III, AVL, AVR, AVF, V1, ..., V6)

query = """
INSERT INTO "ptb-xl".patient_data
(id, gender, age, DI, DII, DIII, AVL, AVR, AVF, V1, V2, V3, V4, V5, V6)
VALUES %s
"""


for i in range(len(df)):
    filename = df.iloc[i]["filename_hr"]

    rec = wfdb.rdrecord(Path("C:/Users/flo_o/Desktop/records/" + filename), sampfrom=0, sampto=None, smooth_frames=False)

    signal = rec.e_p_signal

    row = [(
        int(df.iloc[i]["ecg_id"]),
        df.iloc[i]["sex"],
        int(df.iloc[i]["age"]),
        signal[0].tolist(),
        signal[1].tolist(),
        signal[2].tolist(),
        signal[3].tolist(),
        signal[4].tolist(),
        signal[5].tolist(),
        signal[6].tolist(),
        signal[7].tolist(),
        signal[8].tolist(),
        signal[9].tolist(),
        signal[10].tolist(),
        signal[11].tolist()

    )]

    store_data(query, row)

    if i%100 == 0:
        print(f"{i} signals saved")
