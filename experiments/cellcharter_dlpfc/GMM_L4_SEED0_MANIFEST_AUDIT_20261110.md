# 历史 seed0 L4 两次 GMM manifest 对照（2026-11-10）

## 证据和边界

用户在 Windows PowerShell 使用 `Get-Content -Raw` 读取 2026-11-09 两份原始 manifest，并将完整 JSON 输出于当前会话。**本文件依据用户终端文本审计；不是 GitHub 已收到本地 manifest 原始字节或权重。**

- 旧 L4：`D:\paper\CellCharter_reproduction\runs\151507_hop_ablation_h4_seed0_20261109_151425_400946\manifest.json`
- 固定25维 L4：`D:\paper\CellCharter_reproduction\runs\151507_fixed25_perm_h4_seed0_20261109_174954_951592\manifest.json`
- 两次均标记 `GMM_CONVERGED`、`manual_labels_read=false`、`ARI_computed=false`；151507 是探索性切片，K=7 来源于已知人工类别数。

## 对照结果

| 项目 | 旧 L4 | 固定25维 L4 |
|---|---|---|
| sample / hop / feature dim | 151507 / 4 / 25 | 151507 / 4 / 25 |
| source run | 151507_baseline_seed0_20261109_135812_583663 | 相同 |
| source_aggregated_sha256 | 96844547f535114184defe1eff6ef6bd34ee6b7c22b8bbf51a59da9cd3e0a13a | 相同 |
| source_latent_sha256 | 7cc6d513ec52aea97f346ddc543073c9b2209692f9dd27f2394171f89f5f8d91 | 相同 |
| source_predictions_sha256 | eeff8124a049636299aba75cf129936cf6cbeac955ac180268c42fef2190ab5a | 相同 |
| script_sha256 | 633bb6ed96c776bfd6f7a9e115fcb323684c16489cc4a75f43f9b1fad61a5075 | 20fa357ad7ff43e6408f86be3f5bbcf576058d356d1d8423e2711c1051ab5fdf |
| feature_matrix_sha256 | 未记录 | f653234c166ce80b80e1971b387439779ebe92745087d742c5821beedf1c9463 |
| permuted_neighborhood_blocks | 不适用（截取完整前25列） | []（按设计无置换） |
| random seed | 0 | 0 |
| GMM K/covariance/init | 7 / full / kmeans | 7 / full / kmeans |
| tolerance / regularization / max EM | 0.001 / 1e-6 / 100 | 相同 |
| CPU/software | CellCharter 0.3.2; TorchGMM 0.1.2; torch 2.1.2+cu121; Lightning 1.9.5 | 相同 |
| converged EM iterations | 24 | 29 |
| final NLL | 4.6140360832214355 | 4.721235275268555 |

注：NLL 以用户终端输出的原始 JSON 值为准。先前历史记录两次分区 ARI=0.713871（两次预测互相比，不是人工标签 ARI）。

两次聚类计数：
- 旧 L4: [701,253,604,446,582,615,1025]
- 固定25维 L4: [642,314,527,1385,385,279,694]

## 判断和下一步

1. 两个**来源文件** hash 相同，不代表两份最终 **GMM 输入矩阵**已经按相同序列化方式逐字节核对。旧 manifest 缺少最终矩阵 hash，尽管旧脚本按记录为前25列、新脚本 h4 不置换，仍需实际代码核查。
2. 脚本 hash 不同且历史检查提示 seed 与 AnnData 创建的执行顺序不同；这只能构成待验证原因，**不能据此声称 TorchGMM 非确定性已证实**。
3. 在相同实际输入矩阵、同 seed、同完整拟合调用确认之前，不将 NLL 或分区差异归因于算法模块；也不将历史不同批次的 h4 结果混成一组公平对照。
4. 唯一下一步：只读查看两份 `script_snapshot.py` 的输入矩阵构造、随机种子与 GMM fit 邻近代码，随后决定是否需要仅用现有矩阵/权重开展无训练哈希核查。

## 2026-11-10 后续：两份 script_snapshot 的关键行只读检查

来源：用户通过 PowerShell `Select-String -Context 5,5` 输出的关键代码片段（本次尚未获取两份完整脚本原始文件）。

- 旧 L4 第106行：`X = np.ascontiguousarray(all_features[:, :n_features], dtype=np.float32)`，其中 hop=4，n_features=25；第169–170行在已创建 AnnData 后调用 `torch.manual_seed(SEED)`、`np.random.seed(SEED)`；171行创建 `cc.tl.Cluster`，188行 `model.fit(adata)`。
- 固定25维 L4 第142行返回 `np.ascontiguousarray(X, dtype=np.float32)`；第202行记录 `feature_matrix_sha256`；第246–247行设全局随机种子，第248–250行才创建 AnnData、设置 obs_names/obsm；第251行创建 `cc.tl.Cluster`，268行 fit。
- 两者均在创建 Cluster 之前设种子，**差异在设置种子与创建 AnnData 的先后顺序**。尚未证明 AnnData 构建是否消耗相关随机数、是否造成预测不一致。旧 manifest 未记录实际输入数组 hash，不能把同源文件 hash 等同于最终 GMM 输入完全相同。
- 下一个最小只读操作：从历史来源 `aggregated.npz` 重新构造两种脚本的 hop4 输入，计算按 C-contiguous float32 转换后的数组 SHA256，与固定25维 manifest 记录的 `f653234c166ce80b80e1971b387439779ebe92745087d742c5821beedf1c9463` 核对；此核对不训练模型、不修改历史结果。

