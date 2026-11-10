# CURRENT_RESEARCH_HANDOFF · 第三篇空间转录组聚类论文

> **2026-11-10 文献核查新进展**：已核实 CellCharter 原文/官方邻域拼接 API、AugGCL 2026 PLOS 原文 NIA 表达-邻域相似度加权、CodaST 出版方摘要 LSWC、HarveST PMC 全文及 GATCL/TRACER 的摘要；详见 [第一轮最近邻审计](experiments/cellcharter_dlpfc/NEAREST_PRIOR_ART_AUDIT_20261110_V1.md)。**STOP：**不得将单纯表达相似性加权邻接或 GAT 注意力包装成独创。**条件 GO：**先审查多尺度特征块与 GMM 可分性影响的最小、可证伪机制对照（非新算法）。AugGCL GitHub 代码含根据每epoch ARI选择最佳结果的片段，但尚未证实其用于论文151507的报告值。当前无需 Windows 操作，不自动恢复已暂停的历史 GMM 排查。下方早期“下一步查 GMM”均为旧记录。


> **2026-11-10 用户最新科研决策（优先于下文旧待办）**：停止追查历史两份 seed0 L4 GMM 不一致，根因未明，暂存为局限；**禁止自动继续预测对齐、RNG、重复拟合诊断**。转入 S2/S3：对 CellCharter 边界/连续性权衡作最近邻论文原创性审查，再决定单一最小机制。初步检索与源链接：[研究转向记录](experiments/cellcharter_dlpfc/RESEARCH_PIVOT_AND_PRIOR_ART_SCREEN_20261110.md)。后文涉及“下一步继续查 GMM”的句子是先前历史状态，现已失效。


> 最后整理：2026-11-10。**跨对话读档顺序：** [AGENTS.md](AGENTS.md) → [PROJECT_STATE.md](PROJECT_STATE.md) → [最近科研日记](RESEARCH_JOURNAL/2026-11-10.md) → 按需审查本文件和对应实际实验代码/结果。此文件是交接索引，不是原始证据。历史实验完整记录在 `experiments/`。

## 当前最新路线（2026-11-10，覆盖所有下方历史待办）

**用户确定将论文策略调整为普通SCI毕业目标下的成熟基线、小幅增量、低成本MVP**：已完成 CellCharter adapted 151507 seed22911 L0–L4 与边界审计；立即进入**多尺度块的只读预检**，随后由数据决定是否开展一项最小固定25维校准对照。停止追查历史 seed0 GMM 不一致，停止无限期文献排查；最近邻文献以3–5篇最相似为先。当前所有加权/校准方案均未执行、不是创新成果；151507只能当开发切片，不能把大范围尝试后的幸运值当独立测试。

- 最新研究策略：[MVP 增量计划](experiments/cellcharter_dlpfc/MVP_INCREMENTAL_RESEARCH_PLAN_20261110.md)
- 新预检脚本：[多尺度块只读预检](scripts/cellcharter/preflight_multiscale_blocks_151507.py)
- **下一个唯一操作：** Windows 本地 `git pull --ff-only` 同步 GitHub（已有 Clash 7897 代理成功方案）；用户汇报成功后，单独运行预检，不要同一回合给两条命令。
- 实验终端还没有运行新预检，不能填预检结果。下方任何“继续查历史 GMM”的旧表述是历史记录，不是当前任务。更简明准确的现状以 [PROJECT_STATE.md](PROJECT_STATE.md) 为准。

## 一句话状态

当前母体为 **CellCharter v0.3.2 适配版**。DLPFC **151507、seed22911、Oracle-K=7** 的基线及 L0–L4 五档空间邻域深度诊断均已完成；统一边界审计及逐层边界分析也已运行。**当前优先执行多尺度特征块的只读预检**，不重复 L3，也不再主动排查历史 GMM。

## 研究者与助手分工

- 用户使用 Windows 11 / PowerShell **手动执行本地实验**。助手负责方法审查、代码设计、文献、统计、可编辑绘图、科研写作，并经授权直接维护本私人 GitHub 仓库。
- 本地操作一次仅给一条命令或一个短操作，交代目的、成功标记、失败处理，等待终端真实结果；不默认使用 Codex 或远程操作用户电脑。
- GitHub 可直接编辑不等于助手能访问 Windows 本地任何文件；**不得假称本地未上传的文件已核验或已备份**。GitHub 更新后用户本地 checkout 需另行同步。

## 原始文件与实验环境

