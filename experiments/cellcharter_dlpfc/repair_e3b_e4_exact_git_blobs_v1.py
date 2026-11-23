#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One-time E3B+E4 original data SHA256/Git-blob repair after Git core.autocrlf.
Inputs: 2026-11-22 original E3B export ZIP and 2026-11-20 original E4 Windows outputs.
Creates a FRESH isolated Git clone. NEVER modifies input ZIP, source model predictions,
research CSVs, spatial images, labels, or training settings. No force-push.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import zipfile

REPO = "https://github.com/Hisery123/st-clustering-research.git"
E3B_ROOT = "experiments/cellcharter_dlpfc/E3B_E1E2_1200_PREDICTIONS_20261122"
E4_ROOT = "experiments/cellcharter_dlpfc/E4_SOURCE_FIGURES_20261122_RELEASE"
E3B_ZIP_SHA = "cfad75dbc35723c72e52f8906b07e1b81048ff70fcf04df709d41ae42bc1302b"
SAMPLES = ("151507","151508","151509","151510","151669","151670",
           "151671","151672","151673","151674","151675","151676")


def need(ok, msg):
    if not ok:
        raise RuntimeError(msg)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def git_blob_hash(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") +
                        b"\x00" + data).hexdigest()


def gitrun(*args, cwd=None, proxy="", stdin=None):
    cmd = ["git"]
    if proxy:
        cmd += ["-c", "http.proxy=" + proxy]
    if cwd:
        cmd += ["-C", str(cwd)]
    cmd += [str(a) for a in args]
    result = subprocess.run(
        cmd, input=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        check=False)
    if result.returncode:
        raise RuntimeError(
            "GIT_COMMAND_FAILED rc=%s args=%s\nstdout=%s\nstderr=%s" %
            (result.returncode, " ".join(cmd[:7]),
             result.stdout[-1000:].decode("utf-8", "replace"),
             result.stderr[-2600:].decode("utf-8", "replace")))
    return result.stdout.decode("utf-8", "replace").strip()


def read_csv_bytes(data):
    return list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"), newline="")))


def load_source_manifest(path, expect):
    records = read_csv_bytes(path.read_bytes())
    need(len(records) == expect, "MANIFEST_ROWCOUNT_WRONG " + str(path))
    result = {}
    for row in records:
        relative = row["RelativePath"].replace("\\", "/")
        need(relative not in result, "DUPLICATE_RELATIVE_PATH " + relative)
        expected = row["SHA256"].lower()
        need(len(expected) == 64 and all(c in "0123456789abcdef" for c in expected),
             "INVALID_SHA256_IN_MANIFEST " + relative)
        result[relative] = (expected, row)
    return result


def check_attributes(checkout, root):
    candidate = (root + "/figures/151507/151507_reference_A_B_spatial.svg"
                 if root == E4_ROOT
                 else root + "/predictions/151507/cum_L0/seed_22911/predictions.csv")
    response = gitrun("check-attr", "text", "--", candidate, cwd=checkout)
    need(response.endswith("text: unset"),
         "GITATTRIBUTES_NOT_LOCKED_FOR_EXACT_BYTES " + response)


def old_tree_blobs(checkout):
    output = gitrun("ls-tree", "-r", "HEAD", "--", E3B_ROOT, E4_ROOT, cwd=checkout)
    found = {}
    for line in output.splitlines():
        header, path = line.split("\t", 1)
        mode, kind, sha = header.split()
        if kind == "blob":
            found[path] = sha
    return found


