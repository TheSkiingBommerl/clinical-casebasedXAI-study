import pandas as pd
from sklearn.metrics import jaccard_score
import matplotlib.pyplot as plt
import numpy as np

root = "exp_statistics/experiment_2/charts/tests"

def calculate_jaccard_score(mapping, participent_diagnosis, gold_lable):
    ALL_CONDITIONS = ["1dAVb", "rbbb", "lbbb", "sb", "af", "st", "norm"]
    
    diagnosis = participent_diagnosis.pivot(index="Patient", columns="Condition", values="Selected")
    diagnosis = diagnosis[ALL_CONDITIONS].astype(int)
    
    mapping["patient_id"] = mapping["patient_id"].str.strip("[]").astype(int)
    diagnosis.index = diagnosis.index.map(mapping.set_index("index")["patient_id"])
    diagnosis.index.name = "Patient"

    patient_to_arm = mapping.set_index("patient_id")["study_arm"]
    
    records = []
    for patient_id in diagnosis.index:
        pred_row = diagnosis.loc[[patient_id]]
        true_row = gold_lable.loc[[patient_id]]
        arm = patient_to_arm.loc[patient_id]

        jac = jaccard_score(true_row, pred_row, average="samples", zero_division=1)
        
        records.append({
            "patient":  patient_id,
            "arm":      arm,
            "jaccard":  jac,
        })
    
    return records