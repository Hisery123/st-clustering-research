# E5a 正式阶段末统一审计 PASS（用户Windows真实结果，2026-11-21）

## 状态 / 证据等级

**实际完成（不是计划）**：用户在Windows PowerShell返回了审计脚本的完整最终成功行：

```text
E5A_PHASE_AUDIT_PROGRESS checked=24/288
...
E5A_PHASE_AUDIT_PROGRESS checked=288/288
E5A_PHASE_AUDIT_FINAL status=passed verified=288/288 errors=0 report=D:\paper\CellCharter_reproduction\results\e5a_phase_audit_v1\audit_20261121T035302Z_5292\e5a_phase_audit_report.json
E5A_PHASE_AUDIT_TABLE D:\paper\CellCharter_reproduction\results\e5a_phase_audit_v1\audit_20261121T035302Z_5292\all_288_prediction_checks.csv
E5A_PHASE_AUDIT_DESCRIPTIVES D:\paper\CellCharter_reproduction\results\e5a_phase_audit_v1\audit_20261121T035302Z_5292\method_regime_descriptives.csv
E5A_PHASE_AUDIT_EXIT_CODE=0
```

对应正式实验会话：

| 子批 | 真实成功 | 会话/状态文件 |
|---|---:|---|
| 非空间GMM+Leiden | 144/144 | `results/e5a_baselines_v1/nonspatial_20261120T095303Z_15120/batch_status.json` |
| BANKSY | 72/72 | `results/e5a_baselines_v1/banksy_20261120T101256Z_26540/batch_status.json` |
| BayesSpace v1.1 | 72/72 | `results/e5a_baselines_v1/bayesspace_20261120T103557Z_11440/batch_status.json` |
| **总计** | **288/288** | 最终只读审计`status=passed`、`errors=0`、exit=0 |

只读统一审计的冻结脚本：`experiments/cellcharter_dlpfc/e5a_phase_audit_v1.py`，SHA256=`715922fc8a7ffe4757176396ef5e5d5e22330182e7e06db187b4d6778eb80278`。该脚本检查288任务唯一网格、预测CSV/manifest及SHA、条码顺序、同标签mask重算ARI/NMI、GMM/Leiden/BANKSY/BayesSpace各预冻K策略与轨迹、原输入SHA、冻结脚本本机SHA。**本次成功结论来自用户反馈的真实终端行**；本助手没有直接在GitHub持有这些原始CSV或直接打开Windows本地审计JSON，不能假装已读取某个ARI/NMI数值或声称已审查审计报告内的warning细节。

BayesSpace早先v1读取10x CSC未排序在0/72出现真实失败，失败会话`bayesspace_20261120T102925Z_30592`须永久记录。v1.1独立修复仅修改CSV/CSC加载，未改变Oracle-K/K-blind选K规则、10,000轮MCMC和3个技术seed。标签仅在拟合结果落盘后用于评价；结果中有K-blind选至q=10边界，必须保留并在论文讨论中说明。

## 科研边界

- 12张DLPFC切片来自3名供体，随机种子与spot不是独立生物重复。不能把288项任务当288个独立生物样本。
- GMM、Leiden在固定scVI-L0 5D；BANKSY和BayesSpace在原10x计数各自原生处理，**不是四法相同特征输入**。
- 成功审计代表E5a产物完整、决策规则与文件一致；并不证明CellCharter在ARI/NMI优于各对照，更不能证明原创性或统计显著性。数值由阶段末可重算的真实表导入后方可分析。
- 保留全部正负结果、失败纪录、K选择边界问题。不要为提升ARI临时修改已经执行的分辨率/seed/K范围。
- 按`E3_E6_Q4_EMPIRICAL_RESEARCH_GATE_20261119.md`规定，E5a PASS 后进入**E5b真正独立、有区域真值的外部数据集**，须事前冻结数据许可/样本/真值、训练/测试边界、K选择与预算；之后E6为条件可选。依`EXECUTION_FIRST_CLAUDE_FINAL_REVIEW_DECISION_20261120.md`，全部计划执行后交Claude集中审查，不在当前阶段穿插新增无关消融。

## 下一步

E5b为**设计/数据核查阶段，尚未训练**。先核实至少1个与DLPFC不同、样本来源独立、确有可靠人工空间区域标签的公开数据集，留存来源URL/DOI、授权、spot/barcode/真实坐标、标注独立性，核对数据是否先前参与调参、是否与CellCharter作者12片benchmark重叠；再冻结计算规模与公平协议，确定Windows下载/执行单步计划。不能因BayesSpace慢而事后删掉事前必须的对照；资源取舍要事前声明。
