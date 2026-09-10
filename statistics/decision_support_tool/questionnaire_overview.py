from pathlib import Path
import pandas as pd

QUESTION_MAP = {
    "Q1": "Which configuration did you prefer?",
    "Q2": "What was your experience with the tool?",
    "Q3": "If the correct diagnosis had been provided after every patient case, this tool would have helped me during my earlier years of study to become more familiar with ECG signals:",
    "Q4": "I trusted the AI prediction:",
    "Q5": "What factors made you trust or distrust the AI's prediction?",
    "Q6": "The reference patient was helpful in guiding my diagnostic decision:",
    "Q7": "In general, I found the signals from the reference patient to be similar to the signal I was asked to diagnose:",
    "Q8": "The ECG signals were easy to read and representative of ECGs I am used to interpreting:",
    "Q9": "How would you rate the difficulty of the task?",
    "Q10": "How often do you encounter/work with ECGs in your daily life?",
    "Q11": "When both an AI prediction and a reference patient were presented, which did you trust more in forming your diagnosis?"
}

QUESTION_KEYS = list(QUESTION_MAP)


def merge_survey_files(results_folder, output_file="survey_data_all_participants.csv"):
    """This function was created by: Perplexity"""
    results_path = Path(results_folder)
    rows = []
    files_found = []

    for participant_folder in sorted(results_path.iterdir()):
        if not participant_folder.is_dir():
            continue

        participant_id = participant_folder.name
        survey_files = sorted(
            participant_folder.glob("survey_data_participant_*.csv")
        )

        for survey_file in survey_files:
            files_found.append(survey_file)
            df = pd.read_csv(survey_file, dtype=str)

            row = {key: df[key].iloc[0] if key in df.columns and len(df) else pd.NA
                   for key in QUESTION_KEYS}
            row["participant"] = participant_id
            rows.append(row)

    if not rows:
        raise FileNotFoundError(
            f"No survey_data_participant_*.csv files found below: {results_path}"
        )

    merged = pd.DataFrame(rows, columns=["participant"] + QUESTION_KEYS)
    merged.rename(columns=QUESTION_MAP, inplace=True)
    merged.to_csv(output_file, index=False, encoding="utf-8-sig")

    print(f"Processed {len(files_found)} survey file(s).")
    print(f"Created {len(merged)} participant row(s).")
    print(f"Saved output to: {output_file}")


if __name__ == "__main__":
    RESULTS_FOLDER = "results"
    OUTPUT_FILE = "survey_data_all_participants_final.csv"
    merge_survey_files(RESULTS_FOLDER, OUTPUT_FILE)