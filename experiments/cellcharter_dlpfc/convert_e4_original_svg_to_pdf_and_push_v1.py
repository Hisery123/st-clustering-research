#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert all 36 original E4 SVGs from the validated GitHub release into
XeLaTeX-compatible vector PDFs. Commit results as new DERIVED layout files.
No original SVG/CSV is edited. No model execution, reference relabeling, or plotting.
Only the user manually runs this on their Windows workstation.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from xml.etree import ElementTree

REPO = "https://github.com/Hisery123/st-clustering-research.git"
RELEASE = "experiments/cellcharter_dlpfc/E4_SOURCE_FIGURES_20261122_RELEASE"
SAMPLES = ("151507", "151508", "151509", "151510",
           "151669", "151670", "151671", "151672",
           "151673", "151674", "151675", "151676")
SVG_SUFFIXES = ("reference_A_B_spatial",
                "MOBP_PCP4_SNAP25_expression",
                "reference_A_B_confusion")


def need(value, error):
    if not value:
        raise RuntimeError(error)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as src:
        for part in iter(lambda: src.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def git(*args, cwd=None, proxy=None):
    cmd = ["git"]
    if proxy:
        cmd += ["-c", "http.proxy=" + proxy]
    if cwd is not None:
        cmd += ["-C", str(cwd)]
    cmd += [str(x) for x in args]
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       encoding="utf-8", errors="replace", check=False)
    if r.returncode:
        raise RuntimeError("GIT_FAILED rc=%s cmd=%s\nstdout:%s\nstderr:%s" %
                           (r.returncode, " ".join(cmd[:7]), r.stdout[-3000:], r.stderr[-3000:]))
    return r.stdout.strip()


def find_converter():
    found = shutil.which("inkscape")
    paths = []
    for key in ("ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA"):
        root = os.environ.get(key, "")
        if root:
            paths += [Path(root) / "Inkscape" / "bin" / "inkscape.exe",
                      Path(root) / "Inkscape" / "inkscape.exe"]
    for path in paths:
        if path.is_file():
            found = str(path)
            break
    if found:
        ver = subprocess.run([found, "--version"], capture_output=True, text=True)
        need(ver.returncode == 0, "E4_INKSCAPE_VERSION_CHECK_FAILED")
        return {"name": "inkscape", "binary": found,
                "version": ver.stdout.strip() or ver.stderr.strip()}
    try:
        import cairosvg
        return {"name": "cairosvg", "version": getattr(cairosvg, "__version__", "unavailable")}
    except ImportError:
        raise RuntimeError(
            "E4_CONVERTER_MISSING: No Inkscape installation and no Python cairosvg module. "
            "Nothing was converted or pushed. Do not change original figures."
        )


