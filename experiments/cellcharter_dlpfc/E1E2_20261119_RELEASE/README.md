# CellCharter DLPFC E1/E2 — 完整实验统计与代码归档（2026-11-19）

> **唯一研究对象**：本仓库的第三篇 CellCharter DLPFC 多尺度聚类 E1/E2。**不要将本归档与仓库其他课题的 STAGATE、CARR、CTW-RF 等实验混为一谈。**

## 文件说明（2026-11-19 已上传，24个原始或派生文件）

| 目录 | 文件与作用 |
|---|---|
| [archives/](archives/) | 用户Windows原始12切片统计ZIP（包含每片4 CSV+1 provenance JSON，共12片）、ChatGPT派生审查与SVG完整ZIP |
| [scripts/](scripts/) | 单任务GMM、V1/V2安全批处理、V1/V2统计汇总、夜间顺序调度（6个py原样快照） |
| [derived/](derived/) | 9份派生CSV、3份可编辑SVG、1份完整中文审查报告、审计JSON以及2份复核/绘图Python脚本，共16个文件 |

两个ZIP均以**原二进制字节**写入GitHub Git blob，其Git object SHA与本地计算一致：

- `archives/e1e2_12slices_statistics_20261119_095251.zip`：SHA256 `446ad84a992a83c776ea768042ed198d6bdc794236c313c24f7d09ca8daef6ac`；
- `archives/E1E2_12切片_统计审查报告与矢量图_20261119.zip`：SHA256 `adec65a447d834bea6e6db85c5d71b3eda090bfe67d20efb750a13e204388404`。

**实验代码版本来自先前ChatGPT交付并可获取的源码文件，而非实时从用户Windows硬盘读取。** 任务代码/安全审计器/统计器SHA256与真实provenance记录一致。原始表达矩阵、逐spot预测CSV、完整Windows模型环境/依赖清单**未包含在此归档**，因此不能凭这批统计文件独立重做1200次基础ARI/NMI；统计包内部SHA及聚合结果已由`derived/recompute_zip_audit.py`检查。

## 核心实验状态

- 12 DLPFC slices × 10冻结尺度配置 × 10冻结GMM seed = **1200/1200项已在Windows完成并自动验收**。数据、手动注释和数据集来源按冻结协议；Oracle-K为151669–151672 K5、其余8片K7（依据人工标注类别数）。
- 相同15D候选`fixed_L0_L1_L4` vs 标准`cum_L0_L1_L2`：ARI差值12切片中7正5负（均值+0.003282），NMI9正3负（均值+0.010867）；151674、151675双指标负。不同切片/供体的异质性不能忽略。
- 3名独立供体、每名4片；`derived/sample_metadata.csv`中供体关系属于**公开附录推定分组、未与原始metadata独立比对**；K5与其中一名供体完全混杂。10个GMM seed只是算法重复，不是独立生物学重复；禁止seed/spot/section伪重复显著性检验。
- 12片结果已用于探索，不能再当作后验新方案的未见独立验证集。**E3–E6未完成**（K敏感性、边界、空间/marker、公平成熟基线、外部验证、候选方法及论文）。

## 给Claude的专用入口

**先读 [CLAUDE_REVIEW_START_HERE.md](CLAUDE_REVIEW_START_HERE.md)，再读 `derived/审查报告.md`、冻结协议与原始统计。**

Claude必须仅评审 **CellCharter DLPFC E1/E2结果和该研究后续E3–E6/论文实验章节**；仓库其他STAGATE、CTW-RF、CARR、稀有细胞等研究目录/实验结果都不在审查范围。全局`AGENTS.md`只取科研诚信、Windows手动执行与毕业目标等通用规则，不要借其交叉阅读无关课题。

当前归档可供独立科研规划与统计复核，**不等于方法创新已经确认，也不保证任何论文录用。**
