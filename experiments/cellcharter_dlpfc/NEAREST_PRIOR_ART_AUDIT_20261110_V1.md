# CellCharter 增量方向 · 最近邻公开文献审查 V1（2026-11-10）

**证据边界**：本笔记为本次 ChatGPT 通过公开文章全文/摘要、官方文档以及代码页面完成的**第一轮定向核查**。不是系统性综述；未逐篇复现，不代表所有原始 PDF/补充材料/代码都已审核。引文与作者主张须分清。此文件仅保存可供继续核对的出处，不表示已创建新算法或取得新实验结果。

## 一、问题定义（基于我们自己的已执行实验）

CellCharter v0.3.2 适配版、DLPFC 151507、seed22911、Oracle K7、同一 scVI 5维 latent，L0–L4 共 5、10、15、20、25维，GMM 分别拟合。L4 ARI=0.496146，L5/L6 实际边界检出 0/145，L4/L5 约3/160，但 L0 在同层边也出现大量错误分割；不同界面和全局边界F1**并非完全单调**。证据：`LAYERWISE_BOUNDARY_151507_SEED22911_20261110.md` 与原始相关日志。机制未证实，不能简单把现象命名为过度平滑。

**CellCharter 官方 API**：`gr.aggregate_neighbors` 对每一层邻域**分别求聚合并与自身特征拼接**，而不是把所有原始特征直接覆盖为一个反复递推平均值。详情 https://cellcharter.readthedocs.io/en/stable/generated/cellcharter.gr.aggregate_neighbors.html 。这意味着需额外验证 GMM 对多尺度块的依赖、维度与聚类稳定性，不能未经证明把缺失边界归因于经典 GCN over-smoothing。

## 二、已验证的真实论文和最接近机制

