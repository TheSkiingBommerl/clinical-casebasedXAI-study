from pathlib import Path
from loguru import logger
from clinical_friction.ecg_embeddings.create_mat import save_signals
from clinical_friction.ecg_embeddings.embeddings import create_embeddings

def run_embeddings():
    data_dir = Path("data")
    ckpt_path = data_dir / "raw" / "ecg-model" / "mimic_iv_ecg_finetuned.pt"

    signals_path = data_dir / "processed" / "ecg-mat"
    signals_path.mkdir(exist_ok=True)

    logger.info("Converting code-test signals to .mat files...")
    #save_signals("code-test", signals_path)

    logger.info("Running embedding model...")
    create_embeddings(
        data_path=signals_path,
        ckpt_path=ckpt_path,
    )


if __name__ == "__main__":
    run_embeddings()
