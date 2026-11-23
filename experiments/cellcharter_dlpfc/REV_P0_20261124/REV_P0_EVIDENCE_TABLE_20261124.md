# REV_P0 证据对应表（2026-11-24）

**证据等级标记**

- **[原文]** CellCharter 原文：Varrone et al., *Nat Genet* 56(1):74–84 (2024)，PDF 由用户提供。
- **[补充]** 同文 Supplementary Information，10 页 PDF（`41588_2023_1588_MOESM1_ESM`），由用户提供。
- **[官方库]** `CSOgroup/cellcharter_analyses`，固定在 commit `fd63ac5585a3f18846a0891e120864179d4ca429`（2024-06-06）。相关文件已只读复制到 `official_cellcharter_analyses_fd63ac5/`，许可证为 MIT。
- **[本项目CSV]** 本仓库既有冻结结果文件，路径相对于 `experiments/cellcharter_dlpfc/`。
- **[REV_P0表]** `derived/T1–T8`，由 `rev_p0_derived_summaries_v1.py` 只读汇总得到；输入与输出的 SHA256 见 `derived/MANIFEST_SHA256.csv`。
- **[事后]** 该口径是在看过对应结果之后才定义的。

**关于 PDF 页码：** 原文 PDF 是按"每页一个内容流"的假设用文本抽取推定页码的，图中数字没有读取。Supplementary PDF 使用替换编码字体，助手按已知词表解码后阅读。**页码均为推定，引用时以图号、节名为准。**

---

## A. "原作者已做"与"本研究新增"的划分

| # | 判断 | 出处 | 证据限制 |
|---|---|---|---|
| A1 | 原作者在同一套 12 张 DLPFC Visium 切片上做过基准比较。 | [原文] Results，DLPFC 基准段落（PDF 约第 2 页）；Extended Data Fig. 1d | — |
| A2 | 原作者的调参集为 151507、151672、151673（每位供体随机选 1 张），测试集为其余 9 张；调参方式为网格搜索、每组参数 5 次重复、取平均 ARI 最大者；测试时每张切片重复 10 次，只评价 ARI；未标注 spot 参与聚类，但不参与评分。 | [原文] Methods "Benchmarking comparison of CellCharter with existing tools"及"Hyperparameter tuning"（PDF 约第 13–14 页）；Extended Data Fig. 1e/f | — |
| A3 | 原作者的 CellCharter 网格为：HVG {500,1000,2000,5000}→5000；潜变量维度 {5,10,15}→5；**邻域层数 {2,3,4}→4**。 | [补充] "Hyperparameter tuning: grid search"（推定第 2–3 页）；[官方库] `src/benchmarking/CellCharter/tuning.py` 第 23–25 行；[REV_P0表] T8 | 网格只覆盖 3 张调参切片、只评价 ARI。助手对官方 CSV 的汇总：在 HVG 5000、潜变量 5 维条件下，3 张切片均值最高的是 4 层（0.5249）。 |
| A4 | 在 HVG 5000、潜变量 5 维条件下，原作者网格中的 2/3/4 层分别对应本研究累计 15D/20D/25D。因此"2–4 层邻域影响 ARI"与原作者工作**重叠**。 | 由 A3 推出，并核对 `aggregate_neighbors` 的输出维度（本项目 `prepare_dlpfc_10_features.py` 第 173–176 行，25 维） | 本研究在 12 张切片 × 10 个 GMM 种子上重新比较，属于样本范围与重复结构上的扩展，不是新问题。 |
| A5 | 原作者 Results 写明比较时要求每个工具输出 7 个簇；但官方单切片脚本 `individual.py` 对 151669–151672 用 K=5、其余用 K=7，与本研究的 Oracle-K 相同。 | [原文] Results，"all comparisons were made requiring each tool to detect seven clusters"一句（PDF 约第 3 页）；[官方库] `src/benchmarking/CellCharter/individual.py` 第 16–28 行 | 原文正文与脚本的 K 设置存在出入，本研究不判断原文图件采用了哪一种。 |
| A6 | 原文的主要性能结论来自 9 张测试切片的**联合聚类**；在**单切片**聚类中，STAGATE 最好。 | [原文] Fig. 1d/e 图注（PDF 约第 3 页）；Extended Data Fig. 1g/h 图注（PDF 约第 17 页）；Results"Although STAGATE obtained the best cluster quality when clustering individual samples" | 图中数值没有读取，只依据图注和正文文字。 |
| A7 | 原作者的稳定性选 K 规则：在 DLPFC 12 张切片**联合**数据上，候选 2–20，重复 10 次，峰值 n=9；扩展到 42 张切片时仍为 n=9（另有 n=14）。BIC 的全局最小在 n=19，AIC 与 NLL 没有清晰拐点。原作者还做过 25 次重复的收敛检查。 | [原文] Results（PDF 约第 3–4 页）；Fig. 1h；Extended Data Fig. 2b；[补充] cluster stability 相关小节（推定第 3 页）；[原文] Methods "Cluster stability"（PDF 约第 12 页） | — |
| A8 | **本研究新增（原文与官方库均未见）**：<br>• 0 层（5D）与 1 层（10D）累计特征；<br>• 非连续等维 15D 组合（L0+L1+L3 等）；<br>• 12 张切片 × 10 个 GMM 种子的全网格；<br>• E3c 固定 K=5–9 网格；<br>• E3d **逐切片** AutoK 及其事后 ARI/NMI；<br>• E3b 严格与容差边界指标；<br>• E5a BANKSY/BayesSpace/GMM/Leiden 双 K 臂对照；<br>• E5b 乳腺癌 6 名患者外部复核。 | 依据：A1–A7 已列出原作者做过的全部相关内容；[官方库] 目录树（2026-11-24 列出）中 DLPFC 只有 tuning、individual、joint、joint_downsampled、labels、memory、time 几类结果 | 只核对了 CellCharter 原文、补充材料和官方库，**没有做全领域文献检索**；因此"本研究新增"只相对于 CellCharter 原作者成立。 |

