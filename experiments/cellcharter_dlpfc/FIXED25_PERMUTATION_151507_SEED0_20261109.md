# CellCharter固定25维邻域置换对照 · DLPFC 151507 · 2026-11-09

> **当前状态：五组GMM运行报告均成功且收敛；待独立核验保存产物；未计算ARI/NMI/Boundary F1。**
> 数据来源：用户在Windows手动运行的终端日志。本文件为原始输出的事实归档，不代表助手远程打开或核验过本机全部文件。

## 研究设计

- 所有五组固定4226 spots、同一份scVI潜在表示及CellCharter 25维聚合特征、K=7、GMM种子0、最多100次EM迭代。
- 对`[scVI, hop1, hop2, hop3, hop4]`五组各5维特征中的邻域块采用共享的固定无不动点随机行置换：组h保留1..h跳与spot正确对应，将h+1..4跳特征块分别打乱。置换随机种子20261109。
- 原始scVI 5维始终不置换，各组输出均25维。
- 这是**固定维数的置换负对照**，并非单独检验纯粹邻域距离效应；置换也改变跨特征块相关性并引入与spot错配的数值。
- 训练阶段`NO_MANUAL_LABEL_FILES_READ: True`；仍未进入后验标签评价；151507已经是探索性切片，不是独立测试集。

## 实际运行情况（仅终端报告）

| 组h | 正确对齐邻域块 | 置换邻域块 | GMM迭代 | 收敛 | 预测各簇spot数（簇0至6） |
|---:|---:|---:|---:|---|---|
| 0 | 0 | 4 | 34 | True | 541,789,641,673,495,732,355 |
| 1 | 1 | 3 | 25 | True | 500,243,930,549,988,363,653 |
| 2 | 2 | 2 | 19 | True | 347,1053,509,539,314,898,566 |
| 3 | 3 | 1 | 35 | True | 486,1317,267,401,669,321,765 |
| 4 | 4 | 0 | 29 | True | 642,314,527,1385,385,279,694 |

五组预测各自总量均为4226。2、3、4跳由同一批次顺序运行，显示`HOP_2_EXIT_CODE=0`、`HOP_3_EXIT_CODE=0`、`HOP_4_EXIT_CODE=0`且每组`FIXED25_CONTROL_RESULT_SAVED: GMM_CONVERGED`；0、1跳来自用户此前单独回报，亦都收敛退出0。

本地运行目录：

```text
D:\paper\CellCharter_reproduction\runs\151507_fixed25_perm_h0_seed0_20261109_174433_394836
D:\paper\CellCharter_reproduction\runs\151507_fixed25_perm_h1_seed0_20261109_174648_424396
D:\paper\CellCharter_reproduction\runs\151507_fixed25_perm_h2_seed0_20261109_174920_860393
D:\paper\CellCharter_reproduction\runs\151507_fixed25_perm_h3_seed0_20261109_174937_316711
D:\paper\CellCharter_reproduction\runs\151507_fixed25_perm_h4_seed0_20261109_174954_951592
```

### 预检查记录

五组形状均`(4226,25)`。终端报告各组前16位特征SHA256分别为：
- h0 `67ff7fa1b542be06`
- h1 `0d45e89befdd6c51`
- h2 `76c872f65ce13967`
- h3 `886b13c59a5bfc3a`
- h4 `f653234c166ce80b`

四个固定置换索引散列前16位在每次运行时一致：
`601fb8166d8f8a65`、`f37a7804bb3ef7bb`、`fe89d0b935f5f409`。

## 重要限制与待验收

1. 上述日志显示**训练成功**，还须检查每组`manifest.json`、`predictions.csv`、`gmm_weights.pt`、`script_snapshot.py`、`permutation_indices.npz`、`run.log`、条形码顺序、完整SHA256及跨组参数一致性；此处尚不声称已通过产物验收。
2. 置换对照的h4输入恰为完整25维原始聚合特征，但它的簇分布与上一次独立h4拟合不同。尽管两者都报告GMM seed=0，**这提示应专门核查跨脚本重跑的一致性以及潜在初始化/执行差异**，不能把模型结果变化简单归因于置换。
3. 五组全部执行后统一做训练后ARI/NMI/Boundary F1评价；没有理由选优舍差或根据标签改参数。单张切片、单个随机种子，不能估计跨供体不确定性。

## 五组独立产物审计（用户2026-11-09终端记录）

用户运行文件、参数、条形码及重建特征核查脚本后返回：

```text
HOP_0_AUDIT_PASS: iterations=34
HOP_1_AUDIT_PASS: iterations=25
HOP_2_AUDIT_PASS: iterations=19
HOP_3_AUDIT_PASS: iterations=35
HOP_4_AUDIT_PASS: iterations=29
SAME_SOURCE_FILES: True
SAME_SCRIPT: True
SAME_PERMUTATIONS: True
H4_PARTITION_AGREEMENT_ARI: 0.713871
FIXED25_ALL_FIVE_AUDIT_PASS
EXIT_CODE=0
```

审计对照内容包括：六个预期产物文件、manifest字段、源文件SHA256、保存脚本的SHA256、每组四套permutation索引的散列及无不动点要求、重建25维特征SHA256、4226个barcodes顺序与唯一性、预测簇范围/数量、以及组4与原始25维聚合特征逐元素相等。**这些是研究者在本机执行的自查结果，不代表助手独立读取本地二进制文件。**

**重要跨次一致性疑点：**固定25维置换h4（未置换）与此前变维度消融h4的预测分区的Adjusted Rand Index仅0.713871，虽输入应相同但输出并未重现。不能据此证明置换/空间半径因果效应。下一步对比两次manifest参数与运行配置，保留两次结果并检查聚类随机性，之后统一后验评价五组。

## 两次h4模型manifest参数核对（后续用户终端输出）

- 变维度消融h4：K=7、full covariance、kmeans初始化、容差0.001、正则1e-6、100次最大EM、CPU、seed0；GMM迭代24，NLL=4.6140360832214355。
- 固定25维置换h4：**同名超参数值**（manifest键名不同）；GMM迭代29，NLL=4.721235275268555；输入特征sha256=`f653234c166ce80b80e1971b387439779ebe92745087d742c5821beedf1c9463`。旧h4的打印摘要中**未包含**`feature_matrix_sha256`键，不能单凭该摘要宣称两者实际输入二进制相同。
- 软件包版本完全一致：CellCharter 0.3.2、TorchGMM 0.1.2、Torch 2.1.2+cu121、PyTorch Lightning 1.9.5、AnnData 0.9.2。
- 两份h4预测ARI=0.713871（不需要人工标签）。差异来源仍未查明，可能涉及脚本中的实际随机数/初始化调用或输入实现细节；**不能将输入内容一致或随机数机制直接视为已证实**。须在不覆盖既有实验的前提下核对脚本快照及实际输入字节；评价时标明重复拟合不一致，随后考虑多个随机种子重复。
- 统一后验评价可以进行，但必须复用既有人工标签、空间边的同一口径；原始`evaluation_provenance.json`记录151507有4221已标注spots、12381条有效边、950条参考边界，人工注释与组织坐标CSV的完整SHA256分别为`00b0d2599702ddd1506e6bcb41b0c6fa636f290c3355b605f7d34b49034de428`和`5c5be4dcd51c914bad02634f1ed2d96bd0c200ae487e236f644d94ded983efd0`。
