"""
Find most similar ECG signals using cosine similarity
"""
from clinical_friction.database.useful_queries import get_embeddings
import numpy as np
import csv

# In domain embeddings
results_folder = "emb_id"
db_table_name = "AED_model_embeddings"

#Out of domain embeddings
# results_folder = "emb_ood"
# db_table_name = "FM_model_embeddings"

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
    embeddings = get_embeddings(tablename="AED_model_embeddings", dataset=dataset, ids=id_subset)
    best_id, _ = get_similar_signals(embeddings, patient_id)
    return best_id


if __name__ == '__main__':
    # ids used for experiment 1 - produced by get_test_split.py
    samples = [...]

    embeddings = get_embeddings(db_table_name)

    for sample in samples:
        best_id, best_sim = get_similar_signals(embeddings, sample)
        print(sample, best_id, best_sim)

        with open(f"similarity_measure/results/{results_folder}/{sample}.csv", "w", newline="") as f:
            writer = csv.writer(f)
            results = (sample, best_id, best_sim)
            writer.writerow(results)
