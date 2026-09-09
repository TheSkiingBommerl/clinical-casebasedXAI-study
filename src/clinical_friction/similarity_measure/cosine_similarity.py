"""
Find most similar ECG signals using cosine similarity
"""
from typing import Literal
from pathlib import Path
from loguru import logger
from clinical_friction.database.useful_queries import get_embeddings
from tqdm import tqdm
import numpy as np
import csv


def cosine_sim(a, b):
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)

    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def get_similar_signals(embeddings, signal_id):

    embedding_ids = embeddings["id"].tolist()
    embedding_rows = embeddings["embedding"]

    target = embedding_ids.index(signal_id)
    del embedding_ids[target]
    target_signal = embedding_rows.pop(target)

    results = []

    for i, signal in enumerate(embedding_rows):
        similarity_score = cosine_sim(signal, target_signal)
        results.append((embedding_ids[i], similarity_score))

    best_id, best_sim = max(results, key=lambda x: x[1])

    return best_id, best_sim

def get_ref(patient_id, dataset, id_subset):
    embeddings = get_embeddings(tablename="aed_model_embeddings", dataset=dataset, ids=id_subset)
    best_id, _ = get_similar_signals(embeddings, patient_id)
    return best_id


def find_similar_embeddings(
    samples: list[int],
    table: Literal["fm_model_embeddings", "aed_model_embeddings"],
    dst_dir: Path
):
    """Fetch embeddings from a table and find most similar signals"""
    embeddings = get_embeddings(table, dataset="code-test", ids=samples)
    for sample in tqdm(samples):
        best_id, best_sim = get_similar_signals(embeddings, sample)

        with open(dst_dir / f"{sample}.csv", "w", newline="") as f:
            writer = csv.writer(f)
            results = (sample, best_id, best_sim)
            writer.writerow(results)
