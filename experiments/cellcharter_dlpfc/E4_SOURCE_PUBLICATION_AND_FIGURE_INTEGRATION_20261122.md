# E4原始空间图归档与论文插图对接（2026-11-22）

> 当前状态：**GitHub提交了上传脚本、论文插图位与36图附录；截至此文提交，72份原始SVG/CSV仍在用户Windows，尚未上传并由GitHub核验。** 不以原始审计日志冒充文件已在仓库。

## 固定且真实已运行的原实验

- 原始Windows结果目录：`D:\paper\CellCharter_reproduction\results\e4_spatial_visualization_v1\batch_20261120T080609Z_4732`
- 原始独立审计：`D:\paper\CellCharter_reproduction\results\e4_spatial_visualization_v1\phase_audit_v1\20261120T082135Z_29612\e4_phase_audit_report.json`
- 既有[成功审计记录](E4_FINAL_AUDIT_PASS_20261120.md)：12/12切片、36/36原始SVG和36/36原始CSV审计通过。用户Windows原审计包括输入/输出SHA、SVG XML、真实10x marker原始及归一化计数、参考层×原簇交叉表的核对；这一记录不是远端文件原件已存在的证明。
- [原冻结绘图脚本](e4_spatial_visualization_batch_v1.py)：固定A=`cum_L0_L1_L2`、B=`fixed_L0_L1_L4`，seed22911、Oracle-K；全12切片；MOBP/PCP4/SNAP25；原簇编号不做参考标签有监督重排。
- 固定正文三个说明性案例：**151507**（D1平均B−A ARI正向最大）、**151671**（D2最接近0）、**151675**（D3负向最小）。这是**看到E1/E2结果后**固定的E4展示规则，不是盲测，也不同于旧151671/151676单seed边界解释案例。

## 源文件结构和数目（上传时必须按原字节保留）

每张切片在`figures/<slice>/`中必须包括六个原始输出、一个原始`e4_sample_manifest.json`：
- `<slice>_reference_A_B_spatial.svg`
- `<slice>_MOBP_PCP4_SNAP25_expression.svg`
- `<slice>_reference_A_B_confusion.svg`
- `<slice>_marker_expression_raw_and_log1p10k.csv`
- `<slice>_reference_vs_A_confusion_counts.csv`
- `<slice>_reference_vs_B_confusion_counts.csv`
- `e4_sample_manifest.json`

12切片共**72个实验图/表源文件 +12个样本原始manifest + 原始batch状态 + 原始audit JSON =86份来源文件**。新发布包另加新生成的`SOURCE_SHA256.csv`和`README.md`，总计预期**88份Git文件**。全部保持原CSV/SVG字节；GitHub必须能列出36个`*_spatial.svg`/`*_expression.svg`/`*_confusion.svg`及对应36个CSV。

Windows一键脚本： [publish_e4_original_figures_v1.ps1](publish_e4_original_figures_v1.ps1)。该脚本检查原始manifest输出SHA及原批次记录、审计PASS、源文件精确数目，克隆到新工作目录，提交到`E4_SOURCE_FIGURES_20261122_RELEASE`。不重训、不重新绘图、不改变源CSV/SVG、不强推或覆写已有发布目录。**实际未执行前不可声称上传成功**。

## 与论文草稿的连接（必须区分原SVG与PDF派生版）

- [新版第四章](chapter_04_results_rewrite_v1_20261122.tex)已经按冻好的三个代表切片设置实际图路径，另可展示151671真实marker图；目前在`figures_pdf/<sid>/<name>.pdf`不存在时显示文字待插入。
- [全12切片/36图附录](appendix_e4_all12_figures_v1_20261122.tex)列出所有三种图，`cellcharter_study_full_preview_v1_20261122.tex`仅在PDF存在时加载，避免展示未上传的假图。
- **原E4出图是可编辑SVG，不是PDF**；XeLaTeX的`graphicx`不直接保证支持SVG。后续需对已上传真实SVG进行格式转换，生成`figures_pdf/`下**无绘图逻辑更改**的矢量PDF，再通过原SVG的源SHA、版面、坐标、颜色一致性核验。这一转换是排版工程，不是新实验。
- 除非取得所有原始文件及图中内容，否则不得声称图件形态、marker区域或组织簇的具体新发现已证实。参考层、A、B同色不意味着标签监督式簇一一对齐。

## 下一手动步骤 / 完成判据

**当前唯一操作**：用户Windows运行经GitHub Git-blob SHA固定的原始E4上传脚本；成功应打印`E4_GITHUB_ORIGINALS_PUSH_PASS svg=36 csv=36 manifests=12 total_files=88`和非空新commit SHA。若失败，保留工作目录及错误输出，不重复运行覆盖。

完成后由助手独立重新读取GitHub树统计72份实验原文件+12个manifest及批次/审计JSON的实际存在，抽样或逐项核对源SHA；再开展真实SVG→PDF的排版转换。未经该验收，不将本任务标记“原始E4图件归档PASS”。