## B. 复现对照（P0-1）：只能说明数值处于同一水平，不能称为严格复现

| # | 判断 | 出处 | 证据限制 |
|---|---|---|---|
| B1 | 12 张切片宏平均 ARI：官方 0.4438，本研究 25D 0.4418；9 张测试切片：0.4235 对 0.4244；3 张调参切片：0.5046 对 0.4939。 | [REV_P0表] T7；[官方库] `ARI_CellCharter_hvgs5000_nlatent5_nhoodlayers4_gpu.csv`；[本项目CSV] `E1E2_20261119_RELEASE/derived/all_120_condition_stats.csv` | 官方数值是作者发布的结果文件，本研究没有重跑。 |
| B2 | 逐切片差值从 −0.104（151672）到 +0.041（151673），只有 5/12 为正。 | [REV_P0表] T7 | — |
| B3 | 样本范围：两边都覆盖 12 张；原文图件只报告 9 张测试切片。 | [官方库] `individual.py`；[原文] Extended Data Fig. 1g 图注（"n = 9 samples"） | — |
| B4 | 聚类方式：两边都是单切片；原文的主结论来自联合聚类。 | 同 A6 | — |
| B5 | 预处理一致的部分：`min_counts=3` 过滤、归一化至 1e6 并取 log1p、HVG 5000（seurat_v3，计数层）、scVI n_latent=5、AdamW + early stopping + reduce_lr_on_plateau、4 层邻域。 | 本项目 `scripts/cellcharter/prepare_dlpfc_10_features.py` 第 138–176 行；[官方库] `individual.py` 第 39–65 行 | — |
| B6 | 已知差异：<br>• 种子：官方每次同时更换 scVI 与 GMM 种子；本研究 scVI 固定 22911，只更换 GMM 种子。<br>• scVI 轮次上限：本研究 400，官方为默认值。<br>• GMM：本研究在 CPU 上运行，容差 1e-3、正则 1e-6、最多 100 epoch；官方为默认参数，GPU。<br>• 输入文件：本研究为 10x h5 + `spots_aligned.csv`；官方为 HumanPilot 预处理 h5ad。<br>• 标签字段：本研究为 `layer_guess`；官方为 `sce.layer_guess`。<br>• 软件版本：官方未核对。 | 同 B5；E1/E2 的 GMM 参数见第三章第 3.5 节 | 双方的包版本未逐一比对。 |
| B7 | 技术种子 SD 的含义不同：官方单切片平均 0.051（scVI + GMM 都变），本研究 25D 平均 0.028（只有 GMM 变）。 | [REV_P0表] T7 | 不能据此说本研究流程"更稳定"。 |