- 私人仓库：https://github.com/Hisery123/st-clustering-research
- Windows 训练根目录：`D:\paper\CellCharter_reproduction`
- Git checkout：`D:\paper\st-clustering-research`
- 数据目录：`D:\paper\ST_Benchmark_Planning\mvp\data\151507`
- Python：`D:\paper\CellCharter_reproduction\env_cellcharter\python.exe`
- 正式 L4 基线：[代码](scripts/cellcharter/cellcharter_151507_baseline_v032.py)、[配置](experiments/cellcharter_dlpfc/snapshot_20261110/results/cellcharter_v032_151507_seed22911_oracleK7/config.json)、[指标](experiments/cellcharter_dlpfc/snapshot_20261110/results/cellcharter_v032_151507_seed22911_oracleK7/metrics.json)
- L3 后补：[运行代码](scripts/cellcharter/cellcharter_151507_L3_diagnostic.py)、[非重训结果恢复代码](scripts/cellcharter/recover_151507_L3_metrics.py)、[真实终端转录指标](experiments/cellcharter_dlpfc/snapshot_20261110/results/cellcharter_v032_151507_seed22911_L3_diagnostic/metrics_recovered.json)
- 五档统一边界审计：[代码](scripts/cellcharter/audit_151507_all_depth_boundaries.py)、[完成记录](experiments/cellcharter_dlpfc/snapshot_20261110/BOUNDARY_AUDIT_151507_SEED22911_20261110.md)、[逐层结果](experiments/cellcharter_dlpfc/snapshot_20261110/LAYERWISE_BOUNDARY_151507_SEED22911_20261110.md)
- 历史 2026-11-09 seed0：[跳数消融](experiments/cellcharter_dlpfc/HOP_ABLATION_151507_SEED0_20261109.md)、[固定25维置换](experiments/cellcharter_dlpfc/FIXED25_PERMUTATION_151507_SEED0_20261109.md)。**不可将历史 seed0 当成 22911 的重复**。

原始10x H5、scVI 模型、latent.npy、聚合矩阵及部分本地 CSV 尚未备份到仓库；需要实际文件时再由用户提供，不应擅自宣称已读取。

## 2026-11-10 已完成结果（仅单切片单种子）

- 151507 原始 4226 spots；4221 带人工组织层标注。跨切片 barcode 可能重复：必须先按 `sample_name=="151507"` 筛标签，再对齐 barcode。
- Visium 12385 条无向空间邻边，12381 条两端都具有标签，可评价真实层间边界共 950 条。
- scVI（5000 HVG、latent5、GPU）→ 同一 scVI latent 的 CellCharter L0/L1/L2/L3/L4 聚合，特征维度依次 5/10/15/20/25 → 每档独立 TorchGMM CPU 拟合，Oracle K7（人工类别数）并用固定 seed22911。
- L4：ARI=0.4961464421378273，NMI=0.6754358219165002。协议是 v0.3.2 TorchGMM 与本地重建图的**适配基线**，不是作者 v0.2.0 + PyCave + 预处理 h5ad 的完整同版本复现。

| Depth | ARI | NMI | Boundary F1 | L5/L6 Boundary Recall |
|---|---:|---:|---:|---:|
| L0 | 0.362131 | 0.441915 | 0.175802 | 0.6000 |
| L1 | 0.444156 | 0.569587 | 0.162024 | 0.5448 |
| L2 | 0.457461 | 0.604740 | 0.132590 | 0.4414 |
| L3 | 0.469696 | 0.585078 | 0.136045 | 0.3310 |
| L4 | 0.496146 | 0.675436 | 0.171509 | 0.0000 |

L3 首次运行聚合及 GMM 预测已完成，但边界代码误把 `Layer 5/Layer 6` 写成 `L5/L6` 导致失败；随后直接从保存的预测恢复指标并保留失败状态，不重训。其恢复指标 ARI=0.4696960562716283，NMI=0.5850783791093968，边界 TP/FP/FN=194/1708/756。

逐层结果：L4 下 L5/L6 为 0/145，L4/L5 约为 3/160；但是 L1/L2、L2/L3 在 L4 比 L3 回升。L0 高边界召回伴随大量同层错误分割；全局 F1 亦非单调。**仅可声称单切片探索性权衡，不可声称因果过度平滑、普遍规律或已验证创新。**

## 最新核查补记（2026-11-10）

用户已经提供两份历史 seed0 L4 原始 `manifest.json` 的完整终端内容；见 [GMM manifest 对照归档](experiments/cellcharter_dlpfc/GMM_L4_SEED0_MANIFEST_AUDIT_20261110.md)。来源聚合与 latent 的 SHA256 一致、显式 GMM 超参一致，但旧 manifest 缺少最终输入矩阵 SHA256，脚本 hash 不同，训练实际收敛迭代 24 vs 29，NLL 4.614036 vs 4.721235；此不一致原因仍未定位。**下一步只读比较实际脚本中的矩阵构造、随机种子调用与 GMM fit 位置，不重复已完成的 manifest 检查或训练。**

## 当前阻碍及下一步

