from database.db_connection import store_data

label_mapping = {
    "1AVB": "1dAVb",
    "CRBBB": "RBBB",
    "CLBBB": "LBBB",
    "SBRAD": "SB",
    "AFIB": "AF",
    "STACH": "ST"
}

columns = ["1dAVb", "RBBB", "LBBB", "SB", "AF", "ST"]

import ast

def has_invalid_labels(label_str):
    labels = ast.literal_eval(label_str)
    
    # remove IRBBB & ILBBB -> taking CRBBB as RBBB because it is a clear RBBB
    if any(label in ["IRBBB", "ILBBB"] for label in labels):
        return True
    
    # remove everything where Norm is together with other lables -> doesn't make sense
    if "NORM" in labels and len(labels) > 1:
        return True
    
    return False

def encode_labels(label_str):
    labels = ast.literal_eval(label_str)
    
    row = dict.fromkeys(columns, 0)
    
    if labels != ["NORM"]:
        for label in labels:
            if label in label_mapping:
                col = label_mapping[label]
                row[col] = 1
                
    return row

import pandas as pd

df = pd.read_csv("database/transform_and_load/ptb/datasets/filtered_ecg_experiment_2.csv")

df = df[~df["labels"].apply(has_invalid_labels)].reset_index(drop=True)

encoded = df["labels"].apply(encode_labels)
encoded_df = pd.DataFrame(list(encoded))

df = pd.concat([df, encoded_df], axis=1)

data = [tuple(int(x) for x in row) for row in df[["ecg_id"] + columns].values]

query = """
INSERT INTO "ptb-xl".gold_lable (id, "1dAVb", rbbb, lbbb, sb, af, st)
VALUES %s
"""

store_data(query, data)