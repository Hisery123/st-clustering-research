> **2026-11-23字节级核查说明：** 文件已上传且数量完整，但Windows Git的自动换行规范化使部分原始CRLF文本在Git blob中变成LF。**此时原始SHA256清单与GitHub源文件字节尚不完全相同**；这是行结束符转换而非数据值被重算。已禁用本发布目录的Git文本转换（`.gitattributes: * -text`），并另行准备从用户Windows原始ZIP/原件恢复Git blob的脚本`../repair_e3b_e4_exact_git_blobs_v1.py`。只有其真实运行和远端SHA复核完成后，才能重新宣称GitHub逐字节等同原始来源。

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