1. **立即下一步只读审查历史 GMM 重拟合一致性：** 2026-11-09 两次 seed0、名义上同源 L4 输入和同名超参数的预测分区 ARI=0.713871，而不是 1，原因不明。用户最近已列示两次本地运行目录有 `manifest.json`、`predictions.csv`、`script_snapshot.py`、`gmm_weights.pt` 等。**还未收到新一轮完整 manifest JSON 输出**；不能声称已经核查完该对比。
2. 机制混杂：聚合深度同时改变 GMM 输入维度；旧固定25维置换将不使用的邻域特征行错配，并不等于仅改变传播深度。须先解决模型稳定性与同维控制，再提出候选边界感知模块。
3. 归档/复现：用户终端已展示逐层四位小数，但本地五档新审计原始 CSV、L3 predictions.csv 和失败状态尚未直接读取/上传，不能误当 GitHub 已有。审计代码是事后补写，不可称当时历史实验曾运行该文件。
4. 之后才是预先冻结对照的跨 seed、跨切片/独立供体测试，以及最近邻已有方法、机制创新、论文叙事等审查。151507已被频繁探索，不是独立盲测。

## 最新代码核查（2026-11-10）

用户已运行两份 `script_snapshot.py` 的关键字与上下文检查：旧 h4 在创建 AnnData 之后设 seed，固定25维 h4 在创建 AnnData 之前设 seed；均在 Cluster 构造前设 seed。尚无法断定该顺序影响随机数。旧 h4 从聚合特征取前25列，新 h4 在 hop4 无置换并返回 C-contiguous float32。**下一个唯一动作：只读计算两者的最终输入数组 SHA256，与新 h4 manifest 的哈希比较**。详情见 [历史 GMM 审计](experiments/cellcharter_dlpfc/GMM_L4_SEED0_MANIFEST_AUDIT_20261110.md)。

## 最新输入哈希复核（2026-11-10）

用户实际运行只读 SHA256 检查：共同来源 `aggregated.npz` 中 `X_cellcharter (4226,25) float32`，按旧脚本 `np.ascontiguousarray(..., dtype=np.float32)` 重建后得到 `f653234c166ce80b80e1971b387439779ebe92745087d742c5821beedf1c9463`，与新固定25维 h4 manifest 中的输入矩阵 hash **一致**。这是重建一致性证据，旧运行时最终输入 hash 未被原始日志独立记录。下一步只读检查 AnnData 建立前后 NumPy/Torch RNG 状态是否被消耗，再决定是否需最小训练重复性实验；不可直接声称非确定性已证实。详见 [GMM 审计](experiments/cellcharter_dlpfc/GMM_L4_SEED0_MANIFEST_AUDIT_20261110.md)。

## 最新 RNG 诊断（2026-11-10）

用户完成 AnnData 构造 RNG 状态检测：`old` 与 `fixed25` 均显示 `TORCH_RNG_CHANGED=False`、`NUMPY_RNG_CHANGED=False`。第一次助手给出的测试代码误用 `torch.Generator.get_rng_state()` 导致 `AttributeError`，后修正成功；未重新训练。说明所测模拟 AnnData 创建过程没有消耗 CPU Torch/NumPy 全局 RNG，**不等于 TorchGMM 内部随机性已排除**。下一步只读核查脚本中完整 `cc.tl.Cluster(...)` 构造及特征装载差异。详见 [审计追加记录](experiments/cellcharter_dlpfc/GMM_L4_SEED0_MANIFEST_AUDIT_20261110.md)。

## 最新完整 GMM 调用核查（2026-11-10）

用户回传旧 L4 和固定25维 L4 的脚本原始行号片段；两份 `cc.tl.Cluster` 的 n_clusters、random_state、covariance_type、init_strategy、convergence_tolerance、covariance_regularization、trainer_params 全部一致，且新 h4 的特征置换循环为空。当前尚未发现显式参数差异。**唯一下一步：只读审查两份脚本中的原始 barcode/feature 加载、顺序与此前 ARI 比对对齐口径；不先重复训练**。参见 [GMM 审计](experiments/cellcharter_dlpfc/GMM_L4_SEED0_MANIFEST_AUDIT_20261110.md)。

## 下一次新对话如何接手

先按顶部顺序读取三个记忆文件。若 `PROJECT_STATE.md` 与本文件不一致，以**最新可核实的原始证据**为准并报告冲突；不要从旧 README 中取代当前状态。读取任务相关的 `manifest.json`、脚本、日志与指标，再给用户一条 Windows 手动操作；目前不需重建环境、重跑 L3、L0–L4、跨深度边界审计。

每次归档都同步更新 `PROJECT_STATE.md`、本文件与当天 `RESEARCH_JOURNAL/YYYY-MM-DD.md`，区分已执行、转录日志、待验证假设和计划。
