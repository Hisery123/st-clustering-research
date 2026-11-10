"""Render the two CellCharter 151507 hop ablations as a six-panel editable SVG.

Source: local posthoc evaluation CSVs only. No model training or relabeling.
The plots are descriptive for one exploratory section and one seed. The
fixed-width permutation control is NOT a clean causal isolation of hop radius.

Usage:
    python plot_cellcharter_two_ablation_comparison.py
    python plot_cellcharter_two_ablation_comparison.py --old path.csv --fixed path.csv --out result.svg
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(r"D:\paper\CellCharter_reproduction")
DEFAULT_OLD = ROOT / "runs/151507_hop_ablation_evaluation_seed0/hop_ablation_metrics.csv"
DEFAULT_FIXED = ROOT / "runs/151507_fixed25_permutation_evaluation_seed0/fixed25_permutation_metrics.csv"
DEFAULT_OUT = ROOT / "figures/cellcharter_151507_two_hop_ablations_comparison.svg"

MEASURES = (
    "ARI", "NMI", "boundary_precision", "boundary_recall", "boundary_f1",
    "spatial_neighbor_agreement",
)
PALETTE = {
    "ARI": "#2867A8", "NMI": "#BF6C28",
    "boundary_precision": "#2867A8",
    "boundary_recall": "#BF6C28",
    "boundary_f1": "#19836B",
    "spatial_neighbor_agreement": "#7758A6",
}


def read_metrics(path: Path, dims: list[int]) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"Missing source CSV: {path}")
    df = pd.read_csv(path).sort_values("hop").reset_index(drop=True)
    needed = {"hop", "features", *MEASURES}
    missing = needed.difference(df.columns)
    if missing:
        raise ValueError(f"Missing columns in {path}: {sorted(missing)}")
    if df["hop"].tolist() != [0, 1, 2, 3, 4]:
        raise ValueError(f"Expected exactly hops 0..4 in {path}")
    if df["features"].tolist() != dims:
        raise ValueError(f"Unexpected feature dimensions in {path}: {df['features'].tolist()}")
    vals = df[list(MEASURES)].to_numpy(dtype=float)
    if not np.isfinite(vals).all() or np.any((vals < 0) | (vals > 1)):
        raise ValueError(f"Scores must be finite and within [0,1]: {path}")
    return df


def draw(old: pd.DataFrame, fixed: pd.DataFrame, outfile: Path):
    if outfile.exists():
        raise FileExistsError(f"Output exists; refusing overwrite: {outfile}")
    outfile.parent.mkdir(parents=True, exist_ok=True)

    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 9,
        "axes.titlesize": 11, "axes.labelsize": 9,
        "svg.fonttype": "none",  # text remains editable
        "axes.spines.top": False, "axes.spines.right": False,
        "savefig.facecolor": "white",
    })
    fig, axs = plt.subplots(2, 3, figsize=(14.5, 8.0), dpi=170)
    fig.subplots_adjust(left=0.075, right=0.975, top=0.80, bottom=0.18,
                        hspace=0.62, wspace=0.25)
    names = [
        "(1) Global clustering agreement",
        "(2) Boundary detection",
        "(3) Spatial continuity",
    ]
    panels = [
        [("ARI", "ARI"), ("NMI", "NMI")],
        [("boundary_precision", "Precision"),
         ("boundary_recall", "Recall"), ("boundary_f1", "F1")],
        [("spatial_neighbor_agreement", "Same-cluster neighbors")],
    ]
    limits = [(0, 0.7), (0, 0.9), (0, 1)]
    for row, (df, row_text) in enumerate([
        (old, "A  Variable width: 5 / 10 / 15 / 20 / 25 dimensions"),
        (fixed, "B  Fixed 25 dimensions: unused neighborhood blocks permuted"),
    ]):
        x = df["hop"].to_numpy(dtype=int)
        for col, (title, series) in enumerate(zip(names, panels)):
            ax = axs[row, col]
            for key, label in series:
                ax.plot(x, df[key].to_numpy(dtype=float),
                        color=PALETTE[key], lw=2.15, marker="o", ms=5,
                        markeredgecolor="white", markeredgewidth=0.7, label=label)
            ax.set_title(title, loc="left", pad=9, fontweight="semibold")
            ax.set_xticks(x)
            ax.set_xlim(-0.2, 4.2)
            ax.set_ylim(*limits[col])
            ax.grid(axis="y", alpha=0.22, lw=0.7)
            ax.set_xlabel("Aligned neighborhood hops (h)")
            if col == 0:
                ax.set_ylabel("Score (0–1)")
            if col == 0:
                ax.legend(loc="upper left", fontsize=8.1, frameon=False)
            elif col == 1:
                ax.legend(loc="upper right", fontsize=8.1, frameon=False)
            else:
                ax.legend(loc="lower right", fontsize=7.9, frameon=False)
        fig.text(0.076, 0.855 if row == 0 else 0.483, row_text,
                 fontsize=11, weight="bold", color="#26354B")

    fig.suptitle("CellCharter | DLPFC 151507 | Two exploratory hop ablations",
                 x=0.5, y=0.965, fontsize=15, fontweight="bold")
    fig.text(0.5, 0.918,
             "Identical metric definitions and labeled-spot/edge sets; "
             "not a matched-initialization causal comparison",
             ha="center", fontsize=9, color="#4E5864")
    fig.text(0.075, 0.108,
             "n = 1 explored section, 1 seed per condition; 4,221 labeled spots, "
             "12,381 evaluated edges, 950 reference-boundary edges.",
             fontsize=9, color="#333333")
    fig.text(0.075, 0.082,
             "Group B h=0 contains shuffled neighborhood blocks (not expression-only). "
             "GMM h=4 fits differ across experiments (partition ARI = 0.713871).",
             fontsize=8.4, color="#4E5864")
    fig.text(0.075, 0.056,
             "Higher boundary recall may reflect many false-positive edges; "
             "none of these curves alone establishes spatial over-smoothing.",
             fontsize=8.4, color="#4E5864")
    fig.savefig(outfile, format="svg", bbox_inches="tight")
    plt.close(fig)
    print("COMPARISON_SVG_SAVED:", outfile, flush=True)
    print("SVG_SIZE_BYTES:", outfile.stat().st_size, flush=True)
    print("TWO_ABLATION_PLOT_PASS", flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--old", type=Path, default=DEFAULT_OLD)
    p.add_argument("--fixed", type=Path, default=DEFAULT_FIXED)
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = p.parse_args()
    a = read_metrics(args.old, [5, 10, 15, 20, 25])
    b = read_metrics(args.fixed, [25] * 5)
    print("SOURCE_OLD:", args.old, flush=True)
    print("SOURCE_FIXED:", args.fixed, flush=True)
    print("VALIDATED_ROWS:", len(a), len(b), flush=True)
    draw(a, b, args.out)


if __name__ == "__main__":
    main()