## C. B15D（P0-2）

| # | 判断 | 出处 | 性质 |
|---|---|---|---|
| C1 | B 是在 151507、种子 22911、Oracle-K=7 条件下看到 ΔARI=+0.0472 后提名的。 | [本项目] `MVP_FIXED15_BLOCK_SWAP_151507_SEED22911_20261110.md`（内容为终端输出转录） | 开发集 |
| C2 | 151507 与 151508 都是开发阶段已分析过的切片。 | `FIXED15_10_SECTION_GMM_20261110_FIRST_RESULTS_ARCHIVE.md` 第 24 行 | — |
| C3 | 12 张切片：ΔARI +0.0033（7/12 为正），ΔNMI +0.0109（9/12）。 | [本项目CSV] `E1E2_20261119_RELEASE/derived/B_vs_A_12slices.csv`；[REV_P0表] T2 | 预设 |
| C4 | 排除 151507/151508 后的 10 张切片：ΔARI −0.0035（5/10），ΔNMI +0.0086（7/10）。 | [REV_P0表] T2 | **事后** |
| C5 | 按供体：D1 +0.0393（4/4），D2 +0.0034（2/4），D3 −0.0328（1/4）。 | [REV_P0表] T2 | 描述 |
| C6 | 120 个"切片×种子"配对中 59/120 为正；种子 22911 下新增 10 张切片 ΔARI −0.0256（3/10）。 | [本项目CSV] `all_600_seed_paired.csv`；[REV_P0表] T2 | 种子不是生物学重复 |
| C7 | E5b K-blind：ΔARI −0.0364（1/6），ΔNMI −0.0236（2/6）；Oracle-K：ΔARI +0.0161（4/6），ΔNMI +0.0111（4/6）。 | [本项目CSV] `E5B_20261122_RELEASE/derived/patient_paired_effects.csv`；[REV_P0表] T2 | 预设 |

## D. 严格边界 F1（P0-3，整节均为事后分析）

| # | 判断 | 出处 |
|---|---|---|
| D1 | 0-hop F1：5D 0.1441，**10D 0.1446（略高）**，15D 0.1361，20D 0.1344，25D 0.1179。 | [本项目CSV] `E3B_E1E2_1200_POSTHOC_20261122_RELEASE/derived/macro_mean_30.csv`；[REV_P0表] T3 |
| D2 | 0-hop precision 在 0.086–0.111 之间；recall 从 0.494 降到 0.141。 | [REV_P0表] T3（由 `all_3600_boundary_metric_rows.csv` 先按切片内种子平均，再按切片等权平均） |
| D3 | 预测边界边数与参考边界边数之比：5D 为 6.42，25D 为 1.41；参考边界边数平均为 830。 | [REV_P0表] T3 |
| D4 | 本研究没有构建零模型；参考标注的边界不确定性也没有在本数据上量化。 | 限制 |

## E. 深度效应与不确定性（P0-4）

| # | 判断 | 出处 |
|---|---|---|
| E1 | 5D→10D 的 ARI 提升在 12/12 张切片上为正。 | [本项目CSV] `all_120_condition_stats.csv`（助手逐切片核对） |
| E2 | 6/12 张切片 25D < 15D，6/12 张切片 20D < 15D；D3 的 ARI 为 15D 0.4648、20D 0.4587、25D 0.4480。 | [REV_P0表] T1 |
| E3 | 切片间 SD 为 0.060–0.072；切片内 GMM 种子 SD 为 0.023–0.037。 | [REV_P0表] T1 |
| E4 | E3c 每个 K（5–9）下，宏平均 ARI 都满足 25D > 20D > 15D > 10D。 | [本项目CSV] `E3C_20261120_RELEASE/e3c_macro_K_depth_20groups.csv` |

