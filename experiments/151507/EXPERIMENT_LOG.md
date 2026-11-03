# STAGATE — DLPFC 151507 实验记录

## 1. 实验身份

- 数据集：DLPFC 151507
- 实验阶段：受控基线实验
- 状态：训练、聚类、评价和初步诊断完成
- 研究问题：空间连续性、组织边界识别与类别碎片化之间的关系
- 代码：scripts/stagate_151507_controlled.py

## 2. 训练配置

- 模型：STAGATE_pyG
- Spot数量：4226
- 空间图：Visium六邻域，12385条无向边
- HVG：3000，Seurat v3
- 预处理：原始计数选择HVG；全基因归一化至10000并log1p；最后提取HVG
- 隐藏层：[512, 30]
- 训练轮数：1000
- 学习率：0.001
- 权重衰减：0.0001
- 梯度裁剪：5.0
- 训练随机种子：0
- GPU：RTX 4070 Laptop GPU
- Leiden：15近邻、Euclidean、resolution=1.0、seed=42、leidenalg
- 参考注释：manual_layer，仅用于训练后评价

本实验使用统一六邻域空间图，并非STAGATE官方Radius建图方案的完全原样复现。

## 3. 已完成训练

- 初始记录重建MSE：0.5120212435722351
- 最终重建MSE：0.1669292449951172
- 训练耗时：32.31699090000029秒
- CUDA峰值已分配显存：507.02392578125 MiB
- 嵌入形状：4226 × 30
- 1000轮loss.csv与embedding.csv完整性检查通过
- Barcode与原始元数据顺序完全匹配

## 4. 聚类评价

- 总Spot：4226
- 有效人工注释Spot：4221
- 无注释Spot：5
- 参考类别：7
- 预测簇数：22
- ARI：0.254629
- NMI：0.547126
- 描述性Cluster Purity：0.762852

聚类参数事先固定，没有根据本切片参考标签选择最佳聚类数量。

## 5. 空间边界诊断

- 全部六邻域无向边：12385
- 可评价空间边：12381
- 参考边界：950
- 预测边界：1375
- 正确识别边界：201
- Boundary Precision：0.146182
- Boundary Recall：0.211579
- Boundary F1：0.172903
- Spatial Neighbor Agreement：0.888943
- Chance-adjusted Agreement：0.883148

## 6. 类别碎片化

各参考类别覆盖90% Spot所需的预测簇数：

- Layer 1：4
- Layer 2：5
- Layer 3：10
- Layer 4：5
- Layer 5：5
- Layer 6：4
- WM：2

Layer 3在本次预测中比较分散；WM相对集中。

这些数字描述预测簇的分布，不等于证明组织层发生了真实生物学碎片化。

## 7. 探索性对照

DLPFC 151507已有结果：

- E0：ARI 0.220592，NMI 0.277036
- S0：ARI 0.311535，NMI 0.458778
- STAGATE：ARI 0.254629，NMI 0.547126

STAGATE的NMI最高，S0的ARI最高。

STAGATE在本切片上的Boundary F1高于已有E0/S0描述性结果，但不能将差异直接归因于某一模型模块。

不同方法的表达预处理、表示学习和聚类输入存在差异。

## 8. 研究解释与限制

已观察到：
- STAGATE预测簇数明显多于参考类别数。
- 部分参考类别在预测簇中分布较分散。
- 局部空间一致性较高，但参考边界召回率有限。

仍需验证：
- 这些现象是否在其他切片和组织类型上稳定存在。
- 现象来自表示学习、图构建还是下游聚类。
- 类别碎片化是否主要由固定Leiden resolution导致。

不得把Spot或空间边当作独立生物学重复。
两张DLPFC切片的供体独立性尚未核实。
本切片属于探索性评价，不报告显著性结论。
CAN-N仍为候选改进方案，效果与创新性均未经验证。

## 9. 结果文件

- scripts/stagate_151507_controlled.py
- experiments/151507/config.json
- experiments/151507/loss.csv
- experiments/151507/leiden_n15_r1_seed42.csv
- experiments/151507/leiden_n15_r1_seed42_config.json
- experiments/151507/evaluation_n15_r1_seed42.json
- experiments/151507/boundary_diagnostic_n15_r1_seed42.json
- experiments/151507/reference_cluster_contingency.csv

原始数据与完整30维嵌入保存在本地实验目录。

## 10. 下一步

1. 完成GitHub第二次科研归档。
2. 采用预先固定的配置检查第三张乳腺癌切片。
3. 核实跨切片与跨供体独立性。
4. 设计聚类器控制和必要消融，避免将Leiden参数效应误判为模型机制。