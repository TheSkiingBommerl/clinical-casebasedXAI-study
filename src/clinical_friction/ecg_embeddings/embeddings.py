"""
This file creates the out-of-domain embeddings
This file was based on: https://github.com/bowang-lab/ecg-fm/blob/main/notebooks/infer_quickstart.ipynb
"""

from pathlib import Path
import os
from typing import List
from itertools import chain

# from clinical_friction.similarity_measure.cosine_similarity import embeddings
from scipy.io import loadmat
import numpy as np
from typing import Any, List
import torch
from torch.utils.data import Dataset
from torch.utils.data.dataloader import DataLoader
import pandas as pd
from ecg_transform.inp import ECGInput, ECGInputSchema
from ecg_transform.sample import ECGMetadata, ECGSample
from ecg_transform.t.base import ECGTransform
from ecg_transform.t.common import (
    HandleConstantLeads,
    LinearResample,
    ReorderLeads,
)
from loguru import logger
from ecg_transform.t.scale import Standardize
from ecg_transform.t.cut import SegmentNonoverlapping
from typing import List
import torch
from fairseq_signals.models import build_model_from_checkpoint
from fairseq_signals.models.classification.ecg_transformer_classifier import (
    ECGTransformerClassificationModel,
)
from clinical_friction.database.db_connection import store_data
from clinical_friction.ecg_embeddings.dataset import collate_fn, file_paths_to_loader

ECG_FM_LEAD_ORDER = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
SAMPLE_RATE = 500
N_SAMPLES = SAMPLE_RATE*5


ECG_FM_SCHEMA = ECGInputSchema(
    sample_rate=SAMPLE_RATE,
    expected_lead_order=ECG_FM_LEAD_ORDER,
    required_num_samples=N_SAMPLES,
)

ECG_FM_TRANSFORMS = [
    ReorderLeads(
        expected_order=ECG_FM_LEAD_ORDER,
        missing_lead_strategy='raise',
    ),
    LinearResample(desired_sample_rate=SAMPLE_RATE),
    HandleConstantLeads(strategy='zero'),
    Standardize(),
    SegmentNonoverlapping(segment_length=N_SAMPLES),
]

def to_list(obj: Any) -> List[Any]:
    if isinstance(obj, list):
        return obj

    if isinstance(obj, (np.ndarray, set, dict)):
        return list(obj)

    return [obj]


def encoder_out_to_emb(x, device='cpu'):
    return torch.div(x.sum(dim=1), (x != 0).sum(dim=1))

def flush_to_db(batch_ids: list[int], batch_embs: list[list[float]]):
    """Write a batch of completed embeddings to the database."""
    if not batch_ids:
        return

    data = list(zip(batch_ids, batch_embs))
    query = """
    INSERT INTO "code-test".FM_model_embeddings (id, embedding)
    VALUES %s;
    ON CONFLICT (id) DO UPDATE SET embedding = EXCLUDED.embedding;
    """
    logger.debug(f"Flushing {len(data)} embeddings to database")
    store_data(query, data)

def infer_to_db(
    model,
    loader,
    device: str,
    db_batch_size: int = 100,
):
    """
    Process embeddings and stream results to database in batches.
    """


    # Accumulate
    pending_files: dict[str, tuple[np.ndarray, int]] = {}

    batch_ids: list[int] = []
    batch_embs: list[list[float]] = []

    for batch_idx, (source, inp) in enumerate(loader):
        source = source.to(device)
        out = model(source=source)

        # Compute embeddings for this batch
        batch_embs_tensor = encoder_out_to_emb(out['encoder_out'])
        batch_embs_np = batch_embs_tensor.detach().cpu().numpy()

        # Accumulate per file (handling multiple segments per file)
        for i, item in enumerate(inp):
            file_name = item.meta.file
            file_id = int(file_name.split("ecg_")[-1].split(".mat")[0])
            emb = batch_embs_np[i]

            if file_id in pending_files:
                current_sum, current_count = pending_files[file_id]
                pending_files[file_id] = (current_sum + emb, current_count + 1)
            else:
                pending_files[file_id] = (emb.copy(), 1)

        # Check if any files can be flushed to the DB
        current_batch_files = {int(item.meta.file.split("ecg_")[-1].split(".mat")[0]) for item in inp}

        for file_id in list(pending_files.keys()):
            if file_id not in current_batch_files or batch_idx == len(loader) - 1:
                # File didn't appear in this batch, assume it is complete
                emb_sum, count = pending_files.pop(file_id)
                avg_emb = (emb_sum / count).tolist()

                batch_ids.append(file_id)
                batch_embs.append(avg_emb)

                # Flush when batch is full
                if len(batch_ids) >= db_batch_size:
                    flush_to_db(batch_ids, batch_embs)
                    batch_ids = []
                    batch_embs = []

    # Flush any remaining files
    for file_id, (emb_sum, count) in pending_files.items():
        avg_emb = (emb_sum / count).tolist()
        batch_ids.append(file_id)
        batch_embs.append(avg_emb)

    flush_to_db(batch_ids, batch_embs)
    logger.debug("All embeddings stored successfully")


def create_embeddings(
    data_path: Path,
    ckpt_path: Path,
    device: str = "cpu",
    batch_size: int = 16,
    num_workers: int = 0,
    extract_saliency: bool = True,
    db_batch_size: int = 100,
):
    file_paths = [str(p) for p in data_path.glob("*.mat")]

    loader = file_paths_to_loader(
        file_paths,
        ECG_FM_SCHEMA,
        ECG_FM_TRANSFORMS,
        batch_size=batch_size,
        num_workers=num_workers,
    )

    logger.debug(f"Torch device: {device}")
    logger.debug(f"Loading model checkpoint from {ckpt_path}...")
    model = build_model_from_checkpoint(checkpoint_path=ckpt_path)

    model.eval()
    model.to(device)

    logger.debug(f"Starting inference and streaming to DB...")
    infer_to_db(model, loader, device, db_batch_size)
    logger.debug("Finished!")