## F. AutoK（P0-4/P0-5）

| # | 判断 | 出处 |
|---|---|---|
| F1 | 本研究每个候选 K 做 5 次稳定性重复（种子 22911–22915），逐切片运行；原作者为 10 次重复、联合运行，并另做过 25 次重复的收敛检查。 | `E3D_AUTOK_FROZEN_PROTOCOL_20261120.md`；同 A7 |
| F2 | 选中 K 与参考类别数相同的情况，每个尺度下都只有 1/12；|K − 参考类别数| 的平均值为 1.58–2.83；共有 10/48 次命中边界（K=2 出现 9 次，K=10 出现 1 次）。 | [REV_P0表] T4 |
| F3 | 20D 在 D2 中的 ARI 最低（10D 0.370，15D 0.396，20D 0.357，25D 0.399）。 | [REV_P0表] T4（**事后**评分） |

## G. 基线公平性（P0-5）

| # | 判断 | 出处 | 证据限制 |
|---|---|---|---|
| G1 | 本研究冻结的 BayesSpace K-blind 规则是"qTune q=2–10，取平均伪对数似然最大"。 | `E5A_FROZEN_FAIR_BASELINE_PROTOCOL_20261120.md` 第 24 行 | — |
| G2 | BayesSpace 官方建议在 qPlot 曲线的 elbow 附近选 q。 | Bioconductor vignette（2026-11-24 访问） | 没有核对 1.20.2 版本对应的 vignette 文本。 |
| G3 | BayesSpace 命中 q=10 的次数：DLPFC 28/36，E5b 18/18。 | [REV_P0表] T5（`all_288_prediction_checks.csv`、`all_360_prediction_metrics.csv`） | — |
| G4 | **新发现**：GMM 的 BIC 规则在 DLPFC 命中 K=10 共 32/36 次，在 E5b 共 8/18 次。 | [REV_P0表] T5 | V1 正文没有报告这一点。 |
| G5 | 本研究 BayesSpace 设置为 HVG 2000、PC 15、model=t、nrep 10000；原作者设置为 HVG 1000、PC 15、γ=3、nrep 5000。 | `E5A_FROZEN...md` 第 12 行；[补充] 网格；[官方库] `individual.R` 第 19–22 行 | γ 在本研究中为默认值，没有逐版本核对。 |
| G6 | STAGATE 不在本研究对照集中；官方单切片结果中 STAGATE 的 12 切片宏平均为 0.5186。 | [REV_P0表] T7 | — |
| G7 | E5b Oracle-K 下 A15D 的 ARI 为 0.1916，低于 BayesSpace（0.1981）与 Leiden（0.1959）；K-blind 下 BayesSpace 的 NMI（0.2970）是所有方法中最高的。 | [本项目CSV] `patient_three_seed_summary.csv`；[REV_P0表] T5 | — |
| G8 | 在 ARI < 0.05 的 3 名患者中，A15D 相对各对照的 ΔARI 为 0.002–0.028；这些患者内 3 个种子的 SD 为 0.008–0.011。 | `patient_paired_effects.csv`；[REV_P0表] T6 | — |

## H. 文献与归档（P0-6、P0-7）

| # | 判断 | 出处 |
|---|---|---|
| H1 | CellCharter 作者：Marco Varrone、Daniele Tavernari、Albert Santamaria-Martínez、Logan A. Walsh、Giovanni Ciriello；*Nat Genet* 56(1):74–84。 | [原文] PDF 首页；Europe PMC PMID 38066188 |
| H2 | sun2026 的期号为 9。 | Europe PMC 记录（2026-11-24） |
| H3 | STAGATE（Nat Commun 13:1739, 2022）与 Fowlkes–Mallows（JASA 78:553–569, 1983）的著录信息。 | [原文] 参考文献第 32、45 条 |
| H4 | E4 的 36 张 PDF 已归档（commit `110b7e19`）；39 页 V2 预览已归档（commit `bb730c2a`）。 | `PROJECT_STATE.md` 第三、七节（助手本轮未重新核验远端对象） |
