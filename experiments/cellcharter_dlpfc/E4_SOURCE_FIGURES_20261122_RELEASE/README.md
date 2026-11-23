> **2026-11-23字节级核查说明：** 文件已上传且数量完整，但Windows Git的自动换行规范化使部分原始CRLF文本在Git blob中变成LF。**此时原始SHA256清单与GitHub源文件字节尚不完全相同**；这是行结束符转换而非数据值被重算。已禁用本发布目录的Git文本转换（`.gitattributes: * -text`），并另行准备从用户Windows原始ZIP/原件恢复Git blob的脚本`../repair_e3b_e4_exact_git_blobs_v1.py`。只有其真实运行和远端SHA复核完成后，才能重新宣称GitHub逐字节等同原始来源。

# E4 full original SVG and CSV publication (2026-11-22)
Source: Windows batch_20261120T080609Z_4732, audited 20261120T082135Z_29612.
This directory holds byte-identical copies of 36 genuine SVGs, 36 genuine CSVs,
12 original e4_sample_manifest.json files, the original batch status and final
audit report, and an export-time SOURCE_SHA256.csv manifest.
NO model fitting, image synthesis, post-hoc cluster relabeling, or re-plotting.

figures/<sample>/: three original vector plots, three raw/derived CSV files,
and the manifest with source and prediction SHAs.
The main-text representatives were frozen in the original plot script:
151507 (D1 positive B-A ARI), 151671 (D2 near zero), 151675 (D3 negative).
These are result-informed illustrative samples, not blind test selection.
All twelve are provided, including unfavorable cases.
CellCharter A/B source is seed22911 Oracle-K; other result stages have
different seed/K settings. Never silently mix them.
Independent biological n=3 donors, not n=12 slices or ~43k spots.

Original editable SVGs live in figures/. For XeLaTeX using graphicx,
a separate, exactly derived vector-PDF export may be made later under
figures_pdf/; it is not part of the original E4 Windows plot run.
