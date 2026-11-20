# 第三篇E3d：真正无标签AutoK｜环境及方法学预检（2026-11-20）

> **状态：预检计划，E3d尚未进行新的拟合/没有产生AutoK结果。** 仅CellCharter DLPFC第三篇；保持E1/E2 1200任务和E3c 2400格冻结产物不变。不调用Codex、不在助手环境假装执行用户的Windows命令。

## 现有真实证据

- E3c全部12片×4累计特征(10/15/20/25D)×K5–9×10冻结seed=2400格，480 Oracle-K历史复用、1920新拟合；用户Windows全网格复审`E3C_ALL_2400_AUDITED_PASS`。用户新K 1920行CSV已在 [E3c release](E3C_20261120_RELEASE/README.md) 实际归档。
- E3c冻结代码`e3c_k_sensitivity_single_task_v1.py`使用CellCharter Cluster + CPU TorchGMM、full covariance、kmeans init、tol0.001、reg_covar1e-6、max_epochs100。E3d不同实验，不得中途转换E3c设备或覆盖现有结果。
- 2026-11-20查阅官方 `cellcharter.tl.ClusterAutoK` 文档，入参`n_clusters, max_runs=10, convergence_tol=0.01, model_class, model_params`；`best_k`为相邻K运行稳定性汇总最大处，不能等价于ARI最高K。来源：https://cellcharter.readthedocs.io/en/latest/generated/cellcharter.tl.ClusterAutoK.html 。
- 源码对照：实际读取官方仓库`CSOgroup/cellcharter` tag `v0.3.2`的`src/cellcharter/tl/_autok.py`，Git blob `a0eeca0ffaab6f98317eac0721ca9ce173fc90f6`。其中元组`n_clusters=(4,10)`内部还拟合K=3和11以计算邻接稳定性（`range(max(1, lower-1), upper+2)`）；`model_params`内`random_state`被取出并用于每轮模型`i+random_state`；`convergence_tol`可能提前终止。
- **新发现需审查**：2026-08-07公开的CellCharter issue #122指出部分旧版本`GaussianMixture`接收`random_state`却未真正对拟合随机数播种，AutoK的重启可能依赖环境全局RNG；该issue于2026-10-15标为已修复，0.3.8（2026-10-19）与0.3.9（2026-11-05）已发布；不可由此推断用户安装版本已经修复。官方：https://github.com/CSOgroup/cellcharter/issues/122 ；版本：https://pypi.org/project/cellcharter/ 。**这属于可复现性风险，须先读取用户本机环境版本/实现，不因包版本警报就直接更新或推翻既往审核通过的实验。**

## E3d待冻结方案（不是E3d已执行结果）

1. **主研究问题**：不使用任何人工层标签确定聚类数K，ClusterAutoK选择的K是否与历史Oracle-K不同，以及对12片和4尺度的ARI/NMI/边界后验评价有什么影响？只能在聚类结果固化之后读取参考标签。
2. **候选搜索范围**：原先E3d拟议K4–10，正式冻结前核实包内部是否为稳定性需要额外K3/11；不根据E3c真实ARI结果挑范围。E3c的K5–9仅作敏感性对照，其4/10不在旧网格，不能凭空补入其成绩。
3. **初始化、拟合与预算**：争取使用与E3c一致的共享25D缓存、4累计尺度、full covariance、kmeans init、tol0.001、reg_covar1e-6、max_epochs100；`max_runs`与`convergence_tol`先验证源码、随机状态真正生效、单片CPU/GPU实际墙钟后冻结。不可在有标签评估后倒选最省时间/最高分的K范围、重复数或GPU参数。
4. **验证**：每片先输出AutoK稳定性曲线、完整搜索预算、所有候选K，`best_k`作为预先冻结的主选K，`peaks`仅作探索；无标签选K之后再根据此前相同有标签mask计算ARI/NMI；明确Oracle-K是标签知情参照，种子是技术重复，供体独立n=3。可能需要重复整个AutoK流程以检查选择一致性，并严格记录全部失败。
5. **硬件**：4070笔记本可以测GPU可用性，但CPU/GPU拟合数值可能不同，GPU版需要单独pilot和协议标识；不自动升级CellCharter、不修改旧E3c结果。

## 下一步唯一Windows只读操作

