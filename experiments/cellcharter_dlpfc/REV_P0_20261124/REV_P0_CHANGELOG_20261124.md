# REV_P0 修改前后差异摘要（2026-11-24）

## 范围与保护措施

- **改动范围：** 只修改论文文本，并新增可追溯的汇总表。
- **没有改动：** V1（`*_v1_20261122.*`）、layout V2（`*_layout_v2_20261123.*`、V2 附录、V2 PDF）、E1–E5 全部冻结数据、预测、SVG/PDF 图件。
- **没有执行：** 任何训练、重新拟合或重新预测。
- **完整逐行差异：** `REV_P0_DIFF_vs_V1_20261124.diff`（unified diff，上下文 1 行）。生成方式：比较 V1 / V2 原文件（取自仓库 `main` 分支 `b04957b6`）与本修订版。
- **静态检查结果：** `REV_P0_STATIC_CHECK_20261124.txt`。所有修订文件的括号与环境都已闭合，无未定义 `\ref`，无缺失 `\cite`，正文中没有残留"待插入/尚未上传"字样。**本修订没有经过 XeLaTeX/BibTeX 实际编译。**

## 新增或改名的文件

| 修订版文件 | 来源文件 | 变更块数 |
|---|---|---|
| `cellcharter_study_introduction_module_rev_p0_20261124.tex` | `cellcharter_study_introduction_module_v1_20261122.tex` | 4 |
| `chapter_02_background_rev_p0_20261124.tex` | `chapter_02_background_rewrite_v1_20261122.tex` | 4 |
| `chapter_03_methods_rev_p0_20261124.tex` | `chapter_03_methods_rewrite_v1_20261122.tex` | 8 |
| `chapter_04_results_rev_p0_20261124.tex` | `chapter_04_results_rewrite_v1_20261122.tex` | 17 |
| `cellcharter_study_conclusion_module_rev_p0_20261124.tex` | `cellcharter_study_conclusion_module_v1_20261122.tex` | 9（整体改写） |
| `thesis_cellcharter_references_rev_p0_20261124.bib` | `thesis_cellcharter_verified_references_20261122.bib` | 11 |
| `cellcharter_study_full_preview_rev_p0_20261124.tex` | `cellcharter_study_full_preview_layout_v2_20261123.tex` | 10 |

附录沿用未修改的 `appendix_e4_all12_figures_layout_v2_20261123.tex`。

## 按 P0 项列出的改动

### P0-1：与原作者工作的重叠

- **引言：**
  - 补充原作者的 DLPFC 基准：调参集与测试集划分、2/3/4 层网格、最终配置；
  - 说明 15D/20D/25D 对应原作者网格中的 2/3/4 层；
  - 把"新增内容"限定为原作者未做的几项。
- **第二章：** 删去"未核对补充材料"的声明，新增 §"原作者在 DLPFC 上已完成的工作"，共 4 条，每条都标注了原文、补充材料或官方库的出处；明确写出哪些重叠、哪些是新增。
- **第三章：** 新增表"本研究 DLPFC 25D 流程与 CellCharter 官方单切片基准的设置对照"，共 10 项；说明 25D 配置是原作者在 151507/151672/151673 上按标签调出的。
- **第四章：**
  - 新增 §"与 CellCharter 原作者单切片基准的对照"，含表 T7 的宏平均对照；
  - 逐条写出不能称为严格复现的 4 个理由；
  - 补充"STAGATE 在官方单切片结果中最好"。
- **结论：** 首段明确写出"在原作者基准之上作扩展性的实证评价，不是新方法，也不是首次发现"。

### P0-2：B15D

- **第三章：** 补写 B 的提名经过（151507、种子 22911、+0.047）及选择偏倚。
- **第四章：**
  - 把 V1 中的单段描述改为 5 条分口径说明，并新增表 `tab:cc-b-minus-a-rev-p0`；
  - 12 切片 +0.0033（预设）与排除开发切片后的 −0.0035（事后）**分开写、分开解释**；
  - 补充按供体的结果和 E5b 外部结果（K-blind −0.0364）；
  - 把 B 定性为"开发集提名、经扩展评价未获稳定支持的负结果"。
