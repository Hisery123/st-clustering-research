"""Manual Windows pilot: C0 existing vs C1/C2/C3 STAGATE on the same heterodepth Breast slice.

Run from Windows PowerShell with the existing STAGATE_PyG Python executable.
Creates only new script/result files. Never overwrites original data or C0 outputs.
This is EXPLORATORY, not the pre-registered DLPFC A2 or an independent test.
"""
from pathlib import Path
import ast
import hashlib
import json
import subprocess
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

ROOT = Path(r"D:\paper\ST_Benchmark_Planning\mvp")
TRAIN_SRC = ROOT / "stagate_breast_heterodepth_v1.py"
EVAL_SRC = ROOT / "evaluate_breast_heterodepth_v1.py"
BASE_NAME = "stagate_breast_cancer_block_a_section1_heterodepth_v1_seed0"
BASE = ROOT / "results" / BASE_NAME
PILOT = ROOT / "results" / "cann_breast_heterodepth_pilot_v1"
CODES = {
    "C0": BASE_NAME,
    "C1": "stagate_breast_cancer_block_a_section1_heterodepth_v1_c1_seed0",
    "C2": "stagate_breast_cancer_block_a_section1_heterodepth_v1_c2_seed0",
    "C3": "stagate_breast_cancer_block_a_section1_heterodepth_v1_c3_seed0",
}
NAMES = {
    "C1": "uniform_half",
    "C2": "fixed_distance_half",
    "C3": "adaptive_reliability",
}
EVAL_FILE = "evaluation_n15_r1_seed42.json"
BOUNDARY_FILE = "boundary_diagnostic_n15_r1_seed42.json"


def replace_once(source, old, new):
    n = source.count(old)
    if n != 1:
        raise RuntimeError(f"Expected exactly 1 occurrence ({n}): {old!r}")
    return source.replace(old, new, 1)


# All arms get the SAME observed heterodepth matrix and SAME HVGs.
# Neighbor graph is the original spatial hexagon graph, not expression KNN.
# C1: 50% original expression + 50% uniform neighbor mean.
# C2: 50% original expression + 50% inverse-pixel-distance neighbor mean.
# C3: node-dependent mixture; reliability from observed UMI and detected genes.
# C3 smoothing coefficients do not depend on synthetic assignment or reference annotations.
# The mean smoothing strength is ~0.5 to fairly compare with C1/C2.
SMOOTHING = '''
    # BEGIN EXPLORATORY PRE-SMOOTHING: labels are never read; low_mask is audit-only.
    from scipy import sparse as sp
    import hashlib

    variant = "__VARIANT__"
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

    hvg_signature = hashlib.sha256("\\n".join(adata.var_names).encode("utf-8")).hexdigest()
    depth_signature = hashlib.sha256(
        low_mask.tobytes() + np.asarray(sampled_umi, dtype=np.int64).tobytes()
    ).hexdigest()
    print(f"SMOOTHING AUDIT | mode={variant} | alpha_mean={alpha.mean():.6f} "
          f"| alpha_min={alpha.min():.6f} | alpha_max={alpha.max():.6f} "
          f"| hvg_hash={hvg_signature[:12]} | depth_hash={depth_signature[:12]}", flush=True)
    # END EXPLORATORY PRE-SMOOTHING.
'''


