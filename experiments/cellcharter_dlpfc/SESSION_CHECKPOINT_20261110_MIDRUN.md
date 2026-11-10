# 第三篇论文跨对话交接：2026-11-10 中途归档（批量训练进行中，结果待核实）

> 这是会话切换检查点，不是“今天工作结束”，也不是成功训练十张的证明。用户最后说“行，正在实验”，在这之后尚未提供 `--all --train` 的运行终端或最终 status.json。**严格禁止推定剩余9张训练已完成。**

## 研究目标、角色和重要决策

- 用户在 Windows/PowerShell 手动跑实验，AI 通过 GitHub Connector 维护脚本、结果审计、科研日记。一次只给一条 PowerShell 命令或一个短步骤；不控制本地计算机、不自动用 Codex。
- 第三篇为空间转录组 DLPFC 空间聚类，在成熟 CellCharter/scVI/GMM 基线之上寻找最小可证伪增量；常规SCI论文目标，不保证创新和录用，不能用增加实验数量替代真正贡献。
- 研究目标是**空间边界质量与整体聚类一致性之间潜在权衡**，而非已经证实新机制。冻结 15D A=L0+L1+L2 与 15D B=L0+L1+L4；同 scVI 25D 特征母体、同GMM seed22911与参数，分片 Oracle K。K来自标签类别数（5或7），不是标签独立自动K。
- 用户**已决定不再追查历史GMM seed0 L4不一致**，保留但不继续耗时。已看到的151507、151508结果属于开发观察，不能叫独立验证。
- **供体为独立生物样本**：供体1（151507–151510）；供体2（151669–151672）；供体3（151673–151676）；12张切片不等于12个独立供体，供体2只有5类层标签而非7类。
- 对边界F1、ARI、NMI、TP/FP/FN、L5/L6表现全部报告，包括负结果。151673曾用于本项目其他空间研究，标注来源差异、历史数据接触应披露。

## 今日已完成、证据（来源是用户本地终端，不是GitHub服务器运行）

1. 原始数据：12/12切片 `filtered_feature_bc_matrix.h5` 存在且读过；最初只有151507/151508完整空间及参考标注。通过显式HTTP代理 `127.0.0.1:7897` 从公开 `JinmiaoChenLab/SEDR_analyses` 下载其余10片各2个原始文件 `metadata_source.tsv` 和 `tissue_positions_source.csv`；最初无代理curl部分报错，使用代理后20/20成功。
2. 新10片条码来源对齐审计：10/10 H5条码与空间坐标相符，匹配 spot 全部 in_tissue=1、无坐标条码重复；metadata表行数与H5一致，metadata条码唯一且与坐标完全匹配；`layer_guess`、`layer_guess_reordered` 十片逐行一致，`Layer`列全部NaN。旧片已有标注格式为 `Layer 1...Layer 6, WM`，新片 `Layer1...Layer6, WM` 被标准化；新片标注源是 `layer_guess`，不能无证据称为相同人工真值。
3. 新10片 CSV 转换：`scripts/cellcharter/prepare_dlpfc_10_sources.py` 只读预检10/10，运行 `--write` 后 `DLPFC_10_SOURCE_CONVERSION_WRITTEN_COMPLETE 10/10`；独立读取写后检查 `POST_WRITE_AUDIT_COMPLETE 10/10`。每片在 `D:\paper\ST_Benchmark_Planning\mvp\data\<ID>\` 中有 `spots_aligned.csv`、`manual_layer_annotations.csv`、`source_conversion_manifest.json`。
4. 新10片 CellCharter 图：`scripts/cellcharter/prepare_dlpfc_10_features.py --all` **无训练预检**，10/10 `GRAPH_CHECK_PASS`，终末 `DLPFC_10_FEATURE_CHECK_ONLY_COMPLETE 10/10`。脚本各片6邻居、相同数据处理协议。
5. 单片151509实际GPU训练：`--sample 151509 --train` 成功使用RTX 4070 Laptop GPU，scVI 5D，提前于222/400轮早停；原H5 4789spots，5000HVGS，CellCharter 4-hop聚合25D（4789×25），`151509_FEATURE_CACHE_COMPLETE`，SHA256 aggregate `1f29060473365c02d2c26b51a477d87ff2fb4ee6a4e7ae8e18193895c8dfc32e`、latent `fac7c28ae833e3eb8277b79b3170dcbf9d08bcc80fb6a9f8397e97424ae5d2c4`。**151509尚未运行GMM或得到ARI/NMI/F1**。
6. 历史两个已见结果（仅作开发观察）：
   - 151507，GMM22911：A ARI .480018887/NMI .574796381/边界F1 .154411765；B ARI .527265257/NMI .617565908/F1 .203036053；L5/L6 A64/145 B62/145。
   - 151508，GMM22911：A ARI .462670655/NMI .613217136/F1 .103155752；B ARI .460595717/NMI .569138893/F1 .165137615；边界FP A1868 B1973。
   - B两张都提高边界F1，未一致提高ARI/NMI，不可声称全面优越。
7. 已上传GitHub冻结协议 `experiments/cellcharter_dlpfc/DLPFC_12_SECTION_FROZEN_EVALUATION_PROTOCOL_20261110.md` 与特征批量脚本。用户先前 `git pull --ff-only` 成功到 `ec678f7`，但**在这次新会话归档以后 GitHub 会有新commit，尚未同步到其Windows**。

## 正在做、未知状态、绝不能臆测

- 最后提供给用户且用户表示“正在实验”的命令：
  `& "D:\paper\CellCharter_reproduction\env_cellcharter\python.exe" "D:\paper\st-clustering-research\scripts\cellcharter\prepare_dlpfc_10_features.py" --all --train`
- 该程序先检查151509已完成缓存，哈希一致则复用，然后串行运行151510、151669–151676；每张独立Python进程，失败即停，失败目录保存不覆盖。
- **截至本次会话归档，没有收到这次批量训练的终端输出；151510及其他8张（共9张）的训练完成情况未知。** 绝不能把“正在执行”写成“已完成”；若用户说已结束，请先索取实际最后输出/日志。
- 数据图/新方法、GMM A/B新10片对比、统计、论文写作**尚未完成**。

## 下一次 GPT 接手：优先阅读与唯一下一步

1. 在已连接GitHub读取 `AGENTS.md` → `PROJECT_STATE.md` → `CURRENT_RESEARCH_HANDOFF.md` → 本文件及必要脚本；并按项目用户要求读取本项目当前任务需要的Skill（不要宣称未读规则已执行）。
2. **第一件事仅判断批量训练是否结束、是否出现 `DLPFC_10_FEATURE_TRAIN_COMPLETE 10/10`。** 如果用户尚在训练，不要指示启动新任务、不要求中断；可请其训练结束后提供末尾日志。
3. 若训练完成，则检查10个输出目录 `status.json`、`config.json`、`cellcharter_aggregated.npy`、`spot_order.csv`、hash、样本行序是否匹配；如出现失败保留目录、只做定点诊断，绝不擅自删除/重跑。
4. 特征验证成功以后，才按冻结协议执行每片 A/B 同预算 GMM 和完整全样本报告，分供体汇总、不伪重复；结合最接近文献判断最小创新是否成立。
5. 下一次只能下发**一个**手动PowerShell操作，并说明目的、预期输出和错误时处理。
