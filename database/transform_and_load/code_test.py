import os
import tempfile
from pathlib import Path
from zipfile import ZipFile

import h5py
import numpy as np
import pandas as pd
import psycopg2
import requests
from loguru import logger
from psycopg2.extensions import connection
from psycopg2.extras import execute_values
from tqdm import tqdm


def close_exception(err: BaseException):
    """Close the db connection if an exception occurs"""
    if isinstance(err, psycopg2.Error):
        cur = err.cursor
        conn = cur.connection
        cur.close()
        conn.close()


@logger.catch(reraise=True, onerror=close_exception)
def load_tracings(conn: connection, tracings: Path, attributes: Path):
    """Load ECG tracings from hdf5 file into database"""

    with h5py.File(tracings, "r") as f:
        x = np.array(f['tracings'])

    df = pd.read_csv(attributes)

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
    INSERT INTO "code-test".patient_data
    (id, gender, age, DI, DII, DIII, AVR, AVL, AVF, V1, V2, V3, V4, V5, V6)
    VALUES %s
    """

    cur = conn.cursor()
    try:
        execute_values(cur, query, rows)
        conn.commit()
    except psycopg2.errors.UniqueViolation:
        logger.warning(f"ECG tracings have already been loaded")

    cur.close()


@logger.catch(reraise=True)
def load_annotations(conn: connection, data_path: Path, table_name: str):
    df = pd.read_csv(data_path)

    rows = []

    for i in range(827):

        row = (
            i,
            int(df.iloc[i]["1dAVb"]),
            int(df.iloc[i]["RBBB"]),
            int(df.iloc[i]["LBBB"]),
            int(df.iloc[i]["SB"]),
            int(df.iloc[i]["AF"]),
            int(df.iloc[i]["ST"])
        )

        rows.append(row)
        def close_exception(err: BaseException):
            """Close the db connection if an exception occurs"""
            if isinstance(err, psycopg2.Error):
                cur = err.cursor
                conn = cur.connection
                cur.close()
                conn.close()
    query = f"""
    INSERT INTO "code-test".{table_name}
    (id, "1dAVb",RBBB,LBBB,SB,AF,ST)
    VALUES %s
    """

    cur = conn.cursor()

    try:
        execute_values(cur, query, rows)
        conn.commit()
    except psycopg2.errors.UniqueViolation:

        logger.warning(f"Annotations for {str(data_path)} have already been loaded")

    cur.close()
