# 第三篇建议1：E0本地资产与标签对齐审计（2026-11-12）

> 证据类型：用户在Windows PowerShell实际运行后的原始终端输出，由ChatGPT转录归档。**本助手未直接读取用户Windows上的文件字节，也未启动训练**。原始终端文本在当日会话中。此文档记录E0阶段性通过，不代表上游标签溯源或全部历史结果复核完成。

## 已实测通过
1. 12片DLPFC均存在 `spots_aligned.csv`、`manual_layer_annotations.csv`；10片(151509,151510,151669–151676)在标准 `scvi22911_features_batch_v1` 路径有25D聚合缓存、5D latent、status/config/spot_order。
2. 151507特殊缓存目录：`D:\paper\CellCharter_reproduction\results\cellcharter_v032_151507_seed22911_oracleK7`。25D=(4226,25)、5D=(4226,5)，float32，值全有限；SHA256分别为 `15b1fd58d092277f81fa2a1513bb2fbf865eea71b1b7450a9a2f710c941a8f54` 与 `9815d4f8632a8b460cec38c20023e36792f0aeb8f33fc14a8de947d08e6a9a4b`；`predictions.csv` barcode顺序与当前 `spots_aligned.csv` 一致；status=completed；该目录没有spot_order.csv。
3. 151508特殊缓存目录：`D:\paper\CellCharter_reproduction\results\cellcharter_151508_scvi22911_features_v2`。25D=(4384,25)、5D=(4384,5)，float32，值全有限；SHA256分别为 `094f702ba7fae32fc69c6c8026acb5765bd7bcd39b2802fbe8091b26baba60ee` 与 `b5d6f8dc6adaab44429941b0cb013555cc424455611c6722caa6a82dc3e68183`；spot_order.csv barcode顺序匹配；status=completed。
4. 后10片：25D为(n_spots,25)、5D为(n_spots,5)、float32、无NaN/Inf；每片spot_order与spots_aligned行顺序一致；10/10的聚合文件、latent文件、spots_aligned.csv实际SHA256均与历史status/config记录完全MATCH。原终端最后一行：`HASH_AUDIT_PASS 10/10`。
5. 12片按sample_name筛标签、按barcode reindex后均满足先前冻结的标注数量与K；无本样本标签重复条码、无标签指向不存在的Spot；原终端：`LABEL_ALIGNMENT_PASS 12/12`。
6. 缺少有效参考层标签的spot数：151507=5，151508=3，151509=1，151510=39，151669=25，151670=14，151671=17，151672=127，151673=28，151674=38，151675=26，151676=29；总计352个，不能进入有监督ARI/NMI及参考边界F1的有效评价。151507的5个缺失barcode为 `ACTCGCGATCTGACGC-1`, `CGTCTTGAGTGTGACG-1`, `GACGGTCCTAGGGTGT-1`, `GATAGGATTAATTACA-1`, `TTGGTTCGCTCAAAGG-1`；对应has_label=False，其余4221为True。
7. 151507的manual_layer_annotations.csv含另外740条来自151669的参考记录（`foreign_rows=740`），**并未抹除或修改**。GitHub现有 `mvp_fixed15_dlpfc_10_sections.py` 与 `cellcharter_151507_baseline_v032.py` 的相关评价代码按`sample_name`筛选，并对无标签spot/边掩码；故已审查脚本可避免把那740条直接纳入本片评价；其他历史脚本仍可能需要分别核实。

## 尚未通过/未执行
- 后10片及前2片源数据对官方SpatialLIBD的逐barcode比对、历史所有脚本的标签掩码一致性、不同版本预处理完全相同，尚未证实。
- 尚未盘点151507历史hop/固定25D置换、STAGATE/Leiden结果的全部原始CSV/JSON、配置及能否复用。
- 尚未冻结10配置×12片×10seed的正式矩阵与每次输出隔离规则；E1同seed独立进程重复、GMM测时及新增任何模型训练均**未执行**。
- 同一seed0历史两次GMM聚类互比ARI≈0.713871的原因仍未解释；不得称其为“种子变化效应”。
- DLPFC只有3位生物供体；12片、spot、seed均不能冒充12个独立供体。

## 唯一下步（E0结尾→E1准备）
先只读盘点用户本地现有GMM预测、manifest与历史实验输出目录，标记已完成/仅转录/未见，避免把新重复性冒烟覆盖旧实验；然后设计独立进程的同seed双运行，比较预测对预测ARI，并记录完整配置、时间、哈希及失败。
