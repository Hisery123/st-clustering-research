# E5b六患者外部验证：360项预测独立审计和ARI/NMI评价PASS（2026-11-22）

## 2026-11-22 原始audit_report.json补传完成（晚于此前三CSV归档）

用户后续提供Windows六审计文件ZIP，经SOURCE_SHA256逐份验证，**E5b原本缺失的原audit_report.json已原字节归档**至[E5B_20261122_RELEASE/derived/audit_report.json](E5B_20261122_RELEASE/derived/audit_report.json)，SHA256为`af4061f5072f2b976aee7edbbb73dfeb7704b58eb363f927e1949871eb4f17fb`。JSON中`phase1=passed`、`phase2=passed`、`verified_predictions=360`、`all_metrics_count=360`及3份CSV哈希均与已归档原指标吻合。GitHub远端重读验证PASS。原360份源预测、Reference-only标签、10x原矩阵**未随本次ZIP上传**；这不影响已归档指标的原件真实性，但仍限制第三方在GitHub上重做源级ARI/NMI。


## 2026-11-22补充归档更正（后于首份审计记录）

先前正文写“用户尚未上传CSV”，那是**审计日志刚成功时**的历史状态。用户随后已在ChatGPT上传三份真实原始CSV，并授权将其提交GitHub；现在全部3份CSV、后验审查报告、3张SVG和绘图脚本（共8份原始字节已核SHA）已经在[**E5B_20261122_RELEASE**](E5B_20261122_RELEASE/)公开归档，见[manifest.json](E5B_20261122_RELEASE/manifest.json)。这一补充不更改旧实验状态和时间线；**audit_report.json及原360预测/标签文件仍仅在Windows**。后验结果审查不能反向称为实验前预注册分析。跨阶段总清单见[RESULTS_ARCHIVE_STATUS_20261122.md](RESULTS_ARCHIVE_STATUS_20261122.md)。

## 实测证据（用户Windows原始终端日志）
```text
E5B_AUDIT_STAGE_PASS method=BayesSpace checked=36
E5B_AUDIT_PREDICTIONS_PASS verified=360/360 errors=0 labels_not_yet_read=True
E5B_PHASE_AUDIT_FINAL status=passed verified=360/360 metrics=360/360 errors=0 report=D:\paper\CellCharter_reproduction\results\e5b_external_v1\phase_audit_v1\audit_20261122T030849Z_17404\audit_report.json
E5B_PHASE_AUDIT_FILE D:\paper\CellCharter_reproduction\results\e5b_external_v1\phase_audit_v1\audit_20261122T030849Z_17404\all_360_prediction_metrics.csv
E5B_PHASE_AUDIT_FILE D:\paper\CellCharter_reproduction\results\e5b_external_v1\phase_audit_v1\audit_20261122T030849Z_17404\patient_three_seed_summary.csv
E5B_PHASE_AUDIT_FILE D:\paper\CellCharter_reproduction\results\e5b_external_v1\phase_audit_v1\audit_20261122T030849Z_17404\patient_paired_effects.csv
NO_REFIT_NO_PARAM_CHANGE_PATIENT_N6
E5B_AUDIT_EXIT_CODE=0
```

**正式完成（不是计划）**：六患者共360份正式模型预测由此前Windows日志全部运行完成；本次由独立只读审计程序报告360/360份完整预测文件与决策轨迹均通过文件SHA、barcode对齐和预定选K规则检查，随后以固定病理掩码计算360/360份ARI、NMI；错误数0、退出码0、无重新拟合、无参数改变。注意日志中的labels_not_yet_read=True只对应第一阶段尚未读取标签的验收检查点；通过后第二阶段已读取只读参考病理标签完成指标计算，不能说整个审计都没读标签。

已提交审核工具 experiments/cellcharter_dlpfc/e5b_phase_audit_and_evaluation_v1.py；commit 57fe010d22258e54d080749c60fa57daf42b49d7，SHA256 a9a65171ba6631d07c2eb9f606140c6d3a37d40854bec03e14eeae223594940e。

## 输出文件及证据边界
- all_360_prediction_metrics.csv：全部360份原始种子级ARI/NMI、K臂、方法、预测SHA。
- patient_three_seed_summary.csv：120条六患者×十种方法/尺度×双K臂的患者内3seed均值、SD。
- patient_paired_effects.csv：144条以患者为单位的A15D−L0、B15D−A15D、A15D−四成熟基线差异。
- 用户当前只提供了成功终端日志，并没有上传CSV或audit_report.json。因此本助手不曾直接检查各项真实ARI/NMI数值、效应方向、方法排名或统计不确定性，不能虚构任何性能优势或发表性判断。

## 科研红线与关键异常
1. 仅六名不同患者是独立生物学单位n=6，三个seed和15324个有效spot都非独立患者。
2. K-blind与标签类别数知情的Oracle-K分开：Oracle-K不保证更优得分，也不是真正的无监督K选择。
3. CID4535 BayesSpace Kblind q=10命中冻结K2..10上界；BANKSY CID4535 Kblind实际K8、K7、K8；CID44971某Oracle-K目标K6实际K5；BayesSpace曾提示仅1123/1125识别到邻居，均完整保留、不因结果调整参数或筛spot。
4. E5b每患者自身计数重新拟合scVI，不是DLPFC模型直接跨组织迁移；BANKSY和BayesSpace有原生不同输入及预处理，比较时须解释。
5. 负结果/失败/边界和不平衡小类全部保留；跨样本统计以患者n=6为单位，不将360个预测文件作为独立重复。Oracle单列辅助解释。

## 下一步
单一Windows人工步骤：用户直接上传同一审计目录内的三个CSV原件到对话，供本助手真实读取、复算患者级效应、查看全量正负结果和拟可编辑数据图。完成真实数据分析后再形成供Claude独立科研方法总审的证据包；不重训、不再调K/seed/尺度。
