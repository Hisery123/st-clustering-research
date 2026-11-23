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

## 2026-11-22补充｜E4正文选图规则统一、36图附录和原件发布准备

本轮用户要求继续写作并边写边上传：对`experiments/cellcharter_dlpfc/chapter_04_results_rewrite_v1_20261122.tex`新增完整E4结果解释、按原冻结E4规则将主文示例统一为**151507/151671/151675**（而非旧稿另一目的的151671/151676单seed边界案例），在LaTeX按真实矢量PDF可用性设置条件插图位，缺图时只显示待插入提示。新增`appendix_e4_all12_figures_v1_20261122.tex`：12切片×3类真实图，共36个源文件控制的附录插图位，已接入`cellcharter_study_full_preview_v1_20261122.tex`的条件入口。**这不是36张原SVG已上传，也不是36张PDF已转换。**

GitHub新增`publish_e4_original_figures_v1.ps1` Windows手动一次性上传脚本；它使用用户2026-11-20原完成批次及审计JSON、按每样本manifest逐件核对36SVG+36CSV的SHA，计划提交原72产物、12manifest、原batch/audit及新来源清单/README共88 Git文件。当前**脚本已提交、尚未见用户Windows真实执行成功反馈**，不能称GitHub具有原E4图。来源、脚本、安全边界及上传后SVG→LaTeX矢量PDF转换分别详见`experiments/cellcharter_dlpfc/E4_SOURCE_PUBLICATION_AND_FIGURE_INTEGRATION_20261122.md`。下一唯一用户Windows操作是按固定Git SHA下载、SHA1核验并运行上传脚本；成功后需GitHub重新统计及原字节哈希复核。

## 2026-11-23｜E3B/E4上传后的CRLF字节保真风险（已定位，修复未执行）

**有新核查证据，必须覆盖2026-11-22的“GitHub原件逐字节完全相同”旧说法。** E4确实已经提交GitHub，共88文件：36张SVG、36份CSV、12样本manifest、原batch/audit、README、来源清单；上传提交`0b3a13fbe784711b2c522a09282feeb8a82771e8`。但读取GitHub E4原生SVG `figures/151507/151507_reference_A_B_spatial.svg`并对远端Git blob内容独立计算SHA256，得到`8d3f84cc015bbbefceefd0b4d9744910fc318c8b48ac3e01ebe58442a551a750`，不同于本地原件清单`7d76f7f61d750c9503056aaf60cfd43310e2ce8d72ead91d202655fb868849c1`；远端LF字节仅将每个换行恢复为Windows CRLF后重新计算，则**完全等于原件SHA**。E3B首份原始预测`predictions/151507/cum_L0/seed_22911/predictions.csv`亦发现同样问题：远端LF的SHA`f8b0d04ea183ee4df18882b8f2c43e16f83a1b5a5c3d5144d8d10c7e9d42903c`，恢复CRLF后等于原件`cabbb5f476be36ac7c38270e68ccb87146f9a1d665ace2b780e1b22406671525`。科学数值没有因此重新计算或修改，但旧“Git源字节与Windows原件相同”的表述不成立，必须修复后才能称原始字节完全备份。

已分别为`E3B_E1E2_1200_PREDICTIONS_20261122/`与`E4_SOURCE_FIGURES_20261122_RELEASE/`提交`.gitattributes`、设置`* -text`禁用未来Git换行自动规范化；已上传**综合一次性精确Git blob修复脚本**`experiments/cellcharter_dlpfc/repair_e3b_e4_exact_git_blobs_v1.py`：拟从原始E3B ZIP（固定SHA256 cfad75...）与E4源Windows文件分别校验1200+86=1286份SHA256，`git hash-object -w --stdin`写入原始字节的Git blob，`git update-index --index-info`直接提交原字节，再验证完整提交树并非强制push。**目前只是准备和提交修复脚本，用户尚未报告运行；不得称远端字节修复通过。**早期只修E4的`repair_e4_exact_source_blobs_v1.ps1`被综合版取代，不要先运行它。另已准备`convert_e4_original_svg_to_pdf_and_push_v1.py`，但必须先完成1286份原始Git blob的字节修复，才能开始转换36份真实SVG成论文矢量PDF。

论文正文及36图附录已写入GitHub，原E4图件存在的事实与“严格逐字节匹配原Windows SHA”需要分开报告；同理E3B全部1200文件存在但部分CRLF被规范化。下一步用户在Windows手动执行单条固定SHA脚本下载、核验、精确Git blob修复命令，提供PASS/FAIL；助手再远端核验提交树与来源清单。全程无训练、无更改参考标签、无数据数值重算。

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
