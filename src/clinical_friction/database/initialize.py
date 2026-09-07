import os
import sys
import tempfile
from pathlib import Path
from zipfile import ZipFile

from importlib import resources

import pandas as pd
import psycopg2
import requests
from dotenv import load_dotenv
from loguru import logger
from psycopg2.extensions import connection
from psycopg2.extras import execute_values
from tqdm import tqdm

import clinical_friction.database.db_connection as db
from clinical_friction.database.transform_and_load import code_test as code_test

CODE_URL = "https://zenodo.org/records/3765780/files/data.zip?download=1"
PTBXL_URL = "https://physionet.org/content/ptb-xl/get-zip/1.0.3/"

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


@logger.catch(reraise=True, onerror=db.close_exception)
def get_cursor(dbname: str) -> connection:
    conn = psycopg2.connect(dbname=dbname)
    return conn


@logger.catch(reraise=True, onerror=db.close_exception)
def create_tables():
    """Create code-test and PTB-XL tables"""
    # Load sql query
    sql_path = resources.files("clinical_friction.database") / "create_db.sql"
    query = sql_path.read_text()

    # Execute on database
    conn = db.db_conn()
    cur = conn.cursor()

    cur.execute(query)

    conn.commit()
    cur.close()
    conn.close()


def initialize_database():
    """Populate an existing PSQL database for both experiments"""

    # Check if database exists
    load_dotenv()
    dbname = os.getenv("DB_NAME")

    if dbname is None:
        logger.error("Couldn't find 'dbname' in environment variables")
        sys.exit()


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

    # Create tables
    logger.info(f"Creating code-test and PTB-XL tables...")
    create_tables()
    annotations = code_dir / "data" / "annotations"

    logger.info("Loading code-test annotations into database")
    code_test.load_annotations(annotations / "gold_standard.csv", "gold_lable")
    code_test.load_annotations(annotations / "dnn.csv", "dnn_annotations")

    logger.info("Loading code-test ECG tracings into database...")
    code_test.load_tracings(
        tracings=code_dir / "data" / "ecg_tracings.hdf5",
        attributes=code_dir / "data" / "attributes.csv"
    )
