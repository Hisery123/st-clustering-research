"""Validate and optionally convert ten additional DLPFC sections.

Read-only by default; --write writes two new CSV files per section, refusing any
overwrite. Source metadata labels are `layer_guess` and `layer_guess_reordered`;
the original `Layer` column is all missing. The generated annotations are
metadata-derived reference labels, not newly adjudicated manual ground truth.
No model training, K optimization, or historical 151507/151508 changes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import scanpy as sc

ROOT = Path(r"D:\paper\ST_Benchmark_Planning\mvp\data")
IDS = ("151509", "151510", "151669", "151670", "151671",
       "151672", "151673", "151674", "151675", "151676")
LABEL_MAP = {
    "Layer1": "Layer 1", "Layer2": "Layer 2", "Layer3": "Layer 3",
    "Layer4": "Layer 4", "Layer5": "Layer 5", "Layer6": "Layer 6",
    "WM": "WM"
}
POSITION_COLUMNS = ["barcode", "in_tissue", "array_row", "array_col",
                    "pxl_row_in_fullres", "pxl_col_in_fullres"]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as stream:
        for b in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def validate_one(sid: str):
    folder = ROOT / sid
    h5 = folder / "filtered_feature_bc_matrix.h5"
    meta_file = folder / "metadata_source.tsv"
    position_file = folder / "tissue_positions_source.csv"
    for file in (h5, meta_file, position_file):
        if not file.is_file():
            raise FileNotFoundError(file)

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Variable names are not unique")
        x = sc.read_10x_h5(str(h5))
    barcodes = pd.Index(x.obs_names.astype(str), name="barcode")
    if not barcodes.is_unique:
        raise ValueError("Nonunique expression barcode")

    pos_raw = pd.read_csv(position_file, header=None, names=POSITION_COLUMNS,
                          dtype={"barcode": str})
    meta_raw = pd.read_csv(meta_file, sep="\t", dtype={"barcode": str})
    if not pos_raw["barcode"].is_unique or not meta_raw["barcode"].is_unique:
        raise ValueError("Nonunique source barcodes")
    if not barcodes.isin(pos_raw["barcode"]).all() or not barcodes.isin(meta_raw["barcode"]).all():
        raise ValueError("Missing barcode in position or metadata")
    if len(meta_raw) != len(barcodes):
        raise ValueError("Metadata row count differs from H5 spot count")
    if not {"sample_name", "layer_guess", "layer_guess_reordered"}.issubset(meta_raw.columns):
        raise ValueError("Required metadata columns missing")

    meta = meta_raw.set_index("barcode").reindex(barcodes)
    pos = pos_raw.set_index("barcode").reindex(barcodes)
    if not meta["sample_name"].astype(str).eq(sid).all():
        raise ValueError("Metadata sample_name mismatch")
    if not pos["in_tissue"].eq(1).all():
        raise ValueError("Expression matrix has non-tissue positions")
    if pos[["array_row", "array_col"]].isna().any().any():
        raise ValueError("Missing grid coordinates")
    if pos[["array_row", "array_col"]].duplicated().any():
        raise ValueError("Duplicated grid positions")
    for name in ("array_row", "array_col", "in_tissue"):
        values = pd.to_numeric(pos[name], errors="raise")
        if not np.isfinite(values).all() or not (values == values.astype(int)).all():
            raise ValueError(f"Invalid integer-valued {name}")

    guess = meta["layer_guess"]
    reordered = meta["layer_guess_reordered"]
    if not guess.fillna("<missing>").equals(reordered.fillna("<missing>")):
        raise ValueError("layer_guess and reordered version disagree")
    unknown = set(guess.dropna().astype(str).unique()) - set(LABEL_MAP)
    if unknown:
        raise ValueError(f"Unknown labels: {sorted(unknown)}")

    # Important: retain full H5 spot order in the position table.
    aligned = pos.reset_index()[POSITION_COLUMNS].copy()
    for col in ("in_tissue", "array_row", "array_col"):
        aligned[col] = aligned[col].astype(int)
    annotated = guess.dropna()
    annotations = pd.DataFrame({
        "sample_name": sid,
        "spot_name": annotated.index.astype(str),
        "layer": annotated.map(LABEL_MAP).to_numpy()
    })
    if annotations["layer"].isna().any() or annotations["spot_name"].duplicated().any():
        raise ValueError("Invalid normalized labels")
    distribution = annotations["layer"].value_counts().to_dict()
    expected_k = 5 if sid in ("151669","151670","151671","151672") else 7
    if len(distribution) != expected_k:
        raise ValueError(f"Unexpected reference category count {len(distribution)} vs {expected_k}")
    evidence = {
        "sample": sid, "spots": int(x.n_obs),
        "annotations": int(len(annotations)), "unannotated": int(x.n_obs-len(annotations)),
        "label_counts": distribution, "oracle_k_from_reference_count": len(distribution),
        "reference_label_origin": "SEDR_analyses/data/DLPFC metadata_source.tsv:layer_guess",
        "source_sha256": {p.name: sha256_file(p) for p in (h5, meta_file, position_file)}
    }
    return folder, aligned, annotations, evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write normalized CSV and evidence per section")
    args = parser.parse_args()
    finished = []
    for sid in IDS:
        folder, aligned, annotations, evidence = validate_one(sid)
        outputs = (folder / "spots_aligned.csv", folder / "manual_layer_annotations.csv",
                   folder / "source_conversion_manifest.json")
        if args.write:
            if any(x.exists() for x in outputs):
                raise FileExistsError(f"Refusing overwrite: {sid} output already exists")
            aligned.to_csv(outputs[0], index=False)
            annotations.to_csv(outputs[1], index=False)
            outputs[2].write_text(json.dumps(evidence, ensure_ascii=False, indent=2),
                                  encoding="utf-8")
        print("VALIDATED", sid, "spots", evidence["spots"], "annotated",
              evidence["annotations"], "k", evidence["oracle_k_from_reference_count"],
              "unannotated", evidence["unannotated"], "labels", evidence["label_counts"],
              flush=True)
        finished.append(sid)
    print("DLPFC_10_SOURCE_CONVERSION_" + ("WRITTEN" if args.write else "CHECK_ONLY") +
          f"_COMPLETE {len(finished)}/10", flush=True)


if __name__ == "__main__":
    main()
