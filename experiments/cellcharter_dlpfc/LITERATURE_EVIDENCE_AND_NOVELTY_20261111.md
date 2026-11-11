# 第三篇：文献证据与创新性审查（2026-11-11，第一轮）

> 仅对已取得的期刊网页摘要、部分开放正文和官方API文档作了查证；不宣称阅读了全部付费全文和补充材料。真实本地结果与文献作者报告分开。

## 六篇已核实核心文献

|ID|出版来源、标题|DOI|核查结论|
|---|---|---|---|
|C1|Varrone M, Tavernari D, Santamaria-Martínez A, et al. CellCharter reveals spatial cell niches associated with tissue remodeling and cell plasticity. Nature Genetics 56:74–84 (2024).|10.1038/s41588-023-01588-4|期刊摘要明确是成熟的空间生态位识别、表征及比较框架；不能把CellCharter聚合算子据为原创。|
|C2|Lopez R, Regier J, Cole MB, et al. Deep generative modeling for single-cell transcriptomics. Nature Methods 15:1053–1058 (2018).|10.1038/s41592-018-0229-2|期刊摘要核实：scVI是已有概率深度生成表示方法。|
|C3|Maynard KR, Collado-Torres L, Weber LM, et al. Transcriptome-scale spatial gene expression in the human dorsolateral prefrontal cortex. Nature Neuroscience 24:425–436 (2021).|10.1038/s41593-020-00787-0|开放全文核实：12片来自3位独立供体、每供体两对邻近切片；原文已有空间域的多种数据驱动聚类分析。|
|C4|Xu H, Fu H, Long Y, et al. Unsupervised spatially embedded deep representation of spatial transcriptomics. Genome Medicine 16:12 (2024).|10.1186/s13073-024-01283-x|开放正文核实：SEDR有掩码自监督表示和变分图自编码器。用户本地参考标签CSV来自SEDR分析数据文件中layer_guess列，但不得推断标签由SEDR预测或为本研究人工判读真值。|
|C5|Zhang W, Zhang Z, et al. m2ST: dual multi-scale graph clustering for spatially resolved transcriptomics. Bioinformatics 41(5):btaf221 (2025).|10.1093/bioinformatics/btaf221|期刊正文及摘要：多尺度图表示、尺度共有/特有信息、熵调整尺度重要性均有成熟先例。|
|C6|Sun J, Biharie K, Cai P, et al. Beyond benchmarking: an expert-guided consensus approach to spatially aware clustering. Nature Methods 23:1814–1826 (2026).|10.1038/s41592-026-03194-8|开放全文：SACCELERATOR揭示DLPFC基准表现对参数、标注、复现和参照标签质量敏感，多方法共识与专家反馈并非空白。|

## 官方API事实及代码边界

- CellCharter官方文档 https://cellcharter.readthedocs.io/en/stable/generated/cellcharter.gr.aggregate_neighbors.html 明确：n_layers为整数时拼接spot自己的表示与1至n_layers跳邻域聚合特征；aggregations默认mean。用户代码调用n_layers=4、不显式设置聚合函数。若要断言0.3.2确切实现与文档对应，需锁定安装版本源码。
- 用户10片流程实际代码中SEDR layer_guess是上游参考元数据字段，不等于SEDR算法的输出结果；旧两片标注来源有待核实。
- 用户真实A/B配置是15维的L0+L1+L2 vs L0+L1+L4，每片Oracle K=5或7，固定GMM seed22911。

## 对最近邻方法的审查结论

1. **明确非原创**：scVI编码、CellCharter原有多层聚合、GMM、DLPFC空间聚类、调整邻域层数或挑选已有多跳特征块。
2. **高重叠风险**：尺度权重或融合已有m2ST等近邻研究；不能仅凭改变尺度权重宣称新算法。
3. **本项目真实实证工作**：等维特征块对照、12片/3供体完整正负结果、整体TP/FP/FN，以及选定151671/151676的组织层间边界召回。属于描述性/解释性实证贡献，当前检索不能支持‘全球首次提出’的断言。
4. **方法学风险**：Oracle-K依赖参考类别数，旧/新标注来源不同，只有3位独立供体；事后两片案例不能充当无偏独立测试。
5. **继续决策**：毕业论文章节继续推进；作为独立SCI新算法论文目前不应宣称创新成立。若以后需要创新，需要与m2ST及CellCharter最简单改动进行公平对照并通过预先锁定的跨供体验证。

## 仍待调查

- SEDR数据元信息layer_guess的真正上游标注来源，和旧151507/151508是否一致。
- CellCharter原论文的尺度层数消融、具体评价设置及完整补充材料；尚未取得完整付费全文。
- m2ST对尺度信息的细节及SACCELERATOR公开benchmark的源协议；本轮只核查实际浏览到的内容。

## 可核对原始网址

- https://doi.org/10.1038/s41588-023-01588-4
- https://doi.org/10.1038/s41592-018-0229-2
- https://doi.org/10.1038/s41593-020-00787-0
- https://doi.org/10.1186/s13073-024-01283-x
- https://doi.org/10.1093/bioinformatics/btaf221
- https://doi.org/10.1038/s41592-026-03194-8
