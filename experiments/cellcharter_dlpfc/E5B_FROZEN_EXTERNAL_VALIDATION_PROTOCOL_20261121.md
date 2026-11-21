# E5b：独立来源六患者乳腺癌Visium外部验证 · 正式事前冻结协议 v1
日期：2026-11-21（Asia/Taipei）；**在E5b所有模型首次拟合之前冻结。** 本文是任务计划/规则锁，不是训练完成证据；完整执行脚本尚待适配、Windows尚未运行。

## 1. 研究目的与数据使用边界

- **RQ3：** 在DLPFC 12片开发/探索后，冻结CellCharter多尺度及K选择规则，迁移至另一研究队列、另一组织（人乳腺癌）后，邻域收益递减、15D同维置换差异及K选择敏感性是否具有相同或相反趋势？全六例均须报告，不根据新数据ARI/NMI选择有利样本/配置。
- 这里只验证**分析流程在独立外部队列中的可重复性/可转移性**；每个外部样本从自身RNA counts重新无监督训练scVI，**不是训练好的DLPFC模型直接泛化到癌症**，也不是临床诊断验证。Wu 2021的病理组织区域标签与DLPFC的皮层层级语义不一致；跨组织ARI绝对值不直接比较。
- 来源：Wu et al. *Nature Genetics* 2021, DOI `10.1038/s41588-021-00911-1`；Zenodo `10.5281/zenodo.4739739`。原始归档哈希：metadata `1d0b34ead70635c094ac74ac58a88d68`，spatial `29b02ae433d459d19dc52b75a529e8e9`，filtered count `ea1220f0606c4d4e9307468fb2d5427a`（均MD5，已由用户Windows验证）。`metadata.tar.gz`、`spatial.tar.gz`、`filtered_count_matrices.tar.gz`均位于`D:\paper\CellCharter_reproduction\third_party\e5b_source_preflight_20261121`，**不会上传原始大文件到GitHub**。
- 六个CSV的`patientid`均不同，支持六患者独立来源；按论文及公开元数据记录为**六名不同患者，n=6**，不能把15,611 spots、多个聚类种子或每病人的多个尺度当独立生物学重复。不得为样本量扩大而将每片/seed视为独立患者。
- 六例**全部纳入**，按固定顺序：`1142243F,1160920F,CID4290,CID4465,CID44971,CID4535`。没有因类别不平衡或可预期的效果选样；E5b前尚未计算任一方法在本队列上的ARI/NMI。

## 2. 训练spot范围与独立评价mask：先冻结、后拟合

- 六例外层原始矩阵含15,611列spot，metadata的无标题索引列为barcode，与counts`barcodes.tsv.gz`集合严格相等；同样与空间`tissue_positions_list.csv`内barcode交集完整。实际matrix/features尺寸头2例28,402基因、4例19,237基因，不能在不核实基因ID下跨患者合并表达矩阵。
- **训练输入：** 精确barcode联表，仅保留`in_tissue=1`的spot，**不看Classification内容筛训练spot**；六例模型输入合计15,601 spots。所有方法的训练/拟合使用这一同一spot集合（各原生预处理/特征生成有所不同）。那10个`in_tissue=0`条码不是表达矩阵错位，明示排除。
- **评价标签掩码：** 仅在模型预测及K-blind选择全部落盘之后读取`Classification`评估。空间组织内但标签为`Artefact`、`NA`、`Uncertain`或空值的spot依然保留无监督训练输入，只在计算ARI/NMI时从评价中排除；严格按`str.strip().casefold()`相等判断，不使用任何按ARI最优的标签清洗；保留其原始预测。所有合法的组合组织名称各自为一类，**不折叠任何原始合法类别**。这些类别的语义是病理区域组合，并非单细胞真值。
- **Oracle-K只作“标签类别数知情”对照**，只采用该样本有效人工病理标签的类别数固定K，不可称为无监督K选择；K-blind是主分析，不允许读取这些标签或其类别数来设定/搜索聚类K、选择尺度、早停或挑选模型。人工标签可以先单独静态保存评价真值/Oracle-K的只读对照，但K-blind拟合流程代码不得在拟合/模型选择阶段读取该文件。

