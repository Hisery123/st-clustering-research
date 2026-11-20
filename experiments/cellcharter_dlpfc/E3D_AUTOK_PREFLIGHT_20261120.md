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
