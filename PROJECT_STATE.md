# PROJECT_STATE — 第三篇空间转录组聚类论文

> 当前有效存档，2026-11-10。**先读此文件的当前状态，再按需看实验归档；历史诊断保留于日记和原始记录，不作为当前待办。**
> 新对话阅读顺序：[AGENTS.md](AGENTS.md) → 本文件 → [当日日记](RESEARCH_JOURNAL/2026-11-10.md) → [交接索引](CURRENT_RESEARCH_HANDOFF.md)。

## 当前目标与采用的科研策略

- **目标**：争取符合毕业要求的普通 SCI 方法论文，以成熟可运行基线、低成本可解释的**小幅增量**为导向，不追求重大理论突破，也不承诺任何期刊录用。
- **流程**：成熟基线 → 可测弱点 → 1–2个最小候选 → 低成本开发集 MVP → 同预算必要对照、锁定方案并跨独立样本验证 → 随实验并行写稿。原创性审查优先最近3–5项最相似工作，避免无限审查。
- **诚信边界不变**：开发集可以探索但不能将幸运最佳成绩当独立盲测；保留所有失败、无提升和负结果；人工参考标签不用于所谓独立测试的调参/早停；不伪造引用/结果。Oracle K=7 是根据人工标注类别数设置。
- **暂停事项**：用户要求停止历史 seed0 L4 GMM 两组预测不一致原因排查，已有审计与不确定性保存于实验文档；**不要再让用户跑这两套历史诊断命令**。

## 已完成且可追溯的结果（不是最终论文结果）

- CellCharter **v0.3.2 适配版**，scVI 5D latent、Visium 六邻域、TorchGMM CPU；与作者 v0.2.0/PyCave/原预处理 h5ad 不同，不能宣称一模一样的作者复现。
- DLPFC 151507：4226 spots，4221 有有效人工层标签；12385 无向邻边、12381 有效评价边、950 跨层参考边界。**151507 已用于开发，不是独立测试片**。
- seed22911、Oracle K7、L0–L4 共用一份 scVI latent，特征维度依次 5/10/15/20/25，GMM各自拟合：
  - ARI：0.362131 / 0.444156 / 0.457461 / 0.469696 / 0.496146
  - NMI：0.441915 / 0.569587 / 0.604740 / 0.585078 / 0.675436
  - 全局边界F1：0.175802 / 0.162024 / 0.132590 / 0.136045 / 0.171509
  - L4 的 Layer5/Layer6 边界检出0/145、Layer4/Layer5约3/160；L0 在多个组织层内部错误分割率较高；L4也有部分界面召回反弹，不能声称全体单调下降或过度平滑因果成立。
- L3 初次预测完成但边界评价因 Layer5 标签字符串错误而失败，已从保存预测恢复指标并保留失败；统一五档边界与逐层审计已实际执行。
- 主要证据：[全局边界](experiments/cellcharter_dlpfc/snapshot_20261110/BOUNDARY_AUDIT_151507_SEED22911_20261110.md)、[逐层边界](experiments/cellcharter_dlpfc/snapshot_20261110/LAYERWISE_BOUNDARY_151507_SEED22911_20261110.md)、[L3恢复指标](experiments/cellcharter_dlpfc/snapshot_20261110/results/cellcharter_v032_151507_seed22911_L3_diagnostic/metrics_recovered.json)。
- 最近邻已有研究：[文献审查V1](experiments/cellcharter_dlpfc/NEAREST_PRIOR_ART_AUDIT_20261110_V1.md)。**简单邻域表达相似性权重、注意力或仅重命名模块不能自动声称原创性**；AugGCL 的训练代码存在每epoch ARI选最优的片段，但是否用于对应报告值仍待核实，不能断言原作者整篇泄漏。

## 当前阶段：MVP-0，多尺度特征块的只读预检

- [完整务实方案](experiments/cellcharter_dlpfc/MVP_INCREMENTAL_RESEARCH_PLAN_20261110.md) 已冻结**首项只读检查**，没有训练任何新方法；后续加权候选仅为待决定方案。
- 新建 [预检脚本](scripts/cellcharter/preflight_multiscale_blocks_151507.py)，读取已保存的 seed22911 L4 `cellcharter_aggregated.npy`（4226×25），按五个5维块报告绝对均值、RMS、列STD、自身块相关，**不加载标注、不运行GMM、不写文件**。
- **下一个唯一手动操作**：用户在 Windows 先从 GitHub 同步最新脚本（代理 git pull 的旧成功参数可复用），收到成功日志后再单独执行上述预检脚本。绝不要在用户同步前称本地已有新脚本。
- 预检结果返回后决定是否有理由预先锁定一个**固定25维**块尺度校准候选，以及原始 L4、最简单替代控制与同协议 GMM 的开发集实验。因为 full-covariance GMM 对可逆线性缩放理论上可吸收，任何差别可能来源于初始化/正则/数值，不能直接归因于生物学新机制。

## 仍需面对的局限与实施规则

- 当前仅开发切片单种子，深度与输入特征维度联动；跨独立切片/供体、重复种子、全套公平对照、最近邻完整机制审查、创新验证、论文结果均未完成。
- Windows: `D:\paper\CellCharter_reproduction`；本地 Git: `D:\paper\st-clustering-research`；Python: `D:\paper\CellCharter_reproduction\env_cellcharter\python.exe`。原始 H5、部分本地模型和 CSV 未上传；GitHub 终端转录不是原始文件字节校验。
- 用户本人执行 Windows 本地实验；AI 直接管理允许的 GitHub 文档/脚本。**一次只给一条可复制命令**，说明预期与报错处理。
- 本文件每次关键研究推进时保持简短、移除过期下一步；历史细节去日记和 `experiments/`，不能重复堆叠相互冲突的“下一步”。
