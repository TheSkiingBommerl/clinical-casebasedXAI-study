"""
Randomly choose ids for Experiment 1
"""

from AI_diagnostic_support.database.db_connection import extract_data
from AI_diagnostic_support.database.useful_queries import get_diagnostics
import pandas as pd


SEED = 42

def get_test_split() -> pd.DataFrame:
    """Randomly select ECG id's from code-test"""

    query = """
        SELECT id
        FROM "code-test".gold_lable
        """

    rows = extract_data(query)
    ids = [row[0] for row in rows]

    diagnostic = get_diagnostics()

    norm_df = diagnostic[diagnostic["diagnostic"].apply(lambda x: x == ["NO_ABN"])]
    _1dAVb_df = diagnostic[diagnostic["diagnostic"].apply(lambda x: x == ["1dAVb"])]
    lbbb_df = diagnostic[diagnostic["diagnostic"].apply(lambda x: x == ["LBBB"])]

    norm_df = norm_df.sample(n=10, random_state=SEED)
    _1dAVb_df = _1dAVb_df.sample(n=10, random_state=SEED)
    lbbb_df = lbbb_df.sample(n=11, random_state=SEED)

    df = pd.concat(
        [norm_df["id"], _1dAVb_df["id"], lbbb_df["id"]],
        ignore_index=True
    ).to_frame(name="ids")
    return df

    #df.to_csv("similarity_measure/results/ids_similarity_comparison.csv", index=False)
