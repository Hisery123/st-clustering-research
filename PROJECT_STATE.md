# PROJECT_STATE — CellCharter空间聚类研究专题（最新检查点）

**更新日期：2026-11-23（用户要求科研存档）**  
**仓库：** `Hisery123/st-clustering-research`，`main`。本文档为精简权威快照；原长篇历史已完整备份到 [ARCHIVED_PROJECT_STATE_BEFORE_20261123_CHECKPOINT.md](RESEARCH_JOURNAL/ARCHIVED_PROJECT_STATE_BEFORE_20261123_CHECKPOINT.md)，不应按历史中旧的“待做实验”段落复原当前计划。更详尽交接见 [CURRENT_RESEARCH_HANDOFF.md](CURRENT_RESEARCH_HANDOFF.md)、[2026-11-23科研日记](RESEARCH_JOURNAL/2026-11-23.md)。

## 一、研究目标和科研约束

- **硕士毕业论文优先**：CellCharter成熟流程的多尺度空间聚类、K选择、边界与外部样本系统实证评价；不强行宣称新算法/已证实创新。不为高创新性无限增加实验；已有负结果完整写入论文。
- 用户**在Windows PowerShell手动操作**；助手负责审查、文稿、版本和日志。涉及本地命令每次只给**一条**，收到真实输出后推进；不默认Codex/自动控机。
- 区分真实结果/文献原文/假设/未来计划；Oracle-K与K-blind、事后分析、样本层级不可混淆。DLPFC **3名独立供体（12张嵌套切片）**，Wu乳腺癌外部 **6名独立患者**，seed/spot/空间边不是生物重复。不掩盖BayesSpace对照问题、外部低ARI、边界严格F1下降。
- 以实际源脚本、原始文件及SHA为最高证据，日志和本快照作为导航；用户和Claude最后审核不等于已经通过。

## 二、截至存档已验证

| 内容 | 当前实际状态与证据 |
|---|---|
| E1/E2、E3c、E3d、E3b、E5a、E5b | 原先完成的研究方案、模型运行及对应CSV审计归档；论文主要数值来源见 [THESIS_WRITING_EVIDENCE_MAP_20261122.md](experiments/cellcharter_dlpfc/THESIS_WRITING_EVIDENCE_MAP_20261122.md) 和 [RESULTS_ARCHIVE_STATUS_20261122.md](experiments/cellcharter_dlpfc/RESULTS_ARCHIVE_STATUS_20261122.md)。E3d后验ARI/NMI、E3b边界容差是**事后追加**评价。 |
| E3b原始预测 | **1200/1200原始预测CSV**在GitHub。2026-11-23 Windows端从原始ZIP `cfad75dbc35723c72e52f8906b07e1b81048ff70fcf04df709d41ae42bc1302b` 验证后恢复原字节Git对象，远端1286对象复核中E3b为1200/1200。原件目录 [E3B_E1E2_1200_PREDICTIONS_20261122](experiments/cellcharter_dlpfc/E3B_E1E2_1200_PREDICTIONS_20261122/)。 |
| E4原始可编辑科研图 | GitHub有**36 SVG + 36 CSV +12逐切片manifest +原批次状态和审计JSON**，另有来源清单/README。2026-11-23远端修复后E4 **86/86原始对象SHA匹配**，加上E3b合计**1286/1286**。源目录 [E4_SOURCE_FIGURES_20261122_RELEASE](experiments/cellcharter_dlpfc/E4_SOURCE_FIGURES_20261122_RELEASE/)。修复完成的commit：`6d4bc09bb6f98d0dff13a442fee1dd4759e998c2`。|
| 科研论文正文 | 已上传CellCharter专题[第二章](experiments/cellcharter_dlpfc/chapter_02_background_rewrite_v1_20261122.tex)、[第三章](experiments/cellcharter_dlpfc/chapter_03_methods_rewrite_v1_20261122.tex)、[第四章](experiments/cellcharter_dlpfc/chapter_04_results_rewrite_v1_20261122.tex) V1，专题引言/结论、BibTeX、[合稿预览入口](experiments/cellcharter_dlpfc/cellcharter_study_full_preview_v1_20261122.tex)以及[12切片36图附录](experiments/cellcharter_dlpfc/appendix_e4_all12_figures_v1_20261122.tex)。历史11月12日旧稿保留。**这只是CellCharter研究专题初稿，不等于整篇硕士论文终稿。**|
| 文稿检查 | TeX文本静态检查基本通过。**未进行真实XeLaTeX/BibTeX编译；未应用学校正式学位论文模板；未交导师或Claude正式审阅。**E4图位采用原始SVG派生矢量PDF路径，文件不存在时只显示待插图提示。 |

