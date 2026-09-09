from pathlib import Path
from logging import Logger
from loguru import logger


def patient_logger(root: Path, user: str) -> Logger:

    logger.remove()
    user_path = root / str(user)
    user_path.mkdir(exist_ok=True, parents=True)
    log_file = user_path / "participant_time.csv"
    # Add header if this is a new file
    if not log_file.exists():
        log_file.write_text("time,patient,action\n")

    user_path = root / str(user)
    user_path.mkdir(exist_ok=True, parents=True)
    logger.add(root / str(user) / "participant_time.csv", format="{time},{message}")

    return logger
