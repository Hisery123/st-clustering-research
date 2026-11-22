# 第三篇 CellCharter｜科研结果归档与审查总控（2026-11-22更新）

> 本文档是**最新的GitHub可用证据索引**，用于替代较早记载“E3d/E5a/E5b的CSV尚未上传”的历史状态。**真实实验执行、审计PASS、指标计算、GitHub已持有原件、科学贡献成立**是五个不同命题，不得混用。所有新归档与Windows原件SHA256吻合，且上传后GitHub远端重读校验通过。

## 阶段、原件和可以得出的结论

| 阶段 | 本机冻结实验/审计状态 | GitHub已公开归档的实际文件 | 仍需注意 |
|---|---|---|---|
| E1/E2 12切片旧A/B | 有实际完整评价及审计记录 | [E1E2_20261119_RELEASE](E1E2_20261119_RELEASE/)：原始派生CSV、统计与SVG | 12切片来自3名供体，旧部分比较为Oracle-K或开发性分析 |
| E3c 固定K尺度敏感性 | 1920条条件评价形成派生结果 | [E3C_20261120_RELEASE](E3C_20261120_RELEASE/)：e3c_newK_metrics_1920.csv、不同尺度/K汇总、SVG和脚本 | 固定K不等于无标签选K |
| **E3d K-blind AutoK** | Windows独立审计PASS 48/48；2640个标签拟合数组；搜索边界10/48 | **[E3D_20261122_RELEASE](E3D_20261122_RELEASE/)**：48行无标签AutoK审计CSV+原audit_report.json+SHA清单 | **该阶段未计算ARI/NMI**，目前只能作无标签K选择与技术稳定性描述。若需其性能，单独开展后验标签评价 |
| E4空间域可视化 | 终审通过日志已有文档 | 原图生成代码、审计及可视化计划 | 全套原始图件是否逐张复制到GitHub尚未逐图验收 |
| **E5a 四成熟基线** | Windows独立审计PASS **288/288** | **[E5A_20261122_RELEASE](E5A_20261122_RELEASE/)**：288项评价CSV（含ARI/NMI）、8行方法×K臂汇总、原audit_report.json+SHA清单 | 3独立供体/12嵌套切片/3技术seed；BayesSpace K-blind 28/36选到q=10搜索上界；跨方法并非完全相同特征 |
| **E5b Wu2021乳腺癌六患者** | Windows独立审计PASS **360/360**、ARI/NMI评价360/360 | **[E5B_20261122_RELEASE](E5B_20261122_RELEASE/)**：360项全部真实ARI/NMI、120患者三seed汇总、144患者配对、原audit_report.json、后验分析报告、可重做绘图脚本及3张SVG；SHA清单 | 6独立患者；K-blind与Oracle-K分开；BayesSpace K-blind 18/18选q=10上界；并非DLPFC训练模型的直接跨组织推理 |
| E3b 边界容差 | 尚无完整冻结全量运行/终审通过记录 | 只有历史局部诊断或草案 | 未完成；不得写成已全面验证 |
| P0-1 最近邻文献审查 | 第一轮已留档 | [LITERATURE_EVIDENCE_AND_NOVELTY_20261111.md](LITERATURE_EVIDENCE_AND_NOVELTY_20261111.md) | Varrone et al. 2024 CellCharter全文+补充、已发表层数消融重叠问题尚未闭环 |
| 论文第4章 | 旧fixed-15 A/B写作稿 | [chapter_04_results_integrated.tex](chapter_04_results_integrated.tex) | **未整合E3d/E5a/E5b**；不可当作已完成的正式结果节 |

## 真实原始审计文件溯源

- [Windows原六文件来源SHA256清单](AUDIT_EXPORT_20261122/SOURCE_SHA256.csv) 以及[完整导出对照表](AUDIT_EXPORT_20261122/README.md)：六份原审计CSV/JSON从用户ZIP逐字节保留，GitHub提交后远端7/7复核成功。
- E3d：完整48项审计表及原审计JSON，**无人工标签ARI/NMI**。
- E5a：完整288项基线审计表包含每个seed/切片/method/K臂对应的 `ari_recomputed`、`nmi_recomputed`，没有删负结果；审计JSON `checked=288`、`errors=[]`、warnings见原件。
- E5b：原审计JSON `phase1=passed`、`phase2=passed`、`verified_predictions=360`、`all_metrics_count=360`，其`files_sha256`与当前GitHub三份结果CSV全部匹配。E5b原先已上传的8份报告和图表加上此次JSON现为9份数据/分析文件。
- GitHub**仍不含**所有原始10x counts、360/288源预测任务目录和原reference-only标签文件；源文件SHA+报告可以确认内部完整性声明，不等价于在GitHub重放模型拟合或从头计算所有ARI/NMI。

## 方法学红线

1. **独立生物重复：** DLPFC仅3名供体，Wu乳腺癌仅6名患者。切片、spot、seed、模型文件数量不是独立生物学n。
2. **冻结实验和事后分析必须分开：** 2026-11-21 E5b原方案为冻结运行协议；用户看到CSV后产生的新主要对比、bootstrap或显著性分析仅能作为事后补充，禁止冒称此前预注册。
3. **K-blind和Oracle-K必须分开**。前者对标签盲，后者用参考类别数选K；Oracle-K也不保证ARI/NMI较高。
4. **跨方法预处理不同**：GMM/Leiden共享scVI 5D、BANKSY/BayesSpace原生counts；有框架和K选择差异，不能宣称完全相同输入和预算的严格公平对照。
5. **负结果不能删除**。E5b A15D相比L0虽在六患者正向，但相对BayesSpace的NMI宏均值为负，且跨患者表现差异明显。不得仅挑选最优方法、最有利seed或评价mask做论文结论。
6. **新颖性仍未证实**。不能把CellCharter已有的多层邻域聚合说成原创新算法；正式科研投稿需精读原方法全文与Supplement，判断本项目属于复现/参数敏感性/外部评估的哪类可发表贡献。

## 最新下一任务（不必继续训练）

- **Claude现在可以直接读取全部GitHub派生定量结果**：从[独立审查入口](CLAUDE_INDEPENDENT_REVIEW_BRIEF_20261122.md)出发，复核三阶段真实CSV、选K边界、作者算法与最接近论文的重叠。不能再沿用“E3d/E5a/E5b原审计CSV未提交”的旧结论。
- 后续如需E3d后验ARI/NMI，须基于Windows冻结的原预测与真实参考标签单独执行**只读后验分析**，标注该分析时间点、不重训或扩K。
- 若SCI定位要求边界容差/真实机制证据，再对E3b范围作有约束的补充分析决定，或如实写“未评估”。
- E4图件归档与第四章更新是**论文整理工作**；当前完成GitHub归档不等于论文可直接投稿。
