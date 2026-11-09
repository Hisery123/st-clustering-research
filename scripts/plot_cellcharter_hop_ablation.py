"""Plot CellCharter 0-4-hop exploratory ablation from researcher's local evaluation CSV.

This is a plotting script only: no training, label processing, or statistical significance.
Usage (Windows):
  python scripts/plot_cellcharter_hop_ablation.py --csv hop_ablation_metrics.csv --out figure.svg
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

COLS = [
    "hop", "ARI", "NMI", "boundary_precision",
    "boundary_recall", "boundary_f1", "spatial_neighbor_agreement"
]

def plot(csv: Path, out: Path):
    assert csv.is_file(), f"Missing evaluation CSV: {csv}"
    assert not out.exists(), f"Refusing to overwrite: {out}"
    df = pd.read_csv(csv)
    assert all(c in df.columns for c in COLS), "Required metric column is missing"
    df = df.sort_values("hop").reset_index(drop=True)
    assert df["hop"].tolist() == [0, 1, 2, 3, 4], "Must have exactly 0-4 hop data"
    values = df[COLS].to_numpy(dtype=float)
    assert np.isfinite(values).all(), "NaN/Inf found"
    assert ((df[COLS[1:]] >= 0) & (df[COLS[1:]] <= 1)).all().all()

    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 9,
        "axes.titlesize": 11, "axes.labelsize": 9,
        "svg.fonttype": "none",
        "axes.spines.top": False, "axes.spines.right": False,
    })
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), dpi=160, constrained_layout=True)
    hop = df["hop"].to_numpy(dtype=int)
    colors = ["#285b9f", "#ba6032", "#287f6b"]
    specs = [
        [("ARI", "ARI", colors[0], "o"), ("NMI", "NMI", colors[1], "s")],
        [("boundary_precision", "Precision", colors[0], "o"),
         ("boundary_recall", "Recall", colors[1], "s"),
         ("boundary_f1", "F1", colors[2], "^")],
        [("spatial_neighbor_agreement", "Same-cluster neighbors", colors[0], "o")],
    ]
    titles = [
        "(a) Global label agreement",
        "(b) Reference-boundary detection",
        "(c) Spatial continuity",
    ]
    for ax, title, lines in zip(axes, titles, specs):
        for key, label, color, marker in lines:
            ax.plot(hop, df[key].to_numpy(dtype=float), marker=marker,
                    ms=5.5, lw=1.9, color=color, label=label)
        ax.set_title(title, loc="left", pad=11, fontweight="semibold")
        ax.set_xlabel("Neighborhood aggregation hops")
        ax.set_ylabel("Score")
        ax.set_xticks(hop)
        ax.set_xlim(-0.25, 4.25)
        ax.grid(axis="y", linewidth=0.6, alpha=0.22)
        ax.legend(loc="best", frameon=False, fontsize=8)
    axes[0].set_ylim(0.25, 0.7)
    axes[1].set_ylim(0.0, 0.7)
    axes[2].set_ylim(0.4, 1.0)
    fig.suptitle("CellCharter v0.3.2 | DLPFC 151507 | Exploratory hop ablation",
                 fontsize=14, fontweight="bold")
    fig.supxlabel(
        "One section, one seed (0); scVI fixed; GMM K=7; "
        "feature dimensions: 5, 10, 15, 20, 25",
        fontsize=8, color="#444444"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, format="svg", bbox_inches="tight")
    plt.close(fig)
    print("CSV_ROWS:", len(df))
    print("SVG_SAVED:", out)
    print("SVG_SIZE_BYTES:", out.stat().st_size)
    print("HOP_PLOT_PASS")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    plot(args.csv, args.out)