def convert(svg, pdf, converter):
    if converter["name"] == "inkscape":
        command = [converter["binary"], str(svg), "--export-type=pdf",
                   "--export-text-to-path", "--export-filename=" + str(pdf)]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, errors="replace")
        need(result.returncode == 0, "E4_INKSCAPE_FAILED " + str(svg) + "\n" +
             (result.stderr or "")[-1500:])
    else:
        import cairosvg
        cairosvg.svg2pdf(url=str(svg), write_to=str(pdf))
    need(pdf.is_file() and pdf.stat().st_size > 500,
         "E4_PDF_MISSING_OR_TINY " + str(pdf))
    with pdf.open("rb") as stream:
        header = stream.read(8)
        need(header.startswith(b"%PDF-"), "E4_PDF_BAD_HEADER " + str(pdf))
        stream.seek(max(0, pdf.stat().st_size - 2048))
        need(b"%%EOF" in stream.read(), "E4_PDF_BAD_EOF " + str(pdf))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default=r"D:\paper\CellCharter_reproduction")
    parser.add_argument("--proxy", default="")
    args = parser.parse_args()
    base = Path(args.base)
    work = base / "results" / "github_e4_svg_pdf_layout_20261123"
    checkout = work / "st-clustering-research"
    need(shutil.which("git"), "E4_GIT_MISSING")
    need(not work.exists(), "E4_WORKDIR_ALREADY_EXISTS " + str(work))

    converter = find_converter()
    print("E4_LAYOUT_CONVERTER_FOUND", converter["name"], converter["version"], flush=True)

    work.mkdir(parents=True, exist_ok=False)
    git("clone", "--quiet", "--branch", "main", "--single-branch",
        REPO, str(checkout), proxy=args.proxy)
    need(git("remote", "get-url", "origin", cwd=checkout) == REPO,
         "E4_UNEXPECTED_REMOTE")
    release = checkout / RELEASE
    need(release.is_dir(), "E4_SOURCE_RELEASE_MISSING")
    layout = release / "figures_pdf"
    need(not layout.exists(), "E4_PDF_RELEASE_ALREADY_EXISTS")

    manifest_file = release / "SOURCE_SHA256.csv"
    need(manifest_file.is_file(), "E4_ORIGINAL_SOURCE_MANIFEST_MISSING")
    with manifest_file.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    need(len(rows) == 86, "E4_SOURCE_MANIFEST_EXPECTED_86_FOUND_" + str(len(rows)))
    expected = {str(r["RelativePath"]).replace("\\", "/"): str(r["SHA256"]).lower() for r in rows}
    need(len(expected) == 86, "E4_DUPLICATE_SOURCE_MANIFEST_PATH")

    batch = json.loads((release / "e4_batch_status.json").read_text(encoding="utf-8"))
    audit = json.loads((release / "e4_phase_audit_report.json").read_text(encoding="utf-8"))
    need(batch.get("status") == "completed" and batch.get("pass_count") == 12
         and batch.get("failure_samples") == [], "E4_ORIGINAL_BATCH_NOT_PASSED")
    need(audit.get("status") == "passed" and audit.get("checked_samples") == 12
         and audit.get("svg_checked") == 36 and audit.get("csv_checked") == 36
         and audit.get("issues") == [], "E4_ORIGINAL_AUDIT_NOT_PASSED")

    tasks = []
    for sid in SAMPLES:
        for suffix in SVG_SUFFIXES:
            relative = "figures/%s/%s_%s.svg" % (sid, sid, suffix)
            svg = release / relative
            need(svg.is_file(), "E4_SVG_MISSING " + relative)
            sha = expected.get(relative)
            need(sha is not None and digest(svg) == sha,
                 "E4_SOURCE_SVG_SHA_MISMATCH " + relative)
            record = batch["samples"][sid]
            need(record["output_sha256"].get(svg.name) == sha,
                 "E4_SOURCE_SVG_BATCH_SHA_MISMATCH " + relative)
            xml = ElementTree.parse(svg).getroot()
            need(xml.tag.endswith("svg"), "E4_SVG_NOT_VALID_XML " + relative)
            tasks.append((sid, suffix, svg, sha))
    need(len(tasks) == 36, "E4_SVG_MATRIX_NOT_36")
    print("E4_SOURCE_SVG_SHA_PASS checked=36/36 no_refit_no_replot", flush=True)

    layout.mkdir()
    results = []
    for i, (sid, suffix, svg, sha) in enumerate(tasks, 1):
        dest_dir = layout / sid
        dest_dir.mkdir(exist_ok=True)
        pdf = dest_dir / ("%s_%s.pdf" % (sid, suffix))
        convert(svg, pdf, converter)
        results.append({
            "sample": sid, "figure": suffix,
            "source_svg": "figures/%s/%s" % (sid, svg.name),
            "source_svg_sha256": sha,
            "pdf_path": "figures_pdf/%s/%s" % (sid, pdf.name),
            "pdf_sha256": digest(pdf), "pdf_bytes": pdf.stat().st_size,
        })
        if i % 6 == 0:
            print("E4_PDF_PROGRESS converted=%d/36" % i, flush=True)
    need(len(results) == 36, "E4_PDF_COUNT_WRONG")
    with (layout / "CONVERSION_SHA256.csv").open("w", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=tuple(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
    report = {
        "status": "passed",
        "protocol": "E4_SVG_TO_PDF_LAYOUT_ONLY_V1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_files_checked": 36,
        "converted_pdf_count": 36,
        "original_batch": "batch_20261120T080609Z_4732",
        "original_audit_status": "passed",
        "converter": converter,
        "original_sources_unchanged": True,
        "model_training": False,
        "figure_replotting": False,
        "pdf_validation": "header EOF and nonempty; needs human visual review",
        "warnings": ["Text is outlined with Inkscape, if used; original editable SVG stays in figures/.",
                     "CairoSVG may substitute fonts; review rendered PDFs against SVG before thesis acceptance."],
    }
    (layout / "CONVERSION_AUDIT.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (layout / "README.md").write_text(
        "# E4 derived vector PDFs for XeLaTeX\n\n"
        "These 36 PDFs were converted **without rerunning data plots** from the 36 "
        "original source SVGs in ../figures/. The original SVGs and 36 CSVs are unchanged. "
        "Use CONVERSION_SHA256.csv for exact source SVG and PDF file hashes. "
        "Text may be outlined; the editable originals remain SVG. "
        "Conversion is layout work, NOT new scientific evidence. "
        "PDF header/EOF and nonempty files were checked. "
        "Full visual parity and final university-template compilation still require review.\n",
        encoding="utf-8"
    )
    filenames = git("status", "--short", cwd=checkout)
    need(filenames.startswith("?? " + RELEASE + "/figures_pdf/") or
         filenames.startswith("?? experiments/cellcharter_dlpfc/E4_SOURCE_FIGURES_20261122_RELEASE/figures_pdf/"),
         "E4_WORKTREE_HAS_UNEXPECTED_CHANGES " + filenames[:400])
    git("add", "--", RELEASE + "/figures_pdf", cwd=checkout)
    changed = git("diff", "--cached", "--name-only", cwd=checkout).splitlines()
    need(len(changed) == 39, "E4_STAGED_EXPECTED_39_FOUND_" + str(len(changed)))
    git("commit", "-m", "thesis(cellcharter): add 36 source-verified E4 SVG-derived vector PDFs", cwd=checkout)
    commit = git("rev-parse", "HEAD", cwd=checkout)
    git("push", "origin", "HEAD:refs/heads/main", cwd=checkout, proxy=args.proxy)
    print("E4_LAYOUT_PDF_PUSH_PASS pdfs=36 metadata=3 files=39", flush=True)
    print("E4_LAYOUT_COMMIT=" + commit, flush=True)
    print("E4_LAYOUT_URL=https://github.com/Hisery123/st-clustering-research/tree/main/" + RELEASE + "/figures_pdf", flush=True)
    print("E4_LAYOUT_ORIGINAL_SVG_UNMODIFIED=36/36", flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("E4_LAYOUT_FAILED", type(exc).__name__, str(exc), file=sys.stderr, flush=True)
        sys.exit(2)