| 论文与可核实来源 | 作者主张/方法（本文已查看范围） | 对候选创新的限制 | 需要继续核查 |
|---|---|---|---|
| Varrone et al., CellCharter, Nature Genetics 56, 74–84 (2024), DOI [10.1038/s41588-023-01588-4](https://doi.org/10.1038/s41588-023-01588-4) | 细胞生态位的识别、描述、比较；官方 `aggregate_neighbors` 是邻域分层聚合与拼接 | 当前已成熟母体；不能把拼接多个邻域块本身当创新 | 作者独立调参与测试设置和我们的适配版差异；shape 指标不是分层边界的完整替代 |
| Ji et al., **AugGCL**, PLOS Comput Biol 22(1):e1013912 (2026-01-23), DOI [10.1371/journal.pcbi.1013912](https://doi.org/10.1371/journal.pcbi.1013912) | Neighborhood Information Aggregation 用表达余弦相似性及物理邻接加权、增强表达；加图像形态和双流 GCN。作者在151507报告 ARI 0.67。已阅读官网全文方法段落。 | **「表达相似性+空间距离加权，保护边界」已存在**；无法作为独立全新创新点 | 核对官方 GitHub 对151507的训练标签使用、epoch选择、不同 benchmark 的公正性；直接比较需重新统一流程，不能拿作者0.67对比本实验0.496作结论 |
| Tang et al., **CodaST**, *A local-global dual-contrastive graph learning approach for robust domain identification in spatial transcriptomics*, DOI [10.1016/j.patcog.2026.114923](https://doi.org/10.1016/j.patcog.2026.114923) | 出版方在线摘要描述 local semantic-weighted contrast (LSWC)，用 stop-gradient 语义相似性自适应加权邻域，以抑制跨域干扰、保留边界；GSPC 做远距语义原型对比；报告 DLPFC 12片 ARI 消融改善。 | 对「局部语义权重/跨边界抑制」高度近邻，**不能靠名称重命名证明原创** | Elsevier 全文访问受限，仅据出版方摘要与摘要预览；需要检查具体设计、发布时间（可能 2027 卷）、源码/量化对照 |
| Feng et al., **HarveST**, Communications Biology 9:681 (2026-03-27), DOI [10.1038/s42003-026-09841-2](https://doi.org/10.1038/s42003-026-09841-2) | 建 spot-spot、spot-gene、gene-gene 异质图以识别组织域，同时包括 SVG 和多切片；作者强调边界保真评价。PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC13187054/ | 已有用多模态图处理边界与小群体的研究，但不是 CellCharter 直接增强模型 | 详细检查九种指标与哪一些是边界指标；完整代码和完整方法再核 |
| **GATCL**, Briefings in Bioinformatics (2026), DOI [10.1093/bib/bbag043](https://doi.org/10.1093/bib/bbag043) | 摘要提出 GAT 动态分配邻域权重，融合对比学习处理空间多组学与边界问题 | 进一步排除「Attention 动态加权」是独一创新的说法 | 阅读全文具体加权、数据和与 CellCharter 的可比性 |
| **TRACER**, Bioinformatics 42(11) (2026-10-30), DOI [10.1093/bioinformatics/btag805](https://doi.org/10.1093/bioinformatics/btag805) | 摘要侧重细粒度和稀有空间域、邻域感知对比学习 | 小区域保护也不是无人研究的方向 | 需要比较细粒度/边界定义、评估口径 |

## 三、论文评价协议风险：AugGCL 官方代码需要核实

官网公开仓库：https://github.com/Jtfboom/AugGCL

公开 `train_AugGCL.py` 页面 https://github.com/Jtfboom/AugGCL/blob/master/train_AugGCL.py 中，能看到每个 epoch 把表示聚类后计算 `metrics.adjusted_rand_score(labels, idx)` 并用 `if ari_res > ari_max:` 保存最佳 epoch 的预测。**只是发现代码里有使用人工标签挑选 epoch 的流程**；该流程是否恰好用于论文所报告 DLPFC 151507 的成绩仍需追踪调用链。倘若使用，可能形成使用评价标签模型选择的协议问题；不可不经核查就断言论文作假或某项具体报告值由此而来。

对我们自己的原则：151507已开发使用，不再用此选择最优配置后充当独立测试。独立测试片需要事前锁定、检查供体/切片的独立性及标签使用边界。

## 四、GO/STOP 结论

- **STOP 作为“原创点”的方案**：仅仅用余弦相似度/表达相似度为物理邻居加权；直接采用 GAT 动态邻域权重；无差别宣称边界感知是新的。以上均存在已有工作。
- **允许条件性 GO 的下一步研究**：先把现象定义为**组织内部一致性 vs 组织层间可分性**的多尺度聚合权衡。在不动 scVI 的前提下做一个已知简单对照（如对分层聚合块进行事前固定尺度标准化、固定或规则化的层级权重，并配等维度/等 GMM 预算对照），观察是否使 L4/L5 与 L5/L6 检出有所恢复，同时不显著增加各层内部错误分割。这是**机制探针/候选优化**，不是已获原创性证明。仍须核查是否与相近多尺度加权方法重复。
- 训练预算/数据规则：先冻结开发集151507的设置；不要凭借人工边界直接训练权重。至少比较原 L4、简单权重缩放、等维度负对照、以及已有方法中真正最相近实现；独立切片或供体实验不得自动把已探索的151508称为完全盲测。
- **优先的下一件事（不需要运行本地实验）**：核查上述最近邻中 CodaST/AugGCL 的具体加权公式、作者实现、以及 CellCharter 多跳块尺度差异的可证伪机制，形成1页机制差异表，再选择唯一 MVP。

## 不应表述成已核验的内容

未完整读取 CodaST 全文，未复现 AugGCL/HarveST/GATCL/TRACER；没有跨样本结论，尚无新算法、无新对照或统计检验。本次用户明确停止追查历史 seed0 两份 GMM 预测分区不一致，不重新开启该任务。
