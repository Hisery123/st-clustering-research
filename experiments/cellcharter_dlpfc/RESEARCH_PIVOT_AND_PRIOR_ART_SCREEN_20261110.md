# 2026-11-10 · 停止历史 GMM 原因排查，转向最近邻文献与最小机制研究

## 用户决定（优先级最高）

2026-11-10 用户明确要求**终止对历史两份 seed0 L4 GMM 不一致原因的持续诊断**，认为跨 GPT 对话上下文中断可能造成流程不一致；该解释是**用户提出的可能性，而非已证实根因**。不得再自动要求用户读取两个历史 predictions.csv、重跑拟合、查 RNG、复核 barcode 或循环继续该问题。仅保留历史差异和实验局限；若未来正式结果可信度取决于此，再解释必要性并征求用户意愿。

## 下一阶段（S2/S3）

当前 CellCharter 151507、seed22911、Oracle K7 的 L0–L4 与边界审计已完成。单切片观察：L4 整体 ARI 高，L5/L6 界面 0/145，L4/L5 ~3/160；L0 界面召回高但层内伪边界很多；L4 上层界面部分召回反弹。因此目标是**探索保持组织内部连续性同时保留边界的最小机制**，但不能将过度平滑归为已证实因果。

初步最近邻标题级/摘要级检索（链接供后续阅读全文核验；不应据此断言创新或论文不存在）：

1. Varrone et al., *CellCharter reveals spatial cell niches associated with tissue remodeling and cell plasticity*. Nature Genetics 56, 74–84 (2024). DOI https://doi.org/10.1038/s41588-023-01588-4。当前母体；主要目标 cellular niches 而非直接等同 DLPFC 边界优化。
2. *AugGCL: Multimodal graph learning for spatial transcriptomics analysis with enhanced gene and morphological data*. PLOS Computational Biology (2026). DOI https://doi.org/10.1371/journal.pcbi.1013912。摘要声称将表达相似度与空间距离用于加权图/邻域聚合并关注边界清晰度，和潜在候选机制高度接近。需核查原文与代码。
3. *HarveST uses a heterogeneous graph learning framework to reveal spatial transcriptomics patterns*. Communications Biology (2026). https://www.nature.com/articles/s42003-026-09841-2。论文摘要声称明确评测边界保真，必须检查具体指标和机制。
4. *A local-global dual-contrastive graph learning approach for robust domain identification in spatial transcriptomics*. Pattern Recognition (2026), DOI https://doi.org/10.1016/j.patcog.2026.114923。摘要提出 local semantic weighting 保留锐利组织边界。与候选机制紧密相关，需全文核对。
5. *spAttClu: a spatial domain clustering model leveraging spatially weighted graph attention and contrastive learning*. Bioinformatics (2026), DOI https://doi.org/10.1093/bioinformatics/btag384。用户不将其继续作为新母体，但最近邻审查不可略去。

**注意**：此列表只是初步检索，不是已完成系统综述；未逐篇查完整文献、代码版本、修订/撤稿与真正机制。对任何“自适应邻域权重/边界保护”的创新性主张保持保留态度。尤其已有邻域加权边界保护方案，不能用模块重命名冒充原创。

## 接下来建议

先精读与候选机制最接近的 AugGCL、HarveST 等前作的原始方法、图/伪代码和评价协议，制作可核实的最近邻证据对照，再决定 CellCharter 上**一个**最小改动及不依赖手工标签的门控信号。制定固定预算、固定 K 与独立供体验证协议后，再由用户在 Windows 手动跑最小实验。
