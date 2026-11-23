# CURRENT_RESEARCH_HANDOFF — 2026-11-23 CellCharter论文继续写作

> **本文件是新对话直接接手的精简入口。** 当前状态优先依据 [PROJECT_STATE.md](PROJECT_STATE.md)。完整旧交接历史已归档至 [ARCHIVED_HANDOFF_BEFORE_20261123_CHECKPOINT.md](RESEARCH_JOURNAL/ARCHIVED_HANDOFF_BEFORE_20261123_CHECKPOINT.md)。不要依据早期段落中“E3/E4/E5未做”的历史描述重新启动实验。

## 项目定位与职责

用户使用Windows/PowerShell亲自运行，助手审查设计、代码、实验统计、LaTeX稿件并逐步维护GitHub；按**毕业论文先行**原则，对成熟CellCharter流程开展已完成的多尺度、K敏感性、边界、成熟基线及外部六患者系统评价，不强行宣称新方法。原始实验数据、负结果、后验分析和K选择局限如实披露。DLPFC独立$n=3$供体（12切片嵌套），乳腺癌独立$n=6$患者，不将seed/spot作为生物独立n。

## 今后论文改写的核心风格要求（用户2026-11-23明确）

**请先阅读 [ACADEMIC_WRITING_AND_CONTRIBUTION_STANDARD.md](ACADEMIC_WRITING_AND_CONTRIBUTION_STANDARD.md)，并遵循 [AGENTS.md](AGENTS.md) 的对应规则。** 用户明确不接受把“跑了哪些E1/E2/E3实验”“保存了哪些CSV/SHA/提交”“复现审计通过”依次罗列成正式论文。应先严格内部审查证据，再用成熟的学术表达，围绕**科学问题、尚未充分讨论的评价维度、研究设计、整体与局部指标不一致/跨患者异质性等真实发现、学术和应用意义**组织段落。善于凝练贡献、正向陈述可证实的发现，但不掩盖负结果、不能夸大新颖性或因果。CellCharter既有机制必须在方法中清楚归属原作者，**标题不强制使用“复现”**。目标为硕士毕业、普通SCI四区仅作质量参考，不以顶刊增量要求无限追加实验。Claude修订P0稿也必须遵守这一标准。

## 已确认完成并有文件

1. **E1/E2、E3c、E3d、E3b、E5a、E5b**完成并归档相应结果/审计；主要数值入口 [THESIS_WRITING_EVIDENCE_MAP_20261122.md](experiments/cellcharter_dlpfc/THESIS_WRITING_EVIDENCE_MAP_20261122.md)。E3b容差和E3d ARI/NMI评分属于事后后验。
2. **原始文件字节完整性**：E3b原预测1200份、E4来源86份（36SVG、36CSV、12manifest和2JSON）在Windows源SHA校验与GitHub原始Git对象检查中均通过。用户的修复日志为`E3B_E4_EXACT_SOURCE_PUSH_PASS e3b=1200 e4=86 changed=1286`；修复提交`6d4bc09bb6f98d0dff13a442fee1dd4759e998c2`，助手逐一比对远端完整Git tree与两份修复审计：**1286/1286一致**。**勿再重跑原始数据修复/上传脚本。**
3. **论文已有初稿**：`experiments/cellcharter_dlpfc/`下 `chapter_02_background_rewrite_v1_20261122.tex`、`chapter_03_methods_rewrite_v1_20261122.tex`、`chapter_04_results_rewrite_v1_20261122.tex`，另有`cellcharter_study_introduction_module_v1_20261122.tex`、`cellcharter_study_conclusion_module_v1_20261122.tex`、`thesis_cellcharter_verified_references_20261122.bib`、`cellcharter_study_full_preview_v1_20261122.tex`与`appendix_e4_all12_figures_v1_20261122.tex`。
4. E4真实SVG原件与CSV在`E4_SOURCE_FIGURES_20261122_RELEASE/figures/`下；正文固定三个结果知情代表图151507、151671、151675，附录保留全12切片/36图。本地36份PDF已由Codex归档GitHub main（`110b7e19`），远端提交结构与元数据经助手核查；真实LaTeX编译及代表图排版验收待做。

## 最新E4上传与复核（2026-11-23）

- GitHub `main` 已确认 HEAD `110b7e19a4a5e1af5680bcade7218cc2034bf975`，真实提交含39个新增文件（36个PDF、3份元数据），路径`experiments/cellcharter_dlpfc/E4_SOURCE_FIGURES_20261122_RELEASE/figures_pdf/{slice}/`。PDF来自Windows Codex原有3张+新转换33张，不重新训练/绘图/转换。
- GitHub连接直接检查12个切片子目录、36条远端清单与审计JSON，逐一相符；36源SVG哈希与冻结`SOURCE_SHA256.csv`一致。Codex报告提交后远端重新下载PDF文件字节并检验SHA256 36/36通过；**助手未亲自下载全部36个远端PDF二进制重算**，不能混淆证据等级。Codex归档和转换过程中的下载中断、日志编码/扫描误报已在审计中保留。
- 现有专题初稿`cellcharter_study_full_preview_v1_20261122.tex`和36图附录已引用本次新增PDF对应目录，但**未在Windows本地实际XeLaTeX/BibTeX编译，也未进入学校正式模板/导师Claude终审**。

