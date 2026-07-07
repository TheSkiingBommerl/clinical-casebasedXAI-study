import os
import pandas as pd
from pathlib import Path

root = Path(os.environ["FLO_RESULTS"]) / "results"

def get_resume_state(user):

    progress_csv = root / user / f"progress_{user}.csv"

    if not os.path.exists(progress_csv):
        return "start"
    
    df = pd.read_csv(progress_csv)
    if df.empty:
        return "start"
    
    status = str(df["status"].iloc[-1])

    if status == "in_progress":
        return "main"
    

    if status == "done":
        return "submitted"