在冻结E3d算法前，用项目现有Python环境执行一次版本/API/GPU预检，打印`cellcharter`、`torchgmm`、`torch`版本、`ClusterAutoK`签名、`GaussianMixture`签名、`torch.cuda.is_available()`与GPU名称（有GPU时）。**不调用.fit、不读取参考标签、不写任何本地输出文件、不改依赖**。取得终端真实输出后再决定：先隔离环境修复随机状态，还是制定CPU/GPU公平测时实验。不得声称E3d已经运行。

## 2026-11-20｜E3d AutoK Windows软件版本/API/GPU只读预检已执行

**用户Windows真实终端**（调用`env_cellcharter/python.exe`，未调用拟合）：
```text
CELLCHARTER_VERSION= 0.3.2
TORCHGMM_VERSION= 0.1.2
TORCH_VERSION= 2.1.2+cu121
AUTOK_SIGNATURE= (n_clusters: 'tuple[int, int] | list[int]', max_runs: 'int' = 10, convergence_tol: 'float' = 0.01, model_class: 'type' = None, model_params: 'dict' = None, similarity_function: 'callable' = None)
GMM_SIGNATURE= (n_clusters: 'int' = 1, *, covariance_type: 'str' = 'full', init_strategy: 'str' = 'kmeans', init_means: 'torch.Tensor' = None, convergence_tolerance: 'float' = 0.001, covariance_regularization: 'float' = 1e-06, batch_size: 'int' = None, trainer_params: 'dict' = None, random_state: 'AnyRandom' = 0)
AUTOK_SOURCE= D:\paper\CellCharter_reproduction\env_cellcharter\lib\site-packages\cellcharter\tl\_autok.py
CUDA_AVAILABLE= True
GPU_NAME= NVIDIA GeForce RTX 4070 Laptop GPU
```
首行另有`xarray_schema`提示`pkg_resources is deprecated`，**仅warning，未导致本次导入失败**。确认GPU可见并不等于AutoK已采用CUDA或GPU性能已验收。版本0.3.2仍未升级。
**上游实现已直接读取**GitHub `CSOgroup/cellcharter` **tag v0.3.2**`src/cellcharter/tl/_autok.py`（blob `a0eeca0ffaab6f98317eac0721ca9ce173fc90f6`）和`src/cellcharter/tl/_gmm.py`（blob `d7205846df88d9ff1847bc27ee59e9eaf81fb062`）：AutoK通过`random_state = self.model_params.pop('random_state',0)`及`random_state=i+random_state`传入不同数值；同版本GaussianMixture的`__init__`只是保存`self.random_state`，未见在该类直接调用`torch.manual_seed`。是否由继承的TorchGMM内部实际使用该属性**需进一步核验本机安装实现**，不可直接认定随机种子正确生效。E3c单任务有自己的显式`torch.manual_seed(info['seed'])`，E3c结果仍冻结，**不重跑或从此推翻其完成审计**。AutoK v0.3.2传入tuple K范围会额外算两侧邻近K；具体范围、max_runs/提前停、CPU/GPU、随机可复现、独立输出与评价隔离均**未最终冻结**。**未启动E3d训练，没有产生best_k/ARI/NMI**。
**唯一下一步**：Windows只读查看本机ClusterAutoK.fit和GaussianMixture.__init__中random_state处理及其源文件sha256，确定与上游版本一致后再讨论独立环境随机播种修补和单片CPU/GPU冒烟。不要自动升级现有E1/E2/E3c环境。

## 2026-11-20｜E3d本机v0.3.2源码哈希核验及已知AutoK随机种子缺陷

用户Windows本机原始终端：`AUTOK_RANDOM_LINES= ['random_state = self.model_params.pop("random_state", 0)', 'clustering = self.model_class(n_clusters=k, random_state=i + random_state, **self.model_params)']`；`GMM_INIT_RANDOM_LINES=['random_state: AnyRandom = 0,', 'self.random_state = random_state']`；`GMM_FIT_SEED_LINES=[]`。本地源文件SHA256：`_autok.py=7c2596df24b81472c7518436a6e4f0fb3b031bcf189ea6d9a307c84e562e29f8`、`_gmm.py=bed1a6e897ed662aca2a3642d1cebcfe0a4c1d733d918faeea8671841841243b`。**SHA256与Git blob SHA-1不可直接比值判等**，但检测到的代码语义与上游v0.3.2一致。

