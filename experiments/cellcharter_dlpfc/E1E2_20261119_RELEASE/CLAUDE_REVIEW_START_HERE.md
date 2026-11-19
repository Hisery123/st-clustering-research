# Claude独立科研评审：只看本项目的CellCharter DLPFC第三篇（严禁跨课题）

## A. 研究范围（强制）

你只研究这一个实验：**CellCharter空间转录组DLPFC聚类：12切片E1/E2冻结多尺度GMM对照，以及后续E3–E6扩展实验与论文Experiments章节**。

**请不要查阅、分析或使用本GitHub仓库中其他STAGATE项目、CAN-N、CTW-RF、CARR、细胞反卷积、综述、游戏项目等研究内容。** 这些是完全不同的工作，即使全局`AGENTS.md`、历史`PROJECT_STATE.md`提及它们，也只读取与你当前CellCharter项目直接相关的段落。不要把其他实验结果算到这1200项里。

此处仅审查**已经完成E1/E2的一项实验**，不是重新选择其他硕士课题，也不是让你接管Windows训练。独立思考并批评ChatGPT已有结论可以，但不得篡改证据。

## B. 必读证据（只按下列路径研究）

1. `AGENTS.md` — 仅读通用科研严谨性和用户手动操作原则；跳过其他课题章节。
2. `experiments/cellcharter_dlpfc/THIRD_PAPER_E1E2_FROZEN_GMM_PROTOCOL_20261113.md` — 精确十种配置、十seed、Oracle-K、评估方法及泄漏限制；此文件有历史阶段说明，勿以“尚未运行”的旧文字覆盖最新结果。
3. `experiments/cellcharter_dlpfc/THIRD_PAPER_FULL_EXPERIMENT_EXPANSION_DECISION_20261112.md` 和 `THESIS_FIRST_RESEARCH_CHARTER_20261110.md` — 目标、已确认的实验建议1。
4. 本归档 `derived/审查报告.md` + `derived/audit.json` + `derived/all_1200_tasks.csv` + `derived/all_120_condition_stats.csv` + `derived/all_600_seed_paired.csv` + `derived/all_60_paired_stats.csv` + `derived/sample_metadata.csv`；供体标签仍需原始metadata核实。
5. 本归档 `archives/e1e2_12slices_statistics_20261119_095251.zip`：每张切片4 CSV+provenance.json，确认它们如何生成；可用`derived/recompute_zip_audit.py`复核。
6. 本归档 `scripts/e1e2_multiscale_gmm_task.py`、`scripts/e1e2_safe_batch_runner_v2.py`、`scripts/e1e2_aggregate_multiseed_v2.py`、`scripts/e1e2_overnight_remaining_slices_v1.py`。**仅静态审阅，不运行训练**；这是当时交付脚本的快照，不代表实时Windows文件状态。
7. `RESEARCH_JOURNAL/2026-11-19.md`的CellCharter实验段落（真实夜间1200格完成日志）。

在回复中列出**实际打开过**哪些文件。如果你无法读取ZIP或某个文件，明确指出并依据已读CSV做有限审查，不能声称完成原始预测重算。不要为了补上下文去搜索无关目录。

## C. 已核实的起始事实

- 1200/1200个冻结切片×配置×seed任务在Windows已完成，上传统计ZIP字节SHA、聚合、配对数据一致。12片仅3名供体；GMM seed是算法重复；151669–151672 Oracle-K5、其他K7，K来源人工标注。
- fixed15D(L0+L1+L4) vs 15D标准(L0+L1+L2)的平均差：ARI 7/12切片正、5负，均差约+0.003282；NMI 9/12正、3负，均差约+0.010867；151674/151675明确负效应。供体异质性明显，但供体分组需原metadata证实且K5/供体2混杂。
- 没有一个同15D替换在12片的ARI与NMI上都全正。累计25D与15D不等维，特征维度/尺度同时变化。**尚无已证明普遍改进的新方法**。
- 12片E1/E2都已被看过，未来候选方法需要预冻结外部数据独立测试；不得将探索集改写为盲测。
- 后续E3 K敏感性和AutoK、空间边界F1、E4空间和marker、E5公平基线与独立外部验证、E6可选自适应机制、论文写作尚未完成。

## D. 请独立提出完整、具体、可证伪的方案

**1. 当前结果能支持的核心科学问题：** 只围绕CellCharter DLPFC多尺度聚类，给2–3条Research Questions（RQ）、竞争解释、可反驳证据。提出至少一个反对继续做自适应方法的强论点。别仅因参数扫描数量多而认定创新。

**2. 后续实验E3–E6的执行表：** 对每个任务写明实验目的、输入文件、预冻结参数（包括与K相关的设置）、模型是否需要重拟合、基线公平性、独立单位、输出CSV/SVG、数值判据、失败记录、停止/放弃条件、真实硬件预算（Windows 4070 Laptop 8GB，CPU串行安全运行）。特别说明能从已保存预测直接算的空间边界/可视化和必须重新拟合的K敏感性分开。不要伪造有结果的CSV。

**3. 基线及最近邻文献：** 只找与CellCharter空间聚类尺度选择直接有关的最近邻3–5篇文献/方法，提供可核查标题/作者/年份/DOI及代码，区分本研究的事实与文献作者报告。**STAGATE若仅是一个可能的公平基线，可以评价它作为发表过的方法，但严禁读取本仓库的其他STAGATE复现项目与历史结果。**

**4. 统计推断及避免泄漏：** 区分3供体、12切片、1200 GMM任务、spots、seeds。供体/K混杂；如果供体ID无法确认，列出核实数据源步骤。不要对10seed做生物学推断或凭12slice做显著性结论；不要伪造P值、置信区间或“显著”。

**5. 如何写成毕业论文及SCI Experiments：** 先给详尽中文章节结构和证据对照表，包括Datasets、Preprocessing/Features、Methods与公平Comparators、Experimental Settings、Metrics（ARI/NMI及拟补边界F1）、Results（E1/E2已完成）、Sensitivity、Spatial case studies、Ablations、Limitations、独立验证。针对已完成数据**写2–3段可以直接用的克制结果文字**，给主表与至少4幅可编辑SVG图的具体数据字段、目的、图注和放置位置。**未做实验用TODO占位，严禁用假数据写满。**

**6. 推荐GO/STOP：** 分别给毕业章节可行性与普通SCI增量方法论文可行性，指出至多3个最高优先级的致命风险，列出最省成本解决路径。不要为追新无限刷seed，也不要因为负结果就建议放弃有价值的实证章节。

## E. 输出格式和合作方式

先用一段话给两个目标的GO/条件GO/STOP。接着给P0/P1问题、按依赖关系排序的E3–E6逐项实施表（可分几周）、Experiment章节结构（已完成vs待做）、图表证据映射、可信文献表，最后给**一个最优先的下一实验动作**。不要直接运行脚本、没有必要别让用户手动跑无关STAGATE训练。你负责第二意见与论文写作规划；用户在Windows手动执行；ChatGPT后续对方案做数据/代码一致性复核。
