# Spatial Transcriptomics Clustering Research

> **新对话读档：** [AGENTS.md](AGENTS.md) → [PROJECT_STATE.md](PROJECT_STATE.md) → [最近科研日记](RESEARCH_JOURNAL/2026-11-10.md) → [CURRENT_RESEARCH_HANDOFF.md](CURRENT_RESEARCH_HANDOFF.md)。当前 CellCharter 151507 seed22911 的 L0–L4 五档诊断与逐层边界审计已完成；下一步是审计历史 GMM seed0 L4 重拟合不一致。下方 STAGATE、冒烟等内容为历史背景，不能视为最新状态。

空间转录组聚类研究：可复现实验、方法对照与科研工作日志。

## 1. Research Objective

研究空间转录组聚类中的以下问题：

- 空间连续性（Spatial Continuity）
- 组织边界保留（Boundary Preservation）
- 聚类碎片化（Cluster Fragmentation）
- 表达信息与空间先验之间的权衡

研究目标是通过公平对照与跨切片验证，判断这些现象是否稳定存在，以及是否值得提出新的改进方法。

## 2. Methods

目前涉及：

- E0：Expression-only PCA + Leiden
- S0：Expression-Spatial Graph Fusion + Leiden
- STAGATE：Spatial Graph Attention Auto-Encoder

不同方法的预处理和建图规则可能不同，实验配置需要分别记录。

## 3. Current Experimental Progress

### DLPFC 151669

STAGATE受控实验已经完成：

- 3661个Spot
- 3000个高变基因
- Visium六邻域空间图
- 1000轮训练
- 最终重建MSE：0.146949
- 有效参考注释Spot：3636
- ARI：0.095712
- NMI：0.436221
- Boundary F1：0.116550
- 全部Spot预测簇数：25
- 有效注释Spot中预测簇数：24

观察到类别碎片化以及空间连续性与边界识别之间的权衡。

上述结果仅来自单张切片，属于探索性证据，不代表跨数据集普遍结论。

详细结果见 experiments/151669/EXPERIMENT_LOG.md。

### DLPFC 151507

已完成表达矩阵、Barcode和空间六邻域图检查。

- 4226个Spot
- 12385条无向空间边

STAGATE受控实验已完成（1000轮）：ARI 0.254629，NMI 0.547126；其方法与参数限制见 [151507实验日志](experiments/151507/EXPERIMENT_LOG.md)。

### DLPFC 151507 — CellCharter v0.3.2（技术冒烟与恢复验证）

- 已验证：5000 HVG → 2轮scVI（GPU）→ Visium六邻域（12385条无向边）→ 4跳聚合 → K=7 GMM。
- 保存的scVI潜在特征与CPU重新加载推断最大绝对差异为 1.1920928955078125e-06。
- 保存的GMM权重重新载入后，4226个spot的预测与原CSV完全一致（不一致0个）。
- **GMM在20次迭代上限下未收敛**；2轮scVI仅作冒烟，尚无正式CellCharter ARI/NMI。
- 详见 [CellCharter 151507冒烟与复现审计](experiments/cellcharter_dlpfc/SMOKE_151507_20261108.md)。

## 4. Repository Structure

- scripts/：实验代码
- experiments/：配置、日志、预测及评价结果
- research_notes/：研究问题、假设与文献审查（待建立）
- paper/：论文结构与写作材料（待建立）

## 5. Reproducibility and Limitations

- 原始表达矩阵不包含在本仓库中。
- STAGATE实验依赖独立安装的STAGATE_pyG源码。
- 当前脚本包含本地Windows绝对路径，尚不是可移植的一键复现程序。
- STAGATE使用统一六邻域图，不等同于官方Radius建图的原样复现。
- 参考注释只用于训练后的评价。
- 未利用测试集参考标签寻找最佳聚类参数。
- Spot和空间边不作为独立生物学重复。
- 当前不报告跨样本显著性结论。
- CAN-N仍是候选研究方案，其有效性与创新性尚待验证。

## 6. Research Integrity

区分已完成实验、观察结果、待验证假设与研究计划。

保留负结果和失败记录，不根据评价标签挑选有利配置。

本仓库用于研究过程追踪，不代表论文已经完成或方法得到验证。