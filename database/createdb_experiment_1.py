import os
import tempfile
from pathlib import Path
from zipfile import ZipFile


import pandas as pd
import psycopg2
import requests
from loguru import logger
from psycopg2.extensions import connection
from psycopg2.extras import execute_values
from tqdm import tqdm

from transform_and_load import code_test as code_test

CODE_URL = "https://zenodo.org/records/3765780/files/data.zip?download=1"
PTBXL_URL = "https://physionet.org/content/ptb-xl/get-zip/1.0.3/"

DBNAME = "clinicalfriction"

def download_zip(url: str, dst: Path):
    """Download a zipped dataset and extract"""
    with tempfile.TemporaryDirectory() as tmpdir:

        tmp_zip = Path(tmpdir) / "data.zip"
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))

        with open(tmp_zip, 'wb') as f, tqdm(
            desc="Downloading",
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                size = f.write(chunk)
                pbar.update(size)

        logger.info(f"Extracting to {dst}...")
        with ZipFile(tmp_zip) as zip_file:
            zip_file.extractall(dst)

    response = requests.get(url)



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


def close_exception(err: BaseException):
    """Close the db connection if an exception occurs"""
    if isinstance(err, psycopg2.Error):
        cur = err.cursor
        conn = cur.connection
        cur.close()
        conn.close()


@logger.catch(reraise=True, onerror=close_exception)
def get_cursor(dbname: str) -> connection:
    conn = psycopg2.connect(dbname=dbname)
    return conn


@logger.catch(reraise=True, onerror=close_exception)
def create_tables(conn: connection):
    """Create code-test and PTB-XL tables"""
    query_file = Path("database/create_db.sql")
    cur = conn.cursor()

    with open(query_file, "r") as f:
        query = f.read()
        cur.execute(query)

    conn.commit()
    cur.close()


def initialize_database(
    code_data_dir: Path,
    ptbxl_data_dir: Path,
    dbname: str
):
    """Populate an existing PSQL database for both experiments"""
    # Create database
    logger.info(f"Creating code-test and PTB-XL tables in database {DBNAME}...")

    conn = get_cursor(DBNAME)

    create_tables(conn)
    annotations = code_data_dir / "data" / "annotations"

    logger.info("Loading code-test annotations into database")
    code_test.load_annotations(conn, annotations / "gold_standard.csv", "gold_lable")
    load_annotations(conn, annotations / "dnn.csv", "dnn_annotations")

    logger.info("Loading code-test ECG tracings into database...")
    code_test.load_tracings(
        conn,
        tracings=code_data_dir / "data" / "ecg_tracings.hdf5",
        attributes=code_data_dir / "data" / "attributes.csv"
    )


    conn.close()

if __name__ == "__main__":
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    code_dir = data_dir / "code-test"
    ptbxl_dir = data_dir / "ptbxl"

    # Download and extract code dataset
    if os.path.exists(code_dir / "data"):
        logger.info(f"CODE-test dataset found in {code_dir}.")
    else:
        logger.info(f"CODE-test doesn't exist, downloading from {CODE_URL}")
        download_zip(CODE_URL, code_dir)

    # Download and extract PTB-XL dataset
    if os.path.exists(ptbxl_dir):
        logger.info(f"PTB-XL already found in {ptbxl_dir}")
    else:
        logger.info(f"Downloading PTB-XL from {PTBXL_URL} (slow)")
        download_zip(PTBXL_URL, ptbxl_dir)
