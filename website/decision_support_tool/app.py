import streamlit as st
from components.study_arms import baseline, study_arm_1, study_arm_2, study_arm_3
from components.diagnosis import diagnosis
from components.flag_button import flag_button, load_flags
from helpers.load_parquets import load_case
from components.sidebar import sidebar, init_sidebar_state
from components.scroll_to_top import scroll_to_top
from components.questionnaire import questionnaire, disable_questionnaire
from components.state import get_resume_state
from components.intro import intro, privacy, screenrecording
import csv
import os
import dotenv
from pathlib import Path
from components.recorder import recorder_button, stop_recording
import pandas as pd
import datetime

dotenv.load_dotenv()

required_vars = ["FLOCHALLENGE", "FLO_RESULTS", "FLO_FLASK_BASE"]

for var in required_vars:
    if var not in os.environ:
        raise RuntimeError(f"Variable {var} not found in environment variables!")

root = Path(os.environ["FLO_RESULTS"]) / "results"
root.mkdir(exist_ok=True, parents=True)

@st.cache_data
def get_data(user, index: int) -> dict:
    return load_case(user, index)

# Heart Emoij from: https://emojipedia.org/anatomical-heart
st.set_page_config(
    page_title="ECG Viewer", page_icon="🫀", layout="wide", initial_sidebar_state="expanded"
)

