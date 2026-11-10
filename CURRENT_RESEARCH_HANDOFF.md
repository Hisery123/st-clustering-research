# CURRENT_RESEARCH_HANDOFF · 第三篇空间转录组聚类论文

## 2026-11-10 追加：完整12切片 H5 下载成功（用户终端）

用户 PowerShell 批量下载剩余9张 DLPFC 切片，终端九次 `DOWNLOAD_OK`：151509、151510、151670、151671、151672、151673、151674、151675、151676。此前用户已下载151669，151507/151508为已有数据。因此指定本地根目录 `D:\paper\ST_Benchmark_Planning\mvp\data` 中预计12张切片的 `filtered_feature_bc_matrix.h5` 均已取得；本次脚本判断以 curl 退出码0且文件非空为条件，**尚未逐个打开 H5 验证完整性、条码、空间坐标或人工标签；不能直接宣称12张数据集已准备到可训练阶段**。

按已核对公开供体分组：D1=151507/151508/151509/151510；D2=151669/151670/151671/151672；D3=151673/151674/151675/151676。三位供体，12张切片；论文统计不能将12片视为12位独立受试者。151673此前在其他项目中被触及，后续预注册验证方案前需盘点历史使用，不得未经证据称盲测。

**下一步唯一动作**：Windows 只读批量使用 `scanpy.read_10x_h5` 打开12份H5，列出spot×gene、barcode唯一性、文件大小、失败项；不训练、不改变原文件。之后才批量取得/核查 spatialLIBD 官方切片对应的坐标和人工层标签。

## 新增文献核查：DLPFC 供体结构纠正（2026-11-10，最高优先级）

已查公开来源（本条是**公开文献/数据项目报告**，不是Windows实验结果）：
- BASS论文 https://pmc.ncbi.nlm.nih.gov/articles/PMC9351148/ 描述12张DLPFC切片来自3位独立供体，每供体4张切片。
- 2026 ICLR Workshop公开论文 https://openreview.net/pdf/63a0bb10dd34a1ca90af0deae2bcd06d6de42cec.pdf 附表按供体列出：供体1 `151507/151508/151509/151510`，供体2 `151669/151670/151671/151672`，供体3 `151673/151674/151675/151676`。因此**此前泛称151509可作为独立样本并不准确**：它和已使用的151507、151508同供体。
- 研究机构官方空间LIBD源数据链接 https://github.com/LieberInstitute/spatialLIBD/blob/devel/README.Rmd ，151669 H5官方直链 `https://spatial-dlpfc.s3.us-east-2.amazonaws.com/h5/151669_filtered_feature_bc_matrix.h5`。
**当前方案**：优先选择另一供体的151669用于冻结方案A L0+L1+L2、B L0+L1+L4的扩展验证；需另行核实其标签/坐标来源和过去是否用于模型选型。切片数不等于独立供体数，151507/151508同供体。**尚未下载151669，也未进行新实验。** 先由用户手动下载原始H5到独立新文件夹并核验，其他输入随后准备，不先训练。

## 数据目录清点（2026-11-10，最新）

用户Windows只读执行 `Get-ChildItem "D:\paper\ST_Benchmark_Planning\mvp\data" -Directory | Where-Object { $_.Name -match "^1515\\d{2}$" }`，只返回 `151507` 和 `151508`。因此该特定本地目录中目前只有这两张匹配的 DLPFC 切片；**不能推断其他磁盘/目录或公开数据集没有更多切片**。当前两片已有结果：151507候选B的ARI/NMI/边界F1均改善；151508候选B的ARI略降、NMI下降而边界F1上升。下一步应选定未参与锁定组合选择的额外公开切片（优先核实独立供体），按冻结评价协议验证；暂不新建无终点的 seed/组合搜索或切回STAGATE。目标仍是普通SCI增量方法论文，当前尚未成立。

## 151508 冻结 A/B 对照已完成：边界F1正向、全局ARI/NMI非正向（2026-11-10，最高优先级）

用户Windows运行 `scripts/cellcharter/mvp_fixed15_block_swap_151508.py`，终端明确 `MVP_FIXED15_COMPLETE`，输出目录 `D:\paper\CellCharter_reproduction\results\mvp_fixed15_block_swap_151508_gmm22911_v1`，**已实际执行**。同一151508 scVI seed22911 的25D缓存切出两组15D；Oracle K7，CPU GMM seed22911。A: ARI `0.46267065495944715`, NMI `0.6132171362713753`, boundaryF1 `0.10315575161180861`, TP152/FP1868/FN775，L5/L6 41/139；B: ARI `0.46059571688191825`, NMI `0.5691388933817928`, boundaryF1 `0.16513761467889906`, TP261/FP1973/FN666，L5/L6 49/139。B−A：ARI −0.002075，NMI −0.044078，边界F1 +0.061982，边界FP +105（负面需保留）。真实评估边12846，真界面边927。

