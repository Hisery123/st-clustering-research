# P1 学术写作稿——独立审查与安全并入说明（ChatGPT，2026-11-23）

## 核查范围
- 本文件是对用户上传 `p1_20261124.zip` 的审阅记录，不等于本研究原始实验报告或论文审稿通过。
- ZIP共58个文件，其中根目录 `PROJECT_STATE.md`、`CURRENT_RESEARCH_HANDOFF.md`、`RESEARCH_JOURNAL/2026-11-24.md` 来自朋友电脑，**不直接覆盖远端更权威的项目状态**；本安全合并包保留 `experiments/cellcharter_dlpfc/` 下的文件，原压缩包请另存归档。
- 逐项核对压缩包内 P1 生成脚本及 T9/T9b/T10/T11 派生 CSV 的 SHA256 均与 P1 清单一致（5/5）；4个原始输入文件未随 ZIP 附送，应以 GitHub 冻结原件为准。
- GitHub 远端 `e3c_slice_K_depth_240groups.csv` 的240条记录独立计算得到 T9b 的全部8组汇总相符。
- P1正文图表有2个新 pgfplots 图，附录源码引用36个源PDF图；**尚未真正编译或人工验图**。

## 对Claude P1做出的三项最小文本/排版修正
1. `chapter_04_results_discussion_p1_20261124.tex` §4.4：原句“CellCharter各邻域配置都明显优于非空间方法”与5D数据矛盾（L0 ARI0.3051，GMM0.3101，Leiden0.3265）；改为10--25维及5维分开描述，并区分BANKSY为空间方法。
2. 同一文件 §4.1：原句根据0.4418与官方0.4438接近便称“实现相符、基线可信”证据不足，改为“宏均值同一水平、提供有限外部参照；不能证明实现及逐spot一致”。
3. `cellcharter_study_full_preview_p1_20261124.tex`：原主文件若缺少151507关键PDF，则静默跳过整个36图附录；改为明确 `\PackageError`，避免生成不完整的PDF却误判为成功。

精确文本差异见同目录 `P1_CHATGPT_MINIMAL_REVIEW_PATCH_20261123.diff`。原Claude生成的 `P1_DIFF_vs_REV_P0_20261124.diff`仍保留，反映Claude P1初稿，不含本次三项最小校正；最新改动以本diff为准。

## 其他待验收项（不是重新训练要求）
- 在用户科研电脑使用XeLaTeX→BibTeX→XeLaTeX→XeLaTeX，检查pgfplots图中文字、表格宽度、附录36图及参考文献的实际版式。
- 正式学位论文模板仍未使用；不把专题初稿视为完整毕业论文终稿。
- 引言“尚未被充分回答”、贡献“揭示”仅相对于已读CellCharter原作者工作；后续需要最近邻文献核对，不直接宣称全领域首次。
- 讨论中的“碎片化转平滑”主要由预测边界数和P/R变化所支持，应作为描述性解释而非机制因果证明。
- ZIP中附带的P0/P1文本与结果完整度不能替代对冻结原始CSV、代码和原论文的独立审阅。

## 归档和安全操作
- 本包仅用于并入 `experiments/cellcharter_dlpfc/` 下的新版本；不含顶层PROJECT_STATE/HANDOFF/日记替换，不应使用 `git add -A` 无选择提交。
- GitHub远端文件在本包产生时没有由本操作更改，故仍须在科研电脑确认仓库最新状态，再合并/编译/单独审查后提交。
