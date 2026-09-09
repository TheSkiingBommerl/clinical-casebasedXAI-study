"""
This file was based on paper: "Detection of Power-Line Interference in ECG signals using frequency-domain analysis"
"""

import numpy as np
from scipy.signal import welch
from scipy.ndimage import uniform_filter1d
import matplotlib.pyplot as plt
from AI_diagnostic_support.database.useful_queries import get_ecg_signals
import pandas as pd

df = pd.read_csv("database/transform_and_load/ptb/datasets/filtered_ptbxl.csv")
df = df[df["age"] <= 95]
valid_ids = df["ecg_id"].tolist()

ecgs = get_ecg_signals(patient_ids=valid_ids, dataset="ptb-xl")

ecgs = ecgs["signal"].tolist()

all_psds = []
for ecg in ecgs:
    for lead in ecg:
        lead_uV = lead * 1000
        f, p = welch(lead_uV, fs=500, nperseg=500)
        all_psds.append(p)

mean_psd = np.mean(all_psds, axis=0)
log_psd = 10 * np.log10(mean_psd)

mask = (f > 30) & (f < 80)
f_band = f[mask]
log_psd_band = log_psd[mask]

background = uniform_filter1d(log_psd_band, size=15)
residual = log_psd_band - background

fig, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

axes[0].plot(f_band, log_psd_band, label="PSD (dB)")
axes[0].plot(f_band, background, "--", label="Smoothed background")
axes[0].axvline(50, color="r", linestyle="--", label="50 Hz")
axes[0].axvline(60, color="g", linestyle="--", label="60 Hz")
axes[0].set_ylabel("Power (dB)")
axes[0].legend()

axes[1].plot(f_band, residual, color="purple", label="Residual")
axes[1].axvline(50, color="r", linestyle="--")
axes[1].axvline(60, color="g", linestyle="--")
axes[1].set_xlabel("Frequency (Hz)")
axes[1].set_ylabel("Residual (dB)")
axes[1].legend()

plt.tight_layout()
plt.show()