if not st.user.is_logged_in:
    st.markdown(
        """
        <style>
        div.stButton > button {
            display: block;
            margin: 0 auto;
            width: 200px;
            height: 50px;
            font-size: 20px;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

    st.title("Welcome to the ECG Viewer 🫀")
    st.write("Please press the button below to log in.")

    if st.button("Log in"):
        st.login()
    st.stop()

if st.user.is_logged_in:
    user = st.user.get("preferred_username")

    if "page" not in st.session_state:
        page = get_resume_state(user)
        st.session_state.page = page

    # Introduction Page
    if st.session_state.page == "start":
        st.title("Introduction 🫀")
        intro()
        privacy()

        st.header("Level of expertise")
        
        st.markdown(
                "<p style='font-size: 20px;'>What is your current position?</p>",
                unsafe_allow_html=True,
            )
        text_input = st.text_input(
            "", placeholder="e.g. Resident (Cardiology)", label_visibility="collapsed"
        )

        st.divider()

        st.markdown("""
        <style>
            [data-testid="stCheckbox"] p {
                font-weight: bold;
            }
        </style>
        """, unsafe_allow_html=True)
        

        col1, _, col3 = st.columns([6, 1, 1])


        with col1:

            consent_text = "I consent to the collection, use, and storage of data generated during this study, including my self-reported level of expertise, my responses to the signal comparison tasks, and, where applicable, screen recordings captured during the experiment. The findings derived from the collected data may be used in a master's thesis and in publications resulting from this research."
            agree = st.checkbox(f'{consent_text}')
            

        with col3:
            st.markdown(
                "<p style='font-size: 20px; margin-top: 4px;'</p>", unsafe_allow_html=True
            )
            if st.button(
                "Start →", type="primary", disabled=(not text_input.strip() or not agree), use_container_width=True
            ):

                user_path = root / str(user)
                user_path.mkdir(exist_ok=True, parents=True)
                file_path = user_path / f"responses_{user}.csv"

                file_exists = os.path.isfile(file_path)
                with open(file_path, "a", newline="") as f:
                    writer = csv.writer(f)
                    if not file_exists:
                        writer.writerow(["position"])
                    writer.writerow([text_input.strip()])

                file_path = root / user / f"progress_{user}.csv"

                file_exists = os.path.isfile(file_path)
                with open(file_path, "w", newline="") as f:
                    writer = csv.writer(f)
                    if not file_exists:
                        writer.writerow(["status"])
                    writer.writerow(["in_progress"])

                st.session_state.page = "main"
                st.session_state.scroll_to_top = True
                st.rerun()

    # Decision Support Tool
    if st.session_state.page == "main":

        dataset = user.split("_")[-1]

        folder = Path(f"data/{dataset}")
        patient_count = len(list(folder.glob("*.parquet")))

        patients = {}

        for i in range(patient_count):
            key = f"Patient {i+1}"

            patients[key] = i
        
        patient_keys = list(patients.keys())

        if "patient_index" not in st.session_state:
            st.session_state.patient_index = 0

        st.session_state.reference_index = 2
        if "flagged_patients" not in st.session_state:
            st.session_state.flagged_patients = load_flags(user)

        # Sidebar
        init_sidebar_state()
        sidebar(patient_keys)

        # Page
        if st.session_state.get("scroll_to_top"):
                    scroll_to_top()
                    st.session_state.scroll_to_top = False

        if st.session_state.current_section == "information":
            st.title("Introduction 🫀")
            screenrecording()
            recorder_button(user)
            intro()
            col = st.columns([4, 1, 4])[1]
            with col:
                if st.button("⬇", use_container_width=True):
                    st.session_state.current_section = "patient"
                    st.session_state.scroll_to_top = True
                    st.rerun()

        elif st.session_state.current_section == "patient":
            flag_button(st.session_state.patient_index, user)
            record = get_data(user, patients[patient_keys[st.session_state.patient_index]])
            st.markdown("""
            <style>
            .centered-title { font-size: 30px !important; font-weight: bold; text-align: center; }
            </style>
            """, unsafe_allow_html=True)
            st.markdown(f'<p class="centered-title">Patient {st.session_state.patient_index + 1}</p>', unsafe_allow_html=True)
            st.divider()

            if record["study_arm"] == 0:
                baseline(record["gender"], record["age"], "patient")
            if record["study_arm"] == 1:
                # because we use prerendered ecgs use "patient" instead of passing the whole patient ecg
                study_arm_1(record["gender"], record["age"], "patient", record["prediction"], record["certainty"])
            if record["study_arm"] == 2:
                study_arm_2(record["gender"], record["age"], "patient", record["gender_ref"], record["age_ref"], record["diagnosis_ref"], "reference")
            if record["study_arm"] == 3:
                study_arm_3(record["gender"], record["age"], "patient", record["prediction"], record["certainty"], record["gender_ref"], record["age_ref"], record["diagnosis_ref"], "reference")

            st.divider()
            diagnosis()

            st.markdown("<br>" * 2, unsafe_allow_html=True)
            is_last = st.session_state.patient_index >= len(patient_keys) - 1

            col = st.columns([4, 1, 4])[1]
            with col:
                if not is_last:
                    if st.button("⬇", use_container_width=True, help="Next patient"):
                        st.session_state.patient_index += 1
                        st.session_state.scroll_to_top = True
                        st.rerun()
                if is_last:
                    disable = disable_questionnaire(root, user, patient_count)
                    if st.button("⬇", disabled=disable, use_container_width=True, help="Questionnaire"):
                        st.session_state.current_section = "questionnaire"
                        st.session_state.scroll_to_top = True
                        st.rerun()
                    
        elif st.session_state.current_section == "questionnaire":
            all_filled, survey = questionnaire()
            disable = True
            if all_filled:
                disable = False

            col = st.columns([4, 1, 4])[1]
            with col:
                if st.button("Submit", disabled=disable, use_container_width=True):
                    st.session_state.scroll_to_top = True
                    st.session_state.page = "submitted"
                    
                    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    data = {key: val["value"] for key, val in survey.data.items()}
                    data["time"] = now
                    df = pd.DataFrame([data])
                    df.to_csv(root / user / f"survey_data_{user}.csv", mode="a", header=not pd.io.common.file_exists(root / f"survey_data_{user}.csv"), index=False)
                    
                    file_path = root / user / f"progress_{user}.csv"
                    with open(file_path, "w", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(["status"])  # re-write header
                        writer.writerow(["done"])

                    st.rerun()

    # Log out page
    if st.session_state.page == "submitted":
        stop_recording(user)

        st.success("Thank you! Your responses have been submitted.")
        if st.button("Log out"):
            st.logout()



