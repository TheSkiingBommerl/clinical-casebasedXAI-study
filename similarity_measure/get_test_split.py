"""
Randomly choose ids for Experiment 1
"""

from database.db_connection import extract_data
from database.useful_queries import get_diagnostics
import pandas as pd


query = """
    SELECT id
    FROM "code-15".gold_lable   
    """

rows = extract_data(query)
ids = [row[0] for row in rows]

diagnostic = get_diagnostics()

norm_df = diagnostic[diagnostic["diagnostic"].apply(lambda x: x == ["NO_ABN"])]
_1dAVb_df = diagnostic[diagnostic["diagnostic"].apply(lambda x: x == ["1dAVb"])]
lbbb_df = diagnostic[diagnostic["diagnostic"].apply(lambda x: x == ["LBBB"])]

norm_df = norm_df.sample(n=10, random_state=42) 
_1dAVb_df = _1dAVb_df.sample(n=10, random_state=42) 
lbbb_df = lbbb_df.sample(n=11, random_state=42) 

df = pd.concat(
    [norm_df["id"], _1dAVb_df["id"], lbbb_df["id"]],
    ignore_index=True
).to_frame(name="ids")

df.to_csv("similarity_measure/results/ids_experiment_1.csv", index=False)
