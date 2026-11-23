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

## 三、E4 SVG→PDF 本地转换最新状态（2026-11-23更新）

- **本地批量转换：用户提供的 Codex 最终报告称已完成**：Windows 商店 Inkscape 1.4.4 在已注册应用包上下文中调用CLI，原有 `151507` 的3份PDF未覆盖，新增33份，12切片×3图=36份PDF均与原SVG同目录同名（仅扩展名改为PDF）；采用PDF 1.5、文字转路径、滤镜回退300 dpi。报告称36份源SVG和原有3份PDF的SHA256未变化，PDF转换失败0次；测试阶段发生1次控制台UnicodeEncodeError并已恢复，原始失败记录保留。**以上批量产物存在性、结构与渲染为Codex报告，不能当作助手已打开33份新PDF。**
- **本轮助手独立复核**：收到`final_manifest.csv`（36行）和`FINAL_CHECK_REPORT.txt`；36行没有重复/缺项、字段缺失、哈希格式错误或命名错位；12切片每片三类齐全，状态33 `success` +3 `existing_protected`；全部列出PDF 1.5、单页、0字体资源及非零矢量绘制操作。36份来源SVG的相对路径+SHA256与GitHub冻结`SOURCE_SHA256.csv`对照一致；此前用户上传的151507三张PDF实物经独立SHA256与字节数核算，3/3对应清单。
- **尚未独立验收**：33份新PDF实物、`final_report.json`、最终图件视觉对比及真实学校论文模板编译；不能将Codex报告等价为这些环节已经完成。
- **GitHub当前仅含E4原始SVG/CSV，不含这36份本地派生PDF。** Windows本地清单/报告路径：`D:\paper\CellCharter_reproduction\results\e4_spatial_visualization_v1\svg_pdf_review_20261123_v1\`。PDF位于原E4批次各切片文件夹；本地完成不等于远端上传。
- 过去的`E4_CONVERTER_MISSING`、winget下载中断和商店版CLI拒绝访问均属**已绕过的历史工具问题**，不应再作为当前阻断或要求重新转换。

## 四、恢复工作：只进行一件事

**唯一下一步：本地36份派生PDF及转换清单安全归档到GitHub预定`E4_SOURCE_FIGURES_20261122_RELEASE/figures_pdf/{slice}/`位置**（保持原始SVG/CSV和Git blob不变；先校验36份目标文件SHA、目标目录冲突，保留已有3份PDF，不重训、不重绘、不重复转换）。用户Windows本地亲自操作或明确委托本地Codex；上传后由助手独立核验GitHub PDF文件树36/36、来源/派生SHA、至少151507/151671/151675代表图外观。随后才进行XeLaTeX实际编译、学校模板/参考文献审查及Claude集中审稿。当前不得称论文最终排版或终审完成。

## 五、新对话最重要提醒

1. 先看本快照、[交接](CURRENT_RESEARCH_HANDOFF.md)和最新日记；旧的超过15万字状态已移入历史快照，不要按早期TODO重新训练已完成实验。
2. E3b+E4的CRLF问题**已彻底修复并经远端对象核验**，无需再次运行原始上传/修复脚本。
3. Windows端36个PDF**据Codex报告已本地转换**，清单和旧3份实物已获独立核查；但GitHub尚无36份派生PDF，下一步是安全归档与远端复核，不再重试转换器安装。
4. CellCharter仅为毕业论文中的一个研究专题，数值和局限必须以已有CSV/实际报告为准，不能从论文草稿反推原始实验。
5. 用户要求每做完一个文稿/科研日志即同步GitHub；仅对真实已完成状态标记PASS。
