# CURRENT_RESEARCH_HANDOFF — 2026-11-23 CellCharter论文继续写作

> **本文件是新对话直接接手的精简入口。** 当前状态优先依据 [PROJECT_STATE.md](PROJECT_STATE.md)。完整旧交接历史已归档至 [ARCHIVED_HANDOFF_BEFORE_20261123_CHECKPOINT.md](RESEARCH_JOURNAL/ARCHIVED_HANDOFF_BEFORE_20261123_CHECKPOINT.md)。不要依据早期段落中“E3/E4/E5未做”的历史描述重新启动实验。

## 项目定位与职责

用户使用Windows/PowerShell亲自运行，助手审查设计、代码、实验统计、LaTeX稿件并逐步维护GitHub；按**毕业论文先行**原则，对成熟CellCharter流程开展已完成的多尺度、K敏感性、边界、成熟基线及外部六患者系统评价，不强行宣称新方法。原始实验数据、负结果、后验分析和K选择局限如实披露。DLPFC独立$n=3$供体（12切片嵌套），乳腺癌独立$n=6$患者，不将seed/spot作为生物独立n。

## 已确认完成并有文件

1. **E1/E2、E3c、E3d、E3b、E5a、E5b**完成并归档相应结果/审计；主要数值入口 [THESIS_WRITING_EVIDENCE_MAP_20261122.md](experiments/cellcharter_dlpfc/THESIS_WRITING_EVIDENCE_MAP_20261122.md)。E3b容差和E3d ARI/NMI评分属于事后后验。
2. **原始文件字节完整性**：E3b原预测1200份、E4来源86份（36SVG、36CSV、12manifest和2JSON）在Windows源SHA校验与GitHub原始Git对象检查中均通过。用户的修复日志为`E3B_E4_EXACT_SOURCE_PUSH_PASS e3b=1200 e4=86 changed=1286`；修复提交`6d4bc09bb6f98d0dff13a442fee1dd4759e998c2`，助手逐一比对远端完整Git tree与两份修复审计：**1286/1286一致**。**勿再重跑原始数据修复/上传脚本。**
3. **论文已有初稿**：`experiments/cellcharter_dlpfc/`下 `chapter_02_background_rewrite_v1_20261122.tex`、`chapter_03_methods_rewrite_v1_20261122.tex`、`chapter_04_results_rewrite_v1_20261122.tex`，另有`cellcharter_study_introduction_module_v1_20261122.tex`、`cellcharter_study_conclusion_module_v1_20261122.tex`、`thesis_cellcharter_verified_references_20261122.bib`、`cellcharter_study_full_preview_v1_20261122.tex`与`appendix_e4_all12_figures_v1_20261122.tex`。
4. E4真实SVG原件与CSV在`E4_SOURCE_FIGURES_20261122_RELEASE/figures/`下；正文固定三个结果知情代表图151507、151671、151675，附录保留全12切片/36图。其图位等待矢量PDF，尚未可实际排版使用。

## 最后一次用户Windows实际反馈（不可改写成成功）

- 首次运行`convert_e4_original_svg_to_pdf_and_push_v1.py`：`E4_CONVERTER_MISSING: No Inkscape installation and no Python cairosvg module`；`E4_PDF_CONVERSION_FAILED exit_code=2`。这属于**工具依赖缺失**，不属于模型训练失败或图像数据损坏。脚本先检测转换器后创建工作目录，没有转换成功或推送。
- 用户随后手动运行：
  `winget install --id Inkscape.Inkscape --exact --source winget --accept-package-agreements --accept-source-agreements`；
  仅看到了`Found Inkscape [Inkscape.Inkscape] Version 1.4.4`与下载至`149 MB / 162 MB`。**安装是否真正完成尚未返回输出**。
- 最近一轮助手给用户的唯一操作是PowerShell通过`$env:ProgramFiles\Inkscape\bin\inkscape.exe`或`ProgramFiles(x86)`位置核验`--version`。**用户尚未返回验证输出**。
- 截至此次存档独立查看GitHub main完整树，`figures_pdf/`仍**0文件**，未产生和提交36份派生PDF。

## 下一唯一行动、验收与失败处理

**先让用户核验Inkscape 1.4.4是否已完成安装并能执行`--version`**。如Windows终端仍在下载/安装，只需完成该安装动作；无须同时执行其他命令。发现文件但无法调用应核对具体程序目录和异常日志。

只有核验PASS，才能对现存GitHub `convert_e4_original_svg_to_pdf_and_push_v1.py`进行固定版本下载与本地工作目录防覆盖检查并手动运行，要求：
`E4_SOURCE_SVG_SHA_PASS checked=36/36` → `E4_LAYOUT_PDF_PUSH_PASS pdfs=36 metadata=3 files=39`。禁止重新绘图、改配色或改模型原预测。之后远端核查36PDF+来源SHA，目视至少检查三个代表图后再进行实际XeLaTeX/学校模板编译。

**注意**：学生要求完整研究专题先形成可供Claude审稿的实证论文；尚未进行实际编译、E4图件视觉同等性校验、CellCharter原文补充材料全文核对、导师/Claude终审，不得声称整个学位论文定稿。上传工作与真实成功状态务必分开。

## 自检问题（新GPT接手）

- 原始实验数据是否缺失？E3b/E4当前不缺，字节级已修复；其他E5a/E5b原始逐spot预测的GitHub发布范围另依归档说明，不能假装全部已公开。
- 当前真正卡点？**Inkscape安装未确认，36个SVG派生PDF未生成**。
- 能否继续写作？可以，现有正文完整首稿在仓库；不能因排版未完成就说全部实验未做。
- 最应避免什么？重复训练、伪重复、将事后结果写成预注册、把标签知情Oracle-K写成无标签、把BayesSpace不利结果删掉、虚构图和引用。
