import os
import sys
import tempfile
from pathlib import Path
from zipfile import ZipFile

from importlib import resources

from huggingface_hub import hf_hub_download
import pandas as pd
import psycopg2
import requests
from dotenv import load_dotenv
from loguru import logger
from psycopg2.extensions import connection
from psycopg2.extras import execute_values
from tqdm import tqdm

from clinical_friction.ecg_embeddings.create_mat import save_signals
from clinical_friction.signal_filtering.filter_all_signals import filter_ptbxl, filter_from_db
from clinical_friction.database.transform_and_load.ptb.filter_datafile import filter_ptbxl_entries
import clinical_friction.database.db_connection as db
from clinical_friction.database.transform_and_load import code_test as code_test
from clinical_friction.database.transform_and_load.ptb.initial_load import (
    load_gold_labels,
    load_records
)

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
    raw_dir = data_dir / "raw"
    raw_dir.mkdir(exist_ok=True, parents=True)
    processed_dir = data_dir / "processed"
    processed_dir.mkdir(exist_ok=True)

    code_dir = data_dir / "raw" / "code-test"
    ptbxl_dir = data_dir / "raw"/ "ptbxl"
    model_dir = data_dir / "raw" / "ecg-model"

    # Download and extract code dataset
    if os.path.exists(code_dir / "data"):
        logger.info(f"CODE-test dataset found in {code_dir}.")
    else:
        logger.info(f"CODE-test doesn't exist, downloading from {CODE_URL}")
        download_zip(CODE_URL, code_dir)

    # Download and extract PTB-XL dataset
    if os.path.exists(ptbxl_dir / "ptb-xl-a-large-publicly-available-electrocardiography-dataset-1.0.3"):
        logger.info(f"PTB-XL already found in {ptbxl_dir}")
    else:
        logger.info(f"Downloading PTB-XL from {PTBXL_URL} (slow)")
        download_zip(PTBXL_URL, ptbxl_dir)

    if os.path.exists(model_dir / "mimic_iv_ecg_finetuned.pt"):
        logger.info(f"finetuned model checkpoint already found in {model_dir}")
    else:
        logger.info(f"Downloading ECG model from HuggingFace")
        hf_hub_download(
            repo_id="wanglab/ecg-fm",
            filename="mimic_iv_ecg_finetuned.pt",
            local_dir=model_dir
        )
    # Create code-test tables
    logger.info(f"Creating code-test tables...")
    create_tables()
    annotations = code_dir / "data" / "annotations"

    # Load code-test data into the database
    logger.info("Loading code-test annotations into database")
    code_test.load_annotations(annotations / "gold_standard.csv", "gold_lable")
    code_test.load_annotations(annotations / "dnn.csv", "dnn_annotations")





    logger.info("Loading code-test ECG tracings into database...")
    code_test.load_tracings(
        tracings=code_dir / "data" / "ecg_tracings.hdf5",
        attributes=code_dir / "data" / "attributes.csv"
    )
    filter_from_db("code-test", processed_dir)



    # Select relevant ECG signals and save to .csv
    logger.info("Extracting relevant PTB-XL signals...")
    ptbxl_raw = ptbxl_dir / "ptb-xl-a-large-publicly-available-electrocardiography-dataset-1.0.3"

    ptbxl_csv = processed_dir / "filtered_ecg_experiment_2.csv"
    ptbxl_entries = filter_ptbxl_entries(ptbxl_raw / "ptbxl_database.csv")
    ptbxl_entries.to_csv(ptbxl_csv, index=False)

    # Load unfiltered PTB-XL ECG's into database
    logger.info("Loading relevant unfiltered PTB-XL signals into database...")
    load_gold_labels(ptbxl_csv)
    load_records(ptbxl_csv, ptbxl_raw)

    # Filter PTB-XL signals
    filter_from_db("ptb-xl", processed_dir)







if __name__ == "__main__":
    initialize_database()
