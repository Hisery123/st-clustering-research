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

## 2026-11-23｜E3B/E4原件精确Git字节修复已实际完成并通过远端复核

**当前最新状态覆盖此前“等待执行修复”的旧记录。** 用户Windows端实际运行`repair_e3b_e4_exact_git_blobs_v1.py`，日志报告：

- `E3B_ORIGINAL_BYTES_PASS sources=1200 zip_sha256=cfad75dbc35723c72e52f8906b07e1b81048ff70fcf04df709d41ae42bc1302b`
- `E4_ORIGINAL_BYTES_PASS sources=86`
- `E3B_E4_EXACT_BLOB_STAGE_PASS sources=1286 changed=1286 audits=2`
- `E3B_E4_COMMITTED_SOURCE_BLOB_PASS sources=1286/1286`
- `E3B_E4_EXACT_SOURCE_PUSH_PASS e3b=1200 e4=86 changed=1286`
- `E3B_E4_EXACT_SOURCE_COMMIT=6d4bc09bb6f98d0dff13a442fee1dd4759e998c2`

**本助手独立在GitHub远端取main分支该提交的完整Git tree**（非截断），分别读取`E3B_E1E2_1200_PREDICTIONS_20261122/EXACT_SOURCE_BLOB_REPAIR_AUDIT_20261123.csv`和`E4_SOURCE_FIGURES_20261122_RELEASE/EXACT_SOURCE_BLOB_REPAIR_AUDIT_20261123.csv`，逐条检查`path`对应`blob SHA1`等于`exact_git_blob`：E3B **1200/1200**匹配、E4 **86/86**匹配、缺失0。提交树完整且各对象等于Windows脚本从原源文件SHA256校验后生成的原始Git blob。由此此前CRLF规范化产生的字节保真缺口**已修复**，不是仍待修复。原始报告和修复审计继续保留，不覆盖。

下一任务是把E4真实36SVG无重绘转换为适合XeLaTeX的36个矢量PDF，运行脚本`experiments/cellcharter_dlpfc/convert_e4_original_svg_to_pdf_and_push_v1.py`（已提交但**尚未由Windows执行**），先逐份检查原始SVG的SHA再转换与提交。真实PDF成功后需检查GitHub文件树数量、来源哈希、至少代表图视觉一致性和学校模板编译；当前尚不可称图件已全部排版或PDF已生成。无新增模型训练。