## 下一唯一行动

让用户在Windows PowerShell只执行一条**只读**版本/可执行路径检查，确认`xelatex`和`bibtex`是否可用；用户回传真实输出后再决定实际编译方案。禁止为排版而重训或更改科研CSV、SVG、预测；保持Oracle-K、事后分析、独立供体n=3/外部患者n=6和负结果不变。

## 最新论文编译与排版问题（2026-11-23）

- 用户Windows实际完成 MiKTeX XeLaTeX/BibTeX/XeLaTeX/XeLaTeX，全部退出码0；V1专题预览从42页更新为43页。上传的43页完整PDF经助手实际检查：40张图均插入，其中附录完整36张；没有完全空白页，但P16与P26几乎空白，附录P29–42图件偏小且浮动队列导致P33/P37/P42的分节标题落在对应图后，图40与参考文献混排。**不是图片生成失败，不得将V1版式认定通过。**
- 新增V2两个独立TeX文件，不覆盖旧V1：`experiments/cellcharter_dlpfc/cellcharter_study_full_preview_layout_v2_20261123.tex`和`appendix_e4_all12_figures_layout_v2_20261123.tex`。仅更改预览排版（页边距2.6→2.4 cm，parskip 0.3→0.08 em，正文载入caption、36附录图从可浮动figure换为非浮动minipage+`captionof`；科研文本、图像路径、图注、标签和原PDF无改动）。静态核查覆盖36图；**V2尚未经过真实编译或视觉验收**。
- 下一步唯一命令：本地`D:\paper\st-clustering-research`执行安全`git pull --ff-only`同步V2稿；失败保留输出，不覆盖文件。收到真实结果后按单步操作在**新独立输出目录**编译V2，然后检查小节标题顺序、p16/p26类似孤行以及所有40幅图及参考文献。V1保留可回退。

## 2026-11-23 V2真实PDF审阅（后于早期“V2尚未编译”条目，覆盖旧状态）

- 用户运行V2的XeLaTeX/BibTeX/XeLaTeX/XeLaTeX全部退出码0，最终预览PDF **39页**，已上传至本轮对话。助手实际抽取39页文字、核对图注1–40、小节标题A.1–A.12，渲染与V1的16/26/42页及V2的14/23/25/26/37/38/39页典型页面比较。
- **已修复**：V1 P16、P26仅剩末尾两行的大面积留白/孤行页在V2已无；附录小节先于其三幅科研图，36图齐全，正文4图齐全（图1–40），BibTeX 10条文献列出。V2 P14/23/25的部分留白主要为强制章节换页，不能一律认定异常。
- **尚未修复**：V2第38页仍同时显示最后图40与参考文献，第39页仅剩最后2条，浪费页面；多张附录图在A4尺寸下文字过小；数学排版、术语断行、文献原文核查与学校正式模板均未通过。**不能称正式学位论文排版PASS。**
- **下一行动**：获得学校正式硕士论文格式要求/模板（优先用户本人提供准确版），然后决定正式稿中的图尺寸、附录形式和文献分页；不要反复仅为减少预览页数改版，也不修改任何科学数据/冻结图像。V1/V2均保留可追溯原版本。

## 最新提交：专题39页V2 PDF已归档GitHub（2026-11-23）

- Windows用户正常commit/push到`main`：`bb730c2a60cd20ecb993da9f1406fc94d65aee43`；仅新增`experiments/cellcharter_dlpfc/preview_pdfs/cellcharter_study_full_preview_layout_v2_20261123.pdf`。
- 助手GitHub连接独立核对commit、main HEAD、Git tree文件路径；远端Git blob `d08116b02c6428b44c0ef29cab05490b0b3a248b`，40,556,088字节，与用户本轮上传的PDF实物经Git blob计算完全一致（本地实物SHA256：`021a09d7a72d58b2e2ad97f41d2bcb82c5fbd7f5980e93f8284d973bb51eda87`，39页）。远端并非借助工具完整重下载二进制后计算SHA256，勿夸大。
- 正确状态：**CellCharter研究专题初稿基本完整且PDF已归档**，非硕士整篇终稿；P38最后一张附录图与参考文献混排、P39仅两条文献、附录纸面字偏小、正式学位模板、引文审查与导师/Claude终审未完成。
- 下一步优先取得学校硕士论文正式模板/规范，整合研究专题和其它章节；避免重复实验、重新转换图、盲目压缩页数。

## 自检问题（新GPT接手）

- 原始实验数据是否缺失？E3b/E4当前不缺，字节级已修复；其他E5a/E5b原始逐spot预测的GitHub发布范围另依归档说明，不能假装全部已公开。
- 当前真正卡点？**V2已真实编译39页并经实物审核，主要错位问题修复；仍须学校模板适配及最后图/参考文献分页处理，文献和科研论述终审未完成。**
- 能否继续写作？可以，现有正文完整首稿在仓库；不能因排版未完成就说全部实验未做。
- 最应避免什么？重复训练、伪重复、将事后结果写成预注册、把标签知情Oracle-K写成无标签、把BayesSpace不利结果删掉、虚构图和引用。
