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