def prepare_e3b(base, checkout, manifest, old, zipfile_path):
    need(sha256(zipfile_path.read_bytes()) == E3B_ZIP_SHA,
         "E3B_ORIGINAL_ZIP_SHA256_MISMATCH")
    items = []
    with zipfile.ZipFile(zipfile_path, "r") as z:
        entries = {name.replace("\\", "/"): name for name in z.namelist()
                   if not name.endswith("/")}
        need(len(entries) == 1202 and "SOURCE_SHA256.csv" in entries and
             "LEDGER_SHA256.txt" in entries,
             "E3B_ORIGINAL_ZIP_ENTRY_COUNT_WRONG")
        inside = read_csv_bytes(z.read(entries["SOURCE_SHA256.csv"]))
        need(len(inside) == 1200, "E3B_ZIP_MANIFEST_NOT_1200")
        for row in inside:
            rel = row["RelativePath"].replace("\\", "/")
            need(rel in manifest, "E3B_ZIP_MANIFEST_EXTRA " + rel)
            need(row["SHA256"].lower() == manifest[rel][0],
                 "E3B_ZIP_AND_GITHUB_MANIFEST_DISAGREE " + rel)
        for i, (rel, (expected_sha, _)) in enumerate(manifest.items(), 1):
            need(rel.startswith("predictions/") and
                 rel.endswith("/predictions.csv") and
                 rel.count("/") == 4,
                 "E3B_RELATIVE_PATH_UNEXPECTED " + rel)
            need(rel in entries, "E3B_SOURCE_PREDICTION_NOT_IN_ZIP " + rel)
            data = z.read(entries[rel])
            need(sha256(data) == expected_sha,
                 "E3B_ORIGINAL_SOURCE_SHA256_MISMATCH " + rel)
            gitpath = E3B_ROOT + "/" + rel
            need(gitpath in old, "E3B_REMOTE_ORIGINAL_PATH_MISSING " + gitpath)
            oid = git_blob_hash(data)
            stored = gitrun("hash-object", "-w", "--stdin", cwd=checkout, stdin=data)
            need(stored == oid, "E3B_GIT_RAW_OBJECT_ERROR " + rel)
            items.append({"root":"E3B","path":gitpath,"original_sha256":expected_sha,
                          "previous_git_blob":old[gitpath],"exact_git_blob":oid,
                          "changed_in_git":str(old[gitpath] != oid).lower()})
            if i % 200 == 0:
                print("E3B_RAW_BLOB_VERIFIED", i, "/1200", flush=True)
    need(len(items) == 1200, "E3B_COUNT_NOT_1200")
    print("E3B_ORIGINAL_BYTES_PASS sources=1200 zip_sha256=" + E3B_ZIP_SHA, flush=True)
    return items


def prepare_e4(base, checkout, manifest, old):
    items = []
    baseprefix = (base / "results" / "e4_spatial_visualization_v1").resolve()
    for rel, (expected_sha, row) in manifest.items():
        parts = rel.split("/")
        if len(parts) == 3:
            need(parts[0] == "figures" and parts[1] in SAMPLES and
                 parts[2].endswith((".csv",".svg",".json")),
                 "E4_UNEXPECTED_SOURCE_PATH " + rel)
        else:
            need(rel in ("e4_batch_status.json", "e4_phase_audit_report.json"),
                 "E4_UNEXPECTED_TOPLEVEL_SOURCE_PATH " + rel)
        src = Path(row["OriginalPath"])
        need(src.is_file(), "E4_WINDOWS_ORIGINAL_MISSING " + str(src))
        need(baseprefix == src.resolve() or baseprefix in src.resolve().parents,
             "E4_ORIGINAL_OUTSIDE_EXPECTED_WINDOWS_BATCH " + str(src))
        data = src.read_bytes()
        need(sha256(data) == expected_sha,
             "E4_WINDOWS_ORIGINAL_SHA256_MISMATCH " + rel)
        gitpath = E4_ROOT + "/" + rel
        need(gitpath in old, "E4_REMOTE_ORIGINAL_PATH_MISSING " + gitpath)
        oid = git_blob_hash(data)
        stored = gitrun("hash-object", "-w", "--stdin", cwd=checkout, stdin=data)
        need(stored == oid, "E4_GIT_RAW_OBJECT_ERROR " + rel)
        items.append({"root":"E4","path":gitpath,"original_sha256":expected_sha,
                      "previous_git_blob":old[gitpath],"exact_git_blob":oid,
                      "changed_in_git":str(old[gitpath] != oid).lower()})
    need(len(items) == 86, "E4_SOURCE_COUNT_NOT_86")
    print("E4_ORIGINAL_BYTES_PASS sources=86", flush=True)
    return items


