# Exact 1200 original E1/E2 prediction CSVs (2026-11-22)

This is a BYTE-EXACT COPY of all 1,200 frozen clustering predictions
from the Windows export ZIP, organized by sample/condition/seed.
The experiment was previously conducted; this commit does not re-train
or re-score any predictions.

- Origin: D:\paper\CellCharter_reproduction\results\e3b_e1e2_1200_export_20261122.zip
- Original ZIP SHA256: cfad75dbc35723c72e52f8906b07e1b81048ff70fcf04df709d41ae42bc1302b
- Original 1200-task ledger SHA256: e021ca75958c3d5539dda1987e5031d13ce4fe161d9f0db7f03b5dcfb40e065e
- Prediction SHA256 for EACH task: SOURCE_SHA256.csv
- Every 1200 source prediction CSV SHA256 was verified before git commit.
- Layout: predictions/<sample>/<condition>/seed_<seed>/predictions.csv
- Full posthoc boundary scores: ../E3B_E1E2_1200_POSTHOC_20261122_RELEASE/
- Biological independent unit: 3 donors; slices and seeds are nested.
- Boundary tolerance evaluation is posthoc, not retrospectively preregistered.
- Raw counts matrices and trained model checkpoints are not included.

The original ZIP is NOT uploaded here; its 1200 constituent prediction
CSVs, original export manifest, and original ledger checksum ARE uploaded.