## 2026-11-10 后续：GMM 输入重建 SHA256 校验通过

用户在 Windows 上只读加载历史共同来源 `151507_baseline_seed0_20261109_135812_583663/aggregated.npz`，报告其数组包含 `barcodes (4226,) <U18`、`X_cellcharter (4226,25) float32`。对 `X_cellcharter[:, :25]` 执行 `np.ascontiguousarray(..., dtype=np.float32)` 并计算 `sha256(x.tobytes())`，实际得到：

`f653234c166ce80b80e1971b387439779ebe92745087d742c5821beedf1c9463`

终端显示 `MATCH_FIXED25_L4: True`，与固定25维 L4 manifest 里的 `feature_matrix_sha256` 一致。该结果支持：按旧脚本的输入切片/转换重建出的矩阵与新 h4 记录的矩阵字节一致。**仍非直接读取旧运行时内存的证据，旧 manifest 不含最终矩阵 hash**。

下一步最小诊断：只读/内存内测试在设置相同 Torch/NumPy seed 后创建旧/新形式 AnnData，是否消耗 Torch/NumPy 随机数状态。无需重新训练 GMM、无需创建输出文件。若随机状态均不变，再检查 fit 内部初始化、执行环境/调用差异；不预断定随机性成因。

## 2026-11-10 后续：AnnData 创建与全局 RNG 状态测试

首次检测脚本由助手写错，将 `torch.manual_seed(0)` 返回的 `torch.Generator` 当成具有 `get_rng_state()` 的对象，报 `AttributeError`，无有效结果；随后更正为直接通过 `torch.get_rng_state().clone()` 与 `np.random.get_state()` 比较创建 AnnData 前后的全局状态。

用户 Windows 实际终端输出：

```text
old TORCH_RNG_CHANGED: False NUMPY_RNG_CHANGED: False
fixed25 TORCH_RNG_CHANGED: False NUMPY_RNG_CHANGED: False
```

该结果表明测试代码中旧/新形式 AnnData 创建、设置 obs_names 和 obsm **未改变所检测的 PyTorch CPU 和 NumPy 全局 RNG 状态**。本次代码用全零假特征而非原聚合矩阵，检查的是构造行为而非完整 GMM 拟合；未测试 TorchGMM 内部独立 generator、数据加载器随机性或全训练数值路径。此前“seed 与 AnnData 创建先后顺序”作为差异解释的支持度下降，但仍不可宣称已排除一切 RNG 影响。

下一步：只读比较两份 `script_snapshot.py` 中完整 `cc.tl.Cluster(...)` 参数、AnnData 构造与设置特征的代码，检查有无除了上述显式 GMM manifest 外的调用差异；再决定是否需要最小隔离 GMM 拟合实验。不重复 scVI 或聚合训练。

## 2026-11-10：两份 GMM 代码片段的逐行核查

用户 PowerShell 已实际输出旧 L4 的 `script_snapshot.py` 第100–122和165–190行，以及固定25维 L4 的第110–143和238–270行。

- 旧 L4：`X = np.ascontiguousarray(all_features[:, :25], dtype=np.float32)`，然后创建 AnnData、设置 obs_names/obsm，随后执行 `torch.manual_seed(SEED)` 和 `np.random.seed(SEED)`，再构造 `cc.tl.Cluster` 并 fit。
- 固定25维 L4：`build_features(hop=4)` 的 `range(hop+1, 5)` 是空区间，返回完整 `original.copy()` 的 contiguous float32，之后先设置 Torch/NumPy seed、再创建和填充 AnnData、再构造 Cluster 并 fit。
- **两者完整显式调用均一致：** `n_clusters=K`, `random_state=SEED`, `covariance_type="full"`, `init_strategy="kmeans"`, `convergence_tolerance=0.001`, `covariance_regularization=1e-6`, `trainer_params={"accelerator":"cpu","devices":1,"max_epochs":MAX_EM_ITERATIONS,"enable_progress_bar":False}`。
- 结合共同源和重建数组哈希一致、AnnData 全局 RNG 测试均为 False，本次尚**未发现明确的显式拟合参数或输入值差异**。未完整检查来源的 barcode 顺序、`load_source` 和数据下游取样；也未运行同输入同配置重复拟合，**不能归咎于 TorchGMM 的固有非确定性**。

**下一步**：只读检查两份脚本数据加载、`barcodes` 与 `X` 的排序/对齐方式，重点寻找是否按相同原始顺序将 spot 送入 GMM。尽管聚类本身输入值 hash 已复算，观察的预测分区 ARI 也要求比较两个 predictions.csv 中相同 barcode 的归属，不能仅按行号假设对齐。
