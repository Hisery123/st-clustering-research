# CellCharter 第三篇：结果归档状态总表（2026-11-22，审稿人入口）

> **用途**：区分本机真实运行成功、GitHub是否存在可复算的结果原件、论文阶段是否可作定量论断。本表是归档状态表，不是“实验全部完成即具备SCI创新性”的证明。

## 当前仓库对应的工作

| 阶段 | Windows执行/审计证据 | GitHub实际数据 | 可据此检查什么 | 未解决 |
|---|---|---|---|---|
| E1/E2 DLPFC | 阶段审计记录已归档 | [E1E2_20261119_RELEASE](E1E2_20261119_RELEASE/)：含全任务CSV、审计、配对统计、脚本和SVG | 旧12切片3供体实验完整结果 | 与E3d后验选K主线不可混同 |
| E3c K敏感性 | 真实运行记录与说明 | [E3C_20261120_RELEASE](E3C_20261120_RELEASE/)：含`e3c_newK_metrics_1920.csv`、分层K表、CSV和SVG | 冻结K下10/15/20/25D结果及负结果 | 不得把固定K视为无标签选K |
| E3d K-blind AutoK | 用户Windows报告48/48审计PASS，边界10/48 | 只有协议、脚本、[E3D_FINAL_AUDIT_PASS_20261120.md](E3D_FINAL_AUDIT_PASS_20261120.md)与K表，**没有完整48行审计CSV** | 可审算法/事前K决策、已知K值 | 请补本机审计CSV+JSON；尚未完成后验ARI/NMI |
| E4 空间图 | Windows最终审计PASS的文档证据 | 脚本、图示计划及审计成功记录 | 可审计执行宣告和可视化生成过程 | 原始本机图件是否归档尚未逐图核对 |
| E5a DLPFC四成熟基线 | 用户Windows报告288/288审计PASS | 协议/四基线脚本/[E5A_FINAL_AUDIT_PASS_20261121.md](E5A_FINAL_AUDIT_PASS_20261121.md)，**未上传小派生CSV和审计JSON** | 可核预冻方法、运行和审计程序 | 请补全288任务/方法描述性CSV与审计JSON |
| E5b Wu2021乳腺癌外部六患者 | 用户Windows报告360/360预测+360/360后验指标、独立审计PASS | [E5B_20261122_RELEASE](E5B_20261122_RELEASE/)：**8份真实CSV/报告/作图源文件/SVG已核SHA归档**；含manifest | 360行全部ARI/NMI、120患者汇总、144患者配对，报告正负结果 | 尚缺本机`audit_report.json`及原360预测CSV/labels；GitHub本身无法仅由派生CSV重算标签级ARI |
| E3b 边界容差 | 无预定全量运行成功记录 | 仅有旧单片诊断/计划 | 无法视为完成 | 明确未做或按之后单独定义的补充分析处理 |
| 最近文献/创新性 | 初步文献报告已写 | [LITERATURE_EVIDENCE_AND_NOVELTY_20261111.md](LITERATURE_EVIDENCE_AND_NOVELTY_20261111.md) | 可以了解目前已有工作重叠风险 | CellCharter原文及补充材料的逐项尺度消融重叠审查尚未闭环 |
| 正式论文第4章 | 旧固定A/B稿 | [chapter_04_results_integrated.tex](chapter_04_results_integrated.tex) | 历史草稿 | **尚未整合E3d/E5a/E5b真实数值，不可当最终版** |

## E5b最可靠的当前定量证据

- 直接读取[all_360_prediction_metrics.csv](E5B_20261122_RELEASE/derived/all_360_prediction_metrics.csv)、[patient_three_seed_summary.csv](E5B_20261122_RELEASE/derived/patient_three_seed_summary.csv)、[patient_paired_effects.csv](E5B_20261122_RELEASE/derived/patient_paired_effects.csv)；**所有正负患者/配置/种子原始行都保留**。
- E5b文件的SHA256、byte size、来源Windows审计会话详见[manifest.json](E5B_20261122_RELEASE/manifest.json)，三份CSV经本对话直接验证哈希，GitHub上传后又逐份远程读取重新校验；报告与三张SVG为观测结果**之后**生成的描述性输出，见README。
- 六患者才是独立生物学重复n=6，技术seed≠独立患者；DLPFC12片来自3供体，不能将12切片当12独立生物学重复。
- E5b原冻结的K-blind规则属于事前方案；2026-11-22读取数据之后新设主要比较/置信区间均为**post-hoc**，不能倒填在事前实验协议里。
- E5b BayesSpace qTune选Kblind在18/18次落于搜索上界K=10，需保留边界说明，不能偷偷扩K。跨方法表达特征不完全相同，不宣称全面公平同预算。
- **GitHub有8份完整E5b派生材料，并不等于有六患者的原始10x矩阵、360预测文件或用户Windows上原审计JSON。**

## 优先级顺序（按已有工作补证据，不新跑模型）

1. **P0**：上传E3d的`all_48_autok_audit.csv`、`audit_report.json`及E5a的`all_288_prediction_checks.csv`、`method_regime_descriptives.csv`、`e5a_phase_audit_report.json`，以及E5b的`audit_report.json`。保留本机原文件与SHA，不覆盖旧实验目录。
2. **P1**：将E3d的无标签选K拟合结果与人工标注进行独立后验ARI/NMI评价（如果尚未执行，须清楚列为**待做的新后验分析**，不是E3d冻结运行内容）；E5a原生各对照完整数值公开后按3供体处理。
3. **P1**：逐条核实Varrone et al.原文及补充材料中尺度敏感性/benchmark重叠；定义论文是方法学评估、复现分析或新算法主张，不得预设后者成立。
4. **P2**：E3b未完成则直接写入局限；要补做须独立报告分析时间点和是否看过相关结果。E4原始图件及第四章修订作为后续工作。
5. 全部原件归档后再让Claude根据本索引读取**实际CSV而不是只读PASS日志**做独立同行评阅。

## 原始记录优先与修订规则

此索引只引用已能定位的GitHub材料和用户此前Windows日志，不替代本机原始完整文件。旧文档里“未上传E5b CSV”的陈述在当时为事实，**从本归档提交开始已失效**。任何后续加入的文件均记录来源SHA、生成脚本、Windows原目录、统计单位和上传日期；禁止挑选性上传。仅提交派生CSV和可分享代码/图件，原始数据/模型大文件不自动公开。