def create_scripts():
    if not TRAIN_SRC.is_file() or not EVAL_SRC.is_file():
        raise FileNotFoundError("Existing heterodepth source scripts are missing")
    for name in ("config.json", "depth_assignment.csv", "embedding.csv", EVAL_FILE, BOUNDARY_FILE):
        if not (BASE / name).is_file():
            raise FileNotFoundError(BASE / name)
    if PILOT.exists():
        raise FileExistsError(f"Pilot already exists: {PILOT}")

    train_src = TRAIN_SRC.read_text(encoding="utf-8-sig")
    eval_src = EVAL_SRC.read_text(encoding="utf-8-sig")
    for token in ("depth_seed = 20261103", "rng.binomial(", '"hvg": 3000',
                  "sampled_umi", "low_mask"):
        if token not in train_src:
            raise RuntimeError(f"Missing expected perturbation marker: {token}")

    staged = []
    for code in ("C1", "C2", "C3"):
        new_name = CODES[code]
        train_target = ROOT / f"stagate_breast_heterodepth_v1_{code.lower()}.py"
        eval_target = ROOT / f"evaluate_breast_heterodepth_v1_{code.lower()}.py"
        for path in (train_target, eval_target, ROOT / "results" / new_name):
            if path.exists():
                raise FileExistsError(f"Refusing overwrite: {path}")

        train = replace_once(train_src, BASE_NAME, new_name)
        train = replace_once(
            train, '"dataset": "BreastCancer_BlockA_Section1_Heterodepth"',
            f'"dataset": "BreastCancer_BlockA_Section1_Heterodepth_{code}"')
        train = replace_once(
            train, "    data = Transfer_pytorch_Data(adata)",
            SMOOTHING.replace("__VARIANT__", code) + "\n    data = Transfer_pytorch_Data(adata)")
        train = replace_once(
            train, '        "hvg": 3000,',
            '        "hvg": 3000,\n'
            f'        "smoothing_variant": "{code}_{NAMES[code]}",\n'
            '        "smoothing_mean_alpha": float(alpha.mean()),\n'
            '        "hvg_signature": hvg_signature,\n'
            '        "depth_signature": depth_signature,')

        ev = replace_once(eval_src, BASE_NAME, new_name)
        ev = replace_once(
            ev, '"dataset": "BreastCancer_BlockA_Section1_Heterodepth"',
            f'"dataset": "BreastCancer_BlockA_Section1_Heterodepth_{code}"')

        ast.parse(train, filename=str(train_target))
        ast.parse(ev, filename=str(eval_target))
        staged.extend([(train_target, train), (eval_target, ev)])

    for path, content in staged:
        with path.open("x", encoding="utf-8") as fh:
            fh.write(content)
    print("C1/C2/C3 scripts created and syntax-checked; C0 is reused unchanged.", flush=True)
    return staged


