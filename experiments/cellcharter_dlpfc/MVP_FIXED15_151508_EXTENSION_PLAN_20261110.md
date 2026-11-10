# 151508 · 冻结 A/B 跨切片扩展验证准备（2026-11-10）

## 已完成的真实操作
用户 Windows 成功运行 `scripts/cellcharter/prepare_151508_scvi_aggregation_v2.py`，实际终端出现 `151508_FEATURE_CACHE_COMPLETE`。

- 样本151508：4384 spots；空间无向边数12849；预处理矩阵4384×5000 HVG。
- scVI 5维、seed22911、GPU训练。日志约第260 epoch 提前停止：验证ELBO连续45条记录未改善，最佳1259.730。不能据此自动比较不同数据切片的ELBO。
- `latent_shape: [4384,5]`，`aggregate_shape: [4384,25]`；训练日志显示CUDA使用为True。
- 原始特征缓存 `D:\paper\CellCharter_reproduction\results\cellcharter_151508_scvi22911_features_v2`。
- `latent_sha256` = `b5d6f8dc6adaab44429941b0cb013555cc424455611c6722caa6a82dc3e68183`。
- `aggregate_sha256` = `094f702ba7fae32fc69c6c8026acb5765bd7bcd39b2802fbe8091b26baba60ee`。
- 日志显存统计峰值 `peak_cuda_mib=106.73`（PyTorch分配量，而非整个GPU/训练进程物理占用）。
- `finished_utc=2026-11-10T05:51:15.807540+00:00`。
- 这些数据均来自用户终端，未直接下载用户本地二进制特征文件。

## 待执行：固定比较
已在GitHub建立 `scripts/cellcharter/mvp_fixed15_block_swap_151508.py`，**尚未在用户Windows同步、执行**。
源特征匹配固定SHA256；使用 `spot_order.csv` 对齐barcode，要求4384行。A：L0+L1+L2；B：L0+L1+L4，二者15维；GMM均同样 K7（Oracle人工层类别数）、seed22911、full covariance、KMeans初始化、CPU、max_epochs100。先拟合和保存两组预测、后读取人工标注评估ARI/NMI与全局及L5/L6边界；151508标注4381个，12,849无向边按标注可用边计算真实分母，不从151507复用950/145边界基数。新目录独立、不覆盖旧实验。

科学限制：本切片曾出现在项目早期分析，不宣称严格未接触独立盲测；单一新的切片及一次GMM seed不能支持普遍泛化结论，候选方案也尚不是已确立原创算法。151507锁定组合不根据151508得分做后验修改。

**下一步**：仅让用户先git pull同步新增MVP脚本，收到成功回执后再给实际运行命令。

## 真实运行完成（用户终端，2026-11-10；覆盖上文“待执行”状态）

用户已成功同步并运行 `scripts/cellcharter/mvp_fixed15_block_swap_151508.py`，输出 `MVP_FIXED15_COMPLETE`。结果目录：`D:\paper\CellCharter_reproduction\results\mvp_fixed15_block_swap_151508_gmm22911_v1`。这是**实际已执行**，不是计划；以下数字来自粘贴的终端，尚未直接打开本地results.json/预测CSV。

- 对照 A（L0+L1+L2）簇尺寸：`[619,981,729,597,631,475,352]`
- 候选 B（L0+L1+L4）簇尺寸：`[852,432,471,1024,675,527,403]`
- 两组均CPU GMM，训练日志含 `max_epochs=100 reached`，不能据此认定已数值收敛。
- 151508无向边数12849，存在人工标注的4381/4384 spots，评估边12846，参考真边界927，L5/L6界面参考边139。

### 原始终端 JSON

```json
{
  "control_L0_L1_L2": {
    "ari": 0.46267065495944715,
    "nmi": 0.6132171362713753,
    "boundary_tp": 152,
    "boundary_fp": 1868,
    "boundary_fn": 775,
    "boundary_precision": 0.07524752475247524,
    "boundary_recall": 0.16396979503775622,
    "boundary_f1": 0.10315575161180861,
    "l5_l6_detected": 41,
    "l5_l6_reference": 139,
    "l5_l6_recall": 0.2949640287769784,
    "reference_boundary_edges": 927,
    "evaluated_spatial_edges": 12846
  },
  "candidate_L0_L1_L4": {
    "ari": 0.46059571688191825,
    "nmi": 0.5691388933817928,
    "boundary_tp": 261,
    "boundary_fp": 1973,
    "boundary_fn": 666,
    "boundary_precision": 0.11683079677708147,
    "boundary_recall": 0.2815533980582524,
    "boundary_f1": 0.16513761467889906,
    "l5_l6_detected": 49,
    "l5_l6_reference": 139,
    "l5_l6_recall": 0.35251798561151076,
    "reference_boundary_edges": 927,
    "evaluated_spatial_edges": 12846
  }
}
```

### 冻结比较与方向性

B − A：ARI=`-0.0020749380775289`，NMI=`-0.0440782428895825`，global boundary F1=`+0.06198186306709045`；边界TP +109、FP +105、FN -109，L5/L6命中 +8/139。

151507相同seed22911的先前结果：A的ARI0.4800188870/NMI0.5747963814/F1 0.1544117647，B的ARI0.5272652573/NMI0.6175659085/F1 0.2030360531。151507 B 全部三个指标优于A；151508 B **仅边界F1优于A，ARI/NMI下降**。因而否定“整体聚类稳定改善”主张，保留“两个测试切片下边界F1改善的探索性信号”。151508在此前项目中曾经使用，不属于未经接触的独立盲测；spot及邻接边不得当作独立样本，未开展显著性检验，不能声称泛化已证明、创新已经成立。

**接下来的科研决策**：冻结已完成的两张切片的结果并记录混合/负结果，不在151508上继续刷随机种子以寻找更漂亮的ARI。若要争取SCI方法论文，需要预先定义明确主要评价终点（如边界F1、聚类ARI的容忍恶化范围）、最近邻创新审查和不参与选型的后续切片验证；此外尚缺同预算邻域深度/可选块基线、必要统计重复与实验范围核查。先做样本清点与实验方案设计，不立即大批量训练。