| 样本ID | 模型输入in_tissue | 评价有效spot | 仅评价排除 | Oracle-K | 最小合法类spot数 | 主导类占比 |
|---|---:|---:|---:|---:|---:|---:|
| 1142243F | 4784 | 4665 | 119 | 5 | 10 | 77.75% |
| 1160920F | 4895 | 4846 | 49 | 7 | 9 | 64.92% |
| CID4290 | 2426 | 2419 | 7 | 3 | 122 | 86.07% |
| CID4465 | 1211 | 1207 | 4 | 3 | 3 | 93.70% |
| CID44971 | 1160 | 1159 | 1 | 6 | 81 | 27.35% |
| CID4535 | 1125 | 1028 | 97 | 6 | 3 | 40.66% |
| 总计 | **15601** | **15324** | **277** | 各例分别计算 | — | — |

- 10个在metadata中标为`NA`的spot的关系：CID4290有6个、CID44971有2个、CID4535有2个**共10个`NA`正好均属于`in_tissue=0`**（依据此前QC各列表、in_tissue剔除后有效mask分布推得），因此不得重复减掉这些条码。验证时以真实barcode联表输出为准，不凭数字猜行号。
- **轻微风险的实证义务：** CID4465只3个`Normal duct` spot；CID4535只3个`Invasive cancer + adipose tissue + lymphocytes` spot。维持真实类别，不事后去除；ARI和NMI均报告每位患者并附混淆/类别表，严重失衡须明确披露。

## 3. 模型表示、对照及计算预算：预先全部确定

**共同设置：** 外部六例逐样本独立处理，不使用DLPFC scVI权重、PCA/HVG缓存或患者间人工标签。仍使用研究已固定的CellCharter adapted预处理方案：raw counts→去低表达基因(`min_counts=3`)，spot低总count阈值3为预先数据完整性门槛（若会删掉任何已在in_tissue范围的spot，程序应STOP并保存失败原因、不得静默少报）→raw counts层→normalize_total(1e6)与log1p→HVG5000/`seurat_v3`基于counts层→scVI latent5D、固定representation训练seed22911、GPU、max_epochs400、early_stopping=True、optimizer AdamW、reduce_lr_on_plateau=True→六角Visium grid几何核验（固定Six Neighbors，坐标变换`(array_col,sqrt(3)*array_row)`）→`cc.gr.aggregate_neighbors(n_layers=4)`生成L0-L4的25D。不得用病理标签来做基因选择或调整epochs。固定表示每患者训练一次，后续全部seed/配置复用，记录GPU日志/包版本/模型及表征SHA。若现有CellCharter依赖不兼容或输入内容不合格，只修执行层且保留原失败，不根据效果调方案。
- 原始文件实际`matrix.mtx.gz`、`features.tsv.gz`、`barcodes.tsv.gz`**内容是普通文本，不是二次gzip**。输入适配器必须依据实际魔数读取，并在独立新输出目录中规范化为10x可读文件，原始归档只读；支持不同样本28,402/19,237 genes。首次数据准备期间必须核验数值非负、有限、计数有效、features ID/条码合法和MatrixMarket行列数；失败为真实性阻断，不静默修正。
- **CellCharter六个预定义特征组合：** `L0 (5D)`、`L0+L1 (10D)`、`A=L0+L1+L2 (15D)`、`L0+L1+L2+L3 (20D)`、`L0+L1+L2+L3+L4 (25D)`、`B=L0+L1+L4 (15D)`。A是**本研究固定15D参考**，20D为官方教程示例层数对应；不得称A是CellCharter API默认。所有特征从相同原生25D缓存提取。
- **CellCharter聚类：** CellCharter v0.3.2原生TorchGMM full covariance、kmeans初始化、convergence_tol0.001、regularization1e-6、CPU max_epochs100，技术seed`22911,7449,25842`显式播种（继承此前E3d修复random_state的实现策略）。两K臂：
  - Oracle-K：每患者固定K如第2节表；
  - **K-blind主臂：** 每患者×每配置仅一次以E3d冻结的CellCharter `ClusterAutoK(n_clusters=(2,10),max_runs=5,convergence_tol=0)`、辅助K1..11、内部5次随机播种22911..22915，使用无标签稳定性选K；然后在所选K下按三正式技术seed拟合/输出GMM预测。报告单独AutoK搜K额外耗时，不把三技术seed说成三次独立K选择。边界K=2/10也照实保留，不事后扩K搜索。
