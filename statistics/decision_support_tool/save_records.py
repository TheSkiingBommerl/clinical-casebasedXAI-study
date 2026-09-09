"""
Use this file to collect all the data needed for the analysis and save it in the records.csv file.
"""

import pandas as pd
from src.AI_diagnostic_support.database.db_connection import extract_data
import os
from collections import Counter
import statistics.decision_support_tool.jaccard_scores as js

root = "statistics/decision_support_tool"

def get_mapping(dataset):
    return pd.read_csv(root + "/mappings" + f"/mapping_{str(dataset)}")

def get_questionaire(identifier, dataset):
    return pd.read_csv(root + "/results" + f"/participant_{str(identifier)}_{str(dataset)}/survey_data_participant_{str(identifier)}_{str(dataset)}.csv")

def get_participent_diagnosis(identifier, dataset):
    return pd.read_csv(root + "/results" + f"/participant_{str(identifier)}_{str(dataset)}/diagnosis_participant_{str(identifier)}_{str(dataset)}.csv")

def get_gold_lable(patient_ids):
    placeholders = ",".join(["%s"] * len(patient_ids))

    query = f"""
    Select "id", "1dAVb", rbbb, lbbb, sb, af, st
    FROM "ptb-xl".gold_lable
    WHERE id IN ({placeholders})
    """

    rows = extract_data(query, patient_ids)

    CONDITIONS = ["1dAVb", "rbbb", "lbbb", "sb", "af", "st"]

    gt = pd.DataFrame(rows, columns=["Patient"] + CONDITIONS).set_index("Patient")
    gt["norm"] = (gt[CONDITIONS].sum(axis=1) == 0).astype(int)

    return gt

def get_experience_group(survey_df):

    Expert = ["Several times per week", "Several times per month"]
    Novice = [
        "Several times per year",
        "I used to encounter ECGs frequently, but not anymore",
        "Only a few times throughout my studies and career"
    ]

    column = survey_df["Q10"]
    raw = column.iloc[0]

    if raw in Expert:
        return "Expert"
    if raw in Novice:
        return "Novice"
    
# for these patient ids and study arms the diagnosis of the patient 
# was different to that of the reference patient
diagnosis_diff = {
    (3041, 2), (3041, 3),
    (655,  2), (655,  3),
    (20923,2), (20923,3),
    (1237, 2), (1237, 3),
}

def get_records(jaccard_scores):
    records = []
    for participant_id, data in jaccard_scores.items():
        for entry in data["jaccard_scores"]:
            records.append({
                "participant":      data["participant_id"], #participant_id - if you don't wanna display the original id
                "arm":              entry["arm"],
                "patient":          entry["patient"],
                "jaccard":          entry["jaccard"],
                "experience_level": data["experience_level"],
                "condition":        entry["condition"],
                "pred":             entry["pred"],
                "gold":             entry["gold"],
            })
    df = pd.DataFrame(records)
    df["diagnosis_diff"] = df.apply(
        lambda row: (row["patient"], row["arm"]) in diagnosis_diff, axis=1
    )

    return df



if __name__ == '__main__':
    results_dir = root + "/results/resultsflo"

    # all have same patient_ids, so get any mapping to extract gold_lables
    mapping = get_mapping(0)
    mapping["patient_id"] = mapping["patient_id"].str.strip("[]").astype(int)
    patient_ids = mapping["patient_id"].tolist()
    gold_lable = get_gold_lable(patient_ids)

    participants = {}

    # to see the different diagnosises people gave for a specific patient
    patient_diagnosis_info = {}
    info_patient = None

    for i, folder in enumerate(os.listdir(results_dir), start=1):
        
        if not folder.startswith("participant"):
            continue
        parts = folder.split("_")
        identifier = int(parts[1])
        dataset = int(parts[2])

        survey = get_questionaire(identifier, dataset)
        experience = get_experience_group(survey)
        mapping = get_mapping(dataset)
        participent_diagnosis = get_participent_diagnosis(identifier, dataset)
        
        # due to an interface mistake 2 participents were able to finish without 
        # diagnosing every patient -> remove patients that have False values for every diagnosis
        any_selected = participent_diagnosis.groupby("Patient")["Selected"].any()
        selected_patients = any_selected[any_selected].index
        participent_diagnosis = participent_diagnosis[
            participent_diagnosis["Patient"].isin(selected_patients)
        ]

        if info_patient is not None:
            patient_diag = participent_diagnosis[
            (participent_diagnosis["Patient"] == info_patient) & 
            (participent_diagnosis["Selected"] == True)
            ]["Condition"].tolist()

            patient_diagnosis_info[f"{identifier}_{dataset}"] = {
                "experience": experience,
                "diagnosis": patient_diag
            }

        participants_jaccard_score = js.calculate_jaccard_score(mapping, participent_diagnosis, gold_lable)

        participants[i] = {
            "jaccard_scores": participants_jaccard_score,
            "experience_level": experience,
            "participant_id": f"{identifier}_{dataset}"
        }

    records = get_records(participants)
    records.to_csv("exp_statistics/decision_support_tool/records.csv")
    
    print("Record\n", (records['jaccard'].value_counts(normalize=True))*100)
 
    records_per_arm = records.groupby(["participant", "arm", "experience_level"])["jaccard"].mean().reset_index()
    records_per_arm.to_csv("exp_statistics/decision_support_tool/records_per_arm.csv")


    if info_patient is not None:
        expert_diag = []
        novice_diag = []
        for participant in patient_diagnosis_info.values():
            diagnosis = " + ".join(participant["diagnosis"]) if isinstance(participant["diagnosis"], list) else participant["diagnosis"]
            if participant["experience"] == "Expert":
                expert_diag.append(diagnosis)
            else:
                novice_diag.append(diagnosis)
        
        print(f"Diagnosises for Patient: {info_patient}")
        print("Experts")
        expert_counts = Counter(expert_diag)
        for condition, count in sorted(expert_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {condition}: {count}")
        print("Novice")
        novice_counts = Counter(novice_diag)
        for condition, count in sorted(novice_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {condition}: {count}")

