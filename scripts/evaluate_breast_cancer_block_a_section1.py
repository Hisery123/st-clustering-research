from pathlib import Path
import json
import numpy as np
import pandas as pd
import scanpy as sc
import anndata as ad
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

root = Path(r"D:\paper\ST_Benchmark_Planning\mvp")
base = root / "data" / "breast_cancer_block_a_section1"
out = root / "results" / "stagate_breast_cancer_block_a_section1_controlled_seed0"

names = [
    "leiden_n15_r1_seed42.csv",
    "leiden_n15_r1_seed42_config.json",
    "evaluation_n15_r1_seed42.json",
    "boundary_diagnostic_n15_r1_seed42.json",
    "reference_cluster_contingency.csv",
    "reference_fragmentation.csv",
]
for name in names:
    if (out / name).exists():
        raise FileExistsError(f"Refusing overwrite: {out / name}")

loss = pd.read_csv(out / "loss.csv")
emb = pd.read_csv(out / "embedding.csv").set_index("barcode")
meta = pd.read_csv(base / "spots_aligned.csv").set_index("barcode")

assert np.array_equal(loss["epoch"].to_numpy(), np.arange(1, 1001))
assert np.isfinite(loss["loss"]).all()
assert emb.shape == (3798, 30)
assert emb.index.is_unique and meta.index.is_unique
assert emb.index.equals(meta.index)
assert np.isfinite(emb.to_numpy()).all()
assert meta["annot_type"].notna().all()
assert meta["annot_type"].nunique() == 4

with open(out / "config.json", encoding="utf-8") as f:
    train_config = json.load(f)
assert train_config["epochs"] == 1000
assert train_config["hvg"] == 3000
assert train_config["undirected_edges"] == 11032

print("EMBEDDING AND LOSS VALIDATION PASS", flush=True)
print("Initial loss:", float(loss["loss"].iloc[0]))
print("Final loss:", float(loss["loss"].iloc[-1]))

adata = ad.AnnData(
    X=emb.to_numpy(dtype=np.float32),
    obs=pd.DataFrame(index=emb.index)
)

sc.pp.neighbors(
    adata,
    n_neighbors=15,
    metric="euclidean",
    method="umap",
    use_rep="X",
    random_state=42
)
sc.tl.leiden(
    adata,
    resolution=1.0,
    random_state=42,
    flavor="leidenalg",
    directed=True,
    n_iterations=-1,
    key_added="leiden"
)

pred = pd.Series(
    adata.obs["leiden"].astype(str).to_numpy(),
    index=emb.index,
    name="leiden"
)
ref = meta["annot_type"].astype(str)

ari = float(adjusted_rand_score(ref, pred))
nmi = float(normalized_mutual_info_score(
    ref, pred, average_method="arithmetic"
))
ct = pd.crosstab(ref, pred)
purity = float(ct.max(axis=0).sum() / len(ref))

# Spatial boundary evaluation using the same six-neighbor graph
coords = list(zip(
    meta["array_row"].astype(int),
    meta["array_col"].astype(int)
))
lookup = {coord: i for i, coord in enumerate(coords)}
edges = []

for i, (r, c) in enumerate(coords):
    for dr, dc in [(0, 2), (1, 1), (1, -1)]:
        j = lookup.get((r + dr, c + dc))
        if j is not None:
            edges.append((i, j))

assert len(edges) == 11032
edges = np.asarray(edges, dtype=np.int64)
i, j = edges[:, 0], edges[:, 1]

r = ref.to_numpy()
p = pred.to_numpy()
true_boundary = r[i] != r[j]
pred_boundary = p[i] != p[j]

tp = int(np.sum(true_boundary & pred_boundary))
n_true = int(true_boundary.sum())
n_pred = int(pred_boundary.sum())
precision = tp / n_pred if n_pred else 0.0
recall = tp / n_true if n_true else 0.0
f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

agreement = float(np.mean(~pred_boundary))
freq = pred.value_counts(normalize=True).to_numpy()
expected_agreement = float(np.sum(freq ** 2))
adjusted_agreement = (
    (agreement - expected_agreement) / (1 - expected_agreement)
)

fragmentation = []
for label, row in ct.iterrows():
    counts = np.sort(row.to_numpy())[::-1]
    target = int(np.ceil(0.9 * counts.sum()))
    k90 = int(np.searchsorted(np.cumsum(counts), target) + 1)
    fragmentation.append({
        "reference_class": label,
        "spots": int(counts.sum()),
        "clusters_for_90pct": k90
    })

evaluation = {
    "dataset": "BreastCancer_BlockA_Section1",
    "method": "STAGATE_pyG + Leiden",
    "total_spots": len(ref),
    "evaluated_spots": len(ref),
    "reference_column": "annot_type",
    "reference_classes": int(ref.nunique()),
    "predicted_clusters": int(pred.nunique()),
    "ARI": ari,
    "NMI": nmi,
    "nmi_average_method": "arithmetic",
    "cluster_purity": purity,
    "evaluation_type": "exploratory",
    "reference_labels_used_for_training_or_clustering": False
}

boundary = {
    "evaluated_spatial_edges": len(edges),
    "reference_boundary_edges": n_true,
    "predicted_boundary_edges": n_pred,
    "true_positive_boundary_edges": tp,
    "boundary_precision": precision,
    "boundary_recall": recall,
    "boundary_f1": f1,
    "spatial_neighbor_agreement": agreement,
    "chance_adjusted_agreement": adjusted_agreement,
    "evaluation_type": "exploratory"
}

leiden_config = {
    "method": "Leiden",
    "n_neighbors": 15,
    "metric": "euclidean",
    "neighbor_method": "umap",
    "resolution": 1.0,
    "seed": 42,
    "flavor": "leidenalg",
    "directed": True,
    "n_iterations": -1,
    "reference_labels_used": False,
    "scanpy_version": sc.__version__
}

pred.to_csv(out / names[0], index_label="barcode")
for filename, obj in [
    (names[1], leiden_config),
    (names[2], evaluation),
    (names[3], boundary)
]:
    (out / filename).write_text(
        json.dumps(obj, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
ct.to_csv(out / names[4])
pd.DataFrame(fragmentation).to_csv(out / names[5], index=False)

print("\n=== CLUSTERING RESULTS ===")
print("Predicted clusters:", pred.nunique())
print(f"ARI: {ari:.6f}")
print(f"NMI: {nmi:.6f}")
print(f"Cluster purity: {purity:.6f}")

print("\n=== SPATIAL BOUNDARY ===")
print("Reference boundary edges:", n_true)
print("Predicted boundary edges:", n_pred)
print("True positive boundary edges:", tp)
print(f"Boundary precision: {precision:.6f}")
print(f"Boundary recall: {recall:.6f}")
print(f"Boundary F1: {f1:.6f}")

print("\n=== REFERENCE FRAGMENTATION ===")
for item in fragmentation:
    print(item)

print("\nResults saved:", out)
print("BREAST CANCER CLUSTERING AND EVALUATION PASS")
