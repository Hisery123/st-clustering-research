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

## 两份h4脚本快照关键代码行核对（用户本机只读输出）

- 两份manifest记录的`source_aggregated_sha256`都为`96844547f535114184defe1eff6ef6bd34ee6b7c22b8bbf51a59da9cd3e0a13a`，`source_latent_sha256`都为`7cc6d513ec52aea97f346ddc543073c9b2209692f9dd27f2394171f89f5f8d91`。
- 旧h4代码第106行：`X = np.ascontiguousarray(all_features[:, :n_features], dtype=np.float32)`（对于h4为全25列）；新h4第105行加载`np.asarray(aggregate, dtype=np.float32)`，第142行重建`np.ascontiguousarray(X, dtype=np.float32)`且其preflight在无置换h4下断言输入与原矩阵逐元素一致。**输入应相同仍需用两次实际数据字节直接核验以排除潜在差异**。
- 旧h4快照第169/170行在模型构建前`torch.manual_seed(0)`与`np.random.seed(0)`，第171行开始创建`cc.tl.Cluster`，第188行fit；新h4快照第246/247行同样设置随机种子，随后第248/250行创建AnnData与`obsm`，第251行创建`cc.tl.Cluster`，第268行fit。两套`script_sha256`不同：旧`633bb6ed96c776bfd6f7a9e115fcb323684c16489cc4a75f43f9b1fad61a5075`，新`20fa357ad7ff43e6408f86be3f5bbcf576058d356d1d8423e2711c1051ab5fdf`。
- 上述日志为关键字抽取结果，并未展示完整的模型实例化参数行与函数体。**差异来源仍未定位**，不能直接声称TorchGMM随机性已经被证实，更不能合并两次h4为相同模型。
- 阅读检查`H4_SCRIPT_COMPARISON_READ_PASS`、`EXIT_CODE=0`。

## 随机种子位置与评价数据定位检查（用户2026-11-09终端）

用户进一步打印两套GMM完整实例化参数段：K=7，random_state=0，full协方差，kmeans初始化，收敛容差0.001、正则1e-6，CPU单设备、最多100 epochs、无进度条；**显式设置一致**。

可见执行顺序差异：旧脚本先在GMM函数内构造AnnData，后执行`torch.manual_seed(SEED)`、`np.random.seed(SEED)`并实例化GMM；新脚本先设置这两个全局种子，随后构造AnnData、再实例化GMM。**尚未证明该顺序差异实际消耗随机数或解释跨运行分区ARI=0.713871**，需进一步独立验证；绝不可把来源推测记作结论。

第一次自动发现评价源CSV的脚本在`D:\\paper\\CellCharter_reproduction`下搜索时**排除了`runs`整个子目录**。用户终端显示：`NOT_FOUND_UNDER_PROJECT: manual_annotations`、`NOT_FOUND_UNDER_PROJECT: tissue_positions`以及`EVALUATION_SOURCE_PREFLIGHT_FINISHED`、`EXIT_CODE=0`。因此该输出只能说明限定范围内未发现符合完整SHA256的原始文件，**不能据此判断标签/坐标文件丢失**。下一步扩大到其他研究工作目录，找到文件后必须检查SHA256与旧评价一致，才可直接复用旧指标口径。


## 五组统一后验评价完成（2026-11-09，研究者Windows终端输出）

终端返回：
```text
EVALUATION_SOURCE_PASS: labeled=4221 edges=12381 reference_boundaries=950
FIXED25_HOP_0_EVALUATED
FIXED25_HOP_1_EVALUATED
FIXED25_HOP_2_EVALUATED
FIXED25_HOP_3_EVALUATED
FIXED25_HOP_4_EVALUATED
FIXED25_ALL_FIVE_EVALUATION_PASS
EXIT_CODE=0
```

本次评价在训练后进行，使用之前通过SHA256校验的151507人工层注释`D:\paper\ST_Benchmark_Planning\mvp\data\151507\manual_layer_annotations.csv`及组织坐标`D:\paper\ST_Benchmark_Planning\mvp\data\151507\tissue_positions_list.csv`，与上一轮评价相同口径：4221个有效标注spot、12381条有效空间边、950条参考边界。评价输出来自用户终端摘要；助手尚未直接核验本机CSV/JSON原始字节。

| Hop | Feature dimension | ARI | NMI (arithmetic) | Boundary precision | Boundary recall | Boundary F1 | Spatial neighbor agreement | Pred boundary edges | True positive boundary edges |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 25 | 0.081178 | 0.125404 | 0.083368 | 0.847368 | 0.151801 | 0.220095 | 9656 | 805 |
| 1 | 25 | 0.296666 | 0.425794 | 0.093543 | 0.652632 | 0.163632 | 0.464664 | 6628 | 620 |
| 2 | 25 | 0.379413 | 0.543273 | 0.079572 | 0.328421 | 0.128105 | 0.683305 | 3921 | 312 |
| 3 | 25 | 0.466840 | 0.599026 | 0.108645 | 0.195789 | 0.139745 | 0.861724 | 1712 | 186 |
| 4 | 25 | 0.497627 | 0.624839 | 0.120000 | 0.173684 | 0.141935 | 0.888943 | 1375 | 165 |

