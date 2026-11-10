# PROJECT_STATE — 第三篇空间转录组聚类论文

## v2 语法错误修复（2026-11-10；最新）

用户 Windows 尝试运行 `prepare_151508_scvi_aggregation_v2.py`，Python **编译解析阶段**第169行报 `SyntaxError: unexpected character after line continuation character`。原因是我此前通过GitHub写入脚本时把 `peak_cuda_mib` 条件表达式的换行误写为字面量 `\\n`。在程序运行前已失败，**未触发任何CUDA初始化、训练或输出目录创建**，故 v2 结果目录应尚未由这次命令创建（如存在则另行检查）。我已在同一 v2 脚本中将字面量替换为真实换行，未改实验配置、代码行为或输出目录。修复提交 `2b372dc`。下一步**只需手动git pull同步修复**，等待用户成功结果后再运行 v2。不得再让用户运行旧脚本版本或误判为GPU故障。

## 最新 GPU 诊断与 v2 准备（2026-11-10）

用户原环境实际输出：`TORCH_VERSION 2.1.2+cu121`、`TORCH_CUDA_VERSION 12.1`、`CUDA_AVAILABLE True`、`CUDA_DEVICE_COUNT 1`、`CUDA_ALLOCATION PASS`、`GPU_NAME NVIDIA GeForce RTX 4070 Laptop GPU`、`CUDA_MEMORY_STATS PASS`。此前151508 v1在 `reset_peak_memory_stats(0)` 报 Invalid device，**目前未证实是设备损坏或具体根因**，当次scVI训练未开始。

已在GitHub新建 [v2 特征准备脚本](scripts/cellcharter/prepare_151508_scvi_aggregation_v2.py)，独立结果目录 `cellcharter_151508_scvi22911_features_v2`；在创建目录/开始训练前显式 `torch.cuda.init()`、分配1元素测试张量并同步。统计API故障仅记录警告（不改变是否训练模型），禁止CPU静默回退；保留v1失败目录。**v2尚未同步到用户Windows，也尚未运行。当前唯一下一步：用户手动git pull，确认成功后再单独执行v2。**


## 151508 特征准备首次正式运行失败（2026-11-10）

用户实际运行 `prepare_151508_scvi_aggregation.py`（无 `--check-only`）。终端先输出 `151508_GRAPH_CHECK_PASS spots 4384 edges 12849`、`151508_PREPROCESS_PASS (4384, 5000)`、`Global seed set to 22911`；随后出现 `No GPU/TPU found, falling back to CPU.`，在**任何 `151508_SCVI_TRAIN_START` 之前**的 `torch.cuda.reset_peak_memory_stats(0)` 第127行报 `RuntimeError: Invalid device argument 0: did you call init?`。因此**scVI尚未训练，不存在新的latent/aggregated结果**。脚本已创建专属结果目录并通过except将status.json标为failed（代码预期；未直接读取本地文件，须通过用户后续输出确认）。原脚本禁止覆写，不能立即重试。

当前唯一下一步：用户在原CellCharter Python环境运行一个仅诊断的单条PowerShell命令，检查 torch.cuda.is_available、device_count、NVIDIA设备名、最小CUDA张量能否分配及显存统计 API 是否可用；异常按字符串输出。确认问题后再为失败结果目录设计安全的续跑方案（**新目录、保留失败记录**），不盲目重新安装依赖/换CPU/重训旧数据。

## 151508 六邻域图预检成功（2026-11-10）

用户Windows实际执行 `prepare_151508_scvi_aggregation.py --check-only`，终端输出：
```text
151508_GRAPH_CHECK_PASS spots 4384 edges 12849
151508_CHECK_ONLY_COMPLETE; NO_TRAINING; NO_FILES_WRITTEN
```
另见 `Global seed set to 0`（包导入阶段初始化信息）及 `pkg_resources`、基因名称重复的 UserWarning。正式脚本在拟合scVI前将设置 seed22911，预处理调用 `var_names_make_unique()`。

