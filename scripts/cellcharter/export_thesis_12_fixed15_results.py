"""Read-only source audit and export of frozen 12-section CellCharter A/B metrics.

Reads local original results.json only; does not fit models.
Writes derived CSV and editable SVG into a NEW dedicated directory.
Use --check-only to validate all input files without writing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

DEFAULT_ROOT = Path(r"D:\paper\CellCharter_reproduction\results")
SOURCES = (
    ("151507", "D1", "development", "mvp_fixed15_block_swap_151507_seed22911_v1"),
    ("151508", "D1", "development", "mvp_fixed15_block_swap_151508_gmm22911_v1"),
    ("151509", "D1", "extension", "mvp_fixed15_151509_gmm22911_batch_v1"),
    ("151510", "D1", "extension", "mvp_fixed15_151510_gmm22911_batch_v1"),
    ("151669", "D2", "extension", "mvp_fixed15_151669_gmm22911_batch_v1"),
    ("151670", "D2", "extension", "mvp_fixed15_151670_gmm22911_batch_v1"),
    ("151671", "D2", "extension", "mvp_fixed15_151671_gmm22911_batch_v1"),
    ("151672", "D2", "extension", "mvp_fixed15_151672_gmm22911_batch_v1"),
    ("151673", "D3", "extension", "mvp_fixed15_151673_gmm22911_batch_v1"),
    ("151674", "D3", "extension", "mvp_fixed15_151674_gmm22911_batch_v1"),
    ("151675", "D3", "extension", "mvp_fixed15_151675_gmm22911_batch_v1"),
    ("151676", "D3", "extension", "mvp_fixed15_151676_gmm22911_batch_v1"),
)
A = "control_L0_L1_L2"
B = "candidate_L0_L1_L4"
METRICS = ("ari", "nmi", "boundary_f1")
COUNTS = ("boundary_tp", "boundary_fp", "boundary_fn", "l5_l6_detected", "l5_l6_reference")


def get_metrics(path: Path) -> tuple[dict, str]:
    raw = path.read_bytes()
    report = json.loads(raw)
    if not isinstance(report, dict) or A not in report or B not in report:
        raise ValueError(f"Missing A/B metrics in {path}")
    for side in (A, B):
        d = report[side]
        for key in (*METRICS, *COUNTS):
            if key not in d:
                raise ValueError(f"Missing {side}/{key} in {path}")
        tp, fp, fn = (int(d["boundary_" + x]) for x in ("tp", "fp", "fn"))
        if min(tp, fp, fn) < 0:
            raise ValueError(f"Negative boundary count: {path}")
        denom = 2 * tp + fp + fn
        f1 = 2 * tp / denom if denom else 0.0
        if not np.isclose(f1, float(d["boundary_f1"]), atol=1e-9, rtol=0):
            raise ValueError(f"Boundary F1/count mismatch: {path} {side}")
        if not (0 <= int(d["l5_l6_detected"]) <= int(d["l5_l6_reference"])):
            raise ValueError(f"Invalid L5/L6 count: {path} {side}")
    if int(report[A]["l5_l6_reference"]) != int(report[B]["l5_l6_reference"]):
        raise ValueError(f"L5/L6 denominator mismatch: {path}")
    return report, hashlib.sha256(raw).hexdigest()


def collect(root: Path) -> pd.DataFrame:
    rows = []
    for sid, donor, cohort, dirname in SOURCES:
        path = root / dirname / "results.json"
        report, sha = get_metrics(path)
        row = {"slice": sid, "donor": donor, "cohort": cohort, "source_file": str(path),
               "source_sha256": sha, "gmm_seed": 22911}
        for key in (*METRICS, *COUNTS):
            row[f"{key}_A"] = report[A][key]
            row[f"{key}_B"] = report[B][key]
            row[f"delta_{key}"] = report[B][key] - report[A][key]
        rows.append(row)
        print(f"SOURCE_PASS {sid} {donor} {cohort} {sha}", flush=True)
    return pd.DataFrame(rows)


def plot_deltas(df: pd.DataFrame, key: str, output: Path) -> None:
    # Matplotlib figures are generated only from the validated original JSON values.
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 4.2))
    x = np.arange(len(df))
    vals = df[f"delta_{key}"].to_numpy(dtype=float)
    donor_groups = ["D1", "D2", "D3"]
    for donor in donor_groups:
        mask = df["donor"].eq(donor).to_numpy()
        ax.scatter(x[mask], vals[mask], s=62, label=f"{donor} (4 sections)", zorder=3)
    dev = df["cohort"].eq("development").to_numpy()
    ax.scatter(x[dev], vals[dev], s=160, facecolors="none", edgecolors="black", linewidths=1.3,
               label="Development sections", zorder=4)
    ax.axhline(0, linewidth=1)
    ax.axvline(3.5, linestyle=":", linewidth=0.8)
    ax.axvline(7.5, linestyle=":", linewidth=0.8)
    ax.set_xticks(x, df["slice"], rotation=45)
    ax.set_xlabel("DLPFC section (within donor)")
    ax.set_ylabel(f"Candidate B - control A: {key}")
    ax.set_title(f"Fixed 15D neighborhood blocks: delta {key}")
    ax.legend(fontsize=8, ncol=2)
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(output, format="svg")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--check-only", action="store_true", help="Validate 12 inputs; no writes")
    args = parser.parse_args()
    df = collect(args.root)
    if len(df) != 12 or len(set(df["slice"])) != 12:
        raise RuntimeError("Not exactly 12 unique sections")
    print("THESIS_12_INPUT_CHECK_COMPLETE 12/12", flush=True)
    if args.check_only:
        print("CHECK_ONLY_NO_FILES_WRITTEN", flush=True)
        return

    output = args.root / "thesis_fixed15_12_sections_summary_v1"
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite existing output: {output}")
    output.mkdir(parents=False)
    df.to_csv(output / "section_metrics_A_B_delta.csv", index=False, float_format="%.12g")
    for metric in METRICS:
        plot_deltas(df, metric, output / f"delta_{metric}_by_donor.svg")
    manifest = {
        "purpose": "Descriptive thesis tables/figures from frozen existing GMM results (not independent significance test)",
        "conditions": {"A": A, "B": B}, "gmm_seed": 22911,
        "source_files_sha256": dict(zip(df["slice"].tolist(), df["source_sha256"].tolist())),
        "development_sections": ["151507", "151508"],
        "donors": {"D1": ["151507", "151508", "151509", "151510"],
                   "D2": ["151669", "151670", "151671", "151672"],
                   "D3": ["151673", "151674", "151675", "151676"]},
        "caveats": ["3 biological donors only", "Oracle K=5 for D2, 7 for D1/D3",
                    "source reference labels differ by cohort",
                    "no independent re-evaluation of predictions or alignment in this script",
                    "development sections are not blind test sections"],
    }
    (output / "provenance.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"THESIS_12_EXPORT_COMPLETE {output}", flush=True)


if __name__ == "__main__":
    main()
