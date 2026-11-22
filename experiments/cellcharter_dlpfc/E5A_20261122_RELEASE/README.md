# E5a · DLPFC四成熟基线288份原始审计结果 (2026-11-22归档)
**真实完成：** 四种成熟基线GMM、Leiden、BANKSY、BayesSpace在12张DLPFC切片（3供体）上，按K-blind/Oracle-K×三个技术种子执行，审计报告为 `status=passed`、`checked=288`、`errors=[]`；下列真实CSV含288项全部聚类评价ARI/NMI与各方法/设置8组描述统计，未筛掉负结果。
- [288项原始审计及ARI/NMI](derived/all_288_prediction_checks.csv)
- [8组方法×K模式描述统计](derived/method_regime_descriptives.csv)
- [原始审计JSON及warnings](derived/e5a_phase_audit_report.json)
**重要警示：** 原审计JSON标记BayesSpace K-blind中28/36次选到冻结搜索范围上限q=10；这一问题必须在基线公正性讨论中明确保留，不准因结果调参。12切片嵌套于**3名独立供体**；不能把288个预测当作288份独立生物样本。GMM/Leiden使用scVI 5D、BANKSY/BayesSpace使用原生counts，不是共享全部特征和完全相同预算的公平同输入对比。
**来源：** `D:\paper\CellCharter_reproduction\results\e5a_phase_audit_v1\audit_20261121T035302Z_5292`，经Windows复制文件的压缩包和来源SHA256清单。GitHub三份内容与用户原件**逐字节一致**；见 [manifest.json](manifest.json) 与 [跨阶段Windows来源清单](../AUDIT_EXPORT_20261122/SOURCE_SHA256.csv)。
**后续统计：** 12张切片层次结构须按3名供体处理，每供体内切片/技术seed汇总；若新增患者/供体配对推断或更严格不确定性，明确是本次上传后另行开展的分析，不得倒填为原始预注册统计。
