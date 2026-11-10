# 科研工作交接 / CURRENT RESEARCH HANDOFF
> 更新：2026-11-10（基于本仓库已保存的原始实验文件、当日PowerShell输出与用户确认的研究约束）
> **新对话入口：** 先阅读本文及文中链接到的实际脚本、`config.json`、`metrics.json`。本文是工作索引，不代替原始数据和日志。

> 后续执行补记（2026-11-10）：L3 聚合与GMM已完成，初次边界评价因 `L5` 与真实标签 `Layer 5` 不符而失败；随后使用本地已保存的 predictions.csv 成功恢复指标：ARI 0.4696960563，NMI 0.5850783791，边界 F1 0.1360448808，L5/L6 Recall 48/145。结果已由终端输出转录归档至 [L3指标](experiments/cellcharter_dlpfc/snapshot_20261110/results/cellcharter_v032_151507_seed22911_L3_diagnostic/metrics_recovered.json)，尚未取得原始预测CSV及本地文件哈希。本文下方“L3未执行”等文字是早先状态，应以此补记为准。

## 0. 一句话结论与当前阶段

**第三篇空间转录组聚类方法论文**以成熟开源方法 **CellCharter** 作为当前母体。2026-11-10已完成 DLPFC 151507 的 CellCharter v0.3.2 **单切片、单随机种子、Oracle-K=7** 正式基线，并使用**相同 scVI 表征**完成 L0/L1/L2/L4 邻域聚合深度诊断。L4 的整体 ARI 最高，但深层组织边界（尤其 L5/L6）检出率很低。这是**探索性现象/候选科学问题**，不是已证实的过度平滑机制，也不是已成立的创新点。

**目前下一步：补做 L3 深度诊断；随后固化全部对照脚本、跨随机种子和跨切片验证，并审查最近邻文献。** 不要跳过证据审查直接开发“创新模块”。

## 1. 用户与协作方式（新对话优先遵循）

- 用户本人负责在 **Windows 11 + PowerShell** 上实际运行、检查硬件/文件；ChatGPT 负责方法批判、实验设计、查看日志/CSV、审查统计、编写/修订代码与论文、可编辑矢量科研绘图。
- **默认不使用 Codex 或远程控制用户电脑**。运行本地任务时一般只给一个可复制的 PowerShell 命令/短步骤，解释目的、预期输出、失败处理，并等待真实反馈；**但对于 GitHub 归档/文档维护等用户已授权的仓库操作，请直接使用已连接的 GitHub 工具，不要反复让用户执行琐碎 Git 命令**。
- 研究原则：真实执行结果、推断、论文报道、假设与计划分开；负结果完整保存；不伪造论文、实验、分数、设备状态；不把 spot、空间边、随机种子当独立生物学重复；先核对标签是否泄漏。
- 研究项目路由规则：优先读用户项目来源 `01_科研双Skill总控.md` / 2026-11-07 的 `01_科研双Skill总控_v1.1.md`，以及与此任务相关的 `04_成熟基线驱动增量创新_SKILL_v1.2.md`；未实际读取的上游 Supervisor-Skills 或 Nature-Skills 原始 `SKILL.md`，不能声称执行过其完整规则。
- 用户希望尽量使用高可信、可审计、已出版的强方法作为母体；具体期刊/团队偏好在上述项目规则。**原创性审查不得排除真正最相似的已有工作**。

## 2. 仓库与本地文件位置

