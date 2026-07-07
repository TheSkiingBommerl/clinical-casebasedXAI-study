from database.db_connection import store_data
import h5py
import numpy as np
import pandas as pd

def fill_table():
    filename = "automatic-ecg-diagnosis/data/ecg_tracings.hdf5"

    with h5py.File(filename, "r") as f:
        x = np.array(f['tracings'])

    df = pd.read_csv("automatic-ecg-diagnosis/data/attributes.csv")

    gender_map = {
        "M": "MALE",
        "F": "FEMALE"
    }

    df["sex"] = df["sex"].map(gender_map)

    rows = []

    for i in range(x.shape[0]):
        features = x[i].T.tolist()

        row = (
            i,
            df.iloc[i]["sex"],
            int(df.iloc[i]["age"]),
            features[0],
            features[1],
            features[2],
            features[3],
            features[4],
            features[5],
            features[6],
            features[7],
            features[8],
            features[9],
            features[10],
            features[11]

        )

        rows.append(row)

    # be aware that the leads are ordered as following in ecg_tracings.hdf5: DI, DII, DIII, AVR, AVL, AVF, V1, V2, V3, V4, V5, V6

    query = """
    INSERT INTO "code-15".patient_data
    (id, gender, age, DI, DII, DIII, AVR, AVL, AVF, V1, V2, V3, V4, V5, V6)   
    VALUES %s
    """

    store_data(query, rows)

print("Starting")
fill_table()