终端报告输出目录：`D:\paper\CellCharter_reproduction\runs\151507_fixed25_permutation_evaluation_seed0_20261109`，`fixed25_permutation_metrics.csv`、`evaluation_provenance.json`据评价脚本应当保存在该目录。后续需核对两份文件实际内容以及所引用的五组预测SHA256；目前不得声称助手已打开两份本地文件。

### 描述性趋势

- 0→4跳总体ARI单调上升0.081178→0.497627，NMI单调上升0.125404→0.624839。
- Boundary recall单调下降0.847368→0.173684；Spatial neighbor agreement单调上升0.220095→0.888943。
- **Boundary F1非单调**：0.151801、0.163632、0.128105、0.139745、0.141935。1跳最高，不能宣称F1随邻域对齐跳数单调下降。
- 0跳高召回源自9656条预测边界中的805条正确，Precision 0.083368；假阳性=8851条。4跳预测1375条中的165条正确，Precision 0.12；假阳性1210条。相对于950条真实边界，随机预测边界的基准命中率与边界占比有关，不能简单只比召回。
- 此对照每个未启用的邻域块采用**独立全行随机置换**，因此0跳是由正确scVI与4个错位邻域块组成的25维噪声对照，**不等同于真正的仅5维scVI基线**。虽然维度固定，但已改变信号质量、同spot相关性、变量分布的联合结构，不可宣称「仅空间传播半径变化」或过度平滑因果成立。
- 本次h4（ARI 0.497627、NMI 0.624839、Boundary F1 0.141935）不等于旧变维度h4（ARI 0.467183、NMI 0.590068、Boundary F1 0.120438）；先前两份h4预测分区之间ARI为0.713871，随机性/实现差异尚待核查，**不得将h4两套结果差归因于维度或随机置换（本次h4没有置换）**。
- 一张已探索切片、单种子、GMM已知参考K=7，属探索性后验评价而非独立测试；不能把边/spot视为独立生物学重复，未运行显著性检验。

### 评价数据定位

研究者按旧评价溯源的完整SHA256搜索后确认两个原始CSV：
- `D:\paper\ST_Benchmark_Planning\mvp\data\151507\manual_layer_annotations.csv`：`00b0d2599702ddd1506e6bcb41b0c6fa636f290c3355b605f7d34b49034de428`
- `D:\paper\ST_Benchmark_Planning\mvp\data\151507\tissue_positions_list.csv`：`5c5be4dcd51c914bad02634f1ed2d96bd0c200ae487e236f644d94ded983efd0`

评价运行时报告数据校验通过。下一步应核验本地评价CSV与JSON的内部一致性、五组预测文件SHA256、原始指标口径，并将两组曲线以分面形式展示且标明训练配置不完全可直接对齐；然后考虑多seed及跨切片、预注册的更严格对照。

## 固定25维统一评价CSV产物一致性核查（2026-11-09）

研究者在Windows上读取`fixed25_permutation_metrics.csv`与`evaluation_provenance.json`，逐行根据`true_positive_boundary_edges`、`predicted_boundary_edges`、950条参考边界及12381条有效空间边重新计算Boundary Precision/Recall/F1和空间邻居一致率，并核对每组与CSV的值（atol=1e-6）。终端真实输出：

```text
HOP_0_METRICS_CONSISTENT
HOP_1_METRICS_CONSISTENT
HOP_2_METRICS_CONSISTENT
HOP_3_METRICS_CONSISTENT
HOP_4_METRICS_CONSISTENT
CSV_ROWS: 5
PROVENANCE_KEYS: ['design', 'evaluated_spatial_edges', 'evaluation_type', 'labeled_spots', 'limitations', 'manual_annotations_sha256', 'manual_labels_used_for_training', 'nmi_average_method', 'previous_evaluation_provenance_sha256', 'reference_boundary_edges', 'reference_class_count_used_to_set_K', 'runs', 'sample_unit', 'section', 'seed', 'tissue_positions_sha256']
PROVENANCE_RUNS: 5
FIXED25_EVALUATION_ARTIFACT_AUDIT_PASS
EXIT_CODE=0
```

**审计范围**：上述值的一致性、CSV五行与hop0..4/25维、JSON可解析和五个run条目。此次脚本**没有逐项对比JSON中各份预测的SHA256、没有独立重算ARI/NMI**；不得把`FIXED25_EVALUATION_ARTIFACT_AUDIT_PASS`扩大解释为全部评价指标及全部溯源哈希已经外部独立复算。

**作图决策**：以旧变维度消融`hop_ablation_metrics.csv`和固定25维置换对照`fixed25_permutation_metrics.csv`本机原始文件作2行3列同坐标范围SVG，不绘制虚构误差棒、不将两次h4输出差当作对照效应；后续仍需跨随机种子及独立切片验证。
