import os
from datetime import datetime
from pathlib import Path

import dotenv
import pandas as pd
import streamlit as st
from streamlit_sortables import sort_items
from clinical_friction.helpers.login_bypass import is_bypassed

dotenv.load_dotenv()


def save_ranking():
    row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ecg_index": st.session_state.page_index,
        "best": st.session_state.ranking[0],
        "middle": st.session_state.ranking[1],
        "least": st.session_state.ranking[2],
    }
    df_new = pd.DataFrame([row])
    user_bypass = is_bypassed()
    if user_bypass is None:
        user = st.user.get("preferred_username")
    else:
        user = user_bypass

    root = Path(os.environ["CF_DATA_DIR"]) / "results" /  "similarity_comparison"

    ranking_csv = root / user / f"ranking_data_{user}.csv"
    if os.path.exists(ranking_csv):
        df_new.to_csv(ranking_csv, mode="a", header=False, index=False)
    else:
        df_new.to_csv(ranking_csv, index=False)
    st.session_state.ranking_saved = True


@st.fragment
def ranking_section():
    sorted_items = sort_items(
        st.session_state.ranking,
        direction="vertical",
        key=f"ranking_{st.session_state.page_index}",
    )
    st.session_state.ranking = sorted_items

    _, save_col, _ = st.columns([3, 1, 3])
    with save_col:
        if st.button("Save", type="primary", use_container_width=True):
            save_ranking()
            st.rerun(scope="app")
