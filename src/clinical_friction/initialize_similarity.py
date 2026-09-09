import torch
import sys
from pathlib import Path
from argparse import ArgumentParser
from loguru import logger
from clinical_friction.ecg_embeddings.create_mat import save_signals
from clinical_friction.ecg_embeddings.embeddings import create_embeddings
from clinical_friction.similarity_measure.get_test_split import get_test_split
from clinical_friction.similarity_measure.DTW import process_all
from clinical_friction.similarity_measure.cosine_similarity import find_similar_embeddings
from clinical_friction.similarity_measure.create_parquets import build_save_table
from clinical_friction.automatic_ecg_diagnosis.create_embeddings import create_code15_emb

def run_embeddings(data_dir: Path, device: str, db_batch_size: int):
    data_dir = Path("data")

    ecg_fm_path = data_dir / "raw" / "ecg-model" / "mimic_iv_ecg_finetuned.pt"
    ecg_auto_path = data_dir / "raw" / "ecg-autodiag-model" / "model" / "model.hdf5"

    for mod_path in [ecg_fm_path, ecg_auto_path]:
        if not mod_path.exists:
            logger.error(f"Model checkpoint {mod_path} Doesn't exist. Did you run clinical-friction-init-db?")

    signals_path = data_dir / "processed" / "ecg-mat"
    if not signals_path.parent.exists:
        logger.error(f"{signals_path.parent} Doesn't exist. Did you run clinical-friction-init-db?")
    signals_path.mkdir(exist_ok=True)

    logger.info("Splitting code-test ECG's")
    df_ecg_split = get_test_split()
    df_ecg_split.to_csv(data_dir / "processed" / "ids_experiment_1.csv", index=False)


    hdf5_path = data_dir / "processed" / "code-test_filtered.hdf5"
    simil_dir = data_dir / "processed" / "similarity"
    dtw_dir = simil_dir / "dtw"
    dtw_dir.mkdir(exist_ok=True, parents=True)

    samples = df_ecg_split["ids"].to_list()
    logger.info(f"Running DTW similarity on {len(samples)} samples")
    process_all(samples, dtw_dir, hdf5_path)

    logger.info("Converting ECG's to .mat files...")
    save_signals("code-test", signals_path)

    logger.info("Running ECG-FM embedding model...")
    create_embeddings(
        data_path=signals_path,
        ckpt_path=ecg_fm_path,
        device=device,
        db_batch_size=db_batch_size
    )

    fm_dir = simil_dir / "In_Population"
    fm_dir.mkdir(exist_ok=True)
    logger.info(f"Finding FM-embedding similarity on {len(samples)} samples")
    find_similar_embeddings(samples, "fm_model_embeddings", fm_dir)


    logger.info("Running ecg-automatic-diagnosis embedding model...")
    create_code15_emb(hdf5_path, ecg_auto_path)

    ecg_auto_dir = simil_dir / "Out_Population"
    ecg_auto_dir.mkdir(exist_ok=True)
    logger.info(f"Finding AEM-embedding similarity on {len(samples)} samples")
    find_similar_embeddings(samples, "aed_model_embeddings", ecg_auto_dir)

    logger.info(f"Shuffling DTW - FM - AEM pairs for the similarity tool")
    tool_simil_dir = data_dir / "website" / "similarity_comparison"
    tool_simil_dir.mkdir(exist_ok=True, parents=True)
    build_save_table(samples, simil_dir, tool_simil_dir)

    # Create a results folder
    results_dir = data_dir / "results" / "similarity_comparison"
    results_dir.mkdir(exist_ok=True, parents=True)
    logger.info("Done!")


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
