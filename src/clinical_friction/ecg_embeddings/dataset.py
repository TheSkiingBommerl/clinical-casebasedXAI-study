"""
This file creates the out-of-domain embeddings
This file was based on: https://github.com/bowang-lab/ecg-fm/blob/main/notebooks/infer_quickstart.ipynb
"""

import os
from typing import List
from itertools import chain
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
from ecg_transform.t.scale import Standardize
from ecg_transform.t.cut import SegmentNonoverlapping
from typing import List
import torch
from fairseq_signals.models import build_model_from_checkpoint
from fairseq_signals.models.classification.ecg_transformer_classifier import (
    ECGTransformerClassificationModel
)
from clinical_friction.database.db_connection import store_data
from collections import defaultdict

class ECGFMDataset(Dataset):
    def __init__(
        self,
        schema,
        transforms,
        file_paths,
    ):
        self.schema = schema
        self.transforms = transforms
        self.file_paths = file_paths

    def __len__(self):
        return len(self.file_paths)

    def __getitem__(self, idx):
        mat = loadmat(self.file_paths[idx])

        metadata = ECGMetadata(
            sample_rate=400,
            num_samples=mat['ecg'].shape[1],
            lead_names=['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6'],
            unit=None,
            input_start=0,
            input_end=mat['ecg'].shape[1],
        )

        metadata.file = self.file_paths[idx]

        inp = ECGInput(mat['ecg'], metadata)

        sample = ECGSample(
            inp,
            self.schema,
            self.transforms,
        )
        source = torch.from_numpy(sample.out).float()

        return source, inp

def collate_fn(inps):
    sample_ids = list(
        chain.from_iterable([[inp[1]]*inp[0].shape[0] for inp in inps])
    )
    return torch.concatenate([inp[0] for inp in inps]), sample_ids

def file_paths_to_loader(
    file_paths: List[str],
    schema: ECGInputSchema,
    transforms: List[ECGTransform],
    batch_size = 64,
    num_workers = 7,
):
    dataset = ECGFMDataset(
        schema,
        transforms,
        file_paths,
    )

    return DataLoader(
        dataset,
        batch_size=batch_size,
        num_workers=num_workers,
        pin_memory=True,
        sampler=None,
        shuffle=False,
        collate_fn=collate_fn,
        drop_last=False,
    )
