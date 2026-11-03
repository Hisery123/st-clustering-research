import sys
import time
import json
import random
from pathlib import Path

import numpy as np
import pandas as pd
import scanpy as sc
import torch
import torch.nn.functional as F

sys.path.insert(0, r"D:\paper\STAGATE_pyG_source")
from STAGATE_pyG.STAGATE import STAGATE
from STAGATE_pyG.utils import Transfer_pytorch_Data

ROOT = Path(r"D:\paper\ST_Benchmark_Planning\mvp")
DATA = ROOT / "data" / "151669"
OUT = ROOT / "results" / "stagate_151669_controlled_seed0"
SEED = 0
EPOCHS = 1000

def main():
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable")

    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite existing results: {OUT}")

    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    torch.cuda.manual_seed_all(SEED)

    device = torch.device("cuda:0")
    print("GPU:", torch.cuda.get_device_name(0), flush=True)

    adata = sc.read_10x_h5(DATA / "151669_filtered_feature_bc_matrix.h5")
    adata.var_names_make_unique()
    meta = pd.read_csv(DATA / "metadata.tsv", sep="\t", index_col=0)

    assert adata.shape[0] == 3661
    assert adata.obs_names.is_unique and meta.index.is_unique
    assert adata.obs_names.equals(meta.index)

    coords = list(zip(meta["row"].astype(int), meta["col"].astype(int)))
    assert len(set(coords)) == len(coords)

    lookup = dict(zip(coords, adata.obs_names))
    edges = []
    for barcode, (r, c) in zip(adata.obs_names, coords):
        for dr, dc in [(0, 2), (1, 1), (1, -1)]:
            other = lookup.get((r + dr, c + dc))
            if other is not None:
                edges.extend([(barcode, other), (other, barcode)])

    assert len(edges) == 21194

    net = pd.DataFrame(edges, columns=["Cell1", "Cell2"])
    net["Distance"] = 1.0
    adata.uns["Spatial_Net"] = net

    sc.pp.highly_variable_genes(
        adata, flavor="seurat_v3", n_top_genes=3000
    )
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    adata = adata[:, adata.var["highly_variable"]].copy()

    data = Transfer_pytorch_Data(adata)
    assert data.x.shape == (3661, 3000)
    assert data.edge_index.shape == (2, 24855)
    assert bool(torch.isfinite(data.x).all())

    data = data.to(device)
    model = STAGATE(hidden_dims=[3000, 512, 30]).to(device)
    optimizer = torch.optim.Adam(
        model.parameters(), lr=0.001, weight_decay=0.0001
    )

    config = {
        "dataset": "DLPFC_151669",
        "method": "STAGATE_pyG",
        "graph": "Visium_hex_six_neighbors",
        "undirected_edges": 10597,
        "self_loops": 3661,
        "hvg": 3000,
        "hvg_flavor": "seurat_v3",
        "target_sum": 10000,
        "log1p": True,
        "hidden_dims": [3000, 512, 30],
        "epochs": EPOCHS,
        "seed": SEED,
        "learning_rate": 0.001,
        "weight_decay": 0.0001,
        "gradient_clipping": 5.0,
        "torch_version": torch.__version__,
        "scanpy_version": sc.__version__,
        "gpu": torch.cuda.get_device_name(0),
        "evaluation_labels_used_in_training": False,
    }

    OUT.mkdir(parents=True, exist_ok=False)
    (OUT / "config.json").write_text(
        json.dumps(config, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    losses = []
    torch.cuda.reset_peak_memory_stats(device)
    start = time.perf_counter()
    print("TRAINING START", flush=True)

    try:
        for epoch in range(1, EPOCHS + 1):
            model.train()
            optimizer.zero_grad()
            z, out = model(data.x, data.edge_index)
            loss = F.mse_loss(data.x, out)
            if not bool(torch.isfinite(loss).item()):
                raise RuntimeError(f"Non-finite loss at epoch {epoch}")

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            optimizer.step()

            losses.append({"epoch": epoch, "loss": float(loss.item())})

            if epoch == 1 or epoch % 50 == 0:
                torch.cuda.synchronize(device)
                peak = torch.cuda.max_memory_allocated(device) / 1024**2
                print(
                    f"Epoch {epoch}/{EPOCHS} | loss={loss.item():.6f} "
                    f"| peak_cuda_allocated={peak:.1f}MiB",
                    flush=True
                )

        model.eval()
        with torch.no_grad():
            z, _ = model(data.x, data.edge_index)
            embedding = z.cpu().numpy()

        assert embedding.shape == (3661, 30)
        assert np.isfinite(embedding).all()

        pd.DataFrame(
            embedding,
            index=adata.obs_names,
            columns=[f"STAGATE_{i+1}" for i in range(30)]
        ).to_csv(OUT / "embedding.csv", index_label="barcode")

        torch.cuda.synchronize(device)
        elapsed = time.perf_counter() - start

        config["training_seconds"] = elapsed
        config["peak_cuda_allocated_mib"] = (
            torch.cuda.max_memory_allocated(device) / 1024**2
        )
        (OUT / "config.json").write_text(
            json.dumps(config, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        print("STAGATE FULL TRAINING PASS", flush=True)

    finally:
        pd.DataFrame(losses, columns=["epoch", "loss"]).to_csv(
            OUT / "loss.csv", index=False
        )

if __name__ == "__main__":
    main()
