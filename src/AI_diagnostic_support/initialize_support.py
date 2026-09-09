from tqdm import tqdm
import os
from pathlib import Path
from argparse import ArgumentParser
from loguru import logger
from AI_diagnostic_support.automatic_ecg_diagnosis.predict import fm_prediction
from AI_diagnostic_support.automatic_ecg_diagnosis.certainty import aed_certainty, fm_certainty
from AI_diagnostic_support.automatic_ecg_diagnosis.prediction_to_diagnosis import add_ptbxl_dnn
from AI_diagnostic_support.helpers.parquets import generate_tool_parquets
from AI_diagnostic_support.helpers.prerender import prerender_all
from AI_diagnostic_support.helpers.load_parquets import load_case
from AI_diagnostic_support.automatic_ecg_diagnosis.create_embeddings import create_ptb_emb


def main():
    argparser = ArgumentParser()
    argparser.add_argument('--dir', type=Path, help="Set a custom root data folder", default=Path("data"))
    argparser.add_argument('--rollouts', type=int, help="Number of Monte-Carlo rollouts", default=5)
    args = args = argparser.parse_args()

    raw_dir = Path(args.dir) / "raw"
    processed_dir = Path(args.dir) / "processed"
    support_dir = processed_dir / "support"
    support_dir.mkdir(exist_ok=True)

    # Check if necessary files exist
    code_test_signals = processed_dir / "code-test_filtered.hdf5"
    ptbxl_signals = processed_dir / "ptb-xl_filtered.hdf5"
    model_path = raw_dir / "ecg-autodiag-model" / "model" / "model.hdf5"
    filtered_csv_path = processed_dir / "filtered_ptbxl.csv"
    for path in [code_test_signals, ptbxl_signals, model_path, filtered_csv_path]:
        if not os.path.exists(path):
            logger.error(
                f"{path} not found. Did you run AI-diagnostic-support-init-db"
                "and AI-diagnostic-support-init-similarity?"
            )

    logger.info("Computing uncertainty for code-test and PTB-XL...")
    aed_certainty(
        hdf5_path=code_test_signals,
        model_path=model_path,
        pred_rep=args.rollouts
    )

    fm_certainty(
        hdf5_path=ptbxl_signals,
        model_path=model_path,
        pred_rep=args.rollouts
    )

    logger.info("Predicting model diagnoses on PTB-XL...")
    fm_prediction(
        hdf5_path=ptbxl_signals,
        model_path=model_path,
        dst_dir=support_dir,
        filename="ptb_predictions"
    )

    logger.info("Adding PTB-XL predictions to database...")
    add_ptbxl_dnn(support_dir / "ptb_predictions.csv")

    logger.info("Running ecg-automatic-diagnosis embedding model...")
    create_ptb_emb(ptbxl_signals, model_path)
    # Now, we need to create parquets and prerender the ECG plotly graphs
    tool_dir = Path(args.dir) / "website" / "clinical_decision_support"
    tool_dir.mkdir(exist_ok=True)

    # Generate parquets that the tool loads for each participant - patient
    logger.info("Generating data files for clinical decision tool...")
    generate_tool_parquets(filtered_csv_path, tool_dir)

    # Pre-render plotly HTML plots for faster loading
    logger.info("Pre-rendering plotly plots for 8 datasets...")
    plot_dir = tool_dir / "cached_plots"
    plot_dir.mkdir(exist_ok=True)

    for dataset in range(8):
        bardesc = f"Rendering dataset {dataset}"
        for case in tqdm(range(20), total=20, desc=bardesc):
            data = load_case(tool_dir, dataset, case, prerender = True)
            prerender_all(data["ecg"], data["ecg_ref"], dataset, case, plot_dir)

    # Create a results folder
    results_dir = Path(args.dir) / "results" / "clinical_decision_support"
    results_dir.mkdir(exist_ok=True, parents=True)

    logger.info("All done!")

if __name__ == "__main__":
    main()
