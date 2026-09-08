import torch
import sys
from pathlib import Path
from argparse import ArgumentParser
from loguru import logger
from clinical_friction.ecg_embeddings.create_mat import save_signals
from clinical_friction.ecg_embeddings.embeddings import create_embeddings
from clinical_friction.similarity_measure.get_test_split import get_test_split
from clinical_friction.similarity_measure.DTW import process_all

def run_embeddings(data_dir: Path, device: str, db_batch_size: int):
    data_dir = Path("data")

    ckpt_path = data_dir / "raw" / "ecg-model" / "mimic_iv_ecg_finetuned.pt"

    if not ckpt_path.exists:
        logger.error(f"Model checkpoint {ckpt_path} Doesn't exist. Did you run clinical-friction-init-db?")

    signals_path = data_dir / "processed" / "ecg-mat"
    if not signals_path.parent.exists:
        logger.error(f"{signals_path.parent} Doesn't exist. Did you run clinical-friction-init-db?")
    signals_path.mkdir(exist_ok=True)

    logger.info("Splitting code-test ECG's")
    df_ecg_split = get_test_split()
    df_ecg_split.to_csv(data_dir / "processed" / "ids_experiment_1.csv", index=False)


    hdf5_path = data_dir / "processed" / "code-test_filtered.hdf5"
    dtw_path = data_dir / "processed" / "dtw-similarity"
    dtw_path.mkdir(exist_ok=True)

    samples = df_ecg_split["ids"].to_list()
    logger.info(f"Running DTW similarity on {len(samples)} samples")
    process_all(samples, dtw_path, hdf5_path)

    logger.info("Converting ECG's to .mat files...")
    save_signals("code-test", signals_path)

    logger.info("Running embedding model...")
    create_embeddings(
        data_path=signals_path,
        ckpt_path=ckpt_path,
        device=device,
        db_batch_size=db_batch_size
    )


def main():
    argparser = ArgumentParser()
    argparser.add_argument('--device', type=str, help="A valid PyTorch device for computing the embeddings", default="cpu")
    argparser.add_argument('--dir', type=Path, help="Set a custom root data folder", default=Path("data"))
    argparser.add_argument('--dbbatch', type=int, help="Batch size, decrease if running out of memory", default=100)
    args = argparser.parse_args()
    try:
        torch.device(args.device)
    except RuntimeError as e:
        logger.exception(e)
        sys.exit()

    run_embeddings(args.dir, args.device, args.dbbatch)


if __name__ == "__main__":
    main()