对比151507开发切片：同seed B的ARI/NMI/F1均更好；**151508上整体聚类ARI略差且NMI明显差，不能宣称整体聚类跨切片稳定提升；仅两切片边界F1有探索性改善信号**。所有数值来自用户终端，不是假定已独立读取本地CSV。当前不做统计显著性声明；spot/边不等于生物独立样本，151508是曾经接触的样本，非严格未触碰盲测。完整终端归档：[151508 试验报告](experiments/cellcharter_dlpfc/MVP_FIXED15_151508_EXTENSION_PLAN_20261110.md)。

**下一步**：不追加151508随机种子挑好成绩、不更改已冻结A/B；预先确定下一阶段主要终点、容忍的ARI/NMI损失，盘点是否有未用于设计的其他切片；公平对照和创新性审查之后才评估发展方法论文的可行性。不要转STAGATE或重启历史GMM排错。

## 151508 scVI/25D 缓存完成，锁定跨切片 A/B 脚本待运行（2026-11-10，最新）

**用户终端已证实成功**：v2脚本输出 `151508_SCVI_TRAIN_FINISHED` 及 `151508_FEATURE_CACHE_COMPLETE`，scVI提前停止于epoch260；4384×5 latent，4384×25聚合，空间边12849，CUDA运行，peak_cuda_mib=106.73（仅Torch统计），聚合文件SHA256=`094f702ba7fae32fc69c6c8026acb5765bd7bcd39b2802fbe8091b26baba60ee`。缓存路径 `D:\paper\CellCharter_reproduction\results\cellcharter_151508_scvi22911_features_v2`。**尚未在151508运行GMM、未生成跨切片比较指标。**

**新脚本已上传GitHub（Windows尚未拉取）**：[151508冻结15D对比](scripts/cellcharter/mvp_fixed15_block_swap_151508.py)；A=L0+L1+L2，B=L0+L1+L4；CPU GMM seed22911 K7，标注只在预测之后读入，自动按真实151508标注及边数计算指标。完整记录：[151508实验档案](experiments/cellcharter_dlpfc/MVP_FIXED15_151508_EXTENSION_PLAN_20261110.md)。下一步**仅git pull**，随后单独运行GMM脚本，先不加其他组合、不更改种子，不称严格未接触的独立盲测。 

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

## 151508 输入文件存在（2026-11-10；当前最优先）

用户Windows检查：151508 的表达H5、spots_aligned.csv、manual_layer_annotations.csv 三文件均存在；指定 `CellCharter_reproduction\results` 下没有列出匹配151508的目录。**未检查文件结构/条码匹配、也未确证所有位置没有scVI缓存**。下一步仅只读检验151508矩阵与坐标行顺序及标注覆盖；随后决定最小跨片实验。方案A L0+L1+L2、B L0+L1+L4不变。暂不重训、不查STAGATE。


## 最新结果（2026-11-10）：已完成 Barcode 分区一致性复核

用户实际只读合并两轮各4226行 predictions.csv，结果：对照 A 的跨 GMM seed 分区 ARI=`0.5049001187368433`，候选 B 的分区 ARI=`1.0`。因此 B 在这两个 GMM seed 下为同一分区（簇编号可置换），不是对人工标签 ARI=1.0、不是不同切片验证。原本本文件旧段落“尚未直接读取预测文件”已过期；详细档案见 [MVP-1b](experiments/cellcharter_dlpfc/MVP_FIXED15_GMM_SEED101_151507_20261110.md)。**接下来仅只读检查151508已有数据及特征缓存；不继续刷151507、不恢复STAGATE和历史GMM排查。**


## 最新 MVP-1b 结果（2026-11-10；当前优先）