- **本仓库（Private）：** https://github.com/Hisery123/st-clustering-research
- 当前提交归档：2026-11-10 `snapshot_20261110`（GitHub 提交 `4bd34502fd3522a0b753c75dd7baa99ecba791f0`）。
- 正式基线脚本： [scripts/cellcharter/cellcharter_151507_baseline_v032.py](scripts/cellcharter/cellcharter_151507_baseline_v032.py)
- 当日实验目录：[experiments/cellcharter_dlpfc/snapshot_20261110/results/](experiments/cellcharter_dlpfc/snapshot_20261110/results/)
- 当日较早的原版脚本/历史 seed0 冒烟、跳数消融、固定25维置乱对照等，另见 [experiments/cellcharter_dlpfc/](experiments/cellcharter_dlpfc/) 的 2026-11-08/09 日志；**不要将历史 seed0 结果与本次 seed22911 直接混成同一次实验**。
- Windows 本地训练根目录：`D:\paper\CellCharter_reproduction`
- Windows 本地 Git checkout：`D:\paper\st-clustering-research`
- Windows 本地数据目录：`D:\paper\ST_Benchmark_Planning\mvp\data\151507`
- Python：`D:\paper\CellCharter_reproduction\env_cellcharter\python.exe`（Python 3.10.22）
- 原始表达矩阵：`...\151507\filtered_feature_bc_matrix.h5`；原始坐标与标签：`spots_aligned.csv`、`manual_layer_annotations.csv`。
- 2026-11-10 归档时**没有上传**本地虚拟环境、scVI 模型、`scvi_latent.npy`、`cellcharter_aggregated.npy` 和原始 H5；复跑/复用特征仍需本地文件。GitHub 仓库提供脚本、配置、指标、CSV预测、日志等可核实的文本/小文件。
- **尚需补齐：** 2026-11-10 L0/L1/L2及边界诊断当时以聊天中 PowerShell 内嵌 Python 运行；虽然结果/预测已保存，尚不能假设 GitHub 已有与这些结果逐字一致的独立、可执行 `.py` 脚本。应将它们固化并标记来源，不能以旧 `hop_ablation_v1.py` 冒充本次完整脚本。

## 3. 151507 数据审计与正式基线（已执行）

- 输入数据：4226 spots，原始 H5 33538 genes；基因名存在少量重复，使用 `var_names_make_unique()`；过滤后 18462 genes，`seurat_v3` 5000 HVG。
- 样本 151507 对应有效人工参考标注 **4221 spots**，其余 5 spots 无参考标签；原始注释表混入其他切片（尤其 151669），**必须先按 `sample_name == "151507"` 筛选，再按 barcode 对齐**；barcode 不能跨切片当全局唯一键。
- 利用 `array_row` 和 `array_col` 构建 Visium 六邻域六角图；空间坐标 `x=array_col`，`y=sqrt(3)*array_row`。已验证 24770 条有向边（12385 条无向边），零几何异常边、零非对称边，未发现孤立 spots。
- 正式管线：scVI（5维 latent；5000 HVG，raw count layer；AdamW，最多400 epochs、Early Stopping）→ CellCharter 4 层空间邻域聚合（25维）→ TorchGMM/GMM（K=7）。
- 随机种子 **22911**：作者 benchmarking 脚本的 `np.random.default_rng(12345).integers(0,32768,size=10)` 第一项。**仅完成这一项**，不是十次均值。
- 已执行正式 scVI GPU 训练：NVIDIA RTX 4070 Laptop GPU，日志 `GPU available: True (cuda), used: True`；第215个 epoch 触发早停，属于预期。GMM 使用 CPU，日志 `GPU ... used: False` 不是 scVI GPU 失败。
- 正式结果：[L4/metrics.json](experiments/cellcharter_dlpfc/snapshot_20261110/results/cellcharter_v032_151507_seed22911_oracleK7/metrics.json)：
  - **ARI = 0.4961464421378273；NMI = 0.6754358219165002**；
  - 共4226 spots 聚类，4221 spots计入外部评价，7个预测簇；
  - 预测簇大小 `[858, 387, 810, 955, 374, 494, 348]`。
  - 结果目录包含 `config.json`、`metrics.json`、`status.json`、`predictions.csv`、空间对照SVG等。
- **协议限制：** CellCharter v0.3.2 + TorchGMM，不是作者 v0.2.0 + PyCave 的完全同版本复现；使用原始10x H5 + 重建的物理邻域图，并非作者预处理 `.h5ad`；采用临时 Lightning/TorchGMM DataLoader 兼容补丁。故称“基于官方设置的适配版单种子基线”，不能宣称完全复现作者论文整体均值。
- **Oracle K**：K=7 来自人工标签类别数。这属于使用参考标签信息设定模型阶数，**不是纯无监督K选择**；评价标签除该K设定外不用于scVI/GMM训练。151507 是探索/开发切片，不是独立盲测集。