- **E5a既有4对照全部保留，不因效果/成本事后删：**
  1. 非空间GMM：同患者scVI-L0 5D、sklearn full covariance，Oracle固定K；Kblind最小BIC搜索K2..10。
  2. 非空间Leiden：同scVI-L0 5D、15NN图、Leiden；Oracle按预冻16个resolution网格最接近K取最小resolution，Kblind固定res1.0。
  3. BANKSY 1.3.5：同患者raw10x counts，经自身normalize1e4/log1p/HVG2000（seurat）、15空间邻居、`max_m=1`、lambda0.2、20PC、Leiden50NN；Oracle使用同16-resolution网格逼近K，Kblind固定res1.0。
  4. BayesSpace 1.20.2：同患者raw10x counts和`array_row/array_col`，R SpatialPreprocess Visium、HVG2000、PCA15、t模型MCMC正式10000/burn-in1000、mclust init；Oracle q=预定真实类别数，Kblind原`qTune(q=2..10,nrep1000,burn.in100)`按最大平均伪loglik，并列取小q。旧v1.1的CSC规范读入层修复应重用，原失败和差异记录保留。方法原生预处理**不等于四法相同输入特征**，科学讨论必须准确说明。
- 技术seed对所有输出统一为`22911,7449,25842`；BANKSY/BS特征准备的固定上游seed依E5a为22911，与聚类3seed区分。两K臂所有方法均不根据ARI挑最优seed。正式输出计划：CellCharter `6患者×6配置×2K臂×3seed=216`份预测；4对照`6×4方法×2K臂×3seed=144`份预测；合计**360份预测（计划，不代表执行）**。另外6个scVI表示训练、36组CellCharter无标签AutoK选K运算和各基线预冻K选择轨迹；这并非360个独立患者或等预算的自适应搜索次数。
- **资源取舍：** 6例全部进入，BS可耗时长，不因此减少任何预定方法/样本/seed。若存在GPU OOM/磁盘不足/输入非法才停止并保留真实日志，禁止事后依模型表现缩减设计；必要新协议必须单独版本、在新实验前公开，不能冒充本计划完成。

## 4. 指标、独立分析单位、报告和阶段验收

- 主要指标ARI（Adjusted Rand Index），次要NMI（sklearn normalized_mutual_info_score，`average_method='arithmetic'`，与E5a一致），两者均仅在所有无监督预测文件落盘后用第2节完全固定的样本级评价mask计算。保留每份原始全spot prediction及真实实际clusterK；未恰得Oracle-K不得伪称命中。病理类别名用于后验打分，不进入K-blind分辨率或K选择。
- **主表**K-blind：六个患者逐一展示全部六CellCharter配置的ARI/NMI（3技术seed均值、离散程度、完整原点）；对4基线另按相同K臂展示完整预测和性能。Oracle-K作为明确的标签知情上界/敏感性补充表（只是一种知情K条件，**不保证效果是真正的数学上界**）。主要比较均按同患者配对并以患者n=6为生物学层级，允许描述性平均/中位数、每位患者变化和不确定性；三seed和spots不能伪重复为n=18/n=15324。不能因为六患者就自动断言显著性。
- 预先定义观察目标：L0→10D→15D→20D→25D逐段效应、B15D−A15D、技术seed方向不稳定性、Oracle-K vs Kblind结果差异、异质性/负结果；在观察外部结果前**不挑选最优模型/尺度/类别、也不因负结果追加K或seed范围**。
- 无监督训练/预测阶段与读取评价标签分离。正式批量独立会话`D:\paper\CellCharter_reproduction\results\e5b_external_v1\...`；输出原始预测、每阶段完整状态、源档哈希/脚本SHA/软件版本/固定seed/计算预算/K选择轨迹及失败信息，全部不覆盖E5a和旧DLPFC数据。预测先写后读标注、评价单独脚本。禁止将公开数据或用户原始结果大文件自动推GitHub。
- 软件或数据真实性阻断可最小修复，保留原失败和补丁记录；阶段连续执行、**全部360项或明示未完成**后一次统一数据/预测审计，再汇总所有正负结果，并按用户原定流程交Claude作整阶段独立方法审核。E6仅在后续另行决定，不作为E5b训练途中分支。

