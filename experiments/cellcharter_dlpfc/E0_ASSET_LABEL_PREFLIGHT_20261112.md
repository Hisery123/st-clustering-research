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


## 2026-11-13 用户实际终端：E0第8步，历史产物目录盘点（只读）

用户用PowerShell枚举 `D:\paper\CellCharter_reproduction\results` 的一级子目录，统计与12张切片名匹配的 manifest、结果JSON、预测CSV、25D缓存文件数。以下是**文件存在性证据**，尚未打开这些结果文件核验配置、指标或完成状态。

- 后10张（151509、151510、151669–151676）：每片都有 `mvp_fixed15_<sid>_gmm22911_batch_v1` 目录，均列出 manifest=1、metrics/results JSON=1、prediction CSV=2、feature25D=0（25D缓存另存于features目录，非缺失）。
- 151508：`mvp_fixed15_block_swap_151508_gmm22911_v1` 目录中 manifest=1、JSON=1、预测CSV=2；另有 v1/v2 两个历史features目录，只有v2被核实有25D缓存。
- 151507：`mvp_fixed15_block_swap_151507_scvi22911_gmm101_v1` 与 `mvp_fixed15_block_swap_151507_seed22911_v1` 各存在 manifest=1、JSON=1、预测CSV=2；尚不能认定它们是同输入、同超参、同种子的可重复性双运行。
- 151507还有 `cellcharter_v032_151507_seed22911_L0_diagnostic` 至 `L3_diagnostic` 四个单层目录，各1 JSON、1预测CSV，以及 `cellcharter_v032_151507_seed22911_oracleK7`（L4）1 JSON、1预测CSV、1份25D缓存；单独有 `all_depth_boundary_audit_v1` 目录，但此前命令只统计特定文件名。
- 本次查验未覆盖历史旧hop/25D置换的所有可能存放路径（含子目录）、STAGATE/Leiden其他根目录、也未审查数据文件字节。

**当前明确状态**：E0基础缓存/条码/标签一致性初检已获终端支持，历史产物存在性已盘点；E0仍未彻底结束（需读manifest/评估旧实验可比性和官方标签溯源边界）；E1同seed重复性和任何新增GMM任务均未执行。**下次唯一优先事项**：只读提取151507两份固定15D manifest及151508与后10片代表性manifest的关键字段（input hash、seed、K、GMM参数、完成状态和路径），据实判断旧结果能否复用；不要盲目重跑、改数据或提前启动1200项矩阵。

## 2026-11-13 E0第9步：151507两份固定15D Manifest 原始内容核验

**来源级别**：用户在Windows PowerShell执行只读JSON打印并在会话中粘贴了两份完整manifest；本助手检查了粘贴的字段，尚未直接读取本地文件字节或预测CSV。两份manifest均`status=completed`，`sample=151507`，`split=development only`，`oracle_k=7`，`scvi_retrained=false`，`manual_labels_used_for_fit=false`。

- `mvp_fixed15_block_swap_151507_scvi22911_gmm101_v1`：GMM seed=`gmm_seed:101`，scVI来源seed=`scvi_source_seed:22911`，输入shape=(4226,25)。
- `mvp_fixed15_block_swap_151507_seed22911_v1`：记录`seed:22911`，相同输入shape=(4226,25)。
- 两者source_file_sha256相同：`15b1fd58d092277f81fa2a1513bb2fbf865eea71b1b7450a9a2f710c941a8f54`；15D对照L0/L1/L2 SHA256相同 `12453178bf51f99c3bd247de218b35bec6bfd6818dc259848e01aec19804ba61`；候选L0/L1/L4 SHA256相同 `0332cb6746ddbb630040203ba40aa914f14dd302cf7e3d7928fa8688cfc30ba4`。
- 两者记录的GMM配置一致：full covariance, kmeans init, tolerance 0.001, regularization 1e-6, CPU, max_epochs 100。记录的每条件fit+predict时间：seed101为0.611s/0.683s；seed22911为0.890s/0.606s。仅为这两次任务耗时，不能推断批量总耗时。
- 候选L0/L1/L4的7个cluster_sizes为`[762,1045,331,446,296,568,778]`和`[296,568,446,331,762,1045,778]`，仅排列不同；**簇大小相同不证明实际Spot分区相同**。对照L0/L1/L2的cluster_sizes不同。下一步须读取两份预测CSV按barcode对齐计算两种配置各自的预测-预测ARI/NMI。
- **关键结论**：这两个目录是**跨GMM种子（101 vs 22911）**的开发集结果，不能当作`E1同seed独立进程重复`；不能与历史seed0两次分区互比ARI≈0.713871混淆。没有任何新增GMM实验在本次检查中运行。

