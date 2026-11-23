# E4 PDF archive

This directory archives **36 existing PDFs: 12 DLPFC slices × 3 figures**.
The archive operation does not convert, redraw, fit models, or change scientific data.
Each slice contains spatial, MOBP/PCP4/SNAP25 expression, and confusion figures.

The editable source SVGs remain in [`../figures/`](../figures/). For each PDF,
`CONVERSION_SHA256.csv` records its path relative to this directory, exact byte size,
PDF SHA256, original SVG SHA256, repository source path, project-relative provenance,
converter, and whether it was one of the three pre-existing PDFs.

## Existing conversion evidence

The completed local conversion used Inkscape 1.4.4, PDF 1.5, text converted to paths,
page-area export, and 300 dpi for fallback rasterization of filters. Vector content
is retained; original SVG-embedded images are not promoted to vector data.
The conversion report records 33 new exports and three protected 151507 PDFs,
zero PDF conversion failures, single pages, no font resources, vector painting,
successful rendering, and visual review. SVG and protected PDF hashes were unchanged.
This archive does not establish acceptance in a school thesis template or alter
the scientific interpretation of the plots.

## Integrity checks for this archive

Before copying, all 36 source PDF hashes and sizes were recomputed and matched the
completed local `final_manifest.csv`. All 36 original SVG hashes were checked against
that manifest and the frozen repository Git blobs. Copied PDFs are byte-identical;
the parent release's existing `* -text` attribute preserves exact Git blob bytes.
Only the 36 PDFs and `CONVERSION_SHA256.csv`, `CONVERSION_AUDIT.json`, `README.md`
are included in this archive commit. Original SVGs, CSVs, labels, and manuscript
files are not edited by the archive commit.

The audit JSON contains sanitized conversion evidence and pre-upload checks.
After the normal non-force push, the GitHub file tree and all PDF/metadata bytes
are downloaded again for SHA256 verification. That result is reported separately
with the actual archive commit SHA, rather than asserted before publication.

## Warnings retained

- Historical conversion: one resolved GBK console-output encoding error occurred
  after a successful test export. UTF-8 output was fixed and the existing test PDF
  was revalidated and visually compared before the remaining batch. Raw debug logs
  and personal absolute paths are deliberately excluded.
- Archive preflight: direct Git fetch hit a connection reset; a second direct read
  was cancelled. Reads succeeded through the existing local proxy before any upload.
