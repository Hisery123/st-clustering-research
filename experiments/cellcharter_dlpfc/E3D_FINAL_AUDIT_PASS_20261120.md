# E3d 12切片×4尺度无标签AutoK — 阶段末统一文件审计PASS（2026-11-20）

## 证据等级与原件位置

**真实用户Windows终端回报**；用户已运行冻结`e3d_autok_final_audit_v1.py`并提供48个逐项`E3D_PHASE_AUDIT_PASS`以及终审汇总与退出码。助手未取得或直接查看Windows原始JSON/CSV/NPZ字节，不能说原始结果已上传GitHub，也不能宣称Claude独立审查已完成。

- 批次终审输出：`E3D_PHASE_AUDIT_SUMMARY status=passed verified=48/48 errors=0 label_fit_archives=2640/2640 boundary_hits=10 best_converged=528/528`
- 真实退出码：`E3D_PHASE_AUDIT_EXIT_CODE=0`
- **用户本机审计原件**：`D:\paper\CellCharter_reproduction\results\e3d_autok_phase_audit_v1\20261120T072220Z_24992\audit_report.json`；同目录`all_48_autok_audit.csv`为脚本约定派生表，尚未从用户Windows读取。
- **训练批次**：`D:\paper\CellCharter_reproduction\results\e3d_autok_batch_sessions_v1\20261120T061725Z_16624\session_status.json`；运行终端已确认新算46/跳过已存在2/失败0/待运行0/退出0。
- E3d代码/正式方案已在GitHub：`e3d_autok_single_config_v1.py`、`e3d_autok_batch_runner_v1.py`、`e3d_autok_final_audit_v1.py`、`E3D_AUTOK_FROZEN_PROTOCOL_20261120.md`。

## 48组无标签选K实际记录（按切片与特征维度10/15/20/25D排列）

| DLPFC切片 | 10D | 15D | 20D | 25D |
|---|---:|---:|---:|---:|
| 151507 | 2 | 4 | 4 | 4 |
| 151508 | 2 | 2 | 6 | 2 |
| 151509 | 4 | 3 | 6 | 3 |
| 151510 | 2 | 5 | 5 | 2 |
| 151669 | 5 | 7 | 6 | 8 |
| 151670 | 2 | 8 | 9 | 5 |
| 151671 | 8 | 3 | 6 | 3 |
| 151672 | 9 | 6 | 6 | 6 |
| 151673 | 6 | 7 | 7 | 9 |
| 151674 | 8 | 8 | 6 | 2 |
| 151675 | 8 | 3 | 10 | 4 |
| 151676 | 8 | 2 | 6 | 6 |

**原样分布**：`{'2':9, '3':5, '4':5, '5':4, '6':11, '7':3, '8':7, '9':3, '10':1}`，合计48。K=2下边界9次、K=10上边界1次，共10/48，按冻结协议**仅描述，不拓宽或重新训练**。

**审计通过的含义：** 全48配置各含11种内部K×5运行的标签档案并校验原文件SHA256、条码/维度/协议与K/稳定性；每种K的最佳模型共528/528标记收敛，但**未检查全部2640个GMM运行是否均收敛**。该审核不读取人工层标签，未计算后验ARI/NMI，不能由选K列表断言模型泛化能力、统计显著性或论文新颖性。DLPFC独立供体仅3名，48项不是48个生物重复。

## 下阶段执行纪律

遵照`EXECUTION_FIRST_CLAUDE_FINAL_REVIEW_DECISION_20261120.md`：**E3d不继续新增实验或逐项审核**。按既定顺序进入**E4：全12切片空间图、参考层/原始A/B聚类图与marker表达定性展示**（不重训scVI/GMM，图由真实数据可重复生成，SVG为主，完整12片正文/附录按冻结的选择规则）。E5a成熟基线、E5b独立外部数据、E6可选消融按照下一阶段方案推进；完整计划结束后由Claude集中论文方法学审核，结果阴性不掩盖。
