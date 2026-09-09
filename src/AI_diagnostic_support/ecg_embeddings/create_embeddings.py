"""
This file creates the ECG-FM embeddings
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
from AI_diagnostic_support.database.db_connection import store_data
from collections import defaultdict



root = os.path.dirname(os.getcwd())
ckpt_path: str = os.path.join(root, 'ckpts/mimic_iv_ecg_finetuned.pt')
assert os.path.isfile(ckpt_path)

device: str = 'cpu'
batch_size: int = 16
num_workers: int = 0

extract_saliency: bool = True

def to_list(obj: Any) -> List[Any]:
    if isinstance(obj, list):
        return obj

    if isinstance(obj, (np.ndarray, set, dict)):
        return list(obj)

    return [obj]

file_paths = [
    os.path.join(root, 'data/ecgs', file) for file in \
    os.listdir(os.path.join(root, 'data/ecgs'))
]
file_paths = to_list(file_paths)

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

loader = file_paths_to_loader(
    file_paths,
    ECG_FM_SCHEMA,
    ECG_FM_TRANSFORMS,
    batch_size=batch_size,
    num_workers=num_workers,
)


model: ECGTransformerClassificationModel = build_model_from_checkpoint(
    checkpoint_path=ckpt_path
)

model.eval()
model.to(device)

def encoder_out_to_emb(x, device='cpu'):
    return torch.div(x.sum(dim=1), (x != 0).sum(dim=1))

def infer(
    model,
    loader,
    device,
):
    inps = []
    sources = []
    logits = []
    embs = []
    file_names = []
    for source, inp in loader:
        source = source.to(device)
        out = model(source=source)
        inps.extend(inp)
        sources.append(source)
        logits.append(out['out'])
        embs.append(encoder_out_to_emb(out['encoder_out']))
        file_names.extend([i.meta.file for i in inp])

    results = {
        'inps': inps,
        'sources': torch.concatenate(sources).detach().cpu().numpy(),
        'embs': torch.concatenate(embs).detach().cpu().numpy(),
        'file_names': file_names,
    }

    return results

results = infer(model, loader, device)

print("All embeddings are here")

emb = results['embs']
file_names = results['file_names']

grouped_embs = defaultdict(list)

for file_name, e in zip(results['file_names'], emb):
    grouped_embs[file_name].append(e)

file_embs = {
    int(f.split("ecg_")[-1].split(".mat")[0]): np.mean(v, axis=0)
    for f, v in grouped_embs.items()
}

ids = list(map(int, file_embs.keys()))
embeddings = [v.tolist() for v in file_embs.values()]

data = list(zip(ids, embeddings))


query = """
INSERT INTO "code-test".FM_model_embeddings (id, embedding)
VALUES %s;
"""

store_data(query, data)
