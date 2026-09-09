import streamlit as st
import streamlit.components.v1 as components
import os

LEAD_NAMES = ["DI", "DII", "DIII", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"]
CACHE_DIR  = "data/cached_plots"

SPINNER_HTML = """
<div id="ecg-loader" style="
    display:flex; align-items:center; justify-content:center; gap:10px; padding:20px;
    color:#000000; font-family:monospace; font-size:13px;
">
    <div style="display:flex; gap:6px;">
        <div style="width:8px;height:8px;border-radius:50%;background:#000000;
            animation:p 1s ease-in-out infinite;"></div>
        <div style="width:8px;height:8px;border-radius:50%;background:#000000;
            animation:p 1s ease-in-out .2s infinite;"></div>
        <div style="width:8px;height:8px;border-radius:50%;background:#000000;
            animation:p 1s ease-in-out .4s infinite;"></div>
    </div>
    Loading ECG...
    <style>@keyframes p{0%,100%{opacity:.2;transform:scale(1)}50%{opacity:1;transform:scale(1.4)}}</style>
</div>
"""


@st.cache_resource
def load_lead_html(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def get_lead_path(ecg_id: str, i: int) -> str:
    user    = st.user.get("preferred_username")
    dataset = user.split("_")[-1]
    bubu    = st.session_state.patient_index
    return f"{CACHE_DIR}/{dataset}/{bubu}/{ecg_id}/lead_{i}.html"


def plot_ecg_cached(ecg_id: str) -> None:
    for i in range(len(LEAD_NAMES)):
        html = load_lead_html(get_lead_path(ecg_id, i))
        components.html(html, height=340, scrolling=False)


def set_reference(idx):
    st.session_state.reference_index = idx


@st.fragment
def display_ecg_and_ref(patient_id: str = "patient", reference_id: str = "reference"):
    _, col1, col2, col3, _ = st.columns([2, 2, 3, 2, 2])
    with col1:
        st.button("Patient ECG",
                  type="primary" if st.session_state.reference_index == 1 else "secondary",
                  on_click=set_reference, args=(1,), use_container_width=True)
    with col2:
        st.button("Patient ECG   |   Similar ECG",
                  type="primary" if st.session_state.reference_index == 2 else "secondary",
                  on_click=set_reference, args=(2,), use_container_width=True)
    with col3:
        st.button("Similar ECG",
                  type="primary" if st.session_state.reference_index == 3 else "secondary",
                  on_click=set_reference, args=(3,), use_container_width=True)

    loading = st.empty()
    loading.markdown(SPINNER_HTML, unsafe_allow_html=True)

    if st.session_state.reference_index == 1:
        plot_ecg_cached(patient_id)
    elif st.session_state.reference_index == 2:
        for i in range(len(LEAD_NAMES)):
            pat_html = load_lead_html(get_lead_path(patient_id, i))
            ref_html = load_lead_html(get_lead_path(reference_id, i))
            col_left, col_right = st.columns(2)
            with col_left:
                components.html(pat_html, height=340, scrolling=False)
            with col_right:
                components.html(ref_html, height=340, scrolling=False)
    elif st.session_state.reference_index == 3:
        plot_ecg_cached(reference_id)

    loading.empty()


@st.fragment
def display_ecg(patient_id: str = "patient"):
    plot_ecg_cached(patient_id)