上游官方issue [#122](https://github.com/CSOgroup/cellcharter/issues/122)明确确认旧版`random_state`未实际应用，并于2026-10-15关闭修复；因此当前0.3.2原样`ClusterAutoK`的多次重启**不可当作受控随机重复**。既有E3c脚本独立调用`torch.manual_seed`且E3c全2400格已通过审计，**不因这个E3d风险擅自推翻或重跑E3c**。本地用户报告GPU RTX4070 CUDA=True、cellcharter=0.3.2、torchgmm=0.1.2、torch=2.1.2+cu121；仅警告`pkg_resources`弃用。

新增探索性`experiments/cellcharter_dlpfc/e3d_autok_seeded_pilot_v1.py`：采用在`GaussianMixture.fit`前显式`seed_everything(self.random_state)`的独立子类（**不升级或改写本地第三方包**），只用预定开发切片151509的15D缓存、K候选4..10（AutoK v0.3.2内部还拟合3、11）、仅3次重复用于试测，CPU与GPU顺序运行，无参考标签参与K选择，无ARI/NMI指标、不可纳入正式E3d结果。默认只读、只有显式`--run`启动，输出单独`results/e3d_autok_seeded_pilot_v1`，任何失败保留日志/JSON并停止。**脚本只已上传GitHub，尚未在用户Windows下载/运行，运行性能与正确性未验证；正式E3d的max_runs、设备、统计/复现协议仍未冻结**。下一唯一Windows步骤先只下载到本机独立文件并报告SHA256，后续确认后再执行默认只读/试点；不得现在运行正式全量。

## 2026-11-20｜E3d独立试验脚本已由用户Windows下载并完成SHA256校验

**真实Windows终端回报**：`E3D_PILOT_SCRIPT_READY sha256=830563658a0dacb1bd63652fcccf741fea18edf9c48f480debfec7b4a1254656`。这证明用户本机`D:\paper\CellCharter_reproduction\e3d_autok_seeded_pilot_v1.py`已按GitHub发布内容下载并SHA256检查通过。助手另直接读取GitHub已冻结`e3c_k_sensitivity_single_task_v1.py`计算SHA256=`c3bbe996e8bf5f13775a193061fc4b654d9317170e0dca14b7792c429cd77cca`，与pilot硬编码依赖一致。**截至本回合用户尚未执行E3d预检、更未运行AutoK CPU/GPU拟合或产生best_k，不能认为E3d已经开始正式实验。**

**下一唯一Windows步骤（未执行）**：用原本`env_cellcharter\python.exe`执行`e3d_autok_seeded_pilot_v1.py`，不加`--run`，按脚本验证151509 15D特征与冻结脚本、CUDA，要求看到`E3D_PILOT_PREFLIGHT_PASS`和`DRY_RUN_ONLY NO_TRAINING_NO_FILES_WRITTEN`；如错误提供真实终端全文并停止。预检通过后再另一步决定受控播种CPU/GPU测时，正式E3d网格和统计尚未冻结。E1/E2/E3c全部冻结结果不得修改。

## 2026-11-20 10:35｜E3d seeded AutoK pilot 151509 15D只读预检通过

**证据：用户Windows真实PowerShell输出**：
```text
E3D_PILOT_PREFLIGHT_PASS sample=151509 condition=cum_L0_L1_L2 n=4789 dim=15 cuda=True original_feature_sha256=95879ded7bef09282906b4f992d273472580f5d7748b583342f3e4a64c0cd40f
DRY_RUN_ONLY NO_TRAINING_NO_FILES_WRITTEN
```

先前用户Windows已完成`e3d_autok_seeded_pilot_v1.py`下载SHA256核查（`830563658a0dacb1bd63652fcccf741fea18edf9c48f480debfec7b4a1254656`），此次不带`--run`的程序成功通过源码、数据与CUDA预检；已读取151509的冻结15D缓存，4789spots，特征SHA256如上，与E1/E2已归档一致。另有`xarray_schema`关于`pkg_resources`的弃用UserWarning，当前未阻断执行。**此轮无训练、无拟合、无AutoK best_k、无CPU/GPU测时，也未写入实验文件。** E3c仍冻结，2400/2400完成并已审计。下一唯一建议为Windows单条显式命令运行`e3d_autok_seeded_pilot_v1.py --run`（在隔离目录输出、151509开发样本、15D、K候选4..10，内部包含3与11、3次重复，CPU再GPU；仅探索测时，不用于最终论文结果），保留全部真实输出；若报错停止、留存独立session的`summary.json`和终端日志，先排错，不自动升级软件、不修改冻结E3c。正式E3d盲标签K搜索与运行预算仍未冻结。

## 2026-11-20｜E3d AutoK pilot summary.json CPU/GPU完整结果已从用户终端核对

用户Windows在会话直接粘贴`D:\paper\CellCharter_reproduction\results\e3d_autok_seeded_pilot_v1\20261120T023802Z_28068\summary.json`全文（**仅对话原始文本，助手尚未直接获取本机JSON文件字节或两份预测CSV**）。内容包含`status=completed`、`protocol=E3D_AUTOK_SEEDED_CPU_GPU_PILOT_V1_NOT_PAPER_RESULT`、`sample=151509`、`condition=cum_L0_L1_L2`、`feature_sha256=95879ded7bef09282906b4f992d273472580f5d7748b583342f3e4a64c0cd40f`、`references_used_for_K_selection=false`、`K_candidate_bounds=[4,10]`、`max_runs=3`、`seed_policy=explicit_before_each_GMM_fit`。CPU和GPU均在K=3..11每K完成3次（27次拟合/设备），`chosen_k=4`。

**真实运行时间**：CPU `wall_seconds=25.341`，GPU `19.777`，GPU/CPU加速为`25.341/19.777≈1.281×`，墙钟节省`5.564秒≈21.96%`。这是一张151509切片15D、CPU先GPU后的**单次试运行**，有启动/缓存/顺序影响，不能宣布一般性GPU加速效果。

**CPU稳定性K4..10**：`[0.7986341020,0.7662414500,0.7596862129,0.7675760238,0.7687324854,0.7054318168,0.6938588927]`；**GPU**：`[0.7781916657,0.7444835573,0.7086581291,0.7403812213,0.7382208174,0.7025690473,0.6456510033]`。CPU预测SHA256=`d4eb5f460bfffc7f29b79d5700b1dfe3f76cd126d1e8f271979285ccc7de3779`；GPU预测SHA256=`20aa22a7da099ccf339521ef400dd0b078f8f71b0735162da55aeabfb3147a92`，哈希不同，**不能推断预测相同或不同到何程度**；需直接比较按相同barcode排列的`cpu_predictions.csv`与`gpu_predictions.csv`，用ARI/NMI评价**两预测之间**的一致性，而非与人工参考标签比较。最优K落在候选下边界K4：主方案正式冻结前须有不依赖人工标签的搜索边界规则，避免根据ARI调K范围。

**下一步唯一Windows只读操作**：校验CPU/GPU`predictions.csv`文件SHA256、barcode行数/顺序、聚类标签合法性，计算**设备间**ARI/NMI；不修改数据/不启动训练/不读取人工参考标签。此pilot仅可用于方法/性能可行性，不得作为正式E3d生物学结果；3独立生物供体、E1/E2/E3c冻结结果不变。

## 2026-11-20｜E3d开发试点GPU/CPU预测分区一致性PASS，正式E3d前瞻协议已建立

**用户Windows真实只读验证输出**：
```text
E3D_DEVICE_COMPARISON_PASS n= 4789 ARI= 1.0 NMI= 1.0
CPU_CLUSTER_SIZES= {0: 1183, 1: 1460, 2: 1728, 3: 418}
GPU_CLUSTER_SIZES= {0: 418, 1: 1728, 2: 1460, 3: 1183}
```

用户已根据本机试点`summary.json`中CPU/GPU预测路径和SHA256做只读核对：两文件SHA匹配各自摘要，barcode行数/顺序一致，簇标签为0..3、有效spot数4789、设备间`ARI=NMI=1`。故**在该151509/15D/三次AutoK pilot上**CPU/GPU分区完全一致，仅簇编号交换（按簇大小CPU 0→GPU 3、1→2、2→1、3→0）；**两份预测文件SHA256不同不构成设备结果冲突**。但每K稳定性分值CPU/GPU不完全一样（例如K4 CPU0.798634、GPU0.778192），不能推断其他切片/随机性完全一致。CPU25.341s、GPU19.777s，GPU约1.28倍，只是单次技术试验，非全面性能基准。

**新协议与代码（计划，不是正式数据）**：GitHub新增`experiments/cellcharter_dlpfc/E3D_AUTOK_FROZEN_PROTOCOL_20261120.md`及`e3d_autok_single_config_v1.py`，定稿前瞻**CPU主方案**，K候选2..10（v0.3.2内部辅助K1/11），每切片×尺度5次显式播种、最大100 GMM epochs、无AutoK稳定性早停；全12切片×4尺度×11内部K×5次预计2640次GMM。原边界K4试点之后才扩展到K2，已经看过E3c参考标签表现，因此不能冒充完全独立的历史预注册或最终外部盲测。正式K选择不使用人工标签，所有ARI/NMI仅在产物冻结后评价。源码当前**仅在GitHub生成，未由用户Windows下载/运行/验证**；正式任务尚未开始。下一Windows唯一步骤先下载新脚本并校验SHA256，其后单独只读dry-run，再允许一张切片一尺度冒烟，防止长批量误运行。不得更改任何旧E1/E2/E3c/PILOT输出。此次未上传Windows`summary.json`和预测CSV原始文件到GitHub，仅归档用户终端报告数值。

## 2026-11-20｜E3d单配置dry-run输入校验通过但退出码错误已发现并修复

用户真实Windows终端：
```text
E3D_FIXED_PREFLIGHT_PASS sample=151509 condition=cum_L0_L1_L2 spots=4789 dim=15 cuda=True feature_sha256=95879ded7bef09282906b4f992d273472580f5d7748b583342f3e4a64c0cd40f
DRY_RUN_ONLY NO_TRAINING_NO_FILES_WRITTEN
E3D_FIXED_PREFLIGHT_ABORTED error=SystemExit(0)
```
**结论**：输入/冻结特征/CPU/GPU可见性检查通过，dry-run没有训练或产出结果；但GitHub首发单配置脚本的`if __name__ == '__main__': try: sys.exit(main()) except BaseException`错误地捕获正常`SystemExit(0)`并以错误状态码退出，属于**助手提供代码错误**，不可认定整个脚本退出正常。`--run`也受此退出包装错误影响；**不得直接启动正式拟合直到修复版安装并验证退出码**。

已在GitHub同路径`e3d_autok_single_config_v1.py`仅将最末尾`except BaseException as e`改为`except Exception as e`（不改变数据、算法、实验参数、旧输出），GitHub提交`32c48d77679e022d4cce18f966ef0d385714cc33`；新文件SHA256=`24f500a953e73055d44bfbe3b68e2301f3aeab7e9046035fe31bc2ca81ed8da2`，此前本地旧文件SHA256=`79188c06fbf54aa19b385e606a42f6223551217b710d703a80021a9cf98e8670`。**尚未由用户Windows下载新文件**；下一唯一Windows小步骤先对已验证旧文件做条件检查、备份、下载新文件到临时路径、校验新版SHA256然后替换。成功后再次只读运行并观察`$LASTEXITCODE=0`，不能与下载更新命令合并成一次拟合。E3d主方案仍未产生正式结果；E1/E2/E3c冻结产物不变。

## 2026-11-20｜E3d单配置修复版Windows只读预检及退出码0验收通过

**用户Windows真实终端回报**：
```text
E3D_FIXED_PREFLIGHT_PASS sample=151509 condition=cum_L0_L1_L2 spots=4789 dim=15 cuda=True feature_sha256=95879ded7bef09282906b4f992d273472580f5d7748b583342f3e4a64c0cd40f
DRY_RUN_ONLY NO_TRAINING_NO_FILES_WRITTEN
E3D_FIXED_EXIT_CODE=0
```

已先成功执行旧脚本退出处理bug的安全更新，返回`E3D_FIXED_EXIT_BUG_PATCH_PASS`（修复版`e3d_autok_single_config_v1.py` GitHub SHA256 `24f500a953e73055d44bfbe3b68e2301f3aeab7e9046035fe31bc2ca81ed8da2`）；此次真实只读预检通过且退出码**确实为0**。该预检没有启动训练、没有写入正式实验结果。151509/15D输入n=4789，特征来源哈希如上。**批准的下一唯一步骤**：用户Windows独立执行`& 'D:\paper\CellCharter_reproduction\env_cellcharter\python.exe' 'D:\paper\CellCharter_reproduction\e3d_autok_single_config_v1.py' --sample 151509 --condition cum_L0_L1_L2 --run`；只运行1配置、CPU、11个内部K(1..11)×5 runs=55次GMM；写入隔离目录`results/e3d_autok_fixed_v1/151509/cum_L0_L1_L2`，若该目录已经存在则 fail-closed 不覆盖。需观察`E3D_FIXED_TASK_COMPLETE`及退出码0，或`E3D_FIXED_TASK_FAILED`异常并原样保留manifest/traceback；不因报错自行删目录重跑。正式E3d尚未提供拟合完成证据，E1/E2/E3c及旧pilot保持冻结，人工标签没有用于K选择。

