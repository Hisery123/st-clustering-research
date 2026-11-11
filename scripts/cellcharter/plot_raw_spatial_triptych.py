"""Visium reference-vs-raw-cluster triptych; only reads existing CSVs.

No majority-vote mapping of clusters to biological layers.
No fitting, no evaluation metric changes.
Sample IDs currently limited to pre-audited extension sections 151671/151676.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

DATA_ROOT = Path(r"D:\paper\ST_Benchmark_Planning\mvp\data")
RESULT_ROOT = Path(r"D:\paper\CellCharter_reproduction\results")
SAMPLES = ("151671", "151676")
REF_PALETTE = {
    "Layer 1": "#3366cc", "Layer 2": "#e69f00",
    "Layer 3": "#009e73", "Layer 4": "#d55e00",
    "Layer 5": "#9467bd", "Layer 6": "#8c564b",
    "WM": "#c77eb5", "Unlabeled": "#d4d4d4",
}
CLUSTER_PALETTE = ["#0072b2", "#e69f00", "#009e73", "#d55e00", "#cc79a7", "#555555", "#7f3c8d"]


def read_join(sample: str) -> pd.DataFrame:
    source = DATA_ROOT / sample
    predictions = RESULT_ROOT / f"mvp_fixed15_{sample}_gmm22911_batch_v1"
    spots = pd.read_csv(source / "spots_aligned.csv", dtype={"barcode": str})
    truth = pd.read_csv(source / "manual_layer_annotations.csv", dtype={"spot_name": str, "layer": str})
    a = pd.read_csv(predictions / "control_L0_L1_L2_predictions.csv", dtype={"barcode": str})
    b = pd.read_csv(predictions / "candidate_L0_L1_L4_predictions.csv", dtype={"barcode": str})
    if spots.barcode.duplicated().any() or truth.spot_name.duplicated().any():
        raise ValueError("Duplicated barcode/annotation spot name")
    if a.barcode.duplicated().any() or b.barcode.duplicated().any():
        raise ValueError("Duplicated prediction barcode")
    if set(spots.barcode) != set(a.barcode) or set(spots.barcode) != set(b.barcode):
        raise ValueError("Predictions do not match source spot barcode set")
    if not set(truth.spot_name).issubset(set(spots.barcode)):
        raise ValueError("Unknown reference annotation barcodes")
    if not ((spots.in_tissue == 1).all()):
        raise ValueError("Input includes spots marked out of tissue")
    df = spots.merge(truth[["spot_name", "layer"]], left_on="barcode", right_on="spot_name",
                     how="left", validate="one_to_one")
    df = df.merge(a.rename(columns={"cluster": "A"})[["barcode", "A"]],
                  on="barcode", validate="one_to_one")
    df = df.merge(b.rename(columns={"cluster": "B"})[["barcode", "B"]],
                  on="barcode", validate="one_to_one")
    if df[["A", "B", "pxl_row_in_fullres", "pxl_col_in_fullres"]].isna().any().any():
        raise ValueError("Missing predictions or spatial coordinates")
    if len(df) != len(spots):
        raise ValueError("Barcode alignment changed spot count")
    print(f"SPATIAL_INPUT_CHECK_PASS {sample} spots={len(df)} labeled={df.layer.notna().sum()}")
    print(f"RAW_CLUSTERS A={sorted(df.A.unique().tolist())} B={sorted(df.B.unique().tolist())}")
    return df


def draw(df: pd.DataFrame, sample: str, destination: Path) -> None:
    plt.rcParams["svg.fonttype"] = "none"  # retain editable text in SVG
    panels = [
        ("layer", "Reference annotation"),
        ("A", "Control A: raw GMM clusters"),
        ("B", "Candidate B: raw GMM clusters"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.5), constrained_layout=True)
    for ax, (column, heading) in zip(axes, panels):
        if column == "layer":
            values = df.layer.fillna("Unlabeled")
            categories = sorted(values.unique(), key=lambda x: (x != "Unlabeled", x))
            palette = REF_PALETTE
        else:
            values = df[column]
            categories = sorted(values.unique())
            if len(categories) > len(CLUSTER_PALETTE):
                raise ValueError("Too many clusters for predefined palette")
            palette = {c: CLUSTER_PALETTE[i] for i, c in enumerate(categories)}
        for cat in categories:
            selected = df.loc[values == cat]
            ax.scatter(selected.pxl_col_in_fullres, -selected.pxl_row_in_fullres,
                       c=palette.get(cat, "#888888"), s=8, linewidths=0,
                       rasterized=False, label=str(cat))
        ax.set_title(heading, fontsize=11)
        ax.set_aspect("equal")
        ax.set_xlim(df.pxl_col_in_fullres.min()-200, df.pxl_col_in_fullres.max()+200)
        ax.set_ylim(-df.pxl_row_in_fullres.max()-200, -df.pxl_row_in_fullres.min()+200)
        ax.axis("off")
        ax.legend(title="Layer" if column == "layer" else "Cluster ID", loc="lower center",
                  bbox_to_anchor=(0.5, -0.10), ncol=4, fontsize=8, title_fontsize=8,
                  frameon=False)
    fig.suptitle(f"DLPFC {sample}: reference layers and unmapped spatial clusters\n"
                 "Colors/cluster IDs are NOT aligned between reference, A, and B", fontsize=12)
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite: {destination}")
    fig.savefig(destination, format="svg", bbox_inches="tight")
    plt.close(fig)
    print("RAW_SPATIAL_TRIPTYCH_SAVED", destination)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", choices=SAMPLES, required=True)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    df = read_join(args.sample)
    if args.check_only:
        print("CHECK_ONLY_NO_FILES_WRITTEN")
        return
    output = RESULT_ROOT / "thesis_fixed15_12_sections_summary_v1"
    if not output.is_dir():
        raise FileNotFoundError(output)
    draw(df, args.sample, output / f"spatial_triptych_{args.sample}_raw_clusters.svg")


if __name__ == "__main__":
    main()