## 2026-11-13 E0第10步：151507两GMM种子实际预测分区互比

**证据**：用户Windows PowerShell读取两目录的`control_L0_L1_L2_predictions.csv`和`candidate_L0_L1_L4_predictions.csv`，按barcode集合验证一致后reindex对齐，每配置4226个Spot，直接用sklearn adjusted_rand_score/normalized_mutual_info_score比较**预测对预测**，并提供成功终端输出`CROSS_SEED_COMPARISON_COMPLETE`。

- 同一输入、同一25D源文件SHA、相同15D条件特征SHA、同K=7与GMM配置，种子 **101 vs 22911**。
- 对照A（L0+L1+L2）：prediction-vs-prediction ARI = **0.504900119**，NMI = **0.637920634**，same_partition=False。
- 候选B（L0+L1+L4）：prediction-vs-prediction ARI = **1.0**，NMI = **1.0**，same_partition=True。两者簇编号允许不同。
- **解释限制**：这是151507单切片、仅两GMM种子的探索性**跨seed分区稳定性**结果，不是以人工标签为参照的准确性ARI/NMI，不足以推广到其他切片、供体、10seed或证明B优越/创新。与另一个历史同seed0两次分区ARI≈0.713871不能混为一谈；E1同seed独立重复依然未执行。
- **唯一下一步**：只读核对151508与后10片已保存A/B结果manifest，核查seed、K、输入文件哈希、GMM参数、条件与预测文件的实际可复用性，避免重跑；随后设计E1双独立进程同seed重复实验。

## 2026-11-13 E0第11步：151508与后10片历史固定15D A/B资产复用审计

**来源**：用户Windows PowerShell本地只读逐片校验后，完整提供终端输出，终行 `LEGACY_RESULT_AUDIT_PASS 11/11`。用户实际检查11片（151508、151509、151510、151669–151676）。每片Manifest：`status=completed`、样本号吻合、`seed=22911`、Oracle-K=7（151508/151509/151510/151673–151676）或K=5（151669–151672），特征维度15且条件字典A=L0/L1/L2、B=L0/L1/L4。GMM记录full covariance、kmeans初始化、tol=0.001、regularization=1e-6、CPU、100 max epochs。25D源实际文件SHA256与Manifest相同；从25D切片生成的每个15D矩阵内容SHA256与Manifest记录相同；两个预测CSV均有合法簇ID且行数/条码顺序与对应spots_aligned.csv吻合，Manifest每条件预测阶段已保存。

**可得结论**：11片已有固定15D A/B、GMM seed22911的预测资产可以在同协议的后续比较中复用，不需重复运行相同的配置。已核验的是终端中各断言/比较汇总，助手未直接读取本地Manifest或CSV字节；旧结果与软件运行环境绝对一致性、真实评价指标复算及上游标签源逐barcodes审计不在此次11/11覆盖内。151507已有seed101与seed22911 Manifest，之前另作检查，不计入11/11。

**下一阶段**：E1开始前冻结少量同seed独立进程复现协议：固定25D输入SHA，15D切片、K、GMM hyperparameters、种子、输出不可覆盖、每次独立进程、预测按barcode比较ARI/NMI；同时报告旧模型版本信息是否能完全核实。E1尚未执行，不得把用户过去seed101 vs seed22911比较视为同seed重复。
