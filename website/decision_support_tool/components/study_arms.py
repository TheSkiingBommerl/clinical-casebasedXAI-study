import components.record as pc
import components.ecg as e
import streamlit as st


def baseline(gender, age, ecg):
    """
    the patient data in combination with the AI prediction
    """

    _, col1, _,  _, _ = st.columns([1, 3, 2, 3, 1])

    with col1:

        pc.record("Current Patient", gender, age)

    st.divider()
    
    e.display_ecg(ecg)

def study_arm_1(gender, age, ecg, AI_prediction, certainty):
    """
    the patient data in combination with the AI prediction
    """

    _, col1, _,  _, _ = st.columns([1, 3, 2, 3, 1])

    with col1:

        pc.record("Current Patient", gender, age, diagnosis=AI_prediction, isPrediction=True, certainty=certainty)

    st.divider()
    
    e.display_ecg(ecg)

def study_arm_2(gender, age, ecg, gender_ref, age_ref, diagnosis_ref, ecg_ref):
    """
    the patient data alongside the reference patient
    """

    _, col1, _,  col2, _ = st.columns([1, 3, 2, 3, 1])

    with col1:

        pc.record("Current Patient", gender, age)

    with col2:

        pc.record("Similar Presenting Patient", gender_ref, age_ref, diagnosis_ref, isPrediction=False)

    st.divider()
    
    e.display_ecg_and_ref(ecg, ecg_ref)

def study_arm_3(gender, age, ecg, AI_prediction, certainty, gender_ref, age_ref, diagnosis_ref, ecg_ref):
    """
    the patient data together with the AI prediction and the reference patient
    """

    _, col1, _,  col2, _ = st.columns([1, 3, 2, 3, 1])

    with col1:

        pc.record("Current Patient", gender, age, diagnosis=AI_prediction, isPrediction=True, certainty=certainty)

    with col2:

        pc.record("Similar Presenting Patient", gender_ref, age_ref, diagnosis_ref, False)

    st.divider()
    
    e.display_ecg_and_ref(ecg, ecg_ref)