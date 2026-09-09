"""
This file saves the ecg signals as .mat which is needed to create the embedding with ecg-fm
"""
from tqdm import tqdm
from pathlib import Path
from typing import Literal
from scipy.io import savemat
from AI_diagnostic_support.database.useful_queries import get_ecg_signals
from AI_diagnostic_support.helpers.remove_padding import remove_zero_padding


def save_signal_in_mat_file(id, signal):
    savemat(f"ecgs/ecg_{id:03d}.mat", {
        "ecg": signal
    })

def save_signals(dataset: Literal["ptb-xl", "code-test"], dst: Path):
    """Save signals to .mat files for model consumption"""
    # Retrieve from database
    ecgs = get_ecg_signals(dataset=dataset, filtered=False)

    for row in tqdm(ecgs.itertuples(index=False), total=len(ecgs)):
        id = row.id
        signal = remove_zero_padding(row.signal)

        # Save signal
        savemat(
            str(dst / f"ecg_{id:03d}.mat"),
            {"ecg": signal}
        )

if __name__ == "__main__":
    ecgs = get_ecg_signals()

    for row in ecgs.itertuples(index=False):
        id = row.id
        signal = remove_zero_padding(row.signal)

        save_signal_in_mat_file(id, signal)
