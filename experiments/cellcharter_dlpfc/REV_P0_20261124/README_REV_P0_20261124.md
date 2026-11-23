# REV_P0_20261124：CellCharter 专题 P0 科学文本修订

**基线：** 仓库 `main` 分支 `b04957b6030e5520f39e2ce121aae0cd496127a8`（2026-11-23）。  
**性质：** 独立修订版。V1、layout V2 与全部冻结实验数据保持不变；未训练、未重新拟合、未重新预测。

## 文件说明

正文 TeX 与 bib 放在 `experiments/cellcharter_dlpfc/` 下，与 V1 同级，便于沿用 E4 图件的相对路径：

| 文件 | 内容 |
|---|---|
| `cellcharter_study_full_preview_rev_p0_20261124.tex` | 编译入口（XeLaTeX → BibTeX → XeLaTeX ×2） |
| `cellcharter_study_introduction_module_rev_p0_20261124.tex` | 引言 |
| `chapter_02_background_rev_p0_20261124.tex` | 第二章 研究背景 |
| `chapter_03_methods_rev_p0_20261124.tex` | 第三章 研究方法 |
| `chapter_04_results_rev_p0_20261124.tex` | 第四章 实验结果 |
| `cellcharter_study_conclusion_module_rev_p0_20261124.tex` | 结论 |
| `thesis_cellcharter_references_rev_p0_20261124.bib` | 参考文献 |

附录沿用未修改的 `appendix_e4_all12_figures_layout_v2_20261123.tex`。

本目录 `REV_P0_20261124/` 下的内容：

| 文件或目录 | 内容 |
|---|---|
| `REV_P0_EVIDENCE_TABLE_20261124.md` | 证据对应表：每条"原作者已做/本研究新增"的判断及其出处 |
| `REV_P0_CHANGELOG_20261124.md` | 修改前后差异摘要 |
| `REV_P0_DIFF_vs_V1_20261124.diff` | 逐行差异（unified diff） |
| `REV_P0_OPEN_ISSUES_20261124.md` | 仍未解决的问题 |
| `REV_P0_STATIC_CHECK_20261124.txt` | 静态检查结果 |
| `rev_p0_derived_summaries_v1.py` | 只读汇总脚本，生成 `derived/T1–T8` 与 `MANIFEST_SHA256.csv` |
| `rev_p0_static_check_and_diff_v1.py` | 静态检查与差异生成脚本 |
| `derived/` | T1–T8 汇总表及 SHA 清单 |
| `official_cellcharter_analyses_fd63ac5/` | 从 CSOgroup/cellcharter_analyses（MIT 许可）按固定 commit 只读复制的 DLPFC 结果 CSV、3 个基准脚本和 LICENSE |

## 如何复算汇总表

在仓库根目录执行：

```
python experiments/cellcharter_dlpfc/REV_P0_20261124/rev_p0_derived_summaries_v1.py experiments/cellcharter_dlpfc experiments/cellcharter_dlpfc/REV_P0_20261124/official_cellcharter_analyses_fd63ac5 experiments/cellcharter_dlpfc/REV_P0_20261124/derived
```

脚本只使用 Python 标准库。复算后应与 `MANIFEST_SHA256.csv` 中的输出 SHA 一致；脚本自身的 SHA 也记录在清单中。
