# PROJECT_STATE · 第三篇空间转录组聚类论文

> 更新：2026-11-10。此文件为**当前存档**，不是原始实验记录或独立验证。详见 [交接索引](CURRENT_RESEARCH_HANDOFF.md) 和 [当日日记](RESEARCH_JOURNAL/2026-11-10.md)。旧 README / handoff 正文中的早期「L3未执行」描述已经过期。

## 目标与边界

- 基线：CellCharter v0.3.2 适配版；研究 DLPFC 空间聚类的组织连续性—边界保留权衡。
- 当前证据等级：**探索性单切片（151507）＋单 seed22911＋Oracle K=7**。尚不是完全同版本作者复现或独立测试。
- 与作者协议差异：scVI latent=5、5000 HVG、重建 Visium 六邻域、TorchGMM CPU，而非作者旧版 PyCave 与其预处理 h5ad。基线 scVI 已在 GPU 训练；此后 L0–L4 复用 latent。
- Windows 本地：训练 `D:\paper\CellCharter_reproduction`；数据 `D:\paper\ST_Benchmark_Planning\mvp\data\151507`；Git checkout `D:\paper\st-clustering-research`；Python `D:\paper\CellCharter_reproduction\env_cellcharter\python.exe`。

## 已完成、可追溯的实验

- 151507：4226 spots、4221 有标签 spots，12385 物理无向边、12381 可评价边、950 条人工跨层参考边界。
- seed22911 L0–L4 五档聚合+GMM 已执行，ARI分别为 **0.362131 / 0.444156 / 0.457461 / 0.469696 / 0.496146**；NMI分别为 **0.441915 / 0.569587 / 0.604740 / 0.585078 / 0.675436**。L3 初次评价标签字符串有错，GMM/predictions 已生成；后用独立恢复脚本从预测重算，保留失败记录。L3 [恢复指标](experiments/cellcharter_dlpfc/snapshot_20261110/results/cellcharter_v032_151507_seed22911_L3_diagnostic/metrics_recovered.json) 是按真实终端 JSON 转录入 GitHub，未核对原文件字节。
- 五档统一边界审计已完成（终端显示 `ALL_DEPTH_BOUNDARY_AUDIT_COMPLETE`）；全局边界 F1：**0.175802 / 0.162024 / 0.132590 / 0.136045 / 0.171509**。完整计数见 [全局审计记录](experiments/cellcharter_dlpfc/snapshot_20261110/BOUNDARY_AUDIT_151507_SEED22911_20261110.md)。
- 逐组织层结果已由用户打印，见 [逐层审计](experiments/cellcharter_dlpfc/snapshot_20261110/LAYERWISE_BOUNDARY_151507_SEED22911_20261110.md)：L4 下 L5/L6 边界检出 0/145，L4/L5 约 3/160；但上层界面并非一致单调下降。L0 高检出伴随多个层内的高错误分割率。
- 历史 seed0 的 [跳数消融](experiments/cellcharter_dlpfc/HOP_ABLATION_151507_SEED0_20261109.md) 与 [固定25维置换](experiments/cellcharter_dlpfc/FIXED25_PERMUTATION_151507_SEED0_20261109.md) 已运行；不可混为 seed22911 的重复，也不能视为纯粹深度因果控制。

## 当前阻碍／尚未完成

1. **GMM 重拟合一致性疑点（两份 manifest 已读取）**：2026-11-10 用户提供完整历史 seed0/L4 的两份 manifest，均报告相同来源特征 SHA256、K7/full/kmeans/seed0/CPU、容差0.001/正则1e-6/100上限；但脚本 SHA256 不同，旧 manifest 无最终输入矩阵 hash，GMM 分别在24/29迭代收敛，NLL=4.6140360832/4.7212352753。早先两份预测分区 ARI=0.713871。完整表格见 [GMM manifest 审计](experiments/cellcharter_dlpfc/GMM_L4_SEED0_MANIFEST_AUDIT_20261110.md)。**实际输入矩阵是否完全一致、随机调用顺序是否解释差异仍未知**。
2. 聚合深度从 L0 到 L4 同时把维度从 5 增到 25。旧固定25维置换会破坏块与 spot 对应关系，因此不足以单独证明「过度平滑」。
3. 五档逐层分析 CSV、L3 预测和原始失败状态等本地文件尚未完整上传/外部复核；不能把终端打印的四位小数当全精度 CSV。
4. 跨随机种子、独立样本或供体、最近邻文献查新、候选增量机制及消融**未完成**。151507 已密集探索，不是独立留出测试切片。

## 最优先的一件事

**只读检查两次历史 L4 seed0 的 manifest / script_snapshot / 实际输入证据，排查拟合差异来源；不重跑训练。**

- 旧 L4：`D:\paper\CellCharter_reproduction\runs\151507_hop_ablation_h4_seed0_20261109_151425_400946`
- 固定25维 L4：`D:\paper\CellCharter_reproduction\runs\151507_fixed25_perm_h4_seed0_20261109_174954_951592`
- 两目录经用户列示均存在 `manifest.json`、`predictions.csv`、`gmm_weights.pt`、`run.log`、`script_snapshot.py`；第二目录还含置换索引。完整配置输出仍待确认。
- 用户已回传并核对两份 manifest；下一步查看脚本快照中实际输入矩阵构建、seed 与 GMM fit 调用顺序。**不要重复提出此前已经做完的 L3、五档边界审计。**

## 最新脚本快照审查（2026-11-10）

用户已回传两份 `script_snapshot.py` 的关键行：旧 L4 在构建 AnnData 后设置 `torch.manual_seed(0)` / `np.random.seed(0)`；固定25维 L4 在设置种子后才构建 AnnData。两者均在创建 `cc.tl.Cluster` 前设置种子，不能据此断定 AnnData 消耗随机数或 TorchGMM 非确定性。旧 h4 从原始聚合矩阵截取完整25列，新 h4 返回 C-contiguous float32；下一步**只读核对最终数组 SHA256**（不重训）。详情 [审计追加记录](experiments/cellcharter_dlpfc/GMM_L4_SEED0_MANIFEST_AUDIT_20261110.md)。

## 状态维护规则

每次实验或重要科研判断归档，AI 同步更新本文件、`CURRENT_RESEARCH_HANDOFF.md` 与当日 `RESEARCH_JOURNAL/YYYY-MM-DD.md`；GitHub 提交不等于本地已拉取。
