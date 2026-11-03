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
DATA = ROOT / "data" / "breast_cancer_block_a_section1"
OUT = ROOT / "results" / "stagate_breast_cancer_block_a_section1_heterodepth_v1_c3_seed0"
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

    adata = sc.read_10x_h5(DATA / "filtered_feature_bc_matrix.h5")
    adata.var_names_make_unique()

    # Random spot-level depth assignment, independent of pathology.
    raw = adata.X.tocsr(copy=True)
    assert raw.shape[0] == 3798
    original_umi = np.asarray(raw.sum(axis=1)).ravel()

    depth_seed = 20261103
    rng = np.random.default_rng(depth_seed)

    low_mask = np.zeros(adata.n_obs, dtype=bool)
    selected = rng.choice(
        adata.n_obs, size=adata.n_obs // 2, replace=False
    )
    low_mask[selected] = True

    # Binomial UMI thinning: retain 10% in low-depth spots.
    for i in np.flatnonzero(low_mask):
        start, end = raw.indptr[i], raw.indptr[i + 1]
        values = raw.data[start:end].astype(np.int64)
        raw.data[start:end] = rng.binomial(
            values, 0.10
        ).astype(raw.data.dtype)

    raw.eliminate_zeros()
    sampled_umi = np.asarray(raw.sum(axis=1)).ravel()

    assert np.array_equal(
        original_umi[~low_mask],
        sampled_umi[~low_mask]
    )
    assert np.all(
        sampled_umi[low_mask] <= original_umi[low_mask]
    )

    retention = (
        sampled_umi[low_mask].sum()
        / original_umi[low_mask].sum()
    )
    if not (0.095 < retention < 0.105):
        raise RuntimeError(f"Unexpected retention: {retention}")

    adata.X = raw
    achieved_zero = 1.0 - raw.nnz / (
        raw.shape[0] * raw.shape[1]
    )

    print(
        "HETERODEPTH AUDIT | "
        f"low_spots={low_mask.sum()} "
        f"| high_spots={(~low_mask).sum()} "
        f"| low_UMI_retention={retention:.6f} "
        f"| zero_fraction={achieved_zero:.6f} "
        f"| depth_seed={depth_seed}",
        flush=True
    )
    print(
        "LOW DEPTH MEDIAN UMI:",
        float(np.median(sampled_umi[low_mask])),
        flush=True
    )
    print(
        "HIGH DEPTH MEDIAN UMI:",
        float(np.median(sampled_umi[~low_mask])),
        flush=True
    )

    meta = pd.read_csv(DATA / "spots_aligned.csv").set_index("barcode")

    assert adata.shape[0] == 3798
    assert adata.obs_names.is_unique and meta.index.is_unique
    assert adata.obs_names.equals(meta.index)

    coords = list(zip(meta["array_row"].astype(int), meta["array_col"].astype(int)))
    assert len(set(coords)) == len(coords)

    lookup = dict(zip(coords, adata.obs_names))
    edges = []
    for barcode, (r, c) in zip(adata.obs_names, coords):
        for dr, dc in [(0, 2), (1, 1), (1, -1)]:
            other = lookup.get((r + dr, c + dc))
            if other is not None:
                edges.extend([(barcode, other), (other, barcode)])

    assert len(edges) == 22064

    net = pd.DataFrame(edges, columns=["Cell1", "Cell2"])
    net["Distance"] = 1.0
    adata.uns["Spatial_Net"] = net

    sc.pp.highly_variable_genes(
        adata, flavor="seurat_v3", n_top_genes=3000
    )
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    adata = adata[:, adata.var["highly_variable"]].copy()


    # BEGIN EXPLORATORY PRE-SMOOTHING: labels are never read; low_mask is audit-only.
    from scipy import sparse as sp
    import hashlib

    variant = "C3"
    x = (adata.X.toarray() if sp.issparse(adata.X) else np.asarray(adata.X))
    x = np.asarray(x, dtype=np.float32)
    assert x.shape == (3798, 3000) and np.isfinite(x).all()

    index = {str(b): i for i, b in enumerate(adata.obs_names)}
    src = np.array([index[a] for a, b in edges], dtype=np.int64)
    dst = np.array([index[b] for a, b in edges], dtype=np.int64)
    assert len(edges) == 22064

    if variant == "C2":
        pixels = meta.loc[adata.obs_names, ["pxl_row", "pxl_col"]].to_numpy(dtype=np.float64)
        distances = np.linalg.norm(pixels[src] - pixels[dst], axis=1)
        assert np.isfinite(distances).all() and (distances > 0).all()
        weights = (1.0 / distances).astype(np.float32)
    else:
        weights = np.ones(len(src), dtype=np.float32)

    A = sp.csr_matrix((weights, (src, dst)), shape=(adata.n_obs, adata.n_obs))
    assert A.nnz == 22064
    degree = np.asarray(A.sum(axis=1)).ravel()
    assert np.all(degree > 0)
    neighbor_mean = np.asarray((A @ x) / degree[:, None], dtype=np.float32)

    if variant == "C3":
        # Only observable expression-depth proxies are used, not low_mask.
        library_rank = pd.Series(sampled_umi).rank(method="average", pct=True).to_numpy()
        detected_rank = pd.Series(np.diff(raw.indptr)).rank(method="average", pct=True).to_numpy()
        reliability = (library_rank + detected_rank) / 2.0
        alpha = (0.75 - 0.5 * reliability).astype(np.float32)
        assert alpha.min() >= 0.25 and alpha.max() <= 0.75
    else:
        alpha = np.full(adata.n_obs, 0.5, dtype=np.float32)

    assert abs(float(alpha.mean()) - 0.5) < 0.002
    adata.X = np.asarray((1.0 - alpha[:, None]) * x + alpha[:, None] * neighbor_mean,
                         dtype=np.float32)
    assert np.isfinite(adata.X).all()

    hvg_signature = hashlib.sha256("\n".join(adata.var_names).encode("utf-8")).hexdigest()
    depth_signature = hashlib.sha256(
        low_mask.tobytes() + np.asarray(sampled_umi, dtype=np.int64).tobytes()
    ).hexdigest()
    print(f"SMOOTHING AUDIT | mode={variant} | alpha_mean={alpha.mean():.6f} "
          f"| alpha_min={alpha.min():.6f} | alpha_max={alpha.max():.6f} "
          f"| hvg_hash={hvg_signature[:12]} | depth_hash={depth_signature[:12]}", flush=True)
    # END EXPLORATORY PRE-SMOOTHING.

    data = Transfer_pytorch_Data(adata)
    assert data.x.shape == (3798, 3000)
    assert data.edge_index.shape == (2, 25862)
    assert bool(torch.isfinite(data.x).all())

    data = data.to(device)
    model = STAGATE(hidden_dims=[3000, 512, 30]).to(device)
    optimizer = torch.optim.Adam(
        model.parameters(), lr=0.001, weight_decay=0.0001
    )

    config = {
        "dataset": "BreastCancer_BlockA_Section1_Heterodepth_C3",
        "method": "STAGATE_pyG",
        "graph": "Visium_hex_six_neighbors",
        "undirected_edges": 11032,
        "self_loops": 3798,
        "hvg": 3000,
        "smoothing_variant": "C3_adaptive_reliability",
        "smoothing_mean_alpha": float(alpha.mean()),
        "hvg_signature": hvg_signature,
        "depth_signature": depth_signature,
        "depth_perturbation": "binomial_spot_level",
        "low_depth_fraction_of_spots": 0.5,
        "low_depth_retention_probability": 0.10,
        "high_depth_retention_probability": 1.0,
        "depth_seed": depth_seed,
        "achieved_low_depth_UMI_retention": float(retention),
        "achieved_zero_fraction": float(achieved_zero),
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
    pd.DataFrame({
        "barcode": adata.obs_names,
        "low_depth": low_mask,
        "retention_probability": np.where(low_mask, 0.1, 1.0),
        "original_umi": original_umi,
        "sampled_umi": sampled_umi
    }).to_csv(OUT / "depth_assignment.csv", index=False)
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

        assert embedding.shape == (3798, 30)
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
