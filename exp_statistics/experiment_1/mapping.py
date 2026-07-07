"""
Map results to mapping list
"""

import pandas as pd
import ast
from database.useful_queries import get_diagnostics

def map(ranking, only_abn=False, only_norm=False):
    mapping = pd.read_csv("exp_statistics/experiment_1/data/mapping.csv")
    shuffled = pd.read_csv("exp_statistics/experiment_1/data/data_shuffled.csv")  # load shuffled signal IDs
    ranking = ranking.sort_values(by="ecg_index").reset_index(drop=True)

    if only_abn or only_norm:
        id_list = mapping["id"].tolist()
        diagnostics = get_diagnostics(id_list)
        if only_abn:
            keep = diagnostics[~diagnostics["diagnostic"].apply(lambda x: x == ["NO_ABN"])]
        else:
            keep = diagnostics[diagnostics["diagnostic"].apply(lambda x: x == ["NO_ABN"])]
        
        ids = keep["id"]
        mask = mapping["id"].isin(ids)
        mapping = mapping[mask].reset_index(drop=True)
        ranking = ranking[mask.values].reset_index(drop=True)
        shuffled = shuffled[shuffled["id"].isin(ids)].reset_index(drop=True)

    mapping["column_order"] = mapping["column_order"].apply(ast.literal_eval)
    result_rows = []

    for (_, map_row), (_, rank_row), (_, shuf_row) in zip(mapping.iterrows(), ranking.iterrows(), shuffled.iterrows()):
        methods = map_row["column_order"]

        best_pos   = int(rank_row["best"].split()[-1]) - 1
        middle_pos = int(rank_row["middle"].split()[-1]) - 1
        least_pos  = int(rank_row["least"].split()[-1]) - 1

        best_sig   = shuf_row[str(best_pos)]
        middle_sig = shuf_row[str(middle_pos)]
        least_sig  = shuf_row[str(least_pos)]

        if best_sig == middle_sig == least_sig:
            sig_ranks = {best_pos: 2.0, middle_pos: 2.0, least_pos: 2.0}
        elif best_sig == middle_sig:
            sig_ranks = {best_pos: 1.5, middle_pos: 1.5, least_pos: 3}
        elif middle_sig == least_sig:
            sig_ranks = {best_pos: 1, middle_pos: 2.5, least_pos: 2.5}
        elif best_sig == least_sig:
            sig_ranks = {best_pos: 2.0, middle_pos: 2, least_pos: 2.0}
        else:
            sig_ranks = {best_pos: 1, middle_pos: 2, least_pos: 3}

        out = {"id": map_row["id"]}
        for i, method in enumerate(methods, start=1):
            out[method] = sig_ranks[i - 1]
        result_rows.append(out)

    result = pd.DataFrame(result_rows)
    result = result.reindex(columns=["id", "DTW", "In_Population", "Out_Population"])
    final_array = result[["DTW", "In_Population", "Out_Population"]].values.tolist()
    return final_array