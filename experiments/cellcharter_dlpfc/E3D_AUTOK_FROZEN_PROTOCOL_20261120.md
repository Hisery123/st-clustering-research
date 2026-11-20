# E3d：独立AutoK无标签选择K — 正式实验协议 v1（2026-11-20）

> **状态：前瞻冻结实验方案；本文件形成于151509/15D探索性CPU/GPU试点完成之后、正式E3d全12片训练启动之前。** 过去已对E1/E2/E3c参考层标签ARO/NMI做过分析，因此不能称本研究从未接触过参考标签、也不能把这个方案追溯成探索前预注册。无标签只描述单次**K选择计算过程**不读取标签。用户Windows执行；此文档/代码提交不意味着训练已开始。

## 证据、目的、边界

- E1/E2已审核1200格；E3c固定K=5..9已审核2400格（480格知情Oracle-K历史复用，1920格新拟合）。这些结果是标签知情后验参照，不可当作无标签调参选K。
- AutoK试点：151509、15D、候选K4..10、每K3次（内部K3..11），显式播种，CPU和GPU各27次GMM：CPU25.341s、GPU19.777s，均选K4；设备间聚类ARI=NMI=1、簇编号不同。只有1张开发切片/单次设备对照，不能推广速度/结果稳定性。CPU/GPU稳定性曲线不完全一致。
- E3d研究问题：在不给人工标签决定K的情况下，CellCharter稳定性选K是否随尺度/切片改变，以及固定尺度的ARI/NMI后验评价与历史Oracle-K（标签知情）如何区别。
- **正式E3d主分析固定CPU**，使GMM精度/环境与E3c CPU方案更接近。GPU只作为已完成pilot的计算工程探索；后续若要正式使用GPU须修订协议并分别报告，不合并设备结果。

## 预先固定的方法学与预算

1. 数据：12个DLPFC切片（151507..151510、151669..151676）×4个冻结累计特征10/15/20/25D，全部复用同一E1/E2 25D缓存、相同block顺序/spot barcode/原始SHA。不得重新训练scVI或因为AutoK输出改变输入。151507本地曾有错误metadata.tsv，使用原冻结E1/E2缓存并保留已记录的上游卫生限制。
2. **搜索候选K=2,3,...,10**。变更理由为试点K=4碰到原候选4..10下边界，因此在正式方案启动前，仅根据无标签稳定性边界扩展左侧到K2；原K上界10保留。CellCharter 0.3.2 AutoK使用tuple(2,10)时额外拟合辅助K1和K11，只对K2..10计算并选择best_k。新范围是在**试点之后**修订，不是独立盲选先验；固定后**即使正式结果仍选K=2/10也不再次拓宽**，只记录边界命中率。
3. 每个固定切片×尺度使用**max_runs=5、convergence_tol=0.0**，强制5个AutoK随机初始化/候选K（不触发AutoK自身稳定性提前停止），相同seed序列22911–22915；CPU、full covariance、kmeans初始化、GMM convergence_tolerance=0.001、covariance_regularization=1e-6、max_epochs=100、float32、1 device。不改变梯度/浮点矩阵精度，不设置Torch Float32 matmul_precision为medium/high。每个组合**11种内部K×5次=55次拟合**，全48组合2640次拟合，时间/失败率以实测为准；计算数为计划，不是已执行。
4. 由于本机CellCharter 0.3.2的`random_state`未正确施用于随机数，使用已试点显式播种的`GaussianMixture.fit`子类；每次拟合前`random.seed`、`numpy.random.seed`、`pytorch_lightning.seed_everything(...,workers=True)`，继承CellCharter GMM原拟合/预测、不修改site-packages。**Random seeds are technical replicates, not independent biological samples.**
5. 每个切片×尺度只产出一个原生AutoK`best_k`、稳定性每K值、全部候选/实际重复次数、chosen_k预测CSV与其SHA、来源/特征SHA、elapsed seconds、成功/失败/完整配置、版本。单任务脚本默认只读，只有`--run`才拟合，先从151509一配置做正式方案冒烟；若失败保留单任务输出/状态，不覆盖、不删除、不自动重试。所有输出隔离在`results/e3d_autok_fixed_v1`，不得动E1/E2/E3c与旧pilot目录。
6. **盲标签边界**：AutoK拟合与K选择阶段不得读取人工`manual_layer_annotations.csv`参与打分、挑K、改变参数或选择最优迭代；`e1.preflight`是旧缓存及输入完整性预检，输出的Oracle-K元数据绝不用于新K选择。先保存cluster预测/K/stability和来源信息，再由另一只读审核脚本按**既有相同spot mask**计算ARI/NMI；不可把参考标签数K=5/7称无标签AutoK。
7. **公平分析**：完全报告48个slice×scale组合的K分布、边界命中率、不同深度K变化、后验ARI/NMI和阴性结果；与历史E1/E2 Oracle-K对比须保留标签知情说明。3个供体才是独立生物层级；切片嵌套供体，spot、随机种子、候选K不得混作独立重复。独立外部验证/基线E5后续另做，不能提前断言方法改进或显著性。
8. **GO/STOP**：151509/15D首个正式协议冒烟满足预期K维度、共55次拟合、内生seed正确传入、输出manifest/CSV、每K稳定性有限、设备耗时可接受→可再规划其余47个；否则STOP并公开记录修改原因/时间，形成v2而不是静默改v1。用户本机确认前任何脚本状态标记为**待测试**，不可称全量已完成。

## 代码和日志来源

- 上游CellCharter v0.3.2 `ClusterAutoK` 实现： https://github.com/CSOgroup/cellcharter/blob/v0.3.2/src/cellcharter/tl/_autok.py
- 官方random_state问题： https://github.com/CSOgroup/cellcharter/issues/122
- 历史只读试点与GPU加速结论见 `e3d_autok_seeded_pilot_v1.py` / `E3D_AUTOK_PREFLIGHT_20261120.md`；单次结果不构成设备稳健性证明。
