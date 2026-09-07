from database.db_connection import extract_data, extract_data_efficiently
import numpy as np    
import pandas as pd

def get_patient_info(patient_ids=None, dataset="code-test"): 

    if patient_ids is None:
        query = f"""
        SELECT id, gender, age
        """

        rows = extract_data(query)

    else:
        placeholders = ",".join(["%s"] * len(patient_ids))

        query = f"""
        SELECT id, gender, age
        FROM "{dataset}"."patient_data"
        WHERE id IN ({placeholders})
        """

        rows = extract_data(query, patient_ids)

    return pd.DataFrame(rows, columns=["id", "gender", "age"]).astype({"id": int, "gender": str, "age": int})


def get_ecg_signals(patient_ids=None, dataset="code-test", filtered=False): 

    if filtered:
        db_table = "filtered_ecgs"

    else:
        db_table = "patient_data"


    if patient_ids is None:
        query = f"""
        SELECT id, DI, DII, DIII, AVR, AVL, AVF, V1, V2, V3, V4, V5, V6
        FROM "{dataset}".{db_table}
        """

        rows = extract_data_efficiently(query)

    else:
        placeholders = ",".join(["%s"] * len(patient_ids))

        query = f"""
        SELECT id, DI, DII, DIII, AVR, AVL, AVF, V1, V2, V3, V4, V5, V6
        FROM "{dataset}".{db_table}
        WHERE id IN ({placeholders})
        """

        rows = extract_data_efficiently(query, tuple(patient_ids))

    ids = []
    data = []

    for row in rows:
        ids.append(int(row[0]))
        
        sample = np.stack(row[1:]).astype(np.float32)
        data.append(sample)

    return pd.DataFrame({
        "id": ids,
        "signal": data
    })

def get_certainty(patient_ids=None, dataset="code-test"):
    if patient_ids is None:
        query = f"""Select "id", "1dAVb", rbbb, lbbb, sb, af, st
                    From "{dataset}".prediction_certanties
                """
        
        rows = extract_data(query)

    else:
        placeholders = ",".join(["%s"] * len(patient_ids))

        query = f"""
        Select "id", "1dAVb", rbbb, lbbb, sb, af, st
        FROM "{dataset}".prediction_certanties
        WHERE id IN ({placeholders})
        """
        
        rows = extract_data(query, patient_ids)

    return pd.DataFrame(rows, columns=["id", "1dAVb", "rbbb", "lbbb", "sb", "af", "st"]).astype({"id": int, "1dAVb": float, "rbbb": float, "lbbb": float, "sb": float, "af": float, "st": float})


def get_diagnostics(patient_ids=None, dataset="code-test", tablename="gold_lable"):

    if patient_ids is None:
        query = f"""Select "id", "1dAVb", rbbb, lbbb, sb, af, st
                    From "{dataset}".{tablename}
                """
        
        rows = extract_data(query)

    else:
        placeholders = ",".join(["%s"] * len(patient_ids))

        query = f"""
        Select "id", "1dAVb", rbbb, lbbb, sb, af, st
        FROM "{dataset}".{tablename}
        WHERE id IN ({placeholders})
        """

        rows = extract_data(query, patient_ids)

    position_mapping = {
    0: "1dAVb",
    1: "RBBB",
    2: "LBBB",
    3: "SB",
    4: "AF",
    5: "ST"
    }

    diagnostics = []
    ids = []

    for row in rows:
        diagnostic = [position_mapping.get(idx) for idx, val in enumerate(row[1:]) if val == 1] or ["NO_ABN"]

        ids.append(row[0])
        diagnostics.append(diagnostic)

    return pd.DataFrame({
            "id": ids,
            "diagnostic": diagnostics
        })

def get_embeddings(tablename, dataset="code-test", ids=None):

    if ids:
        placeholders = ",".join(["%s"] * len(ids))

        query = f"""Select *
                    From "{dataset}".{tablename}
                    where id in ({placeholders})
                """
        
    else:
        query = f"""Select *
                From "{dataset}".{tablename}
                """

        
    rows = extract_data(query, ids)

    return pd.DataFrame({
        "id": [row[0] for row in rows],
        "embedding": [np.array(row[1], dtype=float) for row in rows]

    })

def get_ids(dataset="code-test"):
    
    query = f"""
        SELECT id
        FROM "{dataset}".patient_data
        """

    rows = extract_data(query)

    return [row[0] for row in rows]