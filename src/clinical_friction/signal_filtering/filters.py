"""
Filters for ECG signal filtering
"""

from scipy import signal

CUTOFF_HIGH = 0.5
CUTOFF_LOW = 150

# 400 for first experiment
# SAMPLING_FREQ = 400

# 500 for second experiment
SAMPLING_FREQ = 500
AXIS = 1

def butterworth_high(ecg):
    # keep everything above CUTOFF_HIGH
    [b,a] = signal.butter(4, CUTOFF_HIGH, btype='highpass', fs=SAMPLING_FREQ)
    filtered = signal.filtfilt(b, a, ecg, axis=AXIS)
    return filtered

def butterworth_low(ecg, cut_low):
    # keep everything below CUTOFF_LOW
    [b,a] = signal.butter(4, cut_low, btype='lowpass', fs=SAMPLING_FREQ)
    filtered = signal.filtfilt(b, a, ecg, axis=AXIS)
    return filtered

def butterworth_band(ecg):
    # keep everything within range
    [b,a] = signal.butter(4, [CUTOFF_HIGH, CUTOFF_LOW], btype='bandpass', fs=SAMPLING_FREQ)
    filtered = signal.filtfilt(b, a, ecg, axis=AXIS)
    return filtered

def notch(ecg, powerline):
    # remove powerline interferance
    [b,a] = signal.iirnotch(w0=powerline, Q=30, fs=SAMPLING_FREQ)
    filtered = signal.filtfilt(b, a, ecg, axis=AXIS)
    return filtered