## 5. 执行状态和启动前验证

- **已完成：** 6样本三归档MD5、barcode与spatial、count矩阵头、病理标签字段/样本patientid和mask QC；全部由用户Windows原始日志确认，索引见`E5B_EXTERNAL_DATA_SOURCE_PREFLIGHT_20261121.md`。
- **尚未完成/不可声称：** E5b输入标准化及逐元素count/features检查、六样本scVI、CellCharter/BANKSY/BayesSpace/GMM/Leiden新外部拟合、360预测/ARI/NMI、任何外部性能结论；GitHub存在本协议**不等于Windows同步或代码已实际跑通**。
- **下一执行动作：** 在GitHub先制作只读源归档验证及单独输出位置的`e5b_prepare_inputs_v1.py`，核对数据读取与所有选样/评价掩码；用户Windows手动运行一次，若通过再按冻结规则制作连续GPU表示及基线批量执行脚本。预检不得计算任何ARI/NMI。用户每次只接收一个PowerShell步骤，失败保留原件。

## 6. 实际代码提交信息（此处仅证明GitHub存在，不等于运行）

输入标准化脚本：`experiments/cellcharter_dlpfc/e5b_prepare_inputs_v1.py`（Git提交`b75ae81095ed54c03acdeed2d9ddb2bdd6f4ad20`；SHA256 `c37e435a77cb5b7f00242004bb9a1646b686c83a16d6ab34f3c609515e661d52`）；默认无写入许可，必须显式`--stage`才把源归档内容流式校验、规范化输出到独立`results/e5b_external_v1/input_stage_<UTC>_<PID>`。不会运行训练或计算任何ARI/NMI。**代码尚未在Windows或本助手环境中用真实文件运行验证**；若真实读取报错保留新状态目录，仅修复工程读入且不改变以上冻结的科学方法设置。

## 7. Windows staged inputs verification passed; six-patient feature script prepared (2026-11-21)

**用户Windows真实实验日志**：
```text
E5B_STAGE_SCRIPT_SHA_PASS c37e435a77cb5b7f00242004bb9a1646b686c83a16d6ab34f3c609515e661d52
E5B_STAGE_SOURCE_INTEGRITY_PASS archives=3
E5B_STAGE_SAMPLE_PASS sample=1142243F model=4784 eval=4665 genes=28402
E5B_STAGE_SAMPLE_PASS sample=1160920F model=4895 eval=4846 genes=28402
E5B_STAGE_SAMPLE_PASS sample=CID4290 model=2426 eval=2419 genes=19237
E5B_STAGE_SAMPLE_PASS sample=CID4465 model=1211 eval=1207 genes=19237
E5B_STAGE_SAMPLE_PASS sample=CID44971 model=1160 eval=1159 genes=19237
E5B_STAGE_SAMPLE_PASS sample=CID4535 model=1125 eval=1028 genes=19237
E5B_STAGE_FINAL status=completed samples=6 model=15601 eval=15324 result=D:\paper\CellCharter_reproduction\results\e5b_external_v1\input_stage_20261121T083911Z_14272\batch_status.json
NO_TRAINING_NO_ARI_NMI
E5B_STAGE_EXIT_CODE=0
```
这说明在用户Windows上来源完整性与标准化输入准备已真实完成，6/6源文件全量非负整数计数检查、MatrixMarket行/列/nnz、unique gene ID与barcode、预冻结in_tissue mask和有效评价mask在冻结输入脚本内均已通过；但本助手未直接读取完整本地batch_status.json或其生成的每份SHA明细，不把用户Windows未上传的文件称为GitHub备份。**仍没有任何E5b模型训练结果或ARI/NMI**。