def diagnostics():
    base_depth = pd.read_csv(BASE / "depth_assignment.csv").set_index("barcode")
    meta = pd.read_csv(
        ROOT / "data" / "breast_cancer_block_a_section1" / "spots_aligned.csv"
    ).set_index("barcode")
    assert base_depth.index.equals(meta.index) and len(meta) == 3798
    low = base_depth["low_depth"].astype(str).str.lower().eq("true").to_numpy()
    assert int(low.sum()) == 1899
    labels = meta["annot_type"].astype(str).to_numpy()
    coords = list(zip(meta["array_row"].astype(int), meta["array_col"].astype(int)))
    lookup = {xy: i for i, xy in enumerate(coords)}
    edges = [
        (i, lookup[(r + dr, c + dc)])
        for i, (r, c) in enumerate(coords)
        for dr, dc in [(0, 2), (1, 1), (1, -1)]
        if (r + dr, c + dc) in lookup
    ]
    assert len(edges) == 11032
    ei, ej = np.asarray(edges, dtype=np.int64).T
    boundary_truth = labels[ei] != labels[ej]
    is_ll = low[ei] & low[ej]
    is_hh = (~low[ei]) & (~low[ej])
    masks = {"low_low": is_ll, "low_high": ~(is_ll | is_hh), "high_high": is_hh}

    def f1_on_edges(pred, selected):
        actual = boundary_truth[selected]
        estimated = pred[ei[selected]] != pred[ej[selected]]
        tp = np.count_nonzero(actual & estimated)
        return float(2 * tp / (np.count_nonzero(actual) + np.count_nonzero(estimated))) \
            if (np.count_nonzero(actual) + np.count_nonzero(estimated)) else 0.0

    result = []
    hvg_hashes, depth_hashes = [], []
    for code in ("C0", "C1", "C2", "C3"):
        folder = ROOT / "results" / CODES[code]
        for filename in (EVAL_FILE, BOUNDARY_FILE, "depth_assignment.csv", "loss.csv", "embedding.csv"):
            if not (folder / filename).is_file():
                raise FileNotFoundError(folder / filename)
        other_depth = pd.read_csv(folder / "depth_assignment.csv").set_index("barcode")
        pd.testing.assert_frame_equal(other_depth, base_depth)
        emb = pd.read_csv(folder / "embedding.csv").set_index("barcode")
        loss = pd.read_csv(folder / "loss.csv")
        assert emb.index.equals(meta.index) and emb.shape == (3798, 30)
        assert np.isfinite(emb.to_numpy()).all()
        assert len(loss) == 1000 and int(loss["epoch"].iloc[-1]) == 1000
        ev = json.loads((folder / EVAL_FILE).read_text(encoding="utf-8"))
        boundary = json.loads((folder / BOUNDARY_FILE).read_text(encoding="utf-8"))
        p = pd.read_csv(folder / "leiden_n15_r1_seed42.csv").set_index("barcode")
        assert p.index.equals(meta.index)
        pred = p["leiden"].astype(str).to_numpy()
        row = {
            "arm": code,
            "predicted_clusters": int(len(np.unique(pred))),
            "ARI": float(adjusted_rand_score(labels, pred)),
            "NMI": float(normalized_mutual_info_score(labels, pred, average_method="arithmetic")),
            "boundary_f1": f1_on_edges(pred, np.ones(len(edges), dtype=bool)),
            "low_low_boundary_f1": f1_on_edges(pred, masks["low_low"]),
            "low_high_boundary_f1": f1_on_edges(pred, masks["low_high"]),
            "high_high_boundary_f1": f1_on_edges(pred, masks["high_high"]),
            "final_loss": float(loss["loss"].iloc[-1]),
        }
        assert abs(row["ARI"] - float(ev["ARI"])) < 1e-8
        assert abs(row["NMI"] - float(ev["NMI"])) < 1e-8
        assert abs(row["boundary_f1"] - float(boundary["boundary_f1"])) < 1e-8
        if code != "C0":
            cfg = json.loads((folder / "config.json").read_text(encoding="utf-8"))
            hvg_hashes.append(cfg["hvg_signature"])
            depth_hashes.append(cfg["depth_signature"])
        result.append(row)
        print(
            f"{code} | clusters={row['predicted_clusters']} | ARI={row['ARI']:.6f} "
            f"| NMI={row['NMI']:.6f} | F1={row['boundary_f1']:.6f} "
            f"| LL={row['low_low_boundary_f1']:.6f} "
            f"| LH={row['low_high_boundary_f1']:.6f} "
            f"| HH={row['high_high_boundary_f1']:.6f}",
            flush=True,
        )
    if len(set(hvg_hashes)) != 1 or len(set(depth_hashes)) != 1:
        raise AssertionError("C1-C3 HVG or perturbation signatures mismatch")

    PILOT.mkdir(parents=True, exist_ok=False)
    pd.DataFrame(result).to_csv(PILOT / "comparison_summary.csv", index=False)
    manifest = {
        "status": "EXPLORATORY ONLY; not the original DLPFC A2 or independent test",
        "source_training_script": str(TRAIN_SRC),
        "source_evaluation_script": str(EVAL_SRC),
        "C0": "existing heterodepth STAGATE, unchanged",
        "C1": "0.5 * own log-normalized HVG expression + 0.5 * uniform spatial neighbor mean",
        "C2": "0.5 * own expression + 0.5 * inverse-pixel-distance weighted spatial neighbor mean",
        "C3": "alpha_i = 0.75 - 0.5 * average percentile rank(observed UMI, detected genes); alpha_i neighbor mixing",
        "preprocessing": "same perturbation, same HVG procedure, same training settings; smoothing before model input",
        "evaluation": "Leiden n15, Euclidean, UMAP, r1.0, seed42; reference labels for evaluation only",
        "random_seeds": {"training": 0, "depth_assignment": 20261103, "Leiden": 42},
        "all_arms_input_hvg_sha256": hvg_hashes[0],
        "all_arms_depth_assignment_sha256": depth_hashes[0],
        "interpretation_constraint": "Single slice/seed, exploratory; do not select hyperparameters on pathology labels",
    }
    (PILOT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"PILOT COMPARISON SAVED: {PILOT}", flush=True)
    print("CAN-N EXPLORATORY C0-C3 PILOT PASS", flush=True)


def main():
    create_scripts()
    for code in ("C1", "C2", "C3"):
        train = ROOT / f"stagate_breast_heterodepth_v1_{code.lower()}.py"
        evaluation = ROOT / f"evaluate_breast_heterodepth_v1_{code.lower()}.py"
        print(f"\n=== {code} TRAIN ===", flush=True)
        subprocess.run([sys.executable, "-u", str(train)], check=True)
        print(f"\n=== {code} EVALUATE ===", flush=True)
        subprocess.run([sys.executable, "-u", str(evaluation)], check=True)
    print("\n=== C0-C3 PAIRWISE DIAGNOSTICS ===", flush=True)
    diagnostics()


if __name__ == "__main__":
    main()
