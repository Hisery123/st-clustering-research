"""E5b frozen six-patient Wu 2021 Visium input staging and source integrity check.

Input: three verified Zenodo archives; internal *.gz may actually be plain text.
Output (only with --stage): new results/e5b_external_v1/input_stage_<UTC>_<PID>/.
No model fits, no ARI/NMI, no edits to original archives or E5a.
Reference labels are saved in reference_only, separate from model input directory.
Not yet executed on the user's Windows system.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import math
import os
import time
import traceback
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import tarfile

BASE = Path(r"D:\paper\CellCharter_reproduction")
SOURCE = BASE / "third_party" / "e5b_source_preflight_20261121"
RESULTS = BASE / "results" / "e5b_external_v1"
SAMPLES = ("1142243F", "1160920F", "CID4290", "CID4465", "CID44971", "CID4535")
N_MODEL = (4784, 4895, 2426, 1211, 1160, 1125)
N_EVAL = (4665, 4846, 2419, 1207, 1159, 1028)
K_ORACLE = (5, 7, 3, 3, 6, 6)
N_GENES = (28402, 28402, 19237, 19237, 19237, 19237)
SOURCE_MD5 = {
    "metadata.tar.gz": "1d0b34ead70635c094ac74ac58a88d68",
    "spatial.tar.gz": "29b02ae433d459d19dc52b75a529e8e9",
    "filtered_count_matrices.tar.gz": "ea1220f0606c4d4e9307468fb2d5427a",
}
EXCLUDE = {"", "artefact", "na", "uncertain"}

def demand(ok, msg):
    if not ok:
        raise ValueError(msg)

def md5(path):
    h = hashlib.md5()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()

def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()

def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False,
                                     allow_nan=False) + "\n", encoding="utf-8")

def member_text(archive, name):
    src = archive.extractfile(name)
    demand(src is not None, "ARCHIVE_MEMBER_MISSING " + name)
    magic = src.read(2)
    src.seek(0)
    compressed = magic == b"\x1f\x8b"
    stream = gzip.GzipFile(fileobj=src, mode="rb") if compressed else src
    return io.TextIOWrapper(stream, encoding="utf-8-sig", newline=""), (
        "gzip" if compressed else "plain")

def read_csv_member(archive, name):
    stream, _ = member_text(archive, name)
    with stream:
        return list(csv.reader(stream))

def stage_one(sample, expected, meta, spatial, counts, stage):
    n_model, n_eval, oracle_k, n_genes = expected
    meta_name = f"metadata/{sample}_metadata.csv"
    spatial_name = f"spatial/{sample}_spatial/tissue_positions_list.csv"
    prefix = f"filtered_count_matrices/{sample}_filtered_count_matrix/"

    raw_meta = read_csv_member(meta, meta_name)
    demand(len(raw_meta) > 1 and raw_meta[0][0] == "",
           f"METADATA_BAD_INDEX_COLUMN {sample}")
    head = raw_meta[0]
    demand(len(head) == len(set(head)) and
           all(x in head for x in ("patientid", "Classification", "subtype")),
           f"METADATA_BAD_COLUMNS {sample}")
    meta_rows = [dict(zip(head, r)) for r in raw_meta[1:]]
    demand(all(len(r) == len(head) for r in raw_meta[1:]),
           f"METADATA_RAGGED_CSV {sample}")
    metadata_bc = [r[""].strip() for r in meta_rows]
    demand(all(metadata_bc) and len(set(metadata_bc)) == len(metadata_bc),
           f"METADATA_BAD_BARCODES {sample}")

    raw_pos = read_csv_member(spatial, spatial_name)
    demand(raw_pos and raw_pos[0][0].strip().lower() != "barcode",
           f"SPATIAL_HEADER_CHANGED {sample}")
    demand(all(len(r) == 6 for r in raw_pos), f"SPATIAL_BAD_COLUMNS {sample}")
    positions = {}
    for r in raw_pos:
        bc = r[0].strip()
        demand(bc and bc not in positions, f"SPATIAL_DUPLICATE_BC {sample}")
        demand(r[1].strip() in ("0", "1"), f"BAD_IN_TISSUE_FLAG {sample} {bc}")
        demand(all(math.isfinite(float(x)) for x in r[2:]),
               f"SPATIAL_NONFINITE {sample} {bc}")
        positions[bc] = r
    demand(set(metadata_bc) <= set(positions),
           f"METADATA_COORDINATE_MISMATCH {sample}")

    barcode_stream, bc_format = member_text(counts, prefix + "barcodes.tsv.gz")
    with barcode_stream as f:
        bc_rows = [line.rstrip("\r\n") for line in f]
    demand(all(x and "\t" not in x for x in bc_rows) and
           len(bc_rows) == len(set(bc_rows)),
           f"COUNTS_BARCODES_BAD {sample}")
    demand(set(bc_rows) == set(metadata_bc),
           f"COUNTS_METADATA_BARCODE_MISMATCH {sample}")

    input_dir = stage / "inputs" / sample
    input_dir.mkdir(parents=True, exist_ok=False)
    refs_dir = stage / "reference_only"
    refs_dir.mkdir(exist_ok=True)

    feat_stream, feature_format = member_text(counts, prefix + "features.tsv.gz")
    gene_ids = set()
    nfeat = 0
    with feat_stream as src, (input_dir / "features.tsv").open(
        "w", encoding="utf-8", newline=""
    ) as dst:
        for line in src:
            fields = line.rstrip("\r\n").split("\t")
            demand(1 <= len(fields) <= 3 and fields[0].strip(),
                   f"FEATURES_BAD_ROW {sample} {nfeat+1}")
            gene_id = fields[0].strip()
            demand(gene_id not in gene_ids,
                   f"FEATURES_DUPLICATE_GENE_ID {sample} {gene_id}")
            gene_ids.add(gene_id)
            if len(fields) == 1:
                fields.append(gene_id)
            dst.write("\t".join(fields) + "\n")
            nfeat += 1
    demand(nfeat == n_genes, f"FEATURE_COUNT_MISMATCH {sample} {nfeat}")

    matrix_stream, matrix_format = member_text(counts, prefix + "matrix.mtx.gz")
    # Full sparse-file streaming validation; no dense matrix materialization.
    with matrix_stream as src, (input_dir / "matrix.mtx").open(
        "w", encoding="utf-8", newline=""
    ) as dst:
        banner = src.readline()
        demand(banner.lower().startswith("%%matrixmarket matrix coordinate "),
               f"MATRIX_MARKET_BANNER_BAD {sample}")
        dst.write(banner)
        while True:
            line = src.readline()
            demand(line, f"MATRIX_DIMENSIONS_MISSING {sample}")
            if line.startswith("%") or not line.strip():
                dst.write(line)
                continue
            dims = list(map(int, line.split()))
            demand(len(dims) == 3, f"MATRIX_DIMENSIONS_BAD {sample}")
            ng, nc, nnz = dims
            demand(ng == nfeat and nc == len(bc_rows) and nnz > 0,
                   f"MATRIX_SHAPE_MISMATCH {sample} {dims}")
            dst.write(line)
            break
        observed = 0
        for line in src:
            demand(line.strip(), f"MATRIX_EMPTY_DATA_LINE {sample}")
            fields = line.split()
            demand(len(fields) == 3, f"MATRIX_BAD_TRIPLET {sample} {observed}")
            i, j = int(fields[0]), int(fields[1])
            value = float(fields[2])
            demand(1 <= i <= ng and 1 <= j <= nc and
                   math.isfinite(value) and value >= 0 and value.is_integer(),
                   f"MATRIX_BAD_INDEX_OR_COUNT {sample} {observed}")
            observed += 1
            dst.write(line)
        demand(observed == nnz,
               f"MATRIX_NNZ_MISMATCH {sample} observed={observed} declared={nnz}")

    with (input_dir / "barcodes.tsv").open("w", encoding="utf-8") as f:
        for bc in bc_rows:
            f.write(bc + "\n")

    by_barcode = dict(zip(metadata_bc, meta_rows))
    spot_fields = ("barcode", "array_row", "array_col",
                   "pxl_row_in_fullres", "pxl_col_in_fullres")
    model_spots = []
    label_rows = []
    counts_per_label = Counter()
    patient_ids = {r["patientid"].strip() for r in meta_rows}
    demand(len(patient_ids) == 1 and next(iter(patient_ids)),
           f"PATIENT_ID_INVALID {sample}")
    for bc in bc_rows:
        pos = positions[bc]
        if pos[1].strip() != "1":
            continue
        cls = str(by_barcode[bc]["Classification"] or "").strip()
        can_evaluate = cls.casefold() not in EXCLUDE
        model_spots.append({
            "barcode": bc, "array_row": pos[2].strip(), "array_col": pos[3].strip(),
            "pxl_row_in_fullres": pos[4].strip(),
            "pxl_col_in_fullres": pos[5].strip(),
        })
        label_rows.append({"barcode": bc, "Classification": cls,
                           "can_evaluate": "1" if can_evaluate else "0"})
        if can_evaluate:
            counts_per_label[cls] += 1
    demand(len(model_spots) == n_model and
           sum(int(r["can_evaluate"]) for r in label_rows) == n_eval and
           len(counts_per_label) == oracle_k,
           f"FROZEN_MASK_MISMATCH {sample}")

    with (input_dir / "model_spots.csv").open(
        "w", encoding="utf-8", newline=""
    ) as f:
        writer = csv.DictWriter(f, fieldnames=spot_fields)
        writer.writeheader()
        writer.writerows(model_spots)
    with (refs_dir / f"{sample}_reference_labels.csv").open(
        "w", encoding="utf-8", newline=""
    ) as f:
        writer = csv.DictWriter(f, fieldnames=("barcode", "Classification", "can_evaluate"))
        writer.writeheader()
        writer.writerows(label_rows)

    # Spot count filtering and metric selection are not performed here.
    return {
        "sample": sample, "matrix_shape_gene_spot": [ng, nc], "nnz": nnz,
        "barcode_count": len(bc_rows), "model_spots": len(model_spots),
        "eval_spots": n_eval, "reference_category_count_oracle_only": oracle_k,
        "label_counts_reference_only": dict(sorted(counts_per_label.items())),
        "inner_member_format": {"barcodes": bc_format,
                                "features": feature_format, "matrix": matrix_format},
        "input_files_sha256": {
            filename: sha256(input_dir / filename)
            for filename in ("matrix.mtx", "features.tsv",
                             "barcodes.tsv", "model_spots.csv")
        },
        "reference_labels_sha256": sha256(
            refs_dir / f"{sample}_reference_labels.csv"),
    }, next(iter(patient_ids))

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stage", action="store_true",
                   help="Explicitly create a separate new input_stage directory.")
    args = p.parse_args()
    demand(args.stage, "NO_ACTION: rerun with --stage for new input staging")
    for archive, expected in SOURCE_MD5.items():
        file = SOURCE / archive
        demand(file.is_file(), f"SOURCE_ARCHIVE_MISSING {file}")
        actual = md5(file)
        demand(actual == expected,
               f"SOURCE_MD5_MISMATCH {archive} {actual}")
    print("E5B_STAGE_SOURCE_INTEGRITY_PASS archives=3", flush=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stage = RESULTS / f"input_stage_{stamp}_{os.getpid()}"
    demand(not stage.exists(), f"STAGE_OUTPUT_EXISTS {stage}")
    stage.mkdir(parents=True, exist_ok=False)
    status_path = stage / "batch_status.json"
    summary = {
        "status": "running", "purpose": "e5b_source_staging_only",
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "archives_md5": dict(SOURCE_MD5), "samples": [],
        "no_training": True, "no_metric_computation": True,
    }
    write_json(status_path, summary)
    try:
        ids = set()
        with tarfile.open(SOURCE / "metadata.tar.gz", "r:gz") as mt, \
             tarfile.open(SOURCE / "spatial.tar.gz", "r:gz") as sp, \
             tarfile.open(SOURCE / "filtered_count_matrices.tar.gz", "r:gz") as ct:
            for sample, expected in zip(
                SAMPLES, zip(N_MODEL, N_EVAL, K_ORACLE, N_GENES)
            ):
                info, pid = stage_one(sample, expected, mt, sp, ct, stage)
                demand(pid not in ids, f"PATIENT_ID_SHARED {sample}")
                ids.add(pid)
                summary["samples"].append(info)
                write_json(status_path, summary)
                print(f"E5B_STAGE_SAMPLE_PASS sample={sample} "
                      f"model={info['model_spots']} eval={info['eval_spots']} "
                      f"genes={info['matrix_shape_gene_spot'][0]}", flush=True)
        demand(len(summary["samples"]) == 6 and len(ids) == 6,
               "STAGE_SIX_SAMPLES_NOT_COMPLETED")
        summary.update({
            "status": "completed",
            "finished_utc": datetime.now(timezone.utc).isoformat(),
            "total_model_spots": sum(x["model_spots"] for x in summary["samples"]),
            "total_eval_spots": sum(x["eval_spots"] for x in summary["samples"]),
        })
        write_json(status_path, summary)
        print(f"E5B_STAGE_FINAL status=completed samples=6 "
              f"model=15601 eval=15324 result={status_path}", flush=True)
        print("NO_TRAINING_NO_ARI_NMI", flush=True)
    except BaseException as exc:
        summary.update({"status": "failed", "error": repr(exc),
                        "traceback": traceback.format_exc(),
                        "finished_utc": datetime.now(timezone.utc).isoformat()})
        write_json(status_path, summary)
        print(f"E5B_STAGE_FAILED error={exc!r} result={status_path}", flush=True)
        raise

if __name__ == "__main__":
    main()
