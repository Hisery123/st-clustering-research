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