- 用户实际执行 `mvp_fixed15_block_swap_gmm101_151507.py` 成功，`MVP_FIXED15_COMPLETE`；结果在本地 `D:\paper\CellCharter_reproduction\results\mvp_fixed15_block_swap_151507_scvi22911_gmm101_v1`，当前仓库仅终端转录。
- 固定151507/scVI seed22911/15维特征，GMM seed101：A `L0+L1+L2` 的 ARI=`0.4177569883`、NMI=`0.6113343544`、boundary F1=`0.1694744782`、L5/L6=`3/145`；B `L0+L1+L4` 的 ARI=`0.5272652573`、NMI=`0.6175659085`、boundary F1=`0.2030360531`、L5/L6=`62/145`。对照先前seed22911：A的ARI=0.480019、F1=0.154412、L5/L6=64/145，B与本次全部指标完全相同。**B两次cluster_sizes互为排列，但尚未直接读取预测文件确认按barcode分区是否严格一致。**
- **判断**：候选B在这两个GMM初始化下的全局指标均优于A，但A对seed敏感，L5/L6在一个seed中反而是A更好。仅同切片单scVI表征双GMM seed，不能归纳为泛化优势或完整边界修复。实验明细：[MVP-1b真实终端归档](experiments/cellcharter_dlpfc/MVP_FIXED15_GMM_SEED101_151507_20261110.md)。
- **当前最小下一步**：只读比对两次候选B的预测CSV，按barcode计算分区一致性ARI，不训练、不更改原结果；其后考虑冻结方案并规划另一张切片的实际开发/验证协议。不主动重启已取消的历史 seed0 h4 问题或 STAGATE。


> **2026-11-10 文献核查新进展**：已核实 CellCharter 原文/官方邻域拼接 API、AugGCL 2026 PLOS 原文 NIA 表达-邻域相似度加权、CodaST 出版方摘要 LSWC、HarveST PMC 全文及 GATCL/TRACER 的摘要；详见 [第一轮最近邻审计](experiments/cellcharter_dlpfc/NEAREST_PRIOR_ART_AUDIT_20261110_V1.md)。**STOP：**不得将单纯表达相似性加权邻接或 GAT 注意力包装成独创。**条件 GO：**先审查多尺度特征块与 GMM 可分性影响的最小、可证伪机制对照（非新算法）。AugGCL GitHub 代码含根据每epoch ARI选择最佳结果的片段，但尚未证实其用于论文151507的报告值。当前无需 Windows 操作，不自动恢复已暂停的历史 GMM 排查。下方早期“下一步查 GMM”均为旧记录。


> **2026-11-10 用户最新科研决策（优先于下文旧待办）**：停止追查历史两份 seed0 L4 GMM 不一致，根因未明，暂存为局限；**禁止自动继续预测对齐、RNG、重复拟合诊断**。转入 S2/S3：对 CellCharter 边界/连续性权衡作最近邻论文原创性审查，再决定单一最小机制。初步检索与源链接：[研究转向记录](experiments/cellcharter_dlpfc/RESEARCH_PIVOT_AND_PRIOR_ART_SCREEN_20261110.md)。后文涉及“下一步继续查 GMM”的句子是先前历史状态，现已失效。


> 最后整理：2026-11-10。**跨对话读档顺序：** [AGENTS.md](AGENTS.md) → [PROJECT_STATE.md](PROJECT_STATE.md) → [最近科研日记](RESEARCH_JOURNAL/2026-11-10.md) → 按需审查本文件和对应实际实验代码/结果。此文件是交接索引，不是原始证据。历史实验完整记录在 `experiments/`。

## MVP-0 实际结果与下一步（2026-11-10 最新）

- **只读预检已实际运行成功**：源文件 SHA256 `15b1fd58d092277f81fa2a1513bb2fbf865eea71b1b7450a9a2f710c941a8f54`，4226×25 float32；L0–L4 RMS 分别为 `1.01395915, 0.77181948, 0.72375672, 0.69487204, 0.67063472`；同维对L0平均绝对相关分别为 `1.00000000, 0.64353317, 0.64636024, 0.63651649, 0.62608682`。未使用标签、未训练、未写文件。[完整终端转录和决策](experiments/cellcharter_dlpfc/MVP_MULTISCALE_SCREEN_151507_20261110.md)。
- **决策**：无远邻特征幅度异常放大，不把纯可逆分块缩放当新方法创新（full covariance GMM 基本可吸收这种重标度）。选择等维度（均15维）特征组合的**探索性筛查**，控制 `L0+L1+L2`，候选 `L0+L1+L4`，复用已保存25维输入、同一GMM超参数和seed，**两组都重新拟合GMM**以便同一次脚本下公平比较，标签只在预测后读取；执行后报告ARI/NMI与真实边界指标，不重新训练scVI。新脚本：[mvp_fixed15_block_swap_151507.py](scripts/cellcharter/mvp_fixed15_block_swap_151507.py)。**脚本尚未执行**。
- **下一条用户操作**：先 `git pull --ff-only` 同步新的GitHub脚本，等用户实际报告成功，再单独运行MVP脚本。本次没有启动GMM。

## 当前路线的历史摘要

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