## 4. 当日 L0/L1/L2/L4 诊断结果（已执行，非论文最终结论）

四组**复用同一份 scVI latent**，保持 seed22911、K7，变动邻域聚合层数（同时改变GMM特征维度：5/10/15/25），分别重新拟合GMM。

| 聚合深度 | 特征维度 | ARI ↑ | NMI ↑ | 全局边界Precision ↑ | 全局边界Recall ↑ | 全局边界F1 ↑ | L5/L6边界Recall ↑ |
|---|---:|---:|---:|---:|---:|---:|---:|
| L0 | 5 | 0.362131 | 0.441915 | 0.101816 | 0.643158 | 0.175802 | 0.600000 |
| L1 | 10 | 0.444156 | 0.569587 | 0.097953 | 0.468421 | 0.162024 | 0.544828 |
| L2 | 15 | 0.457461 | 0.604740 | 0.083266 | 0.325263 | 0.132590 | 0.441379 |
| **L3** | **20** | **未执行** | **未执行** | **未执行** | **未执行** | **未执行** | **未执行** |
| L4 | 25 | **0.496146** | **0.675436** | **0.154561** | 0.192632 | 0.171509 | 0.000000 |

数据依据：GitHub 的 [L0](experiments/cellcharter_dlpfc/snapshot_20261110/results/cellcharter_v032_151507_seed22911_L0_diagnostic/metrics.json)、[L1](experiments/cellcharter_dlpfc/snapshot_20261110/results/cellcharter_v032_151507_seed22911_L1_diagnostic/metrics.json)、[L2](experiments/cellcharter_dlpfc/snapshot_20261110/results/cellcharter_v032_151507_seed22911_L2_diagnostic/metrics.json)、[L4](experiments/cellcharter_dlpfc/snapshot_20261110/results/cellcharter_v032_151507_seed22911_oracleK7/metrics.json)；L0/L4的全局边界数据及每对边界召回率另依据**本对话2026-11-10原始PowerShell输出**，后续应保存成可重复计算报告。

### 边界指标明确定义

- 在原始物理六邻域无向图中，仅保留两端均有人工标签的边；对每条边，真值两端类别不同=“参考边界”，预测两端簇编号不同=“预测边界”。
- 151507 所有真实层间参考边界共 **950** 条；各方法全局 TP/FP/FN：
  - L0：611 / 5390 / 339；
  - L1：445 / 4098 / 505；
  - L2：309 / 3402 / 641；
  - L4：183 / 1001 / 767。
- L5/L6界面共 **145** 条参考边界：L0 检出87条（60%）、L1 79条（54.48%）、L2 64条（44.14%）、L4 检出0条（0%）。
- L4其余参考边界召回：L1/L2 36.27%；L2/L3 34.44%；L3/L4 17.83%；L4/L5 1.87%；L6/WM 15.38%（均仅一切片一随机种子）。
- L0大量真实同层边也被拆开（例如L5内部错误分割率50.43%、L6内部61.97%）；L4对应10.01%、2.56%。因此**高边界Recall可能只是碎片化，必须同时评价Precision/F1、ARI与内部连续性**。
- L4的 L5/L6 跨层共聚类比例65.21%，L0为37.92%，但该统计亦受簇碎片化影响，不应单独当因果证据。
- 151507的多数投票映射可能把L6的召回率算成0，只因为Cluster 3中L5=463、L6=462，簇被映射为L5；**不表示没有任何L6 spot被分配**。多数投票Accuracy不等于一对一Hungarian ACC，论文应明确指标算法。
- **950条边/4221个spot≠950/4221个独立样本**；不能对它们做伪重复显著性推断。

### 当前可以与不可以声称什么

