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

## 2026-11-23｜E3B/E4上传后的CRLF字节保真风险（已定位，修复未执行）

**有新核查证据，必须覆盖2026-11-22的“GitHub原件逐字节完全相同”旧说法。** E4确实已经提交GitHub，共88文件：36张SVG、36份CSV、12样本manifest、原batch/audit、README、来源清单；上传提交`0b3a13fbe784711b2c522a09282feeb8a82771e8`。但读取GitHub E4原生SVG `figures/151507/151507_reference_A_B_spatial.svg`并对远端Git blob内容独立计算SHA256，得到`8d3f84cc015bbbefceefd0b4d9744910fc318c8b48ac3e01ebe58442a551a750`，不同于本地原件清单`7d76f7f61d750c9503056aaf60cfd43310e2ce8d72ead91d202655fb868849c1`；远端LF字节仅将每个换行恢复为Windows CRLF后重新计算，则**完全等于原件SHA**。E3B首份原始预测`predictions/151507/cum_L0/seed_22911/predictions.csv`亦发现同样问题：远端LF的SHA`f8b0d04ea183ee4df18882b8f2c43e16f83a1b5a5c3d5144d8d10c7e9d42903c`，恢复CRLF后等于原件`cabbb5f476be36ac7c38270e68ccb87146f9a1d665ace2b780e1b22406671525`。科学数值没有因此重新计算或修改，但旧“Git源字节与Windows原件相同”的表述不成立，必须修复后才能称原始字节完全备份。

已分别为`E3B_E1E2_1200_PREDICTIONS_20261122/`与`E4_SOURCE_FIGURES_20261122_RELEASE/`提交`.gitattributes`、设置`* -text`禁用未来Git换行自动规范化；已上传**综合一次性精确Git blob修复脚本**`experiments/cellcharter_dlpfc/repair_e3b_e4_exact_git_blobs_v1.py`：拟从原始E3B ZIP（固定SHA256 cfad75...）与E4源Windows文件分别校验1200+86=1286份SHA256，`git hash-object -w --stdin`写入原始字节的Git blob，`git update-index --index-info`直接提交原字节，再验证完整提交树并非强制push。**目前只是准备和提交修复脚本，用户尚未报告运行；不得称远端字节修复通过。**早期只修E4的`repair_e4_exact_source_blobs_v1.ps1`被综合版取代，不要先运行它。另已准备`convert_e4_original_svg_to_pdf_and_push_v1.py`，但必须先完成1286份原始Git blob的字节修复，才能开始转换36份真实SVG成论文矢量PDF。

论文正文及36图附录已写入GitHub，原E4图件存在的事实与“严格逐字节匹配原Windows SHA”需要分开报告；同理E3B全部1200文件存在但部分CRLF被规范化。下一步用户在Windows手动执行单条固定SHA脚本下载、核验、精确Git blob修复命令，提供PASS/FAIL；助手再远端核验提交树与来源清单。全程无训练、无更改参考标签、无数据数值重算。

## 2026-11-23｜E3B/E4原件精确Git字节修复已实际完成并通过远端复核

**当前最新状态覆盖此前“等待执行修复”的旧记录。** 用户Windows端实际运行`repair_e3b_e4_exact_git_blobs_v1.py`，日志报告：

- `E3B_ORIGINAL_BYTES_PASS sources=1200 zip_sha256=cfad75dbc35723c72e52f8906b07e1b81048ff70fcf04df709d41ae42bc1302b`
- `E4_ORIGINAL_BYTES_PASS sources=86`
- `E3B_E4_EXACT_BLOB_STAGE_PASS sources=1286 changed=1286 audits=2`
- `E3B_E4_COMMITTED_SOURCE_BLOB_PASS sources=1286/1286`
- `E3B_E4_EXACT_SOURCE_PUSH_PASS e3b=1200 e4=86 changed=1286`
- `E3B_E4_EXACT_SOURCE_COMMIT=6d4bc09bb6f98d0dff13a442fee1dd4759e998c2`

**本助手独立在GitHub远端取main分支该提交的完整Git tree**（非截断），分别读取`E3B_E1E2_1200_PREDICTIONS_20261122/EXACT_SOURCE_BLOB_REPAIR_AUDIT_20261123.csv`和`E4_SOURCE_FIGURES_20261122_RELEASE/EXACT_SOURCE_BLOB_REPAIR_AUDIT_20261123.csv`，逐条检查`path`对应`blob SHA1`等于`exact_git_blob`：E3B **1200/1200**匹配、E4 **86/86**匹配、缺失0。提交树完整且各对象等于Windows脚本从原源文件SHA256校验后生成的原始Git blob。由此此前CRLF规范化产生的字节保真缺口**已修复**，不是仍待修复。原始报告和修复审计继续保留，不覆盖。

下一任务是把E4真实36SVG无重绘转换为适合XeLaTeX的36个矢量PDF，运行脚本`experiments/cellcharter_dlpfc/convert_e4_original_svg_to_pdf_and_push_v1.py`（已提交但**尚未由Windows执行**），先逐份检查原始SVG的SHA再转换与提交。真实PDF成功后需检查GitHub文件树数量、来源哈希、至少代表图视觉一致性和学校模板编译；当前尚不可称图件已全部排版或PDF已生成。无新增模型训练。
