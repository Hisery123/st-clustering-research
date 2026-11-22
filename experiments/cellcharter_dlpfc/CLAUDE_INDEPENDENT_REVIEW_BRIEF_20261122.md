# Claude独立审稿入口：CellCharter第三篇（2026-11-22更新）

请在GitHub默认`main`的当前HEAD上重新读取文件，勿仅根据旧会话总结判断。

## 推荐阅读顺序

1. [全项目科研存档状态（已更新）](RESULTS_ARCHIVE_STATUS_20261122.md)，明确区分“运行PASS、指标已算、GitHub可读取结果、仍缺原模型文件”。旧审查中'E3d/E5a/E5b结果未上传'的状态**已过时**。
2. [E5b RELEASE说明及manifest](E5B_20261122_RELEASE/README.md)和[所有360条ARI/NMI](E5B_20261122_RELEASE/derived/all_360_prediction_metrics.csv)、[120条患者汇总](E5B_20261122_RELEASE/derived/patient_three_seed_summary.csv)、[144条患者配对差异](E5B_20261122_RELEASE/derived/patient_paired_effects.csv)。
3. [E5b冻结协议](E5B_FROZEN_EXTERNAL_VALIDATION_PROTOCOL_20261121.md)、[E5b成功审计日志](E5B_FINAL_AUDIT_PASS_20261122.md)、[E5b原audit_report.json](E5B_20261122_RELEASE/derived/audit_report.json)及[执行/审计代码](e5b_phase_audit_and_evaluation_v1.py)。
4. [E1/E2 RELEASE](E1E2_20261119_RELEASE/)和[E3c RELEASE](E3C_20261120_RELEASE/)的完整原始派生表、可复现图源、统计单位。
5. **新归档已可直接打开原始字节**：[E3d 48行AutoK审计CSV和原JSON](E3D_20261122_RELEASE/)以及[E5a 288行四成熟基线真实ARI/NMI和原JSON](E5A_20261122_RELEASE/)。来源SHA256见[六审计文件Windows导出清单](AUDIT_EXPORT_20261122/SOURCE_SHA256.csv)。**E3d仍未计算ARI/NMI**，不能把K审计当性能评价；E5a已计算ARI/NMI，Claude必须直接检查288行数据，而不是仅凭审计PASS。
6. [E4空间图审计](E4_FINAL_AUDIT_PASS_20261120.md)、[旧第四章草稿](chapter_04_results_integrated.tex)、[文献新颖性审查](LITERATURE_EVIDENCE_AND_NOVELTY_20261111.md)。

## 必须审的问题

- **先独立复核公开CSV**：360行预测数据到120行患者级汇总、144行患者配对的数值一致性。六例独立患者；3个随机种子不是18个独立患者。主要结果为K-blind，Oracle-K是标签类别数知情敏感性分析。
- **不得先假设CellCharter有优势**：A15D–L0在六患者ARI/NMI均正向，但对BayesSpace的ARI仅4/6正向，NMI六患者宏均值差为负；各患者绝对ARI存在低值。
- **选K边界**：E5b BayesSpace K-blind的18/18次、**E5a BayesSpace K-blind的28/36次**均落在q=10上限；E3d的K=2/10边界10/48。分辨率和选K是否阻碍公平比较、是否有合理敏感性解释？不许倒改冻结K范围。
- **方法不同输入**：非空间GMM/Leiden共用scVI 5D，BANKSY/BayesSpace有原生基于counts的处理；CellCharter尺度扩增时维度也增长，AutoK可能变动，不能把所有效应归因于空间机制。
- **独立与泄漏**：DLPFC 12切片来自3供体，Wu乳腺癌6独立患者；说明这是对流程/研究结论的独立队列外部评价，不是把DLPFC训练模型直接迁移到乳腺癌。
- **结果选择时间线**：E5b原冻结协议早于360任务，后面的分析报告及比较是在读取全部结果后编写。**不可在结果已读后再伪装成事前主要比较或预注册显著性方案**；若使用bootstrap95%CI，要明确事后补充与n=6的限制。
- **论文定位与创新性**：必须检查Varrone et al. 2024 CellCharter原论文**全文及补充材料**、最近邻尺度消融研究；明确原生算法与本研究的复现/评估贡献不同。引用不因来源/期刊偏好而选择性遗漏。
- **证据边界**：**E3d和E5a审计原始CSV+JSON、E5b原审计JSON现在均已GitHub归档并SHA验证**；但GitHub仍无源模型预测、原始counts、reference-only标签全量内容，不能声称仅凭本仓库就可从头复算360/288项ARI/NMI。E3d新后验ARI/NMI仍是待做，和数据归档是不同工作。

## 审查交付格式

请分别列出：A.已实证验证事实；B.仍缺来源/代码执行/原文件的事项；C.可支持的论文贡献；D.CRITICAL/MAJOR/MINOR问题和最小整改，不修改当前实验规则、不自动运行任何实验。指出无法复算的指标与未形成证据的“显著、优于所有方法、算法创新”等措辞。负结果与边界均保留。确认是否可写Methods / Results / Discussion的各部分，不以是否获得高分作为唯一刊发标准。
