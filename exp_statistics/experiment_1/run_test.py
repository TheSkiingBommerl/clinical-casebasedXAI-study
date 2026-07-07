"""
Test statistical significance of first experiment
"""

import numpy as np
from scipy.stats import friedmanchisquare
import pandas as pd
from exp_statistics.experiment_1.mapping import map

# each participant ranked 8 cases across 3 diagnosises.
df1 = pd.read_csv("exp_statistics/experiment_1/data/ranking_data_participent_1.csv")
df2 = pd.read_csv("exp_statistics/experiment_1/data/ranking_data_participent_5.csv")
df3 = pd.read_csv("exp_statistics/experiment_1/data/ranking_data_participent_6.csv")

# include or exclude normal/abnormal data to see if results differ
rankings_p1 = np.array(map(df1, only_abn=False, only_norm=True))
rankings_p2 = np.array(map(df2, only_abn=False, only_norm=True))
rankings_p3 = np.array(map(df3, only_abn=False, only_norm=True))

rankings_combined = np.vstack([rankings_p1, rankings_p2, rankings_p3])

method1 = rankings_combined[:, 0]
method2 = rankings_combined[:, 1]
method3 = rankings_combined[:, 2]

methods = ["DTW", "Embeddings", "Embeddings Other Model"]

print("Information")
print(f"Patients Considered: {rankings_combined.shape[0]}")
print(f"Nr. different Abnormalities in Experiment: {rankings_combined.shape[1]}\n")

for i, m in enumerate([method1, method2, method3], 1):
    print(f"Method {methods[i-1]} Mean Rank: {np.mean(m):.2f} & SD: {np.std(m):.2f}")

stat, p_value = friedmanchisquare(method1, method2, method3)

print("\nFriedman Test Results")
print(f"Chi-Square Statistic: {stat:.4f}")
print(f"p-value: {p_value:.4f}")