已准备下一子阶段的脚本：`experiments/cellcharter_dlpfc/e5b_scvi_feature_batch_v1.py`，GitHub创建提交`3fc8acc903cbe0f06ff70fa3b756e7b9f2461880`，SHA256 `28f792587a54ac8cb436d82f888dc9a39a2cff204168021ff8591a3f05a2b558`，只读来源为上述`input_stage_20261121T083911Z_14272`，冻结预处理/scVI400 epoch/5D与CellCharter4-hop25D，seed22911、GPU每患者单独子进程、6例连续训练（`--run`显式授权）、每例独立保存model/caches/SHA、父批次状态；绝不访问`reference_only`标签和计算ARI/NMI。该源脚本**未在用户Windows运行或完整语法/真实数据测试**，不能称模型适配成功。下一唯一Windows操作为SHA验证下载脚本并执行六患者连续feature-batch；阶段结束或真实阻断才审计/修复，不能每片穿插新探究或因分数改规则。

## 8. Windows E5b六患者scVI特征正式训练6/6通过（2026-11-21）

**来自用户实际Windows批次结尾终端原始记录（不是计划）**：
```text
Trainer.fit stopped: max_epochs=400 reached.
Epoch 400/400: 100% ... 400/400 [00:55<00:00, 7.23it/s, loss=2.93e+03, v_num=1]
E5B_FEATURE_SAMPLE_PASS sample=CID4535 spots=1125 latent=5D aggregated=25D seconds=55.709
E5B_FEATURE_PROGRESS completed=6/6
E5B_FEATURE_FINAL status=completed completed=6/6 failed=0 result=D:\paper\CellCharter_reproduction\results\e5b_external_v1\features_20261121T090400Z_28460\batch_status.json
NO_GMM_NO_ARI_NMI
E5B_FEATURE_EXIT_CODE=0
```

这证明六个患者的**特征准备/表征训练批次**由Windows脚本报告全部完成，按脚本内定义各自从外部counts重新训练scVI5D并生成CellCharter 25D空间邻域聚合，completed=6/6 failed=0、进程退出码0。显示的400轮及耗时55.709秒**仅针对最后一个CID4535样本**，不得据此推断六样本各自epoch/用时、也不能据训练loss推断聚类质量。此处尚未由本助手读取本地batch_status.json和每个模型文件进行独立审计；实际存储证明在本机报告上，不能声称GitHub已备份二进制特征。**E5b已完成6次scVI表征训练，正式CellCharter GMM聚类/无标签AutoK/四成熟基线以及ARI/NMI均尚未运行**；论文不能将feature success当外部验证性能。

正式feature结果路径：D:\paper\CellCharter_reproduction\results\e5b_external_v1\features_20261121T090400Z_28460，其SHA/状态需后续批量聚类程序验证；**不得重新拟合scVI或用DLPFC权重代替**。下一计划阶段按原冻结36组CellCharter 6尺度×6样本、每组1次AutoK及2 K臂×3seed=216预测，后4对照144预测；先落盘未经人工标签的预测及轨迹，最后统一评价。遵守阶段连续执行、末尾集中审计。

## 9. E5b原定CellCharter聚类脚本已提交，Windows尚未执行