- **可以：** 这一切片/种子上，L4整体ARI/NMI最好；邻域聚合层数与整体质量/边界指标之间存在明显权衡；L2、L1没有优于L4的整体ARI或全局边界F1。
- **不可以：** 已证实“过度平滑是唯一因果机制”；已证实“边界自适应聚合”创新有效；原论文普遍失败；已有统计显著差异；跨切片泛化已完成。
- **关键混杂：** 聚合深度同时改变特征维度和GMM拟合输入/优化，必须设计固定维度、特征量等合适控制（仓库先前 seed0 `fixed25_permutation` 历史实验可审查，但不是自动替代本次验证）。

## 5. 尚未完成的事项与下一步优先级

1. **最近的下一项可执行工作：L3消融诊断（未完成）。** 复用本地 `results\cellcharter_v032_151507_seed22911_oracleK7\scvi_latent.npy`，用和L1/L2完全相同的原始坐标+六邻域构图、`cc.gr.aggregate_neighbors(n_layers=3,use_rep="X_scVI")`（期望4226×20维），TorchGMM K=7 CPU, seed22911；先保存prediction，再按151507样本筛选人工标注，仅用于评价ARI/NMI及边界Precision/Recall/F1。使用**全新不覆盖**结果目录 `results\cellcharter_v032_151507_seed22911_L3_diagnostic`。**新对话只给用户一个操作/一条命令，等真实终端反馈，禁止提前填数**。
2. **可复现性补课：** 将当日内嵌PowerShell的L0/L1/L2/L3及边界分析代码整理为可审计的 `.py` 文件、创建实验注册表（样本、seed、协议、聚合层、输出路径、状态），核对GitHub保存的指标与CSV可重算。新的脚本不得反向宣称“当时已经用该文件执行”。
3. **验证：** 固定预先约定的深度和方法比较，补随机种子、其它切片（例如151508），审查供体独立性与标签对齐；151508此前至少做过原始标签审计，**不可在未确认其历史用途前称其未碰过的独立测试**。不要把此切片上的最大ARI直接作为论文主结果。
4. **方法来源与创新审查：** 与CellCharter及真正最近的边界感知、自适应图聚合方法逐项比较；有必要时再提出小机制修改，并设置等维度、等预算及简单替代基线，保留负结果。当前CAN-N只称候选方案/拟创新点。
5. **论文与绘图：** 以可复核日志/CSV/SVG为源，检查生成图中的图例与层标签映射、人工标注的深度和空间方向；科研数据图使用可编辑SVG或可重复运行Matplotlib，不用生成式图片冒充数据。
6. **GitHub最新内容与本地同步：** 此交接笔记由ChatGPT直接提交GitHub；下次从本地Git仓库推送前应先`git pull --ff-only origin main`避免冲突（如需用户操作，再给单步命令）。

## 6. 直接给下一段GPT的工作指令（复制或让它读取本节）

**新对话请按以下顺序继续：**
1. 先从GitHub读取本文件、当日正式基线脚本及四个 `metrics.json`；仓库是 Private，需当前ChatGPT对该GitHub仓库具备访问授权。**仅有URL、未连接GitHub时不能假装读到了私人内容。**
2. 确认当前最新已完成实验仍是`151507 seed22911 L0/L1/L2/L4`，**L3尚未完成**，若GitHub有更新则以更新的原始文件和用户日志为准，明确差异。
3. 使用科研双Skill总控规则，保持独立标签/独立生物学单位/原始负结果审计。
4. **直接帮用户继续L3诊断**：准备一条适用 Windows PowerShell 的复制即用命令（可复用已有L2的逻辑），交代成功标记和报错处理，随后等待用户反馈；不要重新训练scVI，不要重新克隆仓库，不要让用户重复已解决的环境配置。
5. 之后评估 L0–L4 全深度扫描，再决定是否有必要做边界敏感的最小增量实验。**不先宣布论文创新点已经成立**。

---
**记录边界：** 本文是对截至2026-11-10现有证据的交接整理，不表示后续计划已执行，不表示所有上游Skill的完整文件已读取，也不表示所有本地模型/原始数据已备份到GitHub。
