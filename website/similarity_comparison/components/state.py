import os
import pandas as pd
from pathlib import Path

root = Path(os.environ["CF_DATA_DIR"]) / "results" /  "similarity_comparison"

def get_resume_state(user, total):

    response_csv = root / user / f"responses_{user}.csv"
    if not os.path.exists(response_csv):
        return "start", 0

    ranking_csv = root / user / f"ranking_data_{user}.csv"
    if not os.path.exists(ranking_csv):
        return "main", 0

    df = pd.read_csv(ranking_csv)
    if df.empty:
        return "main", 0

    last_saved = int(df["ecg_index"].max())
    next_index = last_saved + 1

    if next_index >= total:
        return "submitted", total - 1

    return "main", next_index