按本协议第3节事前冻结的六例×六种特征配置×K-blind/Oracle-K×三seed，已在GitHub创建`experiments/cellcharter_dlpfc/e5b_cellcharter_cluster_batch_v1.py`，创建commit `eeb309918dee5c97f15f864134b4178da49cc82f`，内容SHA256 `d8df95cd86116a2a4aec2a6f0b4cf2f63e2a1425956198bb1afe6c1baf91c1aa`。脚本只引用已经完成的特征批次`features_20261121T090400Z_28460`，按来源SHA验证后从其25D缓存抽取固定6个特征组合。每患者×组合运行唯一一次CellCharter 0.3.2原生AutoK稳定性无标签选K（候选2..10，辅助1..11，每K5次显式seed，CPU），再将选定的Kblind K和原冻结标签类别数知情Oracle-K**分别**用于三个技术seed的原生CellCharter GaussianMixture拟合，计划36次AutoK与216份预测。`ClusterAutoK`的5次播种使用E3d的SeededGMM子类，不在AutoK期间读取Oracle-K常数或reference_only文件；新GMM拟合显式播种。所有预测在隔离新目录、以完整barcode保存并记录SHA；配置完成/失败和阶段总进度由manifest记录。每次失败自动停止，用户明确`--resume`可继续此前已完成配置之外的未完成任务，新尝试保留旧失败目录，禁止覆盖。**脚本尚未在Windows跑过，所有216个预测仍是计划、不能称完成**。阶段后还有E5a四成熟基线144预测及统一后验评价（禁在阶段中根据ARI/NMI改K/尺度/seed）。当前源数据准备和scVI6例特征已通过，但聚类AutoK0项/GMM0份、ARI/NMI未知。该阶段唯一下一Windows行动为SHA校验下载、Python语法检查和`--run`一次性运行36配置，若兼容性故障保留原始报错和批次状态。

## 10. Windows E5b CellCharter 36/36 AutoK配置和216/216 GMM预测正式完成（2026-11-21）

用户真实Windows运行终端结尾日志（与第9节计划状态时间先后明确区分）：
```text
GPU available: True (cuda), used: False
E5B_CC_PREDICTION_PASS sample=CID4535 condition=B_L0L1L4_15D arm=oracle_k seed=25842 k=6 actual_k=6
E5B_CC_CONFIG_PASS sample=CID4535 condition=B_L0L1L4_15D predictions=6 autok_k=3 seconds=36.487858 result=D:\paper\CellCharter_reproduction\results\e5b_external_v1\cellcharter_cluster_20261121T100504Z_29172\CID4535\B_L0L1L4_15D\attempt_20261121T104018501249Z_11236
E5B_CC_PROGRESS configs=36/36 predictions=216/216
E5B_CC_FINAL status=completed configs=36/36 predictions=216/216 failed=0 result=D:\paper\CellCharter_reproduction\results\e5b_external_v1\cellcharter_cluster_20261121T100504Z_29172\batch_status.json
NO_REFERENCE_LABELS_NO_ARI_NMI_NO_SCVI_RETRAIN
E5B_CC_EXIT_CODE=0
```

真实结论：按冻结第3节规则，36组六患者×六尺度的AutoK选择及两K臂每臂3seed总**216份CellCharter聚类预测**均由用户Windows脚本报告完成、无失败、退出码0；GMM在CPU上运行（GPU可用但used=False与协议一致）；当前**没有计算任何E5b病理区域ARI/NMI**，也未在此阶段重复scVI训练。末例CID4535 B15D选AutoK=3、Oracle-K=6，合法的预冻双臂差异，不允许按oracle调整blind。原始状态/预测及SHA位于上述本地batch_status.json和各配置attempt目录，GitHub归档仅记录终端日志，未经本助手直接读取本地输出或独立全量审计。第5/8/9节里关于尚未执行的句子是历史时点事实，应以本节为最新状态。**下一按计划执行四成熟基线共144预测**：优先非空间GMM+Leiden 72，之后BANKSY36、BayesSpace36；全部基线拟合和预测完成后再进行统一后验评价/阶段审计与Claude总审，不能因AutoK K或预期指标改变样本/算法/预算。

## 11. 非空间GMM+Leiden六例72预测脚本已冻结提交（尚未Windows执行）

