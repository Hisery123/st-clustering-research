# 第三篇CellCharter DLPFC科研存档：2026-11-19 E3c 首张切片200/200完成

> 最新事实依据：用户在Windows手动训练的原始终端输出及最后一次`--sample 151509`只读完整性审核。此文是**交接与状态摘要**，不是新的模型训练或全12片新审计结果。

## 唯一当前研究范围和目标

仅第三篇**CellCharter DLPFC 12切片聚类多尺度/随机初始化/K敏感性实证评价**，不与仓库中STAGATE、spAttClu、CTW-RF、CARR等其他实验混合。首要目标是硕士论文章节；普通SCI四区实证评价论文属于**有条件GO**，仍需K敏感性与AutoK、公平成熟基线、真正独立外部验证及近期文献原创性审查，不承诺投稿成功，不声称有新算法或普遍尺度增益。

## 冻结协议与已完成任务

- 冻结E1/E2：12片×10尺度配置×10 GMM seed = **1200个已完成且此前统计包审计通过的任务**。原始统计与派生报告、代码快照在 [E1E2_20261119_RELEASE](E1E2_20261119_RELEASE/)，并非所有Windows原始预测均在GitHub。
- E3a供体：Br5292=151507–151510，Br5595=151669–151672，Br8100=151673–151676；其中**10张来自本地正确解析TSV逐行验证，151507/151508来自公开论文补充表**。151507目录下`metadata.tsv`的3661行实为151669 Br5595元数据复制件，和151669源文件SHA256一致，**禁用其作为151507的供体元数据，不删除原文件**。上游特征缓存生成链尚未全盘核验。
- [E3c冻结协议](THIRD_PAPER_E3C_K_SENSITIVITY_FROZEN_PROTOCOL_20261119.md)：4种累计特征配置（10/15/20/25D）×固定K={5,6,7,8,9}×10冻结GMM seed×12片 = **2400格**；其中每片40格原Oracle-K E1/E2结果须逐格审计复用（共480），**另1920格为计划新拟合**。这只是固定K**敏感性试验**，并非无标签AutoK。ARI主指标，NMI次指标，GMM CPU full covariance，固定原冻结种子和同一缓存。不依据标注选择最优K/seed进行“盲测”叙述。
- 已复用的任务和新增任务严格区分：**151509已完成全量160项新K拟合，并经独立只读全矩阵审计**，共**200/200格** = 40旧Oracle-K + 160新K；**NEW_TASK=0**。其他11片按已知最新记录尚未启动新K拟合；全局已有新K **160/1920**、剩余**1760**（根据日志和本样本独立审计推算），**尚未在151509完结后再跑一次全12片`--sample ALL`审计**。
- 用户最后的原始、完整成功标记：
```text
PREFLIGHT_SAMPLE_OK sample=151509 verified_reused=40 verified_existing=160 pending_new=0 total=200
E3C_GRID_PREFLIGHT_PASS total=200 REUSED_AUDITED=40 EXISTING_AUDITED=160 NEW_TASK=0
DRY_RUN_ONLY NO_TRAINING_NO_FILES_WRITTEN
```
- 完成151509新增任务的真实日志由用户提供：1次单任务冒烟 + 分批5、20、134项；末次`E3C_BATCH_COMPLETE new_audited=134`，session目录`D:\paper\CellCharter_reproduction\results\e3c_k_sensitivity_batch_sessions_v1\20261119T100130Z_e8c1b031a6\session_status.json`。后续只读审计核实全部160新任务文件一致，无本次重新训练。

## 代码与数据入口（Windows操作由用户亲自执行）

