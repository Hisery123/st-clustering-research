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

## 三、E4 SVG→PDF 已上传GitHub（2026-11-23最新）

- **真实远端提交**：`110b7e19a4a5e1af5680bcade7218cc2034bf975`（`main` HEAD已核实），提交仅新增`E4_SOURCE_FIGURES_20261122_RELEASE/figures_pdf/`下36个PDF、`CONVERSION_SHA256.csv`、`CONVERSION_AUDIT.json`、`README.md`，合计39文件，未修改科研原件和稿件。目录：[figures_pdf](experiments/cellcharter_dlpfc/E4_SOURCE_FIGURES_20261122_RELEASE/figures_pdf/)。
- **转换事实与原始报告**：用户Windows本地Codex（Microsoft Store Inkscape 1.4.4）按PDF1.5、文字转路径、滤镜回退300dpi处理，原151507的3PDF保留，新增33张，合计12切片×3图=36张；Codex报告转换失败0次，有一次已恢复的GBK日志`UnicodeEncodeError`，完整日志仍在Windows。
- **助手独立核实范围**：通过GitHub连接读取实际commit的39项文件和`main` HEAD；远端目录12切片+3元数据存在。直接检查远端36行`CONVERSION_SHA256.csv`与36项`CONVERSION_AUDIT.json`完整一致（PDF路径、SHA256、字节、原SVG SHA），33项`success`+3项`existing_protected`，无重复/缺项，PDF字节数汇总66,324,070。36/36来源SVG的路径和SHA256与冻结`SOURCE_SHA256.csv`逐项一致。**远端36张PDF的实际字节SHA256系用户Codex后推送报告重下GitHub对象核算36/36；助手这次未亲自下载全部36个二进制PDF重算SHA，因此不得写成助手独立字节验证36/36。**此前151507的3个PDF用户上传实物已与本地清单SHA一致。
- **未完成**：真实XeLaTeX/BibTeX合稿编译、学校学位论文模板适配、图件排版可读性复核、参考文献完整性核查、Claude与导师终审。E4 PDF归档不是科研新实验、新算法或学位论文完成的证据。原始SVG/CSV与E3b之前的原字节修复已完成，不重复转换/训练/修复。

## 四、恢复工作：唯一下一步

**开始论文真实排版编译阶段**：仓库中的`cellcharter_study_full_preview_v1_20261122.tex`和`appendix_e4_all12_figures_v1_20261122.tex`已使用与远端`figures_pdf/`一致的相对路径；但尚未在Windows本地确认可用XeLaTeX/BibTeX。**第一步仅在本地检查`xelatex`和`bibtex`是否可调用**，不运行编译、不覆盖实验数据；根据检查结果再给下一条操作。之后编译独立专题预览、核对代表图151507/151671/151675及参考文献，再接入学校正式模板并送Claude审查。

## 五、首次真实LaTeX编译和PDF布局审查（2026-11-23）

