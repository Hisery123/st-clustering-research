# CellCharter研究专题 · 毕业论文写作进度（2026-11-22）

> 最新真相入口：文件实际存在于GitHub默认main分支。**已撰写/已提交/已静态检查/已LaTeX编译/已导师审定是不同状态。** 用户决定毕业论文优先，完整记载真实实验、不以新算法和高创新为前提；先完成全文草稿，再由Claude独立审稿。

## 本轮真实已提交的新写作文件

| 文稿 | 状态与范围 | GitHub |
|---|---|---|
| 第二部分研究背景与相关工作 | **完整V1**，包含DLPFC、scVI、CellCharter、其他空间基线、空间边界与K策略的背景；不夸大原创性 | [chapter_02_background_rewrite_v1_20261122.tex](chapter_02_background_rewrite_v1_20261122.tex) |
| 第三部分研究方法与实验设计 | **完整V1**，11,486字符；12切片/6患者、预处理、CellCharter、E1/E2/E3c/E3d/E3b/E5a/E5b、标签隔离与公平性、统计单位 | [chapter_03_methods_rewrite_v1_20261122.tex](chapter_03_methods_rewrite_v1_20261122.tex) |
| 第四部分实验结果与分析 | **完整V1**，10,319字符；E1/E2→E3c→E3d→E3b→E5a→E5b、E4图件占位、5张真实数据表及负结果 | [chapter_04_results_rewrite_v1_20261122.tex](chapter_04_results_rewrite_v1_20261122.tex) |
| CellCharter研究专题引言 | **模块草稿**，不能冒充包含其他科研工作的毕业论文全书第一章 | [cellcharter_study_introduction_module_v1_20261122.tex](cellcharter_study_introduction_module_v1_20261122.tex) |
| CellCharter专题结论/展望 | **模块草稿**，不能冒充整个学位论文最终总论 | [cellcharter_study_conclusion_module_v1_20261122.tex](cellcharter_study_conclusion_module_v1_20261122.tex) |
| 参考文献种子库 | **11条BibTeX记录**，其中新增的BANKSY/BayesSpace/Wu/Leiden已于本轮对出版方或PubMed/原数据归档核对标题和DOI；此前已有文献来自项目第一轮证据矩阵；作者全名单与学校引文格式还需正式核对 | [thesis_cellcharter_verified_references_20261122.bib](thesis_cellcharter_verified_references_20261122.bib) |
| 第2—4节独立预览入口 | **已上传未编译**，ctexart/XeLaTeX+BibTeX；不替代学校学位论文正式模板 | [thesis_cellcharter_chapters_2to4_preview_20261122.tex](thesis_cellcharter_chapters_2to4_preview_20261122.tex) |
| 第四章逐结果证据矩阵 | 已有，精确指向GitHub真实CSV/SVG及待核条目 | [THESIS_WRITING_EVIDENCE_MAP_20261122.md](THESIS_WRITING_EVIDENCE_MAP_20261122.md) |

所有11月12日历史第二/三/四章文件均未覆盖。完整相关实验数据及校验见[RESULTS_ARCHIVE_STATUS_20261122.md](RESULTS_ARCHIVE_STATUS_20261122.md)。

## 本轮已执行的静态检查

- 三个主章节+两个模块共5份TeX与预览入口共6份tex文件已从GitHub远程重读；
- 表格、公式、align和enumerate环境的开启/关闭数量全部一致；
- 全部\verb|\label|无重复，当前\verb|\ref|目标都存在；
- 文献\verb|\cite|使用的键都在本轮11条BibTeX之中；
- 以上是**文本级静态核查**，不是实际LaTeX编译、PDF分页验证、学校格式审查或引用文献全文内容验证。

## 已完成写作与尚未完成的边界

1. **正文有来源**：E1/E2、E3c、E3d、E3b、E5a、E5b所有主要定量句从已归档真实指标抽取。E5b患者ARI低于0.05者3/6，A15D较BayesSpace在Kblind下NMI平均差为负，均未隐瞒。
2. **科学结论谨慎**：不把CellCharter已有邻域聚合当新算法，不把严格边界F1下降直接定性为确定的平滑机制；DLPFC n=3供体，乳腺癌n=6患者，种子/切片/spot不作生物学伪重复。
3. **事后标识**：E3d后验ARI/NMI与E3b容差分析属追加评价；Oracle-K与K-blind明确区分。BayesSpace Kblind命中q=10边界28/36、18/18保留。
4. **E4图件待处理**：当前只有E4真实脚本与成功审计记录，没有在本轮取得全12切片原始SVG逐图比对；不能假装原图已插入正文。论文排版阶段需从Windows原件恢复图号及图注。
5. **编译/完整性待验收**：还未调用XeLaTeX/BibTeX检查真实编译输出，也没有学校正式学位论文模板、全论文统一章节编号、图表编号与引文样式的对照；当前独立预览不等于学校规定最终文档。
6. **参考文献**：第二部分已按可核实的文章/DOI撰写，但CellCharter原论文所有补充材料的逐项重叠审查未完成。用户明确毕业论文优先，不为创新性调查暂停写作；文献引用与文字准确性在交Claude前仍需复核。
7. **其他科研线的整合**：本专题是用户第三篇空间聚类研究，不应擅自把其他CTW-RF、稀有细胞工作的实验内容变成已完成章节或把此专题单独称为用户整本硕士论文的最终稿。

## 下一优先任务

1. 取得E4空间图及marker图的**原始可编辑SVG**，按既有审计逐张匹配真实sample/预测/来源SHA；在新版第四章插入完整图文。
2. 使用学校模板把本专题的背景、方法与结果合并，真实编译并检查长表格/公式/中文字体/引用。
3. 整合全论文其他研究工作的真实草稿，完成统一绪论、各专题衔接、总结与中文/英文摘要，不编造尚未提供的其他实验。
4. 提交完整草稿给Claude进行逐段内容、统计独立性、引用与结构审查，按实际缺陷修改。
