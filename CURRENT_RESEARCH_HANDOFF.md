# CURRENT_RESEARCH_HANDOFF — 2026-11-23 CellCharter论文继续写作

> **本文件是新对话直接接手的精简入口。** 当前状态优先依据 [PROJECT_STATE.md](PROJECT_STATE.md)。完整旧交接历史已归档至 [ARCHIVED_HANDOFF_BEFORE_20261123_CHECKPOINT.md](RESEARCH_JOURNAL/ARCHIVED_HANDOFF_BEFORE_20261123_CHECKPOINT.md)。不要依据早期段落中“E3/E4/E5未做”的历史描述重新启动实验。

## 项目定位与职责

用户使用Windows/PowerShell亲自运行，助手审查设计、代码、实验统计、LaTeX稿件并逐步维护GitHub；按**毕业论文先行**原则，对成熟CellCharter流程开展已完成的多尺度、K敏感性、边界、成熟基线及外部六患者系统评价，不强行宣称新方法。原始实验数据、负结果、后验分析和K选择局限如实披露。DLPFC独立$n=3$供体（12切片嵌套），乳腺癌独立$n=6$患者，不将seed/spot作为生物独立n。

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

## 自检问题（新GPT接手）

- 原始实验数据是否缺失？E3b/E4当前不缺，字节级已修复；其他E5a/E5b原始逐spot预测的GitHub发布范围另依归档说明，不能假装全部已公开。
- 当前真正卡点？**E4 PDF 已归档GitHub；现在需要检查本地XeLaTeX/BibTeX并实际编译，随后做学校模板适配和审稿。**
- 能否继续写作？可以，现有正文完整首稿在仓库；不能因排版未完成就说全部实验未做。
- 最应避免什么？重复训练、伪重复、将事后结果写成预注册、把标签知情Oracle-K写成无标签、把BayesSpace不利结果删掉、虚构图和引用。