这只证明空间图几何/对称性等检查成功；**scVI尚未训练，5D/25D缓存尚未生成**。下一步用户仅运行正式 `prepare_151508_scvi_aggregation.py`（无 `--check-only`）来准备151508 5D latent及25D聚合，脚本拒绝覆盖已有结果、不执行GMM或人工标注评价。继续冻结开发阶段A/B组合；151508跨切片不能表述为先前从未探索的独立盲测。 

## 151508 表征缓存盘点与训练准备（2026-11-10，最新）

用户Windows只读搜索 `D:\paper\CellCharter_reproduction` 与 `D:\paper\ST_Benchmark_Planning\mvp` 下路径包含151508且文件名匹配 `latent|aggregat|embedding|scvi`、扩展名为 `.npy/.npz/.h5ad/.pt` 的文件，**终端无输出**。这表示在此匹配范围内未发现缓存，**不代表全盘绝对不存在，也不是训练已执行**。

根据已经核实的151507适配版原始脚本，GitHub新建 [151508 特征准备脚本](scripts/cellcharter/prepare_151508_scvi_aggregation.py)，采用相同5000 HVG/seurat_v3、5维scVI、AdamW/early-stop、4跳25维空间拼接、seed22911和基于Visium六邻域几何校验。仅生成 scVI 5维 latent / 25维聚合/条码顺序，不拟合GMM、不读取人工层标注、不更换已锁定A/B。新结果目录独立且拒绝覆盖。**脚本仅已提交GitHub，Windows尚未同步或运行**。

**唯一下一步：先 `git pull --ff-only` 同步新脚本；然后再单独运行 `--check-only` 核对空间图并确认不会训练写文件；成功后再正式开始scVI训练。** 来源151508曾用于项目其他任务，跨切片检验不称严格全新盲测。避免重复STAGATE与历史GMM排错。

## 151508 预检结果（2026-11-10，最新）

用户在Windows实际以 CellCharter 专用 Python 运行只读核查并输出 `151508_INPUT_PREFLIGHT_COMPLETE`。真实终端：`EXPRESSION_SHAPE: (4384, 33538)`；`POSITION_ROWS: 4384`；`BARCODE_UNIQUE: True`；`BARCODE_ORDER_MATCH: True`；`COORDINATES_VALID: True`；`ANNOTATED_SPOTS: 4381`；`ANNOTATION_CLASSES: 7`；`ANNOTATION_BARCODES_MATCH: True`。读10x H5时有两个基因变量名不唯一 UserWarning，属于预处理注意事项，原151507脚本使用 `var_names_make_unique()`，此轮未写文件。

**证据边界**：以上是用户真实终端转录，不是AI直接取得本地文件；这仅验证矩阵与坐标/标注匹配，不证明历史使用或已有latent缓存、也未运行151508 scVI/GMM。151508不是完全未知的盲测数据（项目早前已涉及该切片），后续应称跨切片验证/扩展开发验证并明确已有接触程度。

**当前唯一下一步**：在指定本地项目目录只读寻找151508可复用的 scVI 5维 latent 和25维聚合特征。若找不到，才准备匹配151507预处理的训练脚本；不重复训练，也不更换锁定 A/B（L0+L1+L2 vs L0+L1+L4）。

## 151508 跨切片准备：Windows 路径清点（2026-11-10）