- **Windows实际编译完成**：MiKTeX的`xelatex`与`bibtex`可调用；用户实际执行 XeLaTeX第一遍退出码0，产出42页；BibTeX退出码0；XeLaTeX第二、第三遍退出码0，最终专题预览`cellcharter_study_full_preview_v1_20261122.pdf` **43页**。输出位于本地`D:\paper\CellCharter_reproduction\results\cellcharter_thesis_preview_compile_20261123\`，不等于整篇硕士论文终稿。
- **助手实物PDF独立检查**：用户上传完整43页PDF；没有全空白页，原36张E4附录图均进入PDF（正文另4张图，共图1–40）；但P16、P26分别仅剩一小段末行，P2/P7/P28也留白较多；附录P29–42小图有大片白边，且`figure[htbp]`浮动导致P33/P37/P42出现切片小节标题迟于其图片，最后一幅图跑到参考文献页附近。这是**实际排版缺陷，当前不得标记论文版式PASS**。有Underfull hbox警告，不等于错误。
- **已安全新增未经编译的排版试验V2，保留V1完全不动**：`experiments/cellcharter_dlpfc/cellcharter_study_full_preview_layout_v2_20261123.tex`及`appendix_e4_all12_figures_layout_v2_20261123.tex`。主文件仅收紧预览页边距/段距、载入caption包和改引用V2附录；附录对36个`figure[htbp]`替换为非浮动minipage+`captionof{figure}`，保持原图路径、内容与caption/label不改。**V2目前静态检查36/36，但没有用户Windows实际编译和视觉验收，是否消除留白待验证。**
- 下一唯一操作：Windows本地 `D:\paper\st-clustering-research` 用`git pull --ff-only`取得已提交的两个V2源稿（若有工作区冲突停止，不强制覆盖）；随后单独编译V2输出到新的隔离目录，经图片顺序/目录标题/页数/参考文献核验再决定如何排版。原V1实验数据、SVG、PDF及稿件保持不变。

## 六、V2真实39页PDF验收（2026-11-23最终本轮反馈）

- 用户Windows真实完成V2 `XeLaTeX→BibTeX→XeLaTeX→XeLaTeX`，全部退出码0；首次38页，二次/三次稳定为**39页**。用户上传`cellcharter_study_full_preview_layout_v2_20261123.pdf`原件；助手使用本地PyMuPDF抽取39页内容并渲染比较V1典型缺陷页面。
- **通过项**：V1中第16/26页仅2行正文的严重孤行页在V2消失；附录12个切片小节标题`A.1–A.12`均先于其对应三幅图；40张插图按图1–40完整出现（正文4 + 附录36）；参考文献10条已在PDF中，未发现全空白页。V1为43页，V2为39页，但减少4页本身不是质量判据。
- **未过项/待正式模板处置**：V2 PDF第38页仍是最后`图40（151676混淆矩阵）`与参考文献同页，第39页仅第9/10条参考文献而大幅留白；附录多为每页3小图，A4纸面文字/矩阵数字可能过小；第14/23/25页各留约半页空白主要因主文件章间`\clearpage`，不必为压页数牺牲章节起始规范；正文部分数学符号、英文术语断行和中英混排需在正式模板中进一步核查。故**V2预览稿排版“部分修复/待模板适配”，非正式学位论文通过**。
- 用户本轮无需继续重训、不必修改任何E4 SVG/PDF，不建议继续盲目追求预览页数最少。下一优先级是取得学校正式硕士论文格式规范和模板（Word/LaTeX），据实际模板确定附录缩放/参考文献独立分页，随后编译验收，再开展文献事实审核、导师/Claude审查。

## 七、CellCharter专题V2 39页PDF正式归档（2026-11-23）

- **用户Windows真实提交/推送**：`bb730c2a60cd20ecb993da9f1406fc94d65aee43`（`main`），仅新增`experiments/cellcharter_dlpfc/preview_pdfs/cellcharter_study_full_preview_layout_v2_20261123.pdf`，不修改已有实验原件、TeX稿或E4图件。
- **助手独立核验**：GitHub连接检查commit只有这1个文件，远端`main` HEAD等于该commit；GitHub完整Git tree中PDF对象`blob d08116b02c6428b44c0ef29cab05490b0b3a248b`、大小`40556088`字节，与用户本轮上传的PDF实物计算出的Git blob SHA1及大小完全相同。该本地实物SHA256为`021a09d7a72d58b2e2ad97f41d2bcb82c5fbd7f5980e93f8284d973bb51eda87`，PDF 39页。哈希验证是Git对象ID与本地实物一致，不误称助手直接下载远端全部PDF再计算SHA256。
- **准确交付定位**：这是CellCharter空间聚类**研究专题完整初稿/可编译预览V2**，含正文+36张附录E4图和10条当前BibTeX引用；**不是整个硕士学位论文终稿**。V2实物排版剩余问题：第38页图40与参考文献同页，第39页仅余两条文献，附录小图A4可读性待正式模板核查；文献真实性/创新性/论文格式与导师/Claude审核尚未完成。
- **下一步**：获取学校最新版硕士论文写作规范/模板，以此整合全论文并修复第38–39页参考文献独立起页、附录尺寸和中英排版；保持原始科研结果和所有V1/V2不变，后续以新稿版本迭代。

## 八、新对话最重要提醒

1. 先看本快照、[交接](CURRENT_RESEARCH_HANDOFF.md)和最新日记；旧的超过15万字状态已移入历史快照，不要按早期TODO重新训练已完成实验。
2. E3b+E4的CRLF问题**已彻底修复并经远端对象核验**，无需再次运行原始上传/修复脚本。
3. GitHub E4 36份PDF已归档；V1与V2均经Windows实际完整编译，V2 PDF39页经助手实物审查修复V1孤行页与附录小节错位；仍有p38图40与文献混排、p39仅2条文献、附录图偏小，当前优先迁入学校正式学位模板，不再盲目压页数。
4. CellCharter仅为毕业论文中的一个研究专题，数值和局限必须以已有CSV/实际报告为准，不能从论文草稿反推原始实验。
5. 用户要求每做完一个文稿/科研日志即同步GitHub；仅对真实已完成状态标记PASS。
