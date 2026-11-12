# 第三篇论文暂停存档｜2026-11-12

## 用户最终决定
用户在发现151507历史标签文件混杂后，明确要求暂时不追查这些问题，先确认第三篇论文完成程度，随后要求存档。接手时勿自动恢复标签排查、勿要求重复训练或编译。

## 已验证的论文进度
- 第二章研究背景/相关工作（3页）、第三章研究方法（5页）、第四章结果分析（7页），连同6篇文献合并为16页PDF工作稿；Windows执行两轮XeLaTeX成功，用户上传PDF并完成内容/图表排版审查。
- 三张图（技术流程、12片差值三面板、151671/151676空间六面板）、四张表、六篇参考文献在PDF中可见。仍有第6–7页图文跨页、第13页表4留白和第14页图例较小等瑕疵。PDF未证明已按学校学位论文模板定稿。
- 整合源码：experiments/cellcharter_dlpfc/THESIS_CHAPTERS_2_4_INTEGRATED_20261112.tex 及3份chapter_0X_*_integrated.tex。三个原独立TeX未被覆盖；GitHub存放TeX源码，不等于用户Windows本地PDF、实验图和数据字节被同步。
- 尚待：第一章绪论、第五章总结与展望、中英文摘要/关键词、学校格式规范、必要的数据质量审查与文献证据补充。核心正文基本写完，但毕业论文未正式定稿，不保证SCI录用。

## 真实结果边界
- DLPFC 12片来自3位供体；A=L0+L1+L2，B=L0+L1+L4，均15维，seed22911；D2采用Oracle-K5，其他K7。
- B相对A在12片切片级平均ΔARI≈−0.0175、ΔNMI≈−0.0047、Δ边界F1≈−0.0047；B优于A的切片数分别4/12、6/12、6/12。没有稳定优势或已验证算法创新，不可用切片/spot/边充当独立供体。

## 最新Windows只读审计日志（本轮实际输出，未更改文件）
- 12张切片均有manual_layer_annotations.csv。后10片有metadata_source.tsv；151507和151508没有这个同名文件。
- 151507目录的metadata.tsv共有3661条数据，首行表头73字段、数据行74字段；对全部数据行按制表符直接提取第3字段，3661行均为151669。此文件与151507目录不符，不能作为151507来源凭据；其原始文件来历尚未最终证明。
- 151507/manual_layer_annotations.csv共4961行，按sample_name分组151507=4221、151669=740；同sample_name+spot_name组合的重复数0。混合切片是已证实事实，但不能直接推出实际评价发生污染。
- 151507/spots_aligned.csv有4226条spot；仅筛选sample_name=151507的4221条参考标签，逐barcode匹配结果MATCHED=4221、MISSING_REFERENCE=5、LABEL_MISMATCH=0；尚未检查5行has_label，以及下游ARI/NMI/边界F1实际标签过滤与关联代码。不得声称污染已经进入结果，也不能声称已彻底排除。
- SEDR/SpatialLIBD layer_guess公开数据来源已有外部文档链初查，详见DLPFC_LABEL_ORIGIN_AUDIT_20261112.md；旧2片是否与后10片完全同源及逐barcode官方对照未完成。

## 下次接手
先读AGENTS.md、PROJECT_STATE.md顶部、CURRENT_RESEARCH_HANDOFF.md及本存档。顺应用户下一次科研任务；如继续写论文，优先绪论/总结/摘要（顺序用户决定），但仍需标注未解决的原始来源核查与研究限制。不默认重跑scVI/CellCharter/GMM。用户Windows本地操作一次一条PowerShell命令，等真实输出。