用户在 Windows 手动执行三输入文件的 `Test-Path` 与结果目录筛查，真实输出表明 `D:\paper\ST_Benchmark_Planning\mvp\data\151508\` 下 `filtered_feature_bc_matrix.h5`、`spots_aligned.csv`、`manual_layer_annotations.csv` 均为 `True`；在 `D:\paper\CellCharter_reproduction\results` 下按目录名匹配 `151508` **未列出目录**。这不证明其他位置不存在缓存或151508未曾用于其他实验。

**下一步唯一动作**：对151508执行只读矩阵/空间坐标和标注表结构检查（数量、barcode唯一性及顺序、标注覆盖；不得拟合、不得写文件）。如无既有CellCharter latent，之后才规划最小scVI缓存生成，不能立即宣称已有跨片实验。候选固定为A=`L0+L1+L2` vs B=`L0+L1+L4`，均15维。151508历史上用于其他任务的情况应说明，不称未经探索的独立盲测。


## 最新分区一致性复核与下一步（2026-11-10，最高优先级）

用户在Windows只读检查两轮 `predictions.csv`，按 `barcode` 一对一合并各4226行，真实输出：对照 `L0+L1+L2` 的跨GMM seed分区ARI=`0.5049001187368433`，候选 `L0+L1+L4` 的跨GMM seed分区ARI=`1.0`。说明候选B在seed22911和101的这两次拟合中得到**相同分区（允许标签编号置换）**；**不是**与人工标签ARI=1，更不能代表跨切片验证。详细记录见 [MVP-1b档案](experiments/cellcharter_dlpfc/MVP_FIXED15_GMM_SEED101_151507_20261110.md)。

**决策**：不继续在151507刷seed/挑更多组合，候选B暂固定待跨片检验；首先**只读盘点151508已有数据及缓存，不开始大规模重训**。此前写的“下一步对比两份CSV”已完成，失效。不要开启STAGATE或历史GMM排错。

## 最新 MVP-1b 结果（2026-11-10；当前优先）

- 用户实际执行 `mvp_fixed15_block_swap_gmm101_151507.py` 成功，`MVP_FIXED15_COMPLETE`；结果在本地 `D:\paper\CellCharter_reproduction\results\mvp_fixed15_block_swap_151507_scvi22911_gmm101_v1`，当前仓库仅终端转录。
- 固定151507/scVI seed22911/15维特征，GMM seed101：A `L0+L1+L2` 的 ARI=`0.4177569883`、NMI=`0.6113343544`、boundary F1=`0.1694744782`、L5/L6=`3/145`；B `L0+L1+L4` 的 ARI=`0.5272652573`、NMI=`0.6175659085`、boundary F1=`0.2030360531`、L5/L6=`62/145`。对照先前seed22911：A的ARI=0.480019、F1=0.154412、L5/L6=64/145，B与本次全部指标完全相同。**B两次cluster_sizes互为排列，但尚未直接读取预测文件确认按barcode分区是否严格一致。**
- **判断**：候选B在这两个GMM初始化下的全局指标均优于A，但A对seed敏感，L5/L6在一个seed中反而是A更好。仅同切片单scVI表征双GMM seed，不能归纳为泛化优势或完整边界修复。实验明细：[MVP-1b真实终端归档](experiments/cellcharter_dlpfc/MVP_FIXED15_GMM_SEED101_151507_20261110.md)。
- **当前最小下一步**：只读比对两次候选B的预测CSV，按barcode计算分区一致性ARI，不训练、不更改原结果；其后考虑冻结方案并规划另一张切片的实际开发/验证协议。不主动重启已取消的历史 seed0 h4 问题或 STAGATE。


> 当前有效存档，2026-11-10。**先读此文件的当前状态，再按需看实验归档；历史诊断保留于日记和原始记录，不作为当前待办。**
> 新对话阅读顺序：[AGENTS.md](AGENTS.md) → 本文件 → [当日日记](RESEARCH_JOURNAL/2026-11-10.md) → [交接索引](CURRENT_RESEARCH_HANDOFF.md)。

## 最新 MVP-1 结果和唯一下一步（2026-11-10）

- 用户 Windows **已实际运行完成** `mvp_fixed15_block_swap_151507.py`，终端确认 `MVP_FIXED15_COMPLETE`；本地结果目录 `D:\paper\CellCharter_reproduction\results\mvp_fixed15_block_swap_151507_seed22911_v1`。本仓库目前是**用户终端转录**，并未直接读取本地结果文件。
- 同为15维、相同scVI表征和单次 GMM seed22911：A=`L0+L1+L2`，B=`L0+L1+L4`。A→B：ARI `0.480019→0.527265`，NMI `0.574796→0.617566`，全局边界F1 `0.154412→0.203036`，FP `2564→1891`；**负结果：L5/L6界面检出64/145→62/145**。GMM有100 max_epochs提示，不能将单次结果视作收敛/稳定性证明。详细 [实际运行档案](experiments/cellcharter_dlpfc/MVP_FIXED15_BLOCK_SWAP_151507_SEED22911_20261110.md)。
- **当前唯一下一步**：用户先同步 GitHub 最新脚本 `scripts/cellcharter/mvp_fixed15_block_swap_gmm101_151507.py`，随后单独运行该脚本，用不同的**GMM初始化seed=101**验证同一输入下对比方向是否保持。**scVI来源仍为seed22911，不是独立生物重复，不重新训练scVI；新脚本未运行。**
- 禁止反向把本次正结果称已证实创新或独立验证；STAGATE不在当前任务范围；历史seed0 GMM不一致不重启。

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

## MVP-0 实际结果与下一步（2026-11-10 最新）

- **只读预检已实际运行成功**：源文件 SHA256 `15b1fd58d092277f81fa2a1513bb2fbf865eea71b1b7450a9a2f710c941a8f54`，4226×25 float32；L0–L4 RMS 分别为 `1.01395915, 0.77181948, 0.72375672, 0.69487204, 0.67063472`；同维对L0平均绝对相关分别为 `1.00000000, 0.64353317, 0.64636024, 0.63651649, 0.62608682`。未使用标签、未训练、未写文件。[完整终端转录和决策](experiments/cellcharter_dlpfc/MVP_MULTISCALE_SCREEN_151507_20261110.md)。
- **决策**：无远邻特征幅度异常放大，不把纯可逆分块缩放当新方法创新（full covariance GMM 基本可吸收这种重标度）。选择等维度（均15维）特征组合的**探索性筛查**，控制 `L0+L1+L2`，候选 `L0+L1+L4`，复用已保存25维输入、同一GMM超参数和seed，**两组都重新拟合GMM**以便同一次脚本下公平比较，标签只在预测后读取；执行后报告ARI/NMI与真实边界指标，不重新训练scVI。新脚本：[mvp_fixed15_block_swap_151507.py](scripts/cellcharter/mvp_fixed15_block_swap_151507.py)。**脚本尚未执行**。
- **下一条用户操作**：先 `git pull --ff-only` 同步新的GitHub脚本，等用户实际报告成功，再单独运行MVP脚本。本次没有启动GMM。

## 历史阶段：MVP-0，只读预检计划（已完成）

- [完整务实方案](experiments/cellcharter_dlpfc/MVP_INCREMENTAL_RESEARCH_PLAN_20261110.md) 已冻结**首项只读检查**，没有训练任何新方法；后续加权候选仅为待决定方案。
- 新建 [预检脚本](scripts/cellcharter/preflight_multiscale_blocks_151507.py)，读取已保存的 seed22911 L4 `cellcharter_aggregated.npy`（4226×25），按五个5维块报告绝对均值、RMS、列STD、自身块相关，**不加载标注、不运行GMM、不写文件**。
- **下一个唯一手动操作**：用户在 Windows 先从 GitHub 同步最新脚本（代理 git pull 的旧成功参数可复用），收到成功日志后再单独执行上述预检脚本。绝不要在用户同步前称本地已有新脚本。
- 预检结果返回后决定是否有理由预先锁定一个**固定25维**块尺度校准候选，以及原始 L4、最简单替代控制与同协议 GMM 的开发集实验。因为 full-covariance GMM 对可逆线性缩放理论上可吸收，任何差别可能来源于初始化/正则/数值，不能直接归因于生物学新机制。

## 仍需面对的局限与实施规则

- 当前仅开发切片单种子，深度与输入特征维度联动；跨独立切片/供体、重复种子、全套公平对照、最近邻完整机制审查、创新验证、论文结果均未完成。
- Windows: `D:\paper\CellCharter_reproduction`；本地 Git: `D:\paper\st-clustering-research`；Python: `D:\paper\CellCharter_reproduction\env_cellcharter\python.exe`。原始 H5、部分本地模型和 CSV 未上传；GitHub 终端转录不是原始文件字节校验。
- 用户本人执行 Windows 本地实验；AI 直接管理允许的 GitHub 文档/脚本。**一次只给一条可复制命令**，说明预期与报错处理。
- 本文件每次关键研究推进时保持简短、移除过期下一步；历史细节去日记和 `experiments/`，不能重复堆叠相互冲突的“下一步”。
