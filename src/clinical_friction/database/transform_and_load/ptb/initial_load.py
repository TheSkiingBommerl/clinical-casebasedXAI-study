import ast
from pathlib import Path

import pandas as pd
import psycopg2
import wfdb
from loguru import logger
from psycopg2.extras import execute_values
from tqdm import tqdm

import clinical_friction.database.db_connection as db

label_mapping = {
    "1AVB": "1dAVb",
    "CRBBB": "RBBB",
    "CLBBB": "LBBB",
    "SBRAD": "SB",
    "AFIB": "AF",
    "STACH": "ST"
}

columns = ["1dAVb", "RBBB", "LBBB", "SB", "AF", "ST"]


def load_records(ptbxl_entries_csv: Path, ptbxl_raw_dir: Path):

    df = pd.read_csv(ptbxl_entries_csv)

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

    records_dir = ptbxl_raw_dir
    logger.debug(f"Inserting {len(df)} ECG's into ptb-xl.patient_data")

    conn = db.db_conn()
    cur = conn.cursor()


    for i in tqdm(range(len(df)), desc="Loading ECGs"):
        filename = df.iloc[i]["filename_hr"]

        rec = wfdb.rdrecord(
            record_name=str(records_dir / filename),
            sampfrom=0,
            sampto=None,
            smooth_frames=False
        )

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

        try:
            execute_values(cur, query, row)
        except psycopg2.errors.UniqueViolation:
            logger.warning(f"ECG tracings have already been loaded")

    conn.commit()
    cur.close()
    conn.close()

def has_invalid_labels(label_str: str):
    labels = ast.literal_eval(label_str)

    # remove IRBBB & ILBBB -> taking CRBBB as RBBB because it is a clear RBBB
    if any(label in ["IRBBB", "ILBBB"] for label in labels):
        return True

    # remove everything where Norm is together with other lables -> doesn't make sense
    if "NORM" in labels and len(labels) > 1:
        return True

    return False

def encode_labels(label_str: str):
    labels = ast.literal_eval(label_str)

    row = dict.fromkeys(columns, 0)

    if labels != ["NORM"]:
        for label in labels:
            if label in label_mapping:
                col = label_mapping[label]
                row[col] = 1

    return row


def load_gold_labels(ptbxl_entries_csv: Path):
    logger.debug("Inserting gold labels into ptb-xl.gold_lable")
    df = pd.read_csv(ptbxl_entries_csv)

    df = df[~df["labels"].apply(has_invalid_labels)].reset_index(drop=True)

    encoded = df["labels"].apply(encode_labels)
    encoded_df = pd.DataFrame(list(encoded))

    df = pd.concat([df, encoded_df], axis=1)

    data = [tuple(int(x) for x in row) for row in df[["ecg_id"] + columns].values]

    query = """
    INSERT INTO "ptb-xl".gold_lable (id, "1dAVb", rbbb, lbbb, sb, af, st)
    VALUES %s
    """

    db.store_data(query, data)
