import streamlit_survey as ss
import streamlit as st
import os
import pandas as pd

def con():
    text = """
        <div style="border: 2px solid black; border-radius: 8px; padding: 1.2rem;">
        <p style="font-weight: 700; margin: 0 0 1rem 0; font-size: 1rem; text-align: center;">Configurations</p>
            <b>Baseline:</b> diagnosis based on solily patient data (age, gender, 12 lead ECG). <br>
            <b>Study Arm 1:</b> diagnosis based on patient data in combination with an AI diagnositc prediction. <br>
            <b>Study Arm 2:</b> diagnosis based on patient data alongside the reference patient. <br>
            <b>Study Arm 3:</b> diagnosis based on patient data together with the AI prediction and the reference patient.
        </div>"""
    
    st.markdown(f'<p style="font-size: 20px;">{text}</p>', unsafe_allow_html=True)

def style(Question):
    st.markdown(f"<p style='font-size: 20px; font-weight: 500;'>{Question}</p>", unsafe_allow_html=True)

def disable_questionnaire(root, user, patient_count):

    diagnosis_csv = root / user / f"diagnosis_{user}.csv"
    if os.path.exists(diagnosis_csv):
        df = pd.read_csv(diagnosis_csv)
        if not df.empty:
            saved_patients = set(df["Patient"].astype(int).unique())
            expected_patients = set(range(patient_count))
            all_saved = expected_patients.issubset(saved_patients)

            # TODO: add that if diagnosis was selected and disselected that it will stay disabled (entry is there but all diagnosises are False)
            
            if all_saved:
                return False
    return True

def questionnaire():
    st.title("Questionnaire")
    st.write("")
    st.subheader("General")
    survey = ss.StreamlitSurvey()
    
    # What was the subjective experience of junior clinicians using the tool and which configurations do they prefer?
    col_1, col_2 = st.columns([3,2])
    with col_1:
        question1 = "Which configuration did you prefer?"
        style(question1)
        answer1 = survey.selectbox(question1, options=["Baseline", "Study Arm 1", "Study Arm 2", "Study Arm 3"], label_visibility="collapsed", id="Q1")
        question2 = "What was your experience with the tool?"
        style(question2)
        answer2 = survey.text_area(question2, label_visibility="collapsed", id="Q2")
        question3 = "If the correct diagnosis had been provided after every patient case, this tool would have helped me during my earlier years of study to become more familiar with ECG signals:"
        style(question3)
        _, col_middle, _ = st.columns([1,3,1])
        with col_middle:
            answer3 = survey.segmented_control(question3, options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"], label_visibility="collapsed", id="Q3")
        st.write("")
        question8 = "The ECG signals were easy to read and representative of ECGs I am used to interpreting:"
        style(question8)
        _, col_middle, _ = st.columns([1,3,1])
        with col_middle:
            answer8 = survey.segmented_control(question3, options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"], label_visibility="collapsed", id="Q8")
        st.write("")
        question9 = "How would you rate the difficulty of the task?"
        style(question9)
        answer9 = survey.select_slider(question9, options=["Very Hard", "Hard", "Doable", "Easy", "Very Easy"], label_visibility="collapsed", id="Q9")
        st.write("")
        question10 = "How often do you encounter/work with ECGs in your daily life?"
        style(question10)
        answer10 = survey.segmented_control(question9, options=["Several times per week", "Several times per month", "Several times per year", "I used to encounter ECGs frequently, but not anymore", "Only a few times throughout my studies and career"], label_visibility="collapsed", id="Q10")

        
        st.subheader("AI Prediction")
        question4 = "I trusted the AI prediction:"
        style(question4)
        _, col_middle, _ = st.columns([1,3,1])
        with col_middle:
            answer4 = survey.segmented_control(question4, options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"], label_visibility="collapsed", id="Q4")
        st.write("")
        question5 = "What factors made you trust or distrust the AI's prediction?"
        style(question5)
        answer5 = survey.text_area(question5, label_visibility="collapsed", id="Q5")
        
        st.subheader("Reference patient")
        question6 = "The reference patient was helpful in guiding my diagnostic decision:"
        style(question6)
        _, col_middle, _ = st.columns([1,3,1])
        with col_middle:
            answer6 = survey.segmented_control(question6, options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"], label_visibility="collapsed", id="Q6")
        st.write("")
        question7 = "In general, I found the signals from the reference patient to be similar to the signal I was asked to diagnose:"
        style(question7)
        _, col_middle, _ = st.columns([1,3,1])
        with col_middle:
            answer7 = survey.segmented_control(question7, options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"], label_visibility="collapsed", id="Q7")
        st.write("")
        question11 = "When both an AI prediction and a reference patient were presented, which did you trust more in forming your diagnosis?"
        style(question11)
        _, col_middle, _ = st.columns([1,3,1])
        with col_middle:
            answer11 = survey.segmented_control(question11, options=["AI prediction", "Reference patient", "Both", "Neither"], label_visibility="collapsed", id="Q11")

        
    with col_2:
        con()

    all_filled = answer1 and answer2 and answer3 and answer4 and answer5 and answer6 and answer7 and answer8 and answer9 and answer10 and answer11

    return all_filled, survey
