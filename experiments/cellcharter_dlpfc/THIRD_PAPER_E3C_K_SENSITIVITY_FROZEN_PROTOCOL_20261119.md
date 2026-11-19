# E3c K值敏感性预冻结协议（2026-11-19；实施前须核验代码版本）

> **类型：计划/预冻结，尚未启动新E3训练。** 研究仅CellCharter DLPFC第三篇。依赖E1/E2已完成1200项、E3a供体来源已核实。任何未来对协议的修订必须另记原因、时点和版本，不得结果导向地“补预注册”。

## E3a证据冻结

供体对照表`E3a_DONOR_MAPPING_EVIDENCE_20261119.csv`：Br5292=151507–151510；Br5595=151669–151672；Br8100=151673–151676。
**证据等级需区分**：10张样本由用户Windows修复TSV的额外行名表头错位（header73而data74，手动插入`_source_rowname`）后，逐行sample/barcode/subject核实；**151507、151508仅由同行评审Bioinformatics 2025增补表Case2佐证**，本地原`subject`元数据未取回，不能标记为用户本地验证。

**数据卫生风险**：`D:\paper\ST_Benchmark_Planning\mvp\data\151507\metadata.tsv`实际上全3661行`sample_name=151669,subject=Br5595`，SHA256= `82CF728854BC30F534438E34BADF59C26CF07E08475F4BA2CE0368E56C572F79`，与`...\151669\metadata_source.tsv`完全同SHA；是误放/重复副本，**不得用于151507样本**。不删除、不覆盖、不静默修改原数据。已审视上传的E1/E2单任务脚本：GMM任务本身从`spots_aligned.csv`、`manual_layer_annotations.csv`、`cellcharter_aggregated.npy`与`spot_order.csv`或指定预测中取得样本信息，**没有直接读取这份误放metadata.tsv**；缓存产生的上游处理路径尚未本轮全盘重审，不能保证从未间接受影响。已完成E1/E2不因本次检查自动认定需要重跑。

外部资料：
- 2025 Bioinformatics论文 `Gene spatial integration: enhancing spatial transcriptomics analysis via deep learning and batch effect mitigation`，补充表 S1，Case 2: Br5292四片151507–151510；Case3 Br5595四片151669–151672，`https://academic.oup.com/bioinformatics/article/41/6/btaf350/8161564`；补充PDF见`https://pdfs.semanticscholar.org/208c/97333825bda7463ac4713c6686d9b27371d9.pdf`。
- 官方`https://research.libd.org/spatialLIBD/articles/spatialLIBD.html`：三供体、每名四张切片，数据可下载spot-level元数据`subject`字段。

## E3c核心研究问题

E1/E2的“邻域尺度收益递减、不同seed/切片/供体敏感性”是否依赖使用人工标签数目选择的Oracle-K？固定K网格下各累计尺度配置的ARI/NMI提升趋势和排序如何变化？**K网格作为受控敏感性试验，不等同真正无标签选K；后续E3d AutoK必须单独执行。**

## 冻结矩阵

- 全部12片，以样本ID固定顺序：`151507,151508,151509,151510,151669,151670,151671,151672,151673,151674,151675,151676`。
- 仅4种预定配置：`cum_L0_L1`(10D), `cum_L0_L1_L2`(15D), `cum_L0_L1_L2_L3`(20D), `cum_L0_L1_L2_L3_L4`(25D)。与既有E1/E2完全同一25D缓存和block顺序，不重新训练scVI。
- `K∈{5,6,7,8,9}`，每样本每配置全K均跑，不因匹配标签/样本表现跳过。实验中不使用人工标签**选择**K；固定K仅对照与后验评价。
- 10预冻结GMM种子：`22911,7449,25842,10379,6690,26128,21059,22159,32389,12815`。
- GMM与E1/E2相同：CPU、full covariance、kmeans init、tol 0.001、reg_covar 1e-6、max_epochs 100；只更改K，不能根据标签挑最优seed/配置/K。
- 完整网格`12×4×5×10=2400`配置格。各片原始Oracle-K（Br5595四片K5，其余八片K7）四配置×10seed共**480格E1/E2已完成**，逐格校验后可标记`REUSED_AUDITED`并**绝不重新计作新训练**；因此预期最多**1920个新拟合**，以本地manifest复查为准，如不匹配必须fail-closed，绝不覆盖旧结果/跳过错误。
- 新输出写入独立`results/e3c_k_sensitivity_v1/<sample>/<condition>/k_<K>/seed_<seed>/`，保留预测CSV、配置manifest、hash、标签mask评价、运行耗时、失败traceback；预检全量依赖后逐批次串行运行，错误中止、无静默重试；允许只读dry-run并基于可信manifest安全续跑。
- 发表时`ARI`为主要已定义指标、`NMI`为次要指标；同时保留各K的全部数值/阴性结果。拟展示：逐切片-配置-K均值±seed SD的CSV、多K对照的配对∆ARI/∆NMI、供体层描述性摘要、可重复SVG折线/热图（种子点是技术重复）。
- 供体作为生物学单元`n=3`，四张同供体切片只能做嵌套描述；单个seed、spot、K和同供体不同切片**不是独立生物重复**，不进行n=12/1200的伪重复p检验。
- 对照E1/E2 Oracle-K时，明确条件为`K=5`或`K=7`（标签知情设置），不声称从标签独立估计K。
- **冒烟/成本关卡**：按一个未跑K组合小规模真实计时和内存检查后，才允许批量全K自动调度。既有776项曾耗时约3小时，不能承诺2400项在1小时跑完。

## 验收门槛与下一步

1. 先由用户Windows现场核验`e1e2_multiscale_gmm_task.py`、`e1e2_safe_batch_runner_v2.py`、`e1e2_aggregate_multiseed_v2.py`与归档源码SHA是否一致；任何差异先审查，不能直接复用训练代码。
2. ChatGPT依据冻结协议构建全新的E3c`--dry-run`验证器和一个新任务K运行脚本，优先在一个样本×一个新K做冒烟；**此时脚本尚未开发，不得称已测试**。
3. 审计原480任务并确定可安全复用，再分批次运行其余最多1920个新拟合，逐片100%完整性核查；只确认真实终端结果。
4. E3c完成后再设计并预冻结E3d`ClusterAutoK`的版本/超参/盲标签选择流程；E5基线及外部验证为SCI目标硬门槛，不能用E3c替代。