## 三、当前唯一实际阻断：E4的SVG→PDF转换器

- 2026-11-23用户在Windows运行 [convert_e4_original_svg_to_pdf_and_push_v1.py](experiments/cellcharter_dlpfc/convert_e4_original_svg_to_pdf_and_push_v1.py)，返回`E4_LAYOUT_FAILED RuntimeError E4_CONVERTER_MISSING: No Inkscape installation and no Python cairosvg module`及`E4_PDF_CONVERSION_FAILED exit_code=2`。脚本在创建新clone/转换PDF前失败；没有改变E4原件。
- 随后用户手动执行`winget install --id Inkscape.Inkscape --exact --source winget --accept-package-agreements --accept-source-agreements`，输出**Found Inkscape 1.4.4；下载进度149 MB /162 MB**，**未提供下载结束/安装成功的输出**，目前仍属「安装是否成功待核对」。原拟用户检查的Inkscape `--version`尚未返回。
- 本次再次独立查看GitHub main文件树：`E4_SOURCE_FIGURES_20261122_RELEASE/figures_pdf/`下**0个文件**。**没有36张已转换PDF，更没有PDF推送成功。**
- 转换脚本使用新的工作目录`D:\paper\CellCharter_reproduction\results\github_e4_svg_pdf_layout_20261123`，之前由于`find_converter()`在`work.mkdir()`之前失败，通常未创建该目录；但不可凭推断认为用户本地目录一定不存在，再次运行前检查其状态。

## 四、恢复工作：只进行一件事

**下一步：先确认Inkscape真实安装。** 由用户在Windows PowerShell通过完整路径执行Inkscape `--version`，返回真实版本和路径；如果安装命令仍在进行，等其结束后再核查。不得把“找到安装包/正在下载”记为安装完成。

成功确认后，才从GitHub固定脚本检查输入及工作目录、按原SHA将36个真实SVG只作**矢量PDF格式转换**并推送（成功标志`E4_LAYOUT_PDF_PUSH_PASS pdfs=36 metadata=3 files=39`）；收到用户日志后再次GitHub远端核验36张PDF与映射SHA，再目视检查代表图（151507/151671/151675），之后是XeLaTeX实际编译、学校论文模板/文献审查、Claude综合审稿。**不重新训练模型或改变实验数据。**

## 五、新对话最重要提醒

1. 先看本快照、[交接](CURRENT_RESEARCH_HANDOFF.md)和最新日记；旧的超过15万字状态已移入历史快照，不要按早期TODO重新训练已完成实验。
2. E3b+E4的CRLF问题**已彻底修复并经远端对象核验**，无需再次运行原始上传/修复脚本。
3. 现在的阻断是**Windows端Inkscape是否安装成功**，不是实验缺数据；GitHub还没有36个派生PDF。
4. CellCharter仅为毕业论文中的一个研究专题，数值和局限必须以已有CSV/实际报告为准，不能从论文草稿反推原始实验。
5. 用户要求每做完一个文稿/科研日志即同步GitHub；仅对真实已完成状态标记PASS。
