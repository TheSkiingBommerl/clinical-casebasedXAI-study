import numpy as np

def remove_zero_padding(signal: np.ndarray) -> np.ndarray:
    """Remove leading/trailing all-zero timesteps from a (12, N) signal."""
    mask = (signal != 0).any(axis=0)
    if not mask.any():
        return signal
    start = mask.argmax()
    end = len(mask) - mask[::-1].argmax()
    return signal[:, start:end]

def add_zero_padding(signal: np.ndarray, target_length: int = 4095) -> np.ndarray:

    current_length = signal.shape[1]

    if current_length >= target_length:
        return signal[:, :target_length]

    total_padding = target_length - current_length

    pad_left = total_padding // 2
    pad_right = total_padding - pad_left

    return np.pad(
        signal,
        pad_width=((0, 0), (pad_left, pad_right)),
        mode="constant",
        constant_values=0,
    )

def get_middle_segment(
    signal: np.ndarray,
    fs: int = 400,
    duration: float = 5.0,
    pad_if_short: bool = True,
) -> np.ndarray:
    n_samples = int(duration * fs)
    sig_len   = signal.shape[1]

    if sig_len < n_samples:
        if pad_if_short:
            print("Padded")
            pad_total = n_samples - sig_len
            pad_left  = pad_total // 2
            pad_right = pad_total - pad_left
            return np.pad(signal, ((0, 0), (pad_left, pad_right)))

    mid   = sig_len // 2
    start = mid - n_samples // 2
    end   = start + n_samples
    return signal[:, start:end]