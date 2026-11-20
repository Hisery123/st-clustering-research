# E3d正式协议v1 首项151509 15D结果与用户本机只读审计（2026-11-20）

> **证据分类：用户Windows真实终端输出 + 一条读取本机输出文件的检查脚本所打印的汇总。** ChatGPT并未取得本机`manifest.json`、`autok_summary.json`、`predictions.csv`、`all_k_run_labels.npz`原文件，亦未直接重算每spot预测。报告文件未备份到GitHub；须在论文最终归档前获取原件与复核。

## 实验、协议、样本单位

- 已通过下载脚本SHA256、dry-run和退出码0的预检后，用户Windows执行`e3d_autok_single_config_v1.py --sample 151509 --condition cum_L0_L1_L2 --run`。
- 单项：DLPFC切片151509、n=4789 spots、冻结特征维度15D，SHA256=`95879ded7bef09282906b4f992d273472580f5d7748b583342f3e4a64c0cd40f`。
- 主方案CPU而非GPU，K候选2–10；CellCharter 0.3.2内部辅助拟合K1–11，每K固定5次受控初始化，计55次GMM。
- 标签不用于K选择。本轮尚未读取参考标签计算后验ARI/NMI。切片并非独立供体重复；全项目供体n=3。
- 正式方案`E3D_AUTOK_FROZEN_PROTOCOL_20261120.md`于本项训练开始前确立，但属于看过探索试点后冻结，不能说成历史独立盲预注册。

## 原始控制台成功证据

```text
GPU available: True (cuda), used: False
E3D_FIXED_TASK_COMPLETE sample=151509 condition=cum_L0_L1_L2 selected_k=3 seconds=55.91 output=D:\paper\CellCharter_reproduction\results\e3d_autok_fixed_v1\151509\cum_L0_L1_L2
```

## 后续用户Windows只读审计输出

```text
E3D_ARTIFACT_AUDIT_PASS sample=151509 dim=15 fits=55 selected_k=3
STABILITY_BY_K= {2: 0.745067, 3: 0.800295, 4: 0.798525, 5: 0.738262, 6: 0.722156, 7: 0.729765, 8: 0.728879, 9: 0.680207, 10: 0.674636}
BEST_MODEL_CONVERGENCE= {1: True, 2: True, 3: True, 4: True, 5: True, 6: True, 7: True, 8: True, 9: True, 10: True, 11: True}
BEST_MODEL_ITERATIONS= {1: 2, 2: 5, 3: 8, 4: 16, 5: 16, 6: 22, 7: 43, 8: 21, 9: 44, 10: 24, 11: 50}
WALL_SECONDS= 55.909676
```

只读审计本机manifest/autok_summary/预测CSV/全K run-labels NPZ，确认`completed`、K3、4789个唯一barcode、正确簇ID、预测及NPZ各自SHA256一致、K1–11每K5×4789预测标签且有限合法、每K 5次和K2–10稳定性平均有限。本校验可证明**文件完整性与11个最佳GMM收敛状态**，不能推论**55个GMM全数收敛**（未逐模型保存收敛标签），也不能证明外部独立复现。

## 解释与下一步

- `best_k=3`，稳定性0.800295，次高K4=0.798525，**差距0.001770**（按6位小数），极接近；不能声称K3科学上显著优于K4或更符合人工层。之前试点同切片K4采用不同K候选与3次运行，因此不应直接判为同协议不稳定。
- 本次`GPU available but not used`为预设CPU运行，而非加速失效。
- **状态：已验收单配置1/48**，其余47项尚无完成证据。拟先对同切片25D最大特征维度运行1项做高维冒烟，确认输入和高维GMM，保留所有结果/失败；然后另行设计安全批量只读清单及断点控制。此顺序为工程风险控制，而非根据K/ARI挑结果。正式K候选范围和5次重复预算不改变。
