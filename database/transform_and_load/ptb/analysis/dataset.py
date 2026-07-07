"""
This file gives basic dataset information about the filter PTB-XL dataset
"""

import pandas as pd

df = pd.read_csv("database/transform_and_load/ptb/datasets/filtered_ecg_experiment_2.csv")
df = df[df["age"] <= 95]

print(len(df))

print(
    df["age"].min(), 
    df["age"].max(), 
    len(df[df["sex"] == 0]),
    len(df[df["sex"] == 1]),
    len(df[df["labels"].apply(lambda x: "NORM" in x)]),
    len(df[df["labels"].apply(lambda x: "NORM" not in x)])
)