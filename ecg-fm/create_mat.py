"""
This file saves the ecg signals as .mat which is needed to create the embedding with ecg-fm
"""

from scipy.io import savemat
from database.useful_queries import get_ecg_signals
from helpers.remove_padding import remove_zero_padding


def save_signal_in_mat_file(id, signal):
    savemat(f"ecgs/ecg_{id:03d}.mat", {
        "ecg": signal
    })


if __name__ == "__main__":
    ecgs = get_ecg_signals()
    
    for row in ecgs.itertuples(index=False):
        id = row.id
        signal = remove_zero_padding(row.signal)

        save_signal_in_mat_file(id, signal)
