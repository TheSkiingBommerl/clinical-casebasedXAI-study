import pandas as pd
import numpy as np
import io
import pickle
from clinical_friction.database.useful_queries import get_ecg_signals, get_patient_info, get_diagnostics, get_certainty
from clinical_friction.database.db_connection import extract_data
from clinical_friction.similarity_measure.cosine_similarity import get_ref
import os
from pathlib import Path
from tqdm import tqdm

def ecg_to_bytes(ecg: np.ndarray) -> bytes:
    buf = io.BytesIO()
    np.save(buf, ecg)
    return buf.getvalue()

def bytes_to_ecg(b: bytes) -> np.ndarray:
    return np.load(io.BytesIO(b))

def df_to_bytes(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    df.to_parquet(buf, index=False)
    return buf.getvalue()

def bytes_to_df(b: bytes) -> pd.DataFrame:
    return pd.read_parquet(io.BytesIO(b))

def list_to_bytes(lst: list) -> bytes:
    return pickle.dumps(lst)

def bytes_to_list(b: bytes) -> list:
    return pickle.loads(b)


def save_mapping(patient_id, ref_id, dataset, index, study_arm, dataset_nr, dst: Path):
    filepath = dst / str(dataset_nr) / "mapping"
    new_row = {
        "index": index,
        "study_arm": study_arm,
        "dataset": dataset,
        "patient_id": patient_id,
        "ref_id": ref_id
    }

    df_new = pd.DataFrame([new_row])

    if os.path.exists(filepath):
        df_new.to_csv(filepath, mode="a", header=False, index=False)
    else:
        df_new.to_csv(filepath, mode="w", header=True, index=False)


def save_case(dst: Path, dataset_nr: int, index: int, study_arm: int, age: int, gender: str,
              ecg: np.ndarray, age_ref: int = None, gender_ref: int = None, ecg_ref: np.ndarray = None, diagnosis_ref: list = None,
              prediction: list = None, certainty: list = None):

    row = {
        "study_arm":  study_arm,
        "age":        age,
        "gender":     gender,
        "prediction": list_to_bytes(prediction) if prediction is not None else None,
        "certainty": list_to_bytes(certainty) if certainty is not None else None,
        "ecg":      ecg_to_bytes(ecg),
        "age_ref":   age_ref,
        "gender_ref": gender_ref,
        "ecg_ref":      ecg_to_bytes(ecg_ref) if ecg_ref is not None else None,
        "diagnosis_ref": list_to_bytes(diagnosis_ref) if diagnosis_ref is not None else None
    }

    path = dst / str(dataset_nr)
    path.mkdir(exist_ok=True)
    pd.DataFrame([row]).to_parquet(path / f"{index}.parquet", index=False)

def get_annotations(patient_ids, dataset, tablename):
    placeholders = ",".join(["%s"] * len(patient_ids))
    query = f"""
        Select "1dAVb", rbbb, lbbb, sb, af, st
        FROM "{dataset}".{tablename}
        WHERE id IN ({placeholders})
        """
    rows = extract_data(query, patient_ids)

    return [row for row in rows[0]]

def get_data(patient_id, ref_id, dataset, index, study_arm, dataset_nr, dst: Path):
    """
    get_data_for_one_patient
    """

    save_mapping(patient_id, ref_id, dataset, index, study_arm, dataset_nr, dst)

    abnormalities = ["1dAVb", "rbbb", "lbbb", "sb", "af", "st"]

    patient_info = get_patient_info(patient_id, dataset)
    gender = patient_info["gender"].values[0]
    age = patient_info["age"].values[0]

    ecg = get_ecg_signals(patient_id, dataset, filtered=True)
    ecg = ecg["signal"].values[0]

    if study_arm == 0:
        save_case(dst, dataset_nr, index, study_arm, age, gender, ecg, None, None, None, None, None, None)
        return

    pred = get_annotations(patient_id, dataset, "dnn_annotations")

    certainty = get_certainty(patient_id, dataset)
    certainty = [np.round(((1 - np.sqrt(certainty[abn].values[0])) * 100), 1) for abn in abnormalities]

    if study_arm == 1:
        save_case(dst, dataset_nr, index, study_arm, age, gender, ecg, None, None, None, None, pred, certainty)
        return

    diagnosis_ref = get_diagnostics(ref_id, dataset, tablename="gold_lable")
    diagnosis_ref = diagnosis_ref["diagnostic"].values[0]

    patient_info = get_patient_info(ref_id, dataset)
    gender_ref = patient_info["gender"].values[0]
    age_ref = patient_info["age"].values[0]

    ecg_ref = get_ecg_signals(ref_id, dataset, filtered=True)
    ecg_ref = ecg_ref["signal"].values[0]

    if study_arm == 2:
        save_case(dst, dataset_nr, index, study_arm, age, gender, ecg, age_ref, gender_ref, ecg_ref, diagnosis_ref, None, None)
        return

    if study_arm == 3:
        save_case(dst, dataset_nr, index, study_arm, age, gender, ecg, age_ref, gender_ref, ecg_ref, diagnosis_ref, pred, certainty)
        return

def get_experiment_ids(dataset, valid_ids):

    goldlabels = get_diagnostics(dataset=dataset, tablename="gold_lable", patient_ids=valid_ids)
    dnn_ann = get_diagnostics(dataset=dataset, tablename="dnn_annotations", patient_ids=valid_ids)

    merged = goldlabels.merge(dnn_ann, how="inner", on="id", suffixes=("_gold", "_dnn"))

    merged["diagnostic_match"] = merged["diagnostic_gold"] == merged["diagnostic_dnn"]

    matches = merged[merged["diagnostic_match"]]

    norm_matches = matches[matches["diagnostic_gold"].apply(lambda x: x == ["NO_ABN"])].sample(4, random_state=None)

    one_abnormality = matches[
        matches["diagnostic_gold"].apply(
            lambda x: x != ["NO_ABN"] and len(x) == 1
        )
    ].sample(10, random_state=None)

    multiple_abnormalities = matches[
        matches["diagnostic_gold"].apply(
            lambda x: x != ["NO_ABN"] and len(x) > 1
        )
    ].sample(6, random_state=None)

    final_sample = pd.concat([norm_matches, one_abnormality, multiple_abnormalities])

    ids = final_sample["id"].tolist()
    np.random.shuffle(ids)
    return ids


def generate_assignments(ids, arms, n_lists=8, seed=42):
    """
    This function was generated by Sonnet 4.8 and uses Latin square to generate the arm assignments
    """
    ids  = list(ids)
    arms = list(arms)
    n, k = len(ids), len(arms)

    if n % k:
        raise ValueError(f"len(ids)={n} must be divisible by len(arms)={k}")
    if n_lists % k:
        raise ValueError(f"n_lists={n_lists} must be divisible by len(arms)={k}")
    if n_lists > 2 * k:
        raise ValueError(f"This construction supports at most 2×len(arms)={2*k} lists.")

    offsets = list(range(k)) * (n // k)

    #random.Random(seed).shuffle(offsets)
    #print("offset", offsets)

    result = []
    for j in range(n_lists):
        # for every list
        # list_idx % len(arms)
        round_ = j // k   # 0 = first k lists,  1 = second k lists
        slot   = j % k    # position within the round

        row = []
        for i in range(n):
            a = offsets[i]
            if round_ == 0:
                # Right-cyclic Latin square
                idx = (a + slot) % k
            else:
                # Left-cyclic Latin square — provably distinct from all round-0 lists
                idx = (k - 1 - a + slot) % k

            #print(f"id: {j} {i}, round: {round_}, slot: {slot}, a:{a}, idx: {idx}")
            row.append(arms[idx])

        result.append(row)

    return result


def randomnize_data(dataset, study_arms, dataset_nr, ids, valid_ids, dst: Path):
    """
    Get random 20 samples where all are predicted correctly by the model.
    And out of the 16 samples 4 have abnormalitites and 2 don't.
    """

    for idx, arm in enumerate(study_arms):
        if arm == 2 or arm == 3:
            valid_ids = valid_ids + [ids[idx]]
            ref_id = get_ref(ids[idx], dataset, id_subset=valid_ids)
            get_data([ids[idx]], ref_id = [ref_id], dataset=dataset, index=idx, study_arm=arm, dataset_nr = dataset_nr, dst=dst)
        else:
            get_data([ids[idx]], ref_id = None, dataset=dataset, index=idx, study_arm=arm, dataset_nr = dataset_nr, dst=dst)


def generate_tool_parquets(filtered_csv_path: Path, website_dir: Path):
    df = pd.read_csv(filtered_csv_path)
    df = df[df["age"] <= 95]
    valid_ids = df["ecg_id"].tolist()
    dataset = "ptb-xl"
    nr_exp_datasets = 8
    exp_ids = get_experiment_ids(dataset, valid_ids=valid_ids)
    assignments = generate_assignments(ids = exp_ids, arms = [0, 1, 2, 3], n_lists = nr_exp_datasets)

    valid_ids = list(set(valid_ids) - set(exp_ids))


    for idx, assignment in tqdm(enumerate(assignments), total=len(assignments)):
        dst = website_dir / str(idx)
        dst.mkdir(exist_ok=True)

        randomnize_data(dataset, assignment, dataset_nr=idx, ids=exp_ids, valid_ids=valid_ids, dst=website_dir)

if __name__ == '__main__':

    dataset = "ptb-xl"

    df = pd.read_csv("database/transform_and_load/ptb/datasets/filtered_ecg_experiment_2.csv")
    df = df[df["age"] <= 95]
    valid_ids = df["ecg_id"].tolist()

    print("valid ids", len(valid_ids))

    nr_exp_datasets = 8
    exp_ids = get_experiment_ids(dataset, valid_ids=valid_ids)

    assignments = generate_assignments(ids = exp_ids, arms = [0, 1, 2, 3], n_lists = nr_exp_datasets)
    print("exp ids", len(exp_ids))
    valid_ids = list(set(valid_ids) - set(exp_ids))
    print("valid ids", len(valid_ids))

    for idx, assignment in enumerate(assignments):
        os.makedirs(f"website/decision_support_tool/data/{idx}", exist_ok=True)
        randomnize_data(dataset, assignment, dataset_nr=idx, ids=exp_ids, valid_ids=valid_ids)