def write_audit(checkout, root, entries):
    path = checkout / root / "EXACT_SOURCE_BLOB_REPAIR_AUDIT_20261123.csv"
    need(not path.exists(), "REPAIR_AUDIT_ALREADY_EXISTS " + str(path))
    fields = ("root","path","original_sha256","previous_git_blob",
              "exact_git_blob","changed_in_git")
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(entries)
    gitrun("add", "--", root + "/" + path.name, cwd=checkout)
    return path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", default=r"D:\paper\CellCharter_reproduction")
    ap.add_argument("--proxy", default="")
    args = ap.parse_args()
    base = Path(args.base)
    original_zip = base / "results" / "e3b_e1e2_1200_export_20261122.zip"
    work = base / "results" / "github_e3b_e4_exact_blobs_repair_20261123"
    checkout = work / "st-clustering-research"

    need(original_zip.is_file(), "E3B_ORIGINAL_ZIP_NOT_FOUND " + str(original_zip))
    need(not work.exists(), "E3B_E4_REPAIR_WORKSPACE_ALREADY_EXISTS " + str(work))
    need(gitrun("--version").startswith("git version"), "GIT_NOT_AVAILABLE")
    # Preflight ZIP integrity before creating fresh clone
    need(sha256(original_zip.read_bytes()) == E3B_ZIP_SHA, "E3B_ZIP_SHA_MISMATCH")
    work.mkdir(parents=True)
    gitrun("clone","--quiet","--branch","main","--single-branch",REPO,str(checkout),
           proxy=args.proxy)
    need(gitrun("remote","get-url","origin",cwd=checkout) == REPO,
         "UNEXPECTED_REPOSITORY_REMOTE")
    check_attributes(checkout, E3B_ROOT)
    check_attributes(checkout, E4_ROOT)
    m3 = load_source_manifest(checkout / E3B_ROOT / "SOURCE_SHA256.csv", 1200)
    m4 = load_source_manifest(checkout / E4_ROOT / "SOURCE_SHA256.csv", 86)
    old = old_tree_blobs(checkout)
    items3 = prepare_e3b(base, checkout, m3, old, original_zip)
    items4 = prepare_e4(base, checkout, m4, old)
    items = items3 + items4
    need(len(items) == 1286, "COMBINED_SOURCE_COUNT_NOT_1286")

    index_data = "".join(
        "100644 " + r["exact_git_blob"] + "\t" + r["path"] + "\n" for r in items
    ).encode("utf-8")
    gitrun("update-index","--index-info",cwd=checkout,stdin=index_data)
    changed = sum(x["changed_in_git"] == "true" for x in items)
    need(changed > 0, "NO_GIT_EOL_NORMALIZATION_FOUND_ABORT")
    write_audit(checkout, E3B_ROOT, items3)
    write_audit(checkout, E4_ROOT, items4)
    staged = gitrun("diff","--cached","--name-only",cwd=checkout).splitlines()
    need(len(staged) == changed + 2,
         "STAGED_DIFF_COUNT_MISMATCH %d != %d" % (len(staged), changed + 2))
    print("E3B_E4_EXACT_BLOB_STAGE_PASS sources=1286 changed=%d audits=2" % changed,
          flush=True)
    need(gitrun("config","user.name",cwd=checkout), "GIT_USER_NAME_MISSING")
    need(gitrun("config","user.email",cwd=checkout), "GIT_USER_EMAIL_MISSING")
    gitrun("commit","-m",
           "fix(data): restore exact E3B+E4 original source Git blobs after CRLF normalization",
           cwd=checkout)
    commit = gitrun("rev-parse","HEAD",cwd=checkout)
    final = old_tree_blobs(checkout)
    mismatches = [x["path"] for x in items
                  if final.get(x["path"]) != x["exact_git_blob"]]
    need(not mismatches, "COMMITTED_TREE_NOT_EXACT_SHA " + str(mismatches[:3]))
    print("E3B_E4_COMMITTED_SOURCE_BLOB_PASS sources=1286/1286", flush=True)
    gitrun("push","origin","HEAD:refs/heads/main",cwd=checkout,proxy=args.proxy)
    print("E3B_E4_EXACT_SOURCE_PUSH_PASS e3b=1200 e4=86 changed=%d" % changed, flush=True)
    print("E3B_E4_EXACT_SOURCE_COMMIT=" + commit, flush=True)
    print("NO_REFIT_NO_DATA_VALUES_CHANGED_ORIGINS_PRESERVED", flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("E3B_E4_EXACT_REPAIR_FAILED",type(exc).__name__,str(exc),file=sys.stderr,flush=True)
        sys.exit(2)