- **V1 中保留的事实：** "早期单个种子下 B 的平均 ARI 与边界 F1 下降"仍然成立，现以种子 22911 新增 10 切片 ΔARI −0.0256（3/10）给出具体数值。

### P0-3：严格边界 F1

- **第四章：**
  - 表 `tab:cellcharter-boundary-v1` 扩展为 0-hop F1/P/R、1/2-hop F1 和"预测/参考"边界数比；
  - 改写解读：5D 与 10D 基本持平，**10D 略高**；严格 F1 的变化主要来自 recall，而 recall 与预测碎片化有关；
  - 新增"无零模型"的限制。
- **结论：** 第四条同步修改。

### P0-4：深度异质性、AutoK 与不确定性

- **第四章：**
  - 表 `tab:cellcharter-e1e2-depth-v1` 增加切片间 SD、种子 SD 与 D1–D3 列；
  - 新增 6/12、5/12 等方向不一致的计数和 D3 方向相反的说明；
  - 新增 E3c 在各 K 下尺度排序稳定的说明；
  - E3d 部分新增：选中 K 与参考类别数一致只有 1/12、20D 在 D2 中最低、5 次重复与逐切片运行的限制。
- **第三章：**
  - 统计一节补充种子 SD 的含义，并与官方 0.051 对比；
  - E3d 一节补充与原作者 10 次重复、联合选 K 及 25 次收敛检查的差异。

### P0-5：基线公平性

- **第二章：** BayesSpace 一段改为"与官方 elbow 建议不一致"并引用 vignette；GMM 一段补充"BIC 偏向多簇"的原作者观察。
- **第三章：**
  - K 规则一段补充 GMM 的 BIC 规则同样大量命中上界；
  - 补充本研究 BayesSpace 设置与原作者基准设置的差异；
  - 补充"对照集不含 STAGATE"。
- **第四章：**
  - E5a 表新增"K-blind 规则"和"命中 K=10"两列，其中 **GMM 为 32/36（V1 未报告）**，BayesSpace 为 28/36；
  - 说明 CellCharter 与基线的 K-blind 结果来自不同协议；
  - E5b 部分新增：BayesSpace 的 K-blind NMI 最高；GMM 8/18 命中上界；在低 ARI 患者中差值很小；Oracle-K 下 A15D 低于 BayesSpace 与 Leiden；B15D 在外部 K-blind 下低于 A15D。
- 所有原冻结结果都保留，没有推测改用 elbow 规则后的结果。

### P0-6：BibTeX

- `varrone2024` 作者改为 Marco Varrone、Daniele Tavernari、Albert Santamaria-Martínez、Logan A. Walsh、Giovanni Ciriello，并补 `number={1}`。
- `sun2026` 补 `number={9}`，并补全前 3 位作者的名。
- `lopez2018` 补全 5 位作者（依据 CellCharter 原文参考文献第 43 条）；`zhang2025` 补全前 3 位作者。
- 新增 4 条：`cellcharteranalyses2024`、`bayesspacevignette`、`dong2022stagate`、`fowlkes1983`。
- 预览文件新增 `url` 宏包，供 `\url` 使用。

### P0-7：E4 过期描述

- 第四章 4 处 `\IfFileExists` 的 else 分支，由"待插入/GitHub尚未验收"改为中性的"编译提示：未找到PDF"。
- 删除"在这些源文件逐张上传GitHub并核对之前……"这一限定语，改为"已归档，尚未作定量形态陈述"。
- 更新相应的注释。

## 没有改动的部分

- 所有数据来源、样本层级、Oracle-K/K-blind 的定义、冻结参数和原有负结果的描述。
- E4 附录（layout V2）。其中 36 个 else 分支仍含"待插入原始E4图件"字样；这些分支只在缺图时才会显示，已列入未解决问题。