- Windows科研根目录：`D:\paper\CellCharter_reproduction`。
- 实际Python：`D:\paper\CellCharter_reproduction\env_cellcharter\python.exe`。
- [E3c单任务代码](e3c_k_sensitivity_single_task_v1.py)；[E3c安全批量审计/续跑器](e3c_k_sensitivity_batch_runner_v1.py)。已在151509真实完成批量训练和独立审计，脚本默认无`--run`为只读，带`--run --max-new`才运行；损坏旧输出/哈希不一致会停止，不覆盖或自动重试。旧版E1/E2源码SHA已在用户Windows核对3/3一致。
- 本地E3c新增输出：`D:\paper\CellCharter_reproduction\results\e3c_k_sensitivity_v1\<sample>\<condition>\k_<K>\seed_<seed>\`（含manifest、predictions、metrics），**截至本次存档未将这160项E3c本地原始预测/结果目录上传GitHub**。GitHub已归档代码、研究协议和终端证据，**不能误称原始Windows结果已经备份**。

## 科研边界和禁忌

1. 只有**3名独立供体**，12片切片属于供体内重复，seed是算法重复，spot亦非独立生物重复；不做伪重复显著性报告。
2. Oracle-K基于人工层标签数，和无标签AutoK必须分开；K5与Br5595供体混杂。预定K网格和阴性结果应全部报告。
3. E1/E2的15D/20D/25D涉及尺度与维度联动；同维15D替换实验结论有负结果，不可宣称普遍改进。151509已被反复查看，不能当独立外部测试集。
4. 新对话要以本次原始结果优先，不得被旧日记中“E3尚未开始”“151509仍待训练”等已过时段落误导。
5. 不得读取或复用其他STAGATE等课题的实验结果来支撑本研究。**默认不使用Codex，不代用户在Windows运行实验。**

## 下次读档的唯一优先任务

先确认本存档与`PROJECT_STATE.md`及最新`RESEARCH_JOURNAL/2026-11-19.md`一致。然后按同一冻结协议推进**151510**（其原Oracle-K=7）：先只读审核该片200格，再在已通过机制下运行最多160个新K任务。批量运行命令（需要用户下一回合主动决定执行，**本次存档未执行**）：

```powershell
& 'D:\paper\CellCharter_reproduction\env_cellcharter\python.exe' 'D:\paper\CellCharter_reproduction\e3c_k_sensitivity_batch_runner_v1.py' --sample 151510 --run --max-new 160
```

此运行器在训练前本身做全量fail-closed审计；若用户希望更保守，可先单独不加`--run`预检。预期成功`E3C_BATCH_COMPLETE new_audited=160`；若失败，保留已有任务与session日志，反馈`E3C_BATCH_HALTED`等原文后审查。**不要以预期结果冒充新数据已完成**。

完成其余11片后，应跑`--sample ALL`全矩阵只读审计并单独开发K敏感性汇总CSV/SVG；E3d AutoK、E3b边界、E4空间图、E5成熟公平基线/独立外部验证、E6可选消融均还未正式完成。

## 2026-11-20 09:34（北京时间，按用户会话时间）｜E3c全12切片K网格2400/2400独立只读审计PASS（正式验收）

**用户Windows真实终端末尾输出**：
```text
PREFLIGHT_SAMPLE_OK sample=151675 verified_reused=40 verified_existing=160 pending_new=0 total=200
PREFLIGHT_SAMPLE_OK sample=151676 verified_reused=40 verified_existing=160 pending_new=0 total=200
E3C_GRID_PREFLIGHT_PASS total=2400 REUSED_AUDITED=480 EXISTING_AUDITED=1920 NEW_TASK=0
DRY_RUN_ONLY NO_TRAINING_NO_FILES_WRITTEN
COMPLETED_SAMPLES 151507,151508,151669,151670,151671,151672,151673,151674,151675,151676
FAILED_SAMPLES
E3C_ALL_2400_AUDITED_PASS
SESSION_LOG D:\paper\CellCharter_reproduction\results\e3c_overnight_20261120_001819.txt
```

**本次关键进展**：前次151509全200格已独立复核、151510新160项已runner内部审核；此次新`--sample ALL`只读复核覆盖全部12切片×4累计尺度×5固定K×10种子=2400格，480旧Oracle-K格审计复用、1920新增K格审计确认为existing，**NEW_TASK=0**。因此现在可标记`E3C_ALL_2400_AUDITED_PASS`，E3c**实验运行及全网格产物审计完结**；夜间其余10片均被PowerShell包装脚本列为完成、`FAILED_SAMPLES`为空。仅据用户贴出的终端而非助手直接打开全部原始Windows文件、session日志；不能将`FAILED_SAMPLES`空行推断为所有历史批次从未出过任何错误。输出总数不等于已经完成E3c跨K/尺度/供体统计、可视化或科学解释；这些尚待进行。

**研究约束**：冻结E3c为CPU TorchGMM 4累计尺度10/15/20/25D×K{5,6,7,8,9}×10 GMM种子；历史Oracle-K参考人工标签类别数，仅作为有标签知情条件；K网格对照不是无标签AutoK。3位供体才是生物学来源，切片和种子不能伪作独立生物学重复。所有K和seed均须完整报告；不得事后以ARI最大K当成独立无标签方法。E3d AutoK、E3b边界指标、E4空间/marker、E5公平基线/独立外部验证、E6可选候选改进仍未完成。

**下一步唯一优先事项**：停止E3c拟合；只读从Windows完整E3c任务输出导出规范化新K逐任务表（1920行）并联合GitHub已有E1/E2真值知情Oracle-K480行构成2400行分析集；逐格核验键唯一、ARI/NMI数值范围、标签mask、供体嵌套和来源哈希，产出跨K稳定性及敏感性汇总、真实SVG。用户尚未上传本地新E3c原始预测CSV/metrics/manifest，GitHub更新仅是文档存档，**不等于原始训练结果备份**。执行前还应实际核查要运行的统计汇总脚本，勿修改冻结原结果。夜间SESSION_LOG在用户Windows本机，助手未直接读取。