依据本协议第3节既定四成熟基线方案，第一批**非空间GMM及Leiden**共六例×二方法×二K臂×三技术seed=**72份计划预测**，复用已经在Windows正式完成且SHA校验的独立乳腺癌scVI-L0 5D潜在表示，完全不重复训练scVI、不用DLPFC表征、不访问`reference_only`病理标签。GMM sklearn full covariance/kmeans/n_init1/tol0.001/reg1e-6/max_iter100，Kblind=K2..10最低BIC，Oracle=原冻结类别数K；Leiden scanpy邻居15/Leidenalg无空间坐标，Kblind固定resolution1.0，Oracle用原固定16档resolution最接近Oracle-K（平局取更小resolution），仅分隔Oracle支路会引用预先冻结的类别数。批处理每任务预测全model_spots barcode+cluster，保存明细/每项原始SHA、失败状态，失败则STOP并保留完成任务，`--resume`为显式独立动作，不会自动隐式重跑。此处不计算ARI/NMI。GitHub代码`experiments/cellcharter_dlpfc/e5b_nonspatial_baselines_batch_v1.py`创建提交`777c90ca32ee1a2db25fc240109648ff652f5abb`，SHA256=`2defb2821370a4c8e60ad6450276a6cd695b5bd26f6a26d6c3cd5c7cc02ec7f1`。**代码提交不是用户Windows执行，72任务尚无真实执行日志，不可称成功**。待用户手动SHA验证下载、py_compile和`--run`；该子阶段通过后按已冻结计划继续BANKSY36、BayesSpace36，再统一评价/审计及Claude总审。

## 12. Windows E5b非空间GMM+Leiden 72/72预测通过；重复执行保护为预期阻断（2026-11-21）

**用户Windows终端真实日志**：
```text
E5B_NONSPATIAL_FINAL status=completed completed=72/72 failed=0 result=D:\paper\CellCharter_reproduction\results\e5b_external_v1\nonspatial_20261121T104630Z_22052\batch_status.json
NO_REFERENCE_LABELS_NO_ARI_NMI_NO_SCVI_RETRAIN
E5B_NONSPATIAL_EXIT_CODE=0
E5B_NONSPATIAL_SCRIPT_ALREADY_EXISTS
```
```

前3行证明按原冻结非空间GMM与Leiden六例×两种K臂×三seed合计72个预测由用户Windows脚本报告全部成功、失败0、退出0。最后一行是随后重复执行相同PowerShell下载命令时被其`Test-Path $dest`主动拒绝，**不是模型运行失败，不应清理已完成会话或重复训练**。非空间结果本地目录`D:\paper\CellCharter_reproduction\results\e5b_external_v1\nonspatial_20261121T104630Z_22052`。与先前CellCharter 216项相加已完成288/360项**预测任务**（非360独立患者）；未做任何独立全量产物审计、病理标签ARI/NMI或方法优越性统计。接下来按冻结方案BANKSY36、BayesSpace36，均先落盘预测，最后统一评价。

## 13. E5b BANKSY36项预测脚本已提交（尚未Windows执行）

E5b当前Windows实际完成CellCharter216 + 非空间GMM/Leiden72=288份聚类预测，BAN​KSY仍**0/36**，BayesSpace仍**0/36**，所有ARI/NMI尚未计算。为按第3节完整冻结对照，已创建`experiments/cellcharter_dlpfc/e5b_banksy_baselines_batch_v1.py`，commit`26e125a8ff1bc9c0ea0248b871dbf3e8437be6f3`，SHA256=`c80a1e7c97d563c8b9e7a83e97c83d7b8c021f583c6b82b91225b9be69ade927`。延续已审计E5a官方BANKSY核心，来自E5b标准化原始counts的6例`in_tissue=1`唯一barcode spot、pixel XY坐标，sc.pp.normalize_total(target_sum=1e4)→log1p→HVG2000 seurat→BANKSY 15空间近邻/decay scaled_gaussian/m1/lambda0.2/PC20、Leiden 50NN及16档预定resolution；嵌入seed22911，聚类seed22911、7449、25842；每seed全部16档拟合，Kblind固定resolution1.0，Oracle使用病理标签**类数**知情挑最接近真实K的原生分辨率（平局取较小resolution），两臂均不读取病理标签文件，预定6患者×3seed×2臂=36份输出预测。不计算ARI/NMI。每例隔离子进程与attempt目录，保留原始BANKSY内部日志和所有候选预测、原始来源哈希、任务manifest，出错停下不覆盖旧成果，人工显式`--resume`需另指令。源代码还未在用户Windows执行，下一单一步骤SHA校验下载+py_compile+`--run`，真实通过标志`E5B_BANKSY_FINAL status=completed completed=36/36 failed=0`及退出0，若失败保留现场最小修复，不调研究预冻规则。随后按计划BayesSpace36，阶段末集中评价及Claude科研审核。

