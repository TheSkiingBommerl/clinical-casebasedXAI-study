import pandas as pd
import os
import streamlit as st
import dotenv
from pathlib import Path


dotenv.load_dotenv()

required_vars = ["FLOCHALLENGE", "FLO_RESULTS", "FLO_FLASK_BASE"]

for var in required_vars:
    if var not in os.environ:
        raise RuntimeError(f"Variable {var} not found in environment variables!")

root = Path(os.environ["FLO_RESULTS"]) / "flags"
root.mkdir(exist_ok=True, parents=True)

def load_flags(user):
    flags_csv = root / f"flags_{user}.csv"
    if os.path.exists(flags_csv):
        df = pd.read_csv(flags_csv)
        return set(df["Patient"].tolist())
    return set()

def save_flags(user):
    flags_csv = root / f"flags_{user}.csv"
    df = pd.DataFrame({"Patient": list(st.session_state.flagged_patients)})
    df.to_csv(flags_csv, index=False)

def flag_button(patient_index, user):
    is_flagged = patient_index in st.session_state.flagged_patients
    label = "Flagged" if is_flagged else "Flag Patient"
    if st.button(label, type="secondary"):
        if is_flagged:
            st.session_state.flagged_patients.discard(patient_index)
        else:
            st.session_state.flagged_patients.add(patient_index)
        save_flags(user)
        st.rerun()