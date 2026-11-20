"""E4: one-shot, all-12-slice true-data spatial/marker plotting (SVG+CSV).

Inputs are frozen existing A/B seed22911 predictions, spots/labels, and original
10x filtered_feature_bc_matrix.h5. No model training, no cluster relabeling,
no manual label driven choice of model. The command without --run only shows
the fixed task list. --run makes a NEW timestamped session and runs ALL 12.
Output inputs are never modified; results remain separate from E1/E2/E3c/E3d.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import traceback
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np
import pandas as pd
from scipy import sparse
import h5py

from e4_spatial_visualization_v1 import resolve_pred_paths, preflight_one

BASE = Path(r"D:\paper\CellCharter_reproduction")
DATA_ROOT = Path(r"D:\paper\ST_Benchmark_Planning\mvp\data")
OUT_ROOT = BASE / "results" / "e4_spatial_visualization_v1"
SAMPLES = ("151507","151508","151509","151510","151669","151670",
           "151671","151672","151673","151674","151675","151676")
MARKERS = ("MOBP", "PCP4", "SNAP25")
# Fixed from PRE-EXISTING E1/E2 seed-mean ΔARI summary:
# D1 highest Δ, D2 closest-to-zero Δ, D3 lowest Δ. Illustrative, not test set.
REPRESENTATIVE = ("151507", "151671", "151675")
REPRESENTATIVE_REASON = {
    "151507": "D1 maximum reported B-A delta_ARI, +0.049888880058",
    "151671": "D2 delta_ARI closest to zero, -0.003548500474",
    "151675": "D3 minimum reported B-A delta_ARI, -0.063314250971",
}
EXPECTED_COUNTS = {"151507":4226,"151508":4384,"151509":4789,
                   "151510":4634,"151669":3661,"151670":3498,
                   "151671":4110,"151672":4015,"151673":3639,
                   "151674":3673,"151675":3592,"151676":3460}
COLORS = list(plt.get_cmap("tab10").colors)
plt.rcParams.update({"svg.fonttype":"none", "font.size":9, "savefig.transparent":False})


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for part in iter(lambda: stream.read(1024*1024), b""):
            h.update(part)
    return h.hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")


def need(test, msg):
    if not test:
        raise ValueError(msg)


def decode(b):
    return b.decode("utf-8") if isinstance(b, (bytes, np.bytes_)) else str(b)


def read_expression(h5path, spot_barcodes):
    """10x v3 CSC genes x barcodes; match every spot by barcode, NOT row index."""
    with h5py.File(h5path, "r") as f:
        group = f["matrix"]
        need(all(k in group for k in ("data","indices","indptr","shape","barcodes","features")),
             "10X_MATRIX_REQUIRED_DATASET_MISSING")
        shape = tuple(int(x) for x in group["shape"][()])
        barcode_names = [decode(x) for x in group["barcodes"][()]]
        feats = group["features"]
        need("name" in feats, "GENE_NAME_FIELD_MISSING")
        gene_names = [decode(x) for x in feats["name"][()]]
        need(len(barcode_names) == shape[1] and len(gene_names) == shape[0],
             "10X_DIMENSION_NAMES_MISMATCH")
        need(len(set(barcode_names)) == len(barcode_names), "DUPLICATE_10X_BARCODES")
        mat = sparse.csc_matrix(
            (group["data"][()], group["indices"][()], group["indptr"][()]),
            shape=shape
        )
    col_idx = pd.Index(barcode_names).get_indexer(spot_barcodes)
    need(np.all(col_idx >= 0), f"MISSING_SPOT_IN_10X_H5 {int((col_idx < 0).sum())}")
    need(np.all(np.diff(mat.indptr) >= 0), "BAD_10X_INDPTR")
    totals = np.asarray(mat[:, col_idx].sum(axis=0)).ravel().astype(np.float64)
    need(np.isfinite(totals).all() and np.all(totals >= 0), "BAD_LIBRARY_SIZES")
    expression = {}
    gene_index = pd.Index(gene_names)
    for symbol in MARKERS:
        matching = np.flatnonzero(gene_index == symbol)
        need(len(matching) > 0, "MISSING_MARKER_" + symbol)
        raw = np.asarray(mat[matching, :][:, col_idx].sum(axis=0)).ravel().astype(np.float64)
        need(np.isfinite(raw).all() and (raw >= 0).all(), "BAD_RAW_COUNTS_"+symbol)
        normal = np.log1p(10000.0 * raw / np.maximum(totals, 1.0))
        expression[symbol] = (raw, normal, len(matching))
    return expression, shape[1], totals


def read_spatial(sid):
    directory = DATA_ROOT / sid
    spotsfile = directory / "spots_aligned.csv"
    labelsfile = directory / "manual_layer_annotations.csv"
    h5file = directory / "filtered_feature_bc_matrix.h5"
    afile, bfile = resolve_pred_paths(sid)
    spots = pd.read_csv(spotsfile, dtype={"barcode":str})
    annotations = pd.read_csv(labelsfile,
                              dtype={"sample_name":str,"spot_name":str,"layer":str})
    annotations = annotations.loc[
        annotations["sample_name"] == sid, ["spot_name","layer"]
    ].rename(columns={"spot_name":"barcode"})
    a = pd.read_csv(afile, dtype={"barcode":str}).rename(columns={"cluster":"A"})
    b = pd.read_csv(bfile, dtype={"barcode":str}).rename(columns={"cluster":"B"})
    need(spots["barcode"].is_unique and a["barcode"].is_unique
         and b["barcode"].is_unique and annotations["barcode"].is_unique,
         "DUPLICATE_BARCODES")
    need(len(spots) == EXPECTED_COUNTS[sid], "EXPECTED_SPOT_COUNT_CHANGED")
    need(set(spots["barcode"]) == set(a["barcode"]) == set(b["barcode"]),
         "A_B_BARCODE_SETS_DIFFER")
    need(annotations["barcode"].isin(spots["barcode"]).all(), "LABEL_OUTSIDE_SPOTS")
    data = spots[["barcode","pxl_col_in_fullres","pxl_row_in_fullres"]].merge(
        a[["barcode","A"]], on="barcode", how="left", validate="one_to_one"
    ).merge(
        b[["barcode","B"]], on="barcode", how="left", validate="one_to_one"
    ).merge(annotations, on="barcode", how="left", validate="one_to_one")
    need(data["A"].notna().all() and data["B"].notna().all(), "PREDICTION_MISSING")
    xy = data[["pxl_col_in_fullres","pxl_row_in_fullres"]].to_numpy(dtype=float)
    need(np.isfinite(xy).all(), "NONFINITE_SPOT_COORDINATES")
    for kind in ("A","B"):
        numeric = pd.to_numeric(data[kind], errors="raise").to_numpy()
        need(np.isfinite(numeric).all() and np.all(numeric == np.floor(numeric)),
             kind + "_PREDICTION_IDS_INVALID")
        data[kind] = numeric.astype(int)
    expression, n_barcode_h5, totals = read_expression(h5file,
                                                       data["barcode"].tolist())
    inputs = {
        "spots": spotsfile, "labels": labelsfile,
        "h5": h5file, "A_predictions": afile, "B_predictions": bfile
    }
    return data, xy, expression, n_barcode_h5, totals, inputs


def configure(ax, xy, title):
    x, y = xy[:,0], xy[:,1]
    dx = max(1.0, float(x.max()-x.min())) * 0.04
    dy = max(1.0, float(y.max()-y.min())) * 0.04
    ax.set_xlim(x.min()-dx, x.max()+dx)
    ax.set_ylim(y.max()+dy, y.min()-dy)  # image row grows downward
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(title, fontsize=10)


def draw_classes(ax, xy, raw_labels, title, colored_reference=False):
    values = np.asarray(raw_labels, dtype=object)
    mask = pd.notna(values)
    ax.scatter(xy[~mask,0], xy[~mask,1], s=3.5, c="#c8c8c8",
               marker="s", linewidths=0, label="unlabeled")
    if colored_reference:
        ordered = sorted(set(str(x) for x in values[mask]))
        colormap = plt.get_cmap("tab20")
        for i, value in enumerate(ordered):
            found = np.asarray([str(t)==value if pd.notna(t) else False for t in values])
            ax.scatter(xy[found,0], xy[found,1], s=3.5,
                       color=colormap(i % 20), marker="s", linewidths=0, label=value)
    else:
        ordered = sorted(set(int(x) for x in values[mask]))
        for value in ordered:
            found = np.asarray([int(t)==value if pd.notna(t) else False for t in values])
            ax.scatter(xy[found,0], xy[found,1], s=3.5,
                       color=COLORS[value % len(COLORS)], marker="s",
                       linewidths=0, label=f"cluster {value}")
    configure(ax, xy, title)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5,-0.03),
              ncol=min(4,max(1,len(ordered))), fontsize=6, frameon=False,
              markerscale=2.4, handletextpad=0.25, columnspacing=0.6)


def save_spatial(data, xy, out, sid):
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.1))
    draw_classes(axes[0], xy, data["layer"].to_numpy(),
                 "Reference layers (post hoc)", colored_reference=True)
    draw_classes(axes[1], xy, data["A"].to_numpy(),
                 "A: L0+L1+L2, Oracle-K")
    draw_classes(axes[2], xy, data["B"].to_numpy(),
                 "B: L0+L1+L4, Oracle-K")
    fig.suptitle(f"DLPFC {sid} | original cluster IDs: colors NOT aligned to layers",
                 fontsize=12)
    fig.text(0.5, 0.012, "Spot positions: full-resolution image pixels, Y-axis downward. "
             "Unlabeled spots gray. No label-informed relabeling.",
             ha="center", fontsize=8)
    fig.subplots_adjust(top=0.84, bottom=0.16, left=0.03, right=0.97, wspace=0.12)
    file = out / f"{sid}_reference_A_B_spatial.svg"
    fig.savefig(file, format="svg")
    plt.close(fig)
    return file


def save_marker_panels(data, xy, expression, out, sid):
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.8))
    result = pd.DataFrame({"barcode": data["barcode"]})
    for ax, gene in zip(axes, MARKERS):
        raw, normal, matched = expression[gene]
        result[gene+"_raw_counts"] = raw
        result[gene+"_log1p_CP10K"] = normal
        plot = ax.scatter(xy[:,0], xy[:,1], s=4.0, c=normal, cmap="viridis",
                          vmin=0.0, vmax=6.0, marker="s", linewidths=0)
        configure(ax, xy, gene + " | log1p(counts per 10k)")
        cb = fig.colorbar(plot, ax=ax, fraction=0.028, pad=0.015, shrink=0.68)
        cb.ax.tick_params(labelsize=7)
    fig.suptitle(f"DLPFC {sid} | actual 10x gene counts, fixed color scale [0,6]",
                 fontsize=12)
    fig.text(0.5, 0.015, "log1p(10,000 × marker raw count / total spot UMI). "
             "Values above 6 are clipped for display; CSV contains un-clipped values.",
             ha="center", fontsize=8)
    fig.subplots_adjust(top=0.84, bottom=0.09, left=0.03, right=0.96, wspace=0.15)
    svgfile = out / f"{sid}_MOBP_PCP4_SNAP25_expression.svg"
    csvfile = out / f"{sid}_marker_expression_raw_and_log1p10k.csv"
    fig.savefig(svgfile, format="svg")
    plt.close(fig)
    result.to_csv(csvfile, index=False, float_format="%.9g")
    return svgfile, csvfile


def save_confusions(data, out, sid):
    labeled = data.loc[data["layer"].notna(), ["layer","A","B"]].copy()
    categories = sorted(labeled["layer"].unique())
    files = []
    tables = []
    for key in ("A","B"):
        matrix = pd.crosstab(labeled["layer"], labeled[key]).reindex(
            index=categories, columns=sorted(data[key].unique()), fill_value=0)
        need(int(matrix.to_numpy().sum()) == len(labeled), "CONFUSION_SUM_MISMATCH")
        path = out / f"{sid}_reference_vs_{key}_confusion_counts.csv"
        matrix.to_csv(path, index_label="reference_layer")
        files.append(path)
        tables.append(matrix)
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 5.2))
    for ax, table, key in zip(axes, tables, ("A","B")):
        grid = table.to_numpy(dtype=int)
        img = ax.imshow(grid, cmap="Blues", aspect="auto", vmin=0)
        ax.set_xticks(range(table.shape[1]), [str(x) for x in table.columns])
        ax.set_yticks(range(table.shape[0]), [str(x) for x in table.index])
        ax.set_xlabel("Original predicted cluster ID")
        ax.set_ylabel("Reference layer")
        ax.set_title("A: L0+L1+L2" if key=="A" else "B: L0+L1+L4")
        for r in range(grid.shape[0]):
            for c in range(grid.shape[1]):
                color = "white" if grid[r,c] > grid.max() * 0.58 else "#202020"
                ax.text(c,r,str(grid[r,c]),ha="center",va="center",
                        fontsize=7,color=color)
        fig.colorbar(img, ax=ax, fraction=0.04, pad=0.03)
    fig.suptitle(f"DLPFC {sid} | labeled spots n={len(labeled)} (counts, not normalized)")
    fig.subplots_adjust(top=0.83, bottom=0.14, wspace=0.35)
    svg = out / f"{sid}_reference_A_B_confusion.svg"
    fig.savefig(svg, format="svg")
    plt.close(fig)
    files.append(svg)
    return files


def run():
    need(len(set(SAMPLES)) == 12, "SAMPLE_MATRIX_MISMATCH")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + str(os.getpid())
    session = OUT_ROOT / ("batch_" + stamp)
    need(not session.exists(), "SESSION_ALREADY_EXISTS")
    session.mkdir(parents=True, exist_ok=False)
    log = {
        "protocol":"E4_SPATIAL_MARKER_REAL_DATA_BATCH_V1",
        "started_utc":now(), "status":"running", "samples":{},
        "reference_label_use":"posthoc_visualization_and_confusion_only",
        "A":"cum_L0_L1_L2_seed22911_OracleK",
        "B":"fixed_L0_L1_L4_seed22911_OracleK",
        "coordinate_system":"pxl_col / pxl_row full-resolution pixels; y inverted",
        "gene_normalization":"log1p(10000*raw_gene_UMI / spot_total_UMI)",
        "gene_color_scale":"vmin=0, vmax=6, values above 6 visually clipped",
        "planned_markers":MARKERS,
        "representative_main_text":REPRESENTATIVE,
        "representative_selection":REPRESENTATIVE_REASON,
        "all_12_saved_for_appendix":True,
        "note":"12 slices nested in 3 donors. Original predicted IDs untouched.",
    }
    write_json(session / "e4_batch_status.json", log)
    errors = []
    for i, sid in enumerate(SAMPLES, 1):
        out = session / sid
        out.mkdir(parents=False, exist_ok=False)
        print(f"E4_BATCH_START {i}/12 sample={sid}", flush=True)
        try:
            pre = preflight_one(sid)  # existing user-verified path/marker preflight
            data, xy, markers, barcode_h5, totals, inputs = read_spatial(sid)
            need(len(data)==pre["spots"] and data["layer"].notna().sum()==pre["labeled"],
                 "PREFLIGHT_COUNT_CHANGED")
            generated = []
            generated.append(save_spatial(data,xy,out,sid))
            generated.extend(save_marker_panels(data,xy,markers,out,sid))
            generated.extend(save_confusions(data,out,sid))
            record = {
                "status":"completed", "sample":sid,
                "spots":len(data), "labeled":int(data["layer"].notna().sum()),
                "unlabeled":int(data["layer"].isna().sum()),
                "A_k":int(data["A"].nunique()), "B_k":int(data["B"].nunique()),
                "10x_h5_total_barcodes":barcode_h5,
                "spots_zero_total_UMI":int((totals==0).sum()),
                "markers":{gene:{"feature_rows":markers[gene][2],
                       "spots_with_nonzero":int((markers[gene][0]>0).sum())}
                        for gene in MARKERS},
                "input_sha256":{name:sha256(path) for name,path in inputs.items()},
                "input_files":{name:str(path) for name,path in inputs.items()},
                "output_sha256":{file.name:sha256(file) for file in generated},
                "output_files":[str(file) for file in generated],
            }
            write_json(out/"e4_sample_manifest.json", record)
            log["samples"][sid] = record
            print(f"E4_BATCH_PASS {i}/12 sample={sid} svg=3 csv=3 "
                  f"spots={len(data)} labeled={record['labeled']}", flush=True)
        except Exception as error:
            err = {"status":"failed", "sample":sid, "error":repr(error),
                   "traceback":traceback.format_exc()}
            errors.append(sid)
            log["samples"][sid] = err
            write_json(out/"e4_sample_failure.json", err)
            print(f"E4_BATCH_FAILED {i}/12 sample={sid} error={error!r}", flush=True)
        write_json(session / "e4_batch_status.json", log)
    successes = sum(r["status"]=="completed" for r in log["samples"].values())
    log["finished_utc"] = now()
    log["status"] = "completed" if successes==12 and not errors else "partial"
    log["pass_count"] = successes
    log["failure_samples"] = errors
    write_json(session / "e4_batch_status.json", log)
    print(f"E4_BATCH_FINAL status={log['status']} passed={successes}/12 "
          f"failed={len(errors)} session={session}", flush=True)
    return 0 if log["status"]=="completed" else 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run",action="store_true",help="render all 12, never train")
    args = parser.parse_args()
    if not args.run:
        print("E4_BATCH_DRY_RUN sample_count=12 markers=MOBP,PCP4,SNAP25 "
              "svgs_per_sample=3 csvs_per_sample=3 NO_FILES_WRITTEN")
        raise SystemExit(0)
    try:
        raise SystemExit(run())
    except Exception as exc:
        print(f"E4_BATCH_FATAL {exc!r}", flush=True)
        raise SystemExit(1)
