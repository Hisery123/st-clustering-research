# PROJECT_STATE — 第三篇空间转录组聚类论文

## 2026-11-12 16页整合PDF用户实测通过、逐页视觉审查（最新）

用户Windows第二轮XeLaTeX成功生成`THESIS_CHAPTERS_2_4_INTEGRATED_20261112.pdf`(16页)并上传，已直接审查PDF：第2章页1–3、第3章页4–8、第4章页9–15、参考文献页16；方法TikZ图1页7、12片Δ三面板图2页10、两例六面板真实空间图3页14，4张表全在，6篇参考文献文末出现，未出现缺图占位框。公式跨章连续到(11)，图表编号已统一。**整合版技术结构初步通过，但有实际页面问题**：第6页3.6标题/引导文字留在页尾而图1在第7页；第13页表4单独位于空白较多的页面；第14页六面板原图图例偏小。另用户终端只有`caption hypcap=true ignored`非致命警告。不要断言达到学校学位模板要求。

科研边界仍是12片/3供体、固定单seed、Oracle-K，B无稳定改善；文献正文是初步核查而非系统综述/全部全文精读。**下一步优先是整合稿的实质性内容质量审查、SEDR标签源头核实和格式改善的优先级规划**，不要机械重训；如果只修复分页，修改整合正文快照片段而非覆盖原始独立版本，修复后必须先Git同步再由用户Windows重新编译验收。此次PDF上传不等于GitHub已备份用户本地PDF与实验图字节。

## 2026-11-12 更新：第二章PDF已核查，通过；2–4章整合TeX已提交，待Windows验证（当前最新）

**用户实际PDF证据：** 最新上传的第二章《研究背景与相关工作》PDF（3页）经逐页检查：页眉误显示“参考文献”的问题已消除，m2ST参考文献间距正常，6条参考文献完整。这只是格式审查通过，不代表已经核查全部付费论文全文或符合学校学位模板。

**GitHub新增：** 保留三个原始独立TeX不变，新建 `experiments/cellcharter_dlpfc/THESIS_CHAPTERS_2_4_INTEGRATED_20261112.tex` 主文件和 `chapter_02_background_integrated.tex`、`chapter_03_methods_integrated.tex`、`chapter_04_results_integrated.tex` 三份正文快照。统一ctexart导言、2/3/4节次序和文末6篇参考文献；从整合版第4节移除“定稿前核查提示”。两张实验图仍只引用用户Windows已有的真实PDF文件，源TeX里有找不到文件时的明确占位提示。**这些新增文件尚未在用户Windows同步，也未经过Windows实际XeLaTeX编译或视觉验收，不可称整合已成功。** 原TeX与真实本地结果均未被覆盖；整合片段是快照，后续更改单章要同步片段。

**当前下一步唯一Windows操作**：运行此前成功的 `git -c http.proxy=http://127.0.0.1:7897 -c https.proxy=http://127.0.0.1:7897 -C "D:\paper\st-clustering-research" pull --ff-only`。确认Fast-forward和四个新文件到位，之后另一回合单独编译主TeX，核查总图/表/公式编号、文末参考文献、横向六联图及缺图占位。禁止重训，禁止把12切片当12独立供体、把B称为已验证创新。


## 2026-11-12 归档冻结点：本地Git同步成功，待编译第二章（当前唯一权威下一步）

**用户Windows实际终端日志**：在 PowerShell 执行带本机代理的 `git ... -C "D:\paper\st-clustering-research" pull --ff-only`，结果 `Updating 0792652..73bbc05`、`Fast-forward`，5个文件共141行新增，明确新增：
- `experiments/cellcharter_dlpfc/LITERATURE_EVIDENCE_AND_NOVELTY_20261111.md`
- `experiments/cellcharter_dlpfc/THESIS_BACKGROUND_RELATED_WORK_20261111.tex`
同时更新 `PROJECT_STATE.md`、`CURRENT_RESEARCH_HANDOFF.md`、`RESEARCH_JOURNAL/2026-11-11.md`。**这次同步已完成，不再让用户重复git pull来取得第二章。**

**论文进度（已知真实状态）**：第二章研究背景和相关工作TeX已在GitHub、现已同步Windows，但用户**尚未编译/上传该章PDF**。第三章研究方法独立5页PDF已由用户编译两轮、上传最新版，经逐页检查：TikZ图处于3.6节、图号“图1”、3.7公式顺序正常、末尾备忘移除。第四章实验结果与分析独立7页PDF已由用户编译、上传，2张真实科研图已出现；仍需最终格式与参考文献统一。**2+3+4尚未合并成完整论文，也不等于满足学位要求。**

**实证/创新界限保持不变**：DLPFC12张切片/3位独立供体；A=L0+L1+L2和B=L0+L1+L4同为15维；固定22911 CPU GMM、D2 K5、D1/D3 K7（Oracle-K）；全12片B的边界F1改善6/12、平均ΔF1约−0.0047，未验证稳定优势/原创算法。旧151507/151508开发切片与新增10片参考标签来源差异，SEDR元数据`layer_guess`上游原始标签来源待追溯。文献证据矩阵已列已核实6篇期刊来源和DOI，但不意味着已精读全部全文/补充材料。

**下一次唯一Windows操作（尚未执行）**：用户手动运行一次XeLaTeX，编译已同步的 `D:\paper\st-clustering-research\experiments\cellcharter_dlpfc\THESIS_BACKGROUND_RELATED_WORK_20261111.tex`，输出目录 `D:\paper\CellCharter_reproduction\results\thesis_fixed15_12_sections_summary_v1`。确认终端输出后处理交叉引用/编译错误，并请用户上传PDF作逐页检查；不要先并章、不要重训。历史段落中与此冲突的“下一步git pull”等已经过时。

**本次归档动作**：只更新GitHub文档与2026-11-12科研日记，不修改`AGENTS.md`稳定规则、不改实验脚本、不执行本地训练/编译。新提交由GitHub工具完成后**尚未同步Windows**；不能误将文档提交当成本地编译或备份Windows模型。


## 2026-11-11 文献核查与第二章TeX已完成（最新）

已通过期刊/PubMed网页核对CellCharter(Varrone 2024 DOI10.1038/s41588-023-01588-4)、scVI(Lopez 2018 DOI10.1038/s41592-018-0229-2)、DLPFC(Maynard 2021 DOI10.1038/s41593-020-00787-0)、SEDR(Xu 2024 DOI10.1186/s13073-024-01283-x)、m2ST(Zhang 2025 DOI10.1093/bioinformatics/btaf221)、SACCELERATOR(Sun 2026 DOI10.1038/s41592-026-03194-8)，并读CellCharter官方aggregate_neighbors API文档。GitHub新建 `experiments/cellcharter_dlpfc/LITERATURE_EVIDENCE_AND_NOVELTY_20261111.md` 与 `THESIS_BACKGROUND_RELATED_WORK_20261111.tex`，完整撰写第二章的研究背景、相关工作与研究问题；TeX带6条已验证参考文献。严格明确多尺度邻域特征本身、尺度赋权不是当然创新，固定B未取得跨供体稳定优势；新版2026 SACCELERATOR提醒DLPFC基准/参考标注局限。**尚未在用户Windows同步和XeLaTeX编译；没有下载/精读付费CellCharter全文及其补充材料；SEDR layer_guess元数据的最初标注来源待追溯。** 最新用户仍在Windows手动操作模式，下一步只给一条带Clash本机7897临时代理的git pull --ff-only，成功后再单独xelatex编译，不重复已完成实验。

## 2026-11-11 方法章节TeX初稿已提交（最新）

基于已从GitHub直接读取的 `scripts/cellcharter/prepare_dlpfc_10_sources.py`、`prepare_dlpfc_10_features.py`、`mvp_fixed15_dlpfc_10_sections.py`、`cellcharter_151507_baseline_v032.py`、`mvp_fixed15_block_swap_151508.py` 编写中文独立XeLaTeX方法章节 `experiments/cellcharter_dlpfc/THESIS_METHODS_20261111.tex`。包括12片/3供体、原始来源与SEDR `layer_guess` 来源边界、barcode/六邻接、HVG5000/5D scVI训练、CellCharter n_layers4/25D、冻结15D A/B、full协方差CPU GMM、Oracle K、ARI/NMI/边界F1和层对召回定义、数据泄漏预防、可重复性与局限。内含TikZ原生矢量方法流程图；所有真实科研图与先前7页结果PDF保持独立。**已提交GitHub，但还没有在用户Windows同步/编译；当前环境不能直接取得Github TeX文件以完成实际编译验证。** 文献引用未编造，旧两片标注来源需进一步核查。下一步先一条PowerShell git pull同步，之后单独XeLaTeX编译检查。不要重训模型或要求重复已提交的数据。

## 2026-11-11 12片等维对照三面板科研图已制作；TeX已更新

基于此前用户上传并确实存放在当前项目环境的三份真实Matplotlib SVG：`delta_ari_by_donor.svg`、`delta_nmi_by_donor.svg`、`delta_boundary_f1_by_donor.svg`，用独立嵌套与ID防冲突方式合成为上下A/B/C三个面板的`DLPFC_12_sections_A_B_delta_three_panel.svg`，通过Inkscape导出`DLPFC_12_sections_A_B_delta_three_panel.pdf`，PDF图像已实际渲染核查，图中有12片按3供体着色、旧2片开发标圈。打包`DLPFC_12_sections_A_B_delta_three_panel.zip`向用户提供下载；**这些二进制图件尚未保存到用户Windows，亦未上传GitHub**。GitHub中的TeX `THESIS_RESULTS_DISCUSSION_20261111.tex`已添加条件性真实图插入，路径在Windows结果目录，缺文件时保留占位。尚未在用户Windows同步或编译，不能声称最终PDF已更新。下一步先让用户解压PDF到已有结果文件夹，再单步同步/编译。保持数值图来源与12片独立供体n=3的限制，旧两片开发集清晰圈出。

## 2026-11-11 中文LaTeX实验结果章节已提交GitHub（最新）

用户要求将已归档的实验结果与分析章节改写为TeX并上传GitHub。已新建 [THESIS_RESULTS_DISCUSSION_20261111.tex](experiments/cellcharter_dlpfc/THESIS_RESULTS_DISCUSSION_20261111.tex)，采用 `ctexart` 独立XeLaTeX草稿结构，保留已有真实12片ARI/NMI/F1、供体差异、TP/FP/FN总计、151671/151676层间边界召回、局限；内含4个数据表、1个边界F1公式、2个**明确的待插图占位**（不冒充实图），没有编造DOI或外部引文。已通过GitHub读取新文件并检查正文起止及表格环境数量；**尚未在用户Windows编译、未宣称PDF已生成**。独立文件并入学校论文模板须适配ctex导言和章节编号。下一步可由用户Windows手动同步，再运行一次XeLaTeX检查（每次一条命令）。


## 2026-11-11 实验结果与分析初稿已写入GitHub（最新）

已直接核对用户上传的12片CSV（全部ARI/NMI/F1及计数）与用户终端提供的151671、151676分层边界审计，正式建立 [毕业论文实验结果与分析初稿](experiments/cellcharter_dlpfc/THESIS_RESULTS_DISCUSSION_DRAFT_20261111.md)。包含数据/评价协议、12片总体比较、供体与开发/扩展差异、整体TP/FP/FN、两张典型空间图及分层边界结果、局限与成稿检查清单。**这是有证据的写作草稿，不是新增实验结果、新算法或者已经完成的文献核查**；尚未写正式引用和排版成稿。下一阶段优先对照原始结果检查图表/正文的最终一致性，形成六面板图和论文章节的正式图注；不需要重训模型。


## 2026-11-11 12片边界错误计数已补齐；科研图表脚本已提交（最新）

用户实际从新增10片本地 `results.json` 输出20行A/B TP、FP、FN、L5/L6检出；与此前旧2片原始JSON合并后全12片计数齐备。按供体计数相加的候选B相对A：D1 ΔTP+72/ΔFP−1207/ΔFN−72，D2 ΔTP−18/ΔFP−225/ΔFN+18，D3 ΔTP−158/ΔFP+11/ΔFN+158；全12片ΔTP−104/ΔFP−1421/ΔFN+104。汇总是描述性的，供体n=3，不能以边为生物独立样本。详情及逐片原始读出：[证据矩阵](experiments/cellcharter_dlpfc/THESIS_CHAPTER_EVIDENCE_MATRIX_20261111.md)。

GitHub新建 `scripts/cellcharter/export_thesis_12_fixed15_results.py`：拟从本地12份已有原始`results.json`只读提取完整ARI/NMI/F1/TP/FP/FN/L5L6，并做一致性检查；默认另建独立目录生成CSV、三个Matplotlib矢量SVG及来源哈希清单；**尚未同步Windows，尚未运行，图表与CSV尚未生成**。有 `--check-only` 预检不写文件。**下一步唯一Windows操作先git pull --ff-only**同步脚本；确认成功后才单独运行`--check-only`；不重训scVI/GMM。软件随机性源码检查已止损。


## 2026-11-11 毕业论文章节证据矩阵已建（最新）

基于12片/3供体、冻结15D A/B结果与10片核心指标独立复核，GitHub已建立 [毕业论文章节证据矩阵/实验与作图清单](experiments/cellcharter_dlpfc/THESIS_CHAPTER_EVIDENCE_MATRIX_20261111.md)。明确旧2片属于开发、新10片是扩展，Oracle-K、标签来源差异、边界F1改善6/12及新方法尚未成立。源码检查止损：不是GMM建议“失败”，只是尚未证明稳定性问题且当前不再无终点追查；CellCharter0.3.2/TorchGMM0.1.2版本与源码只读检查已执行。**下一现场唯一操作**：Windows只读盘点151507/151508已存在的15D A/B原始结果目录与文件，为12片主表提供可追溯来源；不训练、不重新拟合。


## 2026-11-11 TorchGMM随机种子实现只读检查已完成；转入毕业论文章节组织（最新）

用户在Windows实测环境：CellCharter 0.3.2、TorchGMM 0.1.2、PyTorch 2.1.2+cu121。源码显示CellCharter `Cluster`向中间 `GaussianMixture` 传递 `random_state`，中间类仅保存 `self.random_state`；用户完整打印的 TorchGMM `estimator.py` `GaussianMixture.fit` 没有显式使用该参数，KMeans初始化由 `KMeans(...).fit(data)` 执行。既有A/B实验脚本还显式调用 `np.random.seed(SEED)` 与 `torch.manual_seed(SEED)`。**不能据此判断整个底层随机路径失控或旧实验失效**；未开展新的GMM重拟合。基于毕业优先、有限预算决定停止无终点的源码追查（历史seed0 L4问题继续封存）。下步应优先组织全12片结果、供体级图表与论文章节；有明确必要时才按预声明最小范围开展跨seed诊断。详见 [源码检查归档](experiments/cellcharter_dlpfc/FIXED15_PREDICTION_REAUDIT_AND_NEXT_DECISION_20261110.md)。


## 2026-11-10 最新用户目标：毕业论文优先、SCI增量创新为争取项（最高优先级）

**必须优先执行的研究定位**：第三篇CellCharter首先服务于硕士**毕业论文的一章实质性研究内容**，而不是必须独立发表一篇SCI论文。以普通SCI/会议方法论文的规范与实验强度作参考，争取有真实最小增量创新，但**不以找到新算法作为完成研究的唯一条件**。学位论文的最终合格标准、是否需要正式发表与章节是否足够，仍须依据学校培养方案及导师意见，不能承诺一定毕业。

**用户明确强调的论文重点**：简练摘要；研究背景及意义；充分、有说服力的研究方法、实验设计与实验分析（允许补充相关实验，绝不是为了凑数量而堆砌冗余实验）；结论与总结。真实结果、负结果、假设、计划严格区分；实验要公平、可重复，供体n=3不伪重复。

**双轨交付与止损规则**：
- **保底主线（必须推进）**：将当前CellCharter成熟方法的复现、DLPFC12片/3供体的多尺度特征消融与固定A/B对照、ARI/NMI/边界F1与TP/FP/FN、真实跨片/跨供体差异、必要的稳定性与局限分析整理成一章逻辑完整、图表充分、可追溯的**实证研究章节**；即使没有确认新机制或方法改进，也不丢弃前期工作。不得将无创新的结果伪装成原创算法；不能保证章节自动达到学校标准。
- **争取主线（严格限时/限实验预算）**：优先已有文献依据、易于复用现有25D特征缓存且不重训scVI的**小而真实的增量改进**，仅在低成本诊断出现可信信号后试验；先完成最小可证伪MVP、检查最相近已有方法，再视证据扩展。多重启/共识聚类已有成熟先例，不可凭拼装自称新颖。
- **禁止无终点探索**：不以“没找到创新”作为无限增加seed、搜索特征块或追查历史故障的理由。保存阴性结果，按明确停止标准及时退出无效候选。
- **写作应并行**：在继续必要小规模诊断时，可以同步准备毕业论文该章的背景、方法、数据/实验协议、已验证结果与讨论骨架；未完成实验不得写成已有结果。

**最新已确认实验状态**：新增10片GMM A/B预测CSV与结果JSON，用户Windows独立复核Barcode顺序、ARI/NMI/边界F1/TP/FP/FN，`PREDICTION_METRIC_REAUDIT_COMPLETE 10/10`；旧2片为开发集。新10片B边界F1改善4/10，全12片6/12；未确立固定B的优势或原创方法。**当前唯一下一步**仍是只读检查本地CellCharter/TorchGMM安装版本及random_state实际传递，然后才考虑小规模稳定性MVP。旧seed0 L4不一致追查仍封存。未经本轮操作结果，不得宣称已检查软件版本或已启动新试验。

完整研究目标决议见 [毕业优先研究约定](experiments/cellcharter_dlpfc/THESIS_FIRST_RESEARCH_CHARTER_20261110.md)。


## 2026-11-10 最新：10片预测与关键指标独立复核10/10；Claude外审后冻结下一诊断路径

用户Windows实际运行只读程序，读取新10片每片 `manifest.json`、`results.json`、A/B预测CSV、位置CSV与参考标签CSV。对两份预测逐行核查Barcode顺序，重建Visium无向六邻接图并排除未标注端点，独立重算**ARI/NMI/边界F1/TP/FP/FN**；与每片已存 `results.json` 原始值误差<1e-9。终端十行 `PASS`，结束 `PREDICTION_METRIC_REAUDIT_COMPLETE 10/10`，没有发现不一致；**没有重训、重拟合、修改文件**。本次未独立重新核算precision/recall/L5L6、未直接取得用户本地数据字节或复核旧两片预测，不能宣称所有指标已复核。

现12片 A=`L0+L1+L2`、B=`L0+L1+L4` 固定15D单种子结果：B边界F1改善6/12（后续10片4/10）；供体D1 3/4、D2 2/4、D3 1/4（仅3个独立供体）。固定B不能视为跨供体有效方法创新。Claude独立科研审查提出GMM运行间稳定性、边界过预测/碎片化的可能混杂；采纳**诊断优先**、不接受“选型噪声已证实”“F1无效”“直接240次GMM/多重启即原创”这些未经支持结论。先核对本地软件版本与随机种子实际传递，再视情况设计少量预注册跨seed试点；不重新打开此前封存的旧seed0 L4争议。**下一步唯一操作**：Windows只读查看CellCharter/TorchGMM版本、文件路径与随机种子实现/传递，收到实际输出后再决定小规模重复。详见 [独立复核与研究决策](experiments/cellcharter_dlpfc/FIXED15_PREDICTION_REAUDIT_AND_NEXT_DECISION_20261110.md)。


## 2026-11-10 新增10片GMM完整结果已由Windows只读检查补齐（最新）

用户实际PowerShell批量读取10片 `manifest.json` 和 `results.json`：10/10 `STATUS=completed`，两组预测文件均 `True`，没有缺失。此前终端截断的151509、151510已补齐：151509 A/B ARI 0.437996/0.488331、NMI 0.595607/0.639697、边界F1 0.117785/0.102159；151510 A/B ARI 0.430863/0.374885、NMI 0.559271/0.569489、边界F1 0.137725/0.142899。完整10片B相对A，ARI改善3/10，NMI改善5/10，边界F1改善4/10；结合旧151507/151508，边界F1改善6/12，按供体D1=3/4、D2=2/4、D3=1/4。候选B并未显示跨供体稳定优势，创新尚未成立。

证据局限：Windows终端只读显示四舍五入6位的数值、状态及预测文件存在；尚未逐行读预测/独立重算指标或核验本地原始结果哈希。记录详见 [GMM完整10片检查补记](experiments/cellcharter_dlpfc/FIXED15_10_SECTION_GMM_20261110_FIRST_RESULTS_ARCHIVE.md)。**唯一下一步**：对已存在的预测、manifest与结果做只读一致性复核，随后以真实原始结果形成全12片供体分组表；不要重训scVI/GMM或看结果后重新挑组合。



## 2026-11-10 固定15D A/B 新10片GMM运行完成；已见结果不支持普遍改善（最新）

用户上传 `粘贴的文本 (1)(20261110-081623).txt` Windows终端摘录675行，末尾明确 `DLPFC_10_FIXED15_FIT_COMPLETE 10/10`，表示新10片A/B GMM批量程序正常完成。**但上传文本从151510某项结果尾部开始，151509/151510完整`RESULT`不在此附件中**；这不等于本地没有结果，须读本地`results.json`，不得补造数值。我们没有直接取得该次10片的原始预测CSV/manifest，只能据用户终端复核。

本附件8片完整可见结果，Δ=B−A：

|切片|Δ边界F1|ΔARI|ΔNMI|Δ边界FP|
|---|---:|---:|---:|---:|
|151669|−0.034586|−0.098259|−0.053348|+455|
|151670|+0.014431|+0.063475|−0.001003|−257|
|151671|+0.028170|−0.001288|+0.030651|−525|
|151672|−0.027079|−0.003232|+0.024421|+102|
|151673|−0.015907|+0.028066|+0.000479|−179|
|151674|−0.037797|−0.082799|−0.045147|+101|
|151675|+0.006969|−0.117841|−0.060466|+119|
|151676|−0.091048|−0.038142|−0.004394|−30|

仅8片已有完整`RESULT`行中F1提高3/8，下降5/8；供体2为2/4提高，供体3为1/4提高。**不能声称候选B跨供体稳定改善边界；不能把已知151507/151508正向结果挑出来报告**。GMM日志`GPU available True, used False`符合CPU计划；多次max_epochs100是上限停止，不等于收敛。候选只是简单固定尺度块选择，没有已证实方法创新。

已归档精确A/B数值和来源边界：[FIXED15_10_SECTION_GMM_20261110_FIRST_RESULTS_ARCHIVE.md](experiments/cellcharter_dlpfc/FIXED15_10_SECTION_GMM_20261110_FIRST_RESULTS_ARCHIVE.md)。**下一次唯一操作**：用户Windows只读批量核验10片`results.json`、manifest与预测文件存在性，并显示151509/151510缺失于贴文的真实指标；先归档12片完整配对表再决定新假设，**不重训不重新随机挑方案**。本次科研归档完成但**没有验证本地文件本身**。
## 2026-11-10 新增10片冻结A/B GMM只读预检完成（接下来可显式--fit）

用户Windows执行 `python scripts/cellcharter/mvp_fixed15_dlpfc_10_sections.py --all`（**未附加--fit**）。终端10次`FIXED15_CHECK_PASS`，最终`DLPFC_10_FIXED15_CHECK_ONLY_COMPLETE 10/10`：
151509 n4789 K7 edges14086 sha1f29060473365c02d2c26b51a477d87ff2fb4ee6a4e7ae8e18193895c8dfc32e；
151510 n4634 K7 edges13599 sha bcdbe68d60ab802f5752406e45cd6ccbe95ee87b67be390b1f8431e16e298d17；
151669 n3661 K5 edges10597 sha50071ef3b8f0abe8507c2697df7cccc9c0dc05d1d95d65b4ece9bc2cef732fa4；
151670 n3498 K5 edges10185 sha6006e085aaa2c455c210e3a055bd83b99b843a9a05356f9a25dd0e8f4ca5732a；
151671 n4110 K5 edges12026 sha b121f6a63f344c05d7a67a703f53f2d399b4a579c23bd5ec208c9939a13522c3；
151672 n4015 K5 edges11691 sha bb979d485a4b939d455e987ca9fe7c3312092e16521ec03b609409ba14fbb943；
151673 n3639 K7 edges10562 sha a43e600dc41d58cd353f0d0ec67748e5c776bd2f7572de08491b7dd2758ae0a0；
151674 n3673 K7 edges10629 sha6e2d2bfa006ed836eb256215736dda81808b1ed7c1b3542c3e7623bc187e340a；
151675 n3592 K7 edges10381 sha210aebd5225eedbc4c4430e1f43d81b87c09e663422a7c0e747d0e762ba0cf80；
151676 n3460 K7 edges10026 sha834d10f10d4880523ddcd3d0df04b3696998c5dc01d1d98f72c9d1c0f635d4e2。
反复xarray_schema pkg_resources deprecated仅警告。

**未运行新增GMM、未生成ARI/NMI/边界F1**。下一步用户手动一条PowerShell命令带`--all --fit`执行冻结A/B两种CPU GMM；每片独立Python子进程，两种预测保存后方读取标注评价，失败保留目录且终止。不改参数，不因结果改K/挑种子，不重新训练scVI。

## 2026-11-10 新增10片 25D特征写后缓存独立审计通过，已准备冻结A/B脚本（待运行）

用户Windows真实只读输出：151509,151510,151669,151670,151671,151672,151673,151674,151675,151676 均 `PASS`，最终 `FEATURE_CACHE_AUDIT_COMPLETE 10/10`。审计条件包括每片 `status.json` completed、sample与config匹配、scVI latent数组(spot数,5)、CellCharter aggregate数组(spot数,25)、spot_order.csv与源spots_aligned.csv条码逐行匹配、两数组SHA256与status记录一致、源H5与坐标CSV哈希与config一致。**该证明限十片新增缓存；用户本人本地读审。**

已在GitHub创建 `scripts/cellcharter/mvp_fixed15_dlpfc_10_sections.py`，移植此前151508同预算A=L0+L1+L2/B=L0+L1+L4各15D的CellCharter CPU GMM、seed22911/full covariance/kmeans/cov reg1e-6/tol.001/maxepochs100，以及相同六邻居无向边的boundary F1/ARI/NMI/L5L6指标；冻结每片K与spot/edge/annotation统计，源哈希与缓存顺序核验。该脚本默认无拟合、无写入；单片`--sample 151509`或`--all`纯检查。只有带`--fit`才在不同新目录分别保存 A/B prediction CSV、manifest、results，**先两组聚类再读标注**；出错保留失败状态，拒绝覆盖。需先同步GitHub并实际进行无写入检查，不能宣称已经测试脚本在Windows正确跑通，也没有任何新增GMM结果。

冻结协议: `experiments/cellcharter_dlpfc/DLPFC_12_SECTION_FROZEN_EVALUATION_PROTOCOL_20261110.md`，已知151507/151508开发结果不重跑，供体n3，K5/7，所有负结果完整报告。下一步用户`git pull --ff-only`，确认后再运行`python ...mvp_fixed15_dlpfc_10_sections.py --all`。下个里程碑才启动CPU GMM。

## 2026-11-10 批量10片特征生成终端证据：全部成功（此前“运行中”状态已更新）

用户贴出`prepare_dlpfc_10_features.py --all --train`的终端尾部，**最终明确打印 `DLPFC_10_FEATURE_TRAIN_COMPLETE 10/10`**。按已归档脚本该标志说明全部10个子进程正常返回，各样本走完整成功保存或通过原有已完成缓存哈希检查的重用分支，因而不再应把批量状态写作运行中；但尚未在本地针对所有缓存执行独立写后审计。终端直接展示：
- 151674: scVI epoch275/400早停、`FEATURE_CACHE_COMPLETE`，n3673，latent[3673,5]、aggregate[3673,25]、edges10629，latent sha256`d55bd042b8b7da7e99572a17df5abb93c7099138d79d8412f75846c88dd3d303`，aggregate sha256`6e2d2bfa006ed836eb256215736dda81808b1ed7c1b3542c3e7623bc187e340a`。
- 151675: epoch313/400早停、`FEATURE_CACHE_COMPLETE`，n3592，latent[3592,5]、aggregate[3592,25]、edges10381，latent sha256`2d0555ddad15354c190043ba07f2470f4dd902832ad309256f620aab4bf8af74`，aggregate sha256`210aebd5225eedbc4c4430e1f43d81b87c09e663422a7c0e747d0e762ba0cf80`。
- 151676: epoch274/400早停、`FEATURE_CACHE_COMPLETE`，n3460，latent[3460,5]、aggregate[3460,25]、edges10026，latent sha256`504af4b34a3dbfc303452a4cfda3abe983d3ac8d388448e209d15836520c34ed`，aggregate sha256`834d10f10d4880523ddcd3d0df04b3696998c5dc01d1d98f72c9d1c0f635d4e2`。
- 其余151510、151669–151673单片完整日志未在这次摘录展示；不补造其epoch或SHA。
- 151509先前独立训练已完成，批量脚本具备已完成hash匹配cache复用机制。
- 显示 `GPU available: True(cuda), used: True`，警告`No GPU/TPU found`来自另一框架、不会否定Lightning CUDA训练。

**下一步唯一动作**：只读批量审计10片output目录中 status.json、config.json、spot_order.csv、scvi_latent.npy、cellcharter_aggregated.npy、shape/条码对齐及文件SHA，核实无一张错片/截断，再创建冻结A/B GMM + evaluation脚本；不得重复scVI，不允许看新结果后改A/B/K/seed。仍仅3个独立供体，方法创新尚未成立。
## 2026-11-10 跨对话中途归档：批量GPU训练已启动，最终状态未知（最高优先级）

**当前主任务**：第三篇 DLPFC/CellCharter 方法论文。用户提出换新对话时已表示正在执行 `prepare_dlpfc_10_features.py --all --train`，但本次归档时**尚未发回整批终端日志**；除了先前151509已成功完成5D scVI和25D缓存，其余9片的训练完成情况**未知**，严禁称十片训练完成。

**从这里接手**：先阅读[中途归档与接手手册](experiments/cellcharter_dlpfc/SESSION_CHECKPOINT_20261110_MIDRUN.md)，再根据任务阅读[冻结12片评价协议](experiments/cellcharter_dlpfc/DLPFC_12_SECTION_FROZEN_EVALUATION_PROTOCOL_20261110.md)和[批量特征脚本](scripts/cellcharter/prepare_dlpfc_10_features.py)。用户下一条消息优先判断批量运行是否结束、有无 `DLPFC_10_FEATURE_TRAIN_COMPLETE 10/10`；如正在运行不打扰训练，结束后收集实际日志及各片status/hash验证。**不要提前启动GMM，也不要重新训练已经完成的样本，更不要碰已封存的seed0 GMM历史矛盾**。

**已完成且确认**：新增10片来源下载与位置/metadata标注对齐、转换 `--write`、10/10写后读审计、十片6邻居空间图无训练预检；151509 GPU scVI于epoch222早停并成功缓存25D。历史已见151507、151508固定A/B结果见冻结协议，新片尚无GMM评价。仅3位供体，供体2 K5，其他K7；标注来源 `layer_guess` 需要说明。研究方法创新**尚未成立**，目标为真实可靠的普通SCI增量研究。Github是笔记/脚本，不含未上传的本地H5及模型。

**跨对话工作约定**：下一位助手先调用GitHub Connector读取原始权威记录，再给“已完成/未完成/风险/唯一下一步”；用户Windows一次只执行一条PowerShell命令；中途归档并不等于一天科研结束。


## 2026-11-10 151509 GPU scVI+CellCharter25D 首片训练成功

用户真实Windows日志：执行 `prepare_dlpfc_10_features.py --sample 151509 --train`，先 `151509_GRAPH_CHECK_PASS spots 4789 edges 14086`，`151509_CUDA_READY NVIDIA GeForce RTX 4070 Laptop GPU`，`151509_PREPROCESS_PASS (4789,5000)`；`Global seed set to 22911`。Lightning明确 `GPU available: True (cuda), used: True`，于 epoch222/400 early-stop（连续45 records无validation ELBO提升、best score1395.943），正常得到`151509_SCVI_TRAIN_FINISHED`、`151509_FEATURE_CACHE_COMPLETE`。status completed; latent[4789,5], aggregate[4789,25], graph undirected edges14086; latent sha256 `fac7c28ae833e3eb8277b79b3170dcbf9d08bcc80fb6a9f8397e97424ae5d2c4`; aggregate sha256 `1f29060473365c02d2c26b51a477d87ff2fb4ee6a4e7ae8e18193895c8dfc32e`; script reported peak_cuda_mib106.73 (PyTorch allocated memory diagnostic only, not full GPU usage); finished UTC 2026-11-10T07:08:01.204473+00:00。TensorFlow `No GPU/TPU found, falling back to CPU` 与Lightning明确CUDA使用非同一框架，不视为失败。

输出目录 `D:\paper\CellCharter_reproduction\results\cellcharter_151509_scvi22911_features_batch_v1`；模型训练成功、25D完成，**尚未进行151509的GMM和性能评价**。下一步用户可执行 `--all --train`，脚本对于已完成且源文件哈希匹配的151509缓存会跳过，后续9片每片独立进程训练、失败即停止并保留现场。不会重新挑seed或筛选有利结果。

## 2026-11-10 十张新增DLPFC切片批量空间图只读预检全部通过

用户上传真实PowerShell日志：`python scripts/cellcharter/prepare_dlpfc_10_features.py --all`，未附加`--train`。十片依次输出`{sid}_GRAPH_CHECK_PASS`和`{sid}_CHECK_ONLY_COMPLETE; NO_TRAINING; NO_FILES_WRITTEN`，末行`DLPFC_10_FEATURE_CHECK_ONLY_COMPLETE 10/10`。图均通过六邻居几何和无向图检查。

|片|spots|无向edges|
|---|---:|---:|
|151509|4789|14086|
|151510|4634|13599|
|151669|3661|10597|
|151670|3498|10185|
|151671|4110|12026|
|151672|4015|11691|
|151673|3639|10562|
|151674|3673|10629|
|151675|3592|10381|
|151676|3460|10026|

日志有xarray_schema `pkg_resources`弃用警告和AnnData var_names非唯一警告但**无错误**；该预检不意味着GPU模型已训练，也未生成25D缓存。下一步为尽量节省GPU及排错成本，先单独151509运行`--sample 151509 --train`，确认scVI CUDA +4-hop25D全链成功后再`--all --train`。如单片失败请保留失败目录/status.json；不要删除或偷偷改配置。

## 2026-11-10 新增10片写后核验10/10 + 冻结后续协议和批量特征脚本（最新）

用户Windows实测新增10张的 `POST_WRITE_AUDIT_COMPLETE 10/10`，每张 `PASS`：151509 4789/4788/K7、151510 4634/4595/K7、151669 3661/3636/K5、151670 3498/3484/K5、151671 4110/4093/K5、151672 4015/3888/K5、151673 3639/3611/K7、151674 3673/3635/K7、151675 3592/3566/K7、151676 3460/3431/K7（格式：总spots/有标签spots/Oracle K）。这证明生成CSV的行数/条码/标注/转换manifest基本一致，非完全人工独立重审或原始标签质量保证。

已在GitHub新增 **[冻结协议](experiments/cellcharter_dlpfc/DLPFC_12_SECTION_FROZEN_EVALUATION_PROTOCOL_20261110.md)**：在已知151507、151508结果之后锁定新增样本的固定A=L0+L1+L2、B=L0+L1+L4，同15D，GMM seed22911，K按切片已知参考类别5或7，主要观察boundaryF1差值并共同报告ARI/NMI/FP等负结果。仅3位供体，供体1已开发，151673之前在其他项目使用过；**不能冒充全12片事先注册或全新独立盲测，不能把12张切片视为12个生物学重复**。

已上传 **[新增10片 scVI+25D 通用批量准备脚本](scripts/cellcharter/prepare_dlpfc_10_features.py)**。基于已成功的151508 v2协议，只有显式`--train`才训练；`--all`按每片独立Python进程串行运行，每张输出不同 `cellcharter_{sample}_scvi22911_features_batch_v1` 目录，已完整生成且hash匹配的缓存会跳过，失败目录不被覆盖；不读层标签、不拟合GMM。**该脚本仅已在GitHub上传，尚未用户Windows git pull，也未执行。** 下一步唯一动作用户 `git pull --ff-only`；成功后再单独运行无训练 `--all` 检查，绝不能提前声称训练已完成。

## 2026-11-10 10张新增切片已正式完成统一输入文件转换

用户Windows实际执行 `scripts/cellcharter/prepare_dlpfc_10_sources.py --write`，连续打印十张 `VALIDATED` 并以 `DLPFC_10_SOURCE_CONVERSION_WRITTEN_COMPLETE 10/10` 正常完成。按照脚本行为，每张新增切片应已写出 `spots_aligned.csv`、`manual_layer_annotations.csv`、`source_conversion_manifest.json`。未改151507/151508，也未运行scVI/GMM；**文件写出已获终端完成标记，尚未进行独立的写后内容核查**。逐片样本量/类别来自此前预检：151509 4789 spots/4788标注/K7，151510 4634/4595/K7，151669 3661/3636/K5，151670 3498/3484/K5，151671 4110/4093/K5，151672 4015/3888/K5，151673 3639/3611/K7，151674 3673/3635/K7，151675 3592/3566/K7，151676 3460/3431/K7。

**下一步**：Windows 单命令只读写后核验每张CSV存在、列名/记录数量、空间坐标barcode顺序和manifest/label数量对应；通过后再制定冻结的跨供体A/B预注册分析计划，包括Oracle-K各供体差异、边界F1/ARI/NMI主次终点、GMM初始化的处理、切片与供体的分析单位、避免按结果挑片，以及 `layer_guess` 来源与历史标注的可比性。不要立即无协议启动全10张训练。

## 2026-11-10 10张新增DLPFC切片批量转换只读预检全部通过

用户 Windows 实际运行 `scripts/cellcharter/prepare_dlpfc_10_sources.py` **未带 `--write`**，终端输出 `DLPFC_10_SOURCE_CONVERSION_CHECK_ONLY_COMPLETE 10/10`。每张均有 `VALIDATED`，对应spot/有标注/未标注/Oracle-K：
- 151509:4789/4788/1/K7
- 151510:4634/4595/39/K7
- 151669:3661/3636/25/K5
- 151670:3498/3484/14/K5
- 151671:4110/4093/17/K5
- 151672:4015/3888/127/K5
- 151673:3639/3611/28/K7
- 151674:3673/3635/38/K7
- 151675:3592/3566/26/K7
- 151676:3460/3431/29/K7

该脚本已验证原始H5/坐标/metadata barcode、行序、样本ID、合法标签取值及缺失情况，并计算待转换的标准字段。**本次纯只读；新spots_aligned.csv/manual_layer_annotations.csv/source_conversion_manifest.json 尚未由此命令写出**。用户可在下一步单独运行 `--write`，脚本拒绝覆盖旧结果。十张新切片标签来自 SEDR metadata的 `layer_guess`，与旧片标注来源的潜在差异必须披露，不能声称统一人工金标准。运行后的实际输出必须由用户回传再判断成功，不得推定。

## 2026-11-10 标签版本一致性检查已完成；10片转换脚本待本地预检

用户Windows真实输出：历史 `manual_layer_annotations.csv` 的151507含4221有效7类、151508含4381有效7类，命名 `Layer 1` 至 `Layer 6` 及 `WM`。新增十片的 `layer_guess` 与 `layer_guess_reordered` 每片 `MISMATCHES=0`，脚本输出 `LABEL_COMPATIBILITY_CHECK_COMPLETE`。**来源差异仍然要披露**：新增切片标注来自SEDR metadata中的 `layer_guess`；不能自动保证和历史两个切片人工标注采用完全相同的注释流程，原 `Layer` 列全NaN。供体2四张片仅5类，不允许拆分Layer3。

已上传新脚本 [prepare_dlpfc_10_sources.py](scripts/cellcharter/prepare_dlpfc_10_sources.py)：默认只读，10片逐个以H5条码为行序检查坐标和metadata、标签允许值、来源SHA256；将 `Layer1` 等改为 `Layer 1`、保留WM，未标注spot不写入annotation表；只有显式`--write`才为每片生成`spots_aligned.csv`、`manual_layer_annotations.csv`、`source_conversion_manifest.json`，拒绝覆盖。类别数由实际标签5或7决定，未来Oracle-K随片匹配而不能只用7。**GitHub已建脚本，用户Windows尚未拉取，也尚未运行脚本或生成新文件**。下一步仅git pull，然后独立执行无写入预检；不可提前说转换已成功。

## 2026-11-10 全10张新增切片 layer_guess / 元数据参考标签审计

用户Windows只读检查10张 `metadata_source.tsv`，每张 `META_BARCODE_UNIQUE=True`，`META_POSITION_MATCH=metadata总行数`。每张 `Layer` 原列**全部NaN**；可用标签列为 `layer_guess`、`layer_guess_reordered`、`layer_guess_reordered_short`。实际终端各片 `layer_guess` 值计数如下（每张均有未标注NaN，不可默认为背景）：

- 151509：Layer3 1884、Layer1 1189、Layer2 602、Layer4 369、Layer5 363、Layer6 215、WM166、NaN1；7有效类。
- 151510：Layer3 1774、Layer1 1180、Layer2 650、Layer4 318、Layer5 310、Layer6 179、WM184、NaN39；7类。
- 151669：Layer3 2141、Layer4 364、Layer5 510、Layer6 391、WM230、NaN25；**5类**。
- 151670：Layer3 2175、Layer4 211、Layer5 581、Layer6 308、WM209、NaN14；5类。
- 151671：Layer3 1918、Layer4 245、Layer5 721、Layer6 760、WM449、NaN17；5类。
- 151672：Layer3 1575、Layer4 304、Layer5 728、Layer6 882、WM399、NaN127；5类。
- 151673：Layer3 989、Layer1 273、Layer2 253、Layer4 218、Layer5 673、Layer6 692、WM513、NaN28；7类。
- 151674：Layer3 924、Layer1 380、Layer2 224、Layer4 247、Layer5 621、Layer6 614、WM625、NaN38；7类。
- 151675：Layer3 771、Layer1 328、Layer2 275、Layer4 275、Layer5 732、Layer6 533、WM652、NaN26；7类。
- 151676：Layer3 836、Layer1 289、Layer2 254、Layer4 254、Layer5 649、Layer6 616、WM533、NaN29；7类。

**严格限定**：当前还没有验证这些 `layer_guess` 与151507/151508既有 `manual_layer_annotations.csv` 标注**来源、格式及一致性**。标签列名有猜测性质，不得直接称真值或说是 `Layer`（全空）；如按每片实测类数进行Oracle-K，供体2为5，其余7，需预先公布K的切片级规则、禁止用聚类结果挑K，并且不能比较跨供体绝对边界F1不考虑标注粒度差异。**下一步**：只读核查151507/151508历史标签示例、缺失情况及新增10片 `layer_guess` 与 `layer_guess_reordered` 是否实际一致，再编写批量一致转换脚本。当前未转换也未开始新训练。

## 2026-11-10 新增10张数据源的只读对齐审计成功

用户在Windows运行批量只读 Python/scanpy 审计，终端为10张切片逐张报告 H5_SPOTS、POSITION_MATCH、IN_TISSUE_1、POSITION_DUPLICATES、METADATA_ROWS，结尾 `SOURCE_ALIGNMENT_AUDIT_COMPLETE`，无FAIL。

| slice | H5 spots | position matches | in_tissue=1 among matching spots | spatial barcode duplicates | metadata rows |
|---|---:|---:|---:|---:|---:|
|151509|4789|4789|4789|0|4789|
|151510|4634|4634|4634|0|4634|
|151669|3661|3661|3661|0|3661|
|151670|3498|3498|3498|0|3498|
|151671|4110|4110|4110|0|4110|
|151672|4015|4015|4015|0|4015|
|151673|3639|3639|3639|0|3639|
|151674|3673|3673|3673|0|3673|
|151675|3592|3592|3592|0|3592|
|151676|3460|3460|3460|0|3460|

前20个metadata字段包含 `barcode, sample_name, tissue, row, col, imagerow, imagecol, Cluster, ...`，但**尚未查看所有列，不能将 Cluster 擅自认作人工组织层标签**。上一轮命令也未检查metadata的barcode唯一性和与H5完全匹配（仅长度相等），仍需只读核对。下一步：一次性列出所有metadata列（至少一张及其跨片列集合差异）、候选人工layer字段的值计数、metadata barcode唯一性及匹配量；确定真实参考标签字段后才允许生成 spots_aligned/manual_layer_annotations，尤其供体2 K可能不同。**尚未转换任何新增数据，未训练新增样本**。

## 2026-11-10 批量坐标/标注来源下载成功（终端核实）

用户再次执行十张切片（151509/151510/151669/151670/151671/151672/151673/151674/151675/151676）的 metadata_source.tsv 和 tissue_positions_source.csv 下载，显式 `curl.exe --proxy http://127.0.0.1:7897`。终端显示先前成功项目 `SKIP`，其余全部 `OK`，没有 `FAILED`。因此指定本地目录预计已有十套这两个来源文件（20个原始文件），已有151507/151508的转换文件不改动。用户第一次无显式代理的尝试曾因连接重置失败，代理下载后成功。**只确认curl成功和文件非空，尚未读取验证来源表列名、metadata标注、barcode对齐、空间 in_tissue 及层类别。**

**下一步唯一动作**：用本地专用 Python 一条只读命令批量审计十张：检查 H5的barcode唯一、spatial位置barcodes及in_tissue匹配、元数据列名及可能barcode键/Layer字段。只读查看统计，后续依据真实格式编写保真转换脚本，不在识别标签协议前训练全套12片。

## 2026-11-10 全12张H5已实测读取成功；发现关键 Oracle-K / 标注协议差异

用户在Windows用CellCharter Python逐一 `scanpy.read_10x_h5` 并检查 barcode唯一性，终端 `H5_AUDIT_COMPLETE 12/12`，所有文件可读，所有切片33538 genes、无重复barcode，spot数：151507=4226，151508=4384，151509=4789，151510=4634，151669=3661，151670=3498，151671=4110，151672=4015，151673=3639，151674=3673，151675=3592，151676=3460。**H5内部读取通过**，但尚未批量验证空间坐标和人工标签；本地用户未传原H5，不得说AI已独立检查。

**重要新文献审查（对未来实验设计有实质影响）**：
1. LieberInstitute/HumanPilot `get_barcode_lists.R` https://github.com/LieberInstitute/HumanPilot/blob/master/get_barcode_lists.R 记录供体2的151669–151672大量 “Layer 2/3” 合并标注，供体1/3为分开的Layer2、Layer3。具体标注类别不完全相同，边界 F1 的基数及含义可能因供体差异变化。
2. SEDR_analyses https://github.com/JinmiaoChenLab/SEDR_analyses 的DLPFC benchmark `n_clusters` 表给151669/151670/151671/151672 **K=5**，其余切片K=7；与BASS https://pmc.ncbi.nlm.nih.gov/articles/PMC9351148/ 写的“所有12片K=7（oracle）”协议不一致。**必须先确认来源、标注映射、K的统一规则并预先声明比较目标，不能直接把151507 K7脚本循环到供体2，也不能把不同K造成的效果当作新算法改进。**
3. spatialLIBD https://research.libd.org/spatialLIBD/articles/spatialLIBD.html 可通过 `fetch_data(type="spe")` 得到全12片colData含 `array_row,array_col,spatialLIBD` 等，但目前没有在用户本地加载，不应默认已有坐标/标签。

**下一步先不训练**：只读检查各本地目录对应 `spots_aligned.csv` 和 `manual_layer_annotations.csv` 是否存在及大小，确认缺口后统一下载/转换，并核对 barcode、坐标与标注取值。随后设计冻结的统一 Oracle-K 协议及报告不同供体的标签差异。

## 2026-11-10 追加：完整12切片 H5 下载成功（用户终端）

用户 PowerShell 批量下载剩余9张 DLPFC 切片，终端九次 `DOWNLOAD_OK`：151509、151510、151670、151671、151672、151673、151674、151675、151676。此前用户已下载151669，151507/151508为已有数据。因此指定本地根目录 `D:\paper\ST_Benchmark_Planning\mvp\data` 中预计12张切片的 `filtered_feature_bc_matrix.h5` 均已取得；本次脚本判断以 curl 退出码0且文件非空为条件，**尚未逐个打开 H5 验证完整性、条码、空间坐标或人工标签；不能直接宣称12张数据集已准备到可训练阶段**。

按已核对公开供体分组：D1=151507/151508/151509/151510；D2=151669/151670/151671/151672；D3=151673/151674/151675/151676。三位供体，12张切片；论文统计不能将12片视为12位独立受试者。151673此前在其他项目中被触及，后续预注册验证方案前需盘点历史使用，不得未经证据称盲测。

**下一步唯一动作**：Windows 只读批量使用 `scanpy.read_10x_h5` 打开12份H5，列出spot×gene、barcode唯一性、文件大小、失败项；不训练、不改变原文件。之后才批量取得/核查 spatialLIBD 官方切片对应的坐标和人工层标签。

## 新增文献核查：DLPFC 供体结构纠正（2026-11-10，最高优先级）

已查公开来源（本条是**公开文献/数据项目报告**，不是Windows实验结果）：
- BASS论文 https://pmc.ncbi.nlm.nih.gov/articles/PMC9351148/ 描述12张DLPFC切片来自3位独立供体，每供体4张切片。
- 2026 ICLR Workshop公开论文 https://openreview.net/pdf/63a0bb10dd34a1ca90af0deae2bcd06d6de42cec.pdf 附表按供体列出：供体1 `151507/151508/151509/151510`，供体2 `151669/151670/151671/151672`，供体3 `151673/151674/151675/151676`。因此**此前泛称151509可作为独立样本并不准确**：它和已使用的151507、151508同供体。
- 研究机构官方空间LIBD源数据链接 https://github.com/LieberInstitute/spatialLIBD/blob/devel/README.Rmd ，151669 H5官方直链 `https://spatial-dlpfc.s3.us-east-2.amazonaws.com/h5/151669_filtered_feature_bc_matrix.h5`。
**当前方案**：优先选择另一供体的151669用于冻结方案A L0+L1+L2、B L0+L1+L4的扩展验证；需另行核实其标签/坐标来源和过去是否用于模型选型。切片数不等于独立供体数，151507/151508同供体。**尚未下载151669，也未进行新实验。** 先由用户手动下载原始H5到独立新文件夹并核验，其他输入随后准备，不先训练。

## 数据目录清点（2026-11-10，最新）

用户Windows只读执行 `Get-ChildItem "D:\paper\ST_Benchmark_Planning\mvp\data" -Directory | Where-Object { $_.Name -match "^1515\\d{2}$" }`，只返回 `151507` 和 `151508`。因此该特定本地目录中目前只有这两张匹配的 DLPFC 切片；**不能推断其他磁盘/目录或公开数据集没有更多切片**。当前两片已有结果：151507候选B的ARI/NMI/边界F1均改善；151508候选B的ARI略降、NMI下降而边界F1上升。下一步应选定未参与锁定组合选择的额外公开切片（优先核实独立供体），按冻结评价协议验证；暂不新建无终点的 seed/组合搜索或切回STAGATE。目标仍是普通SCI增量方法论文，当前尚未成立。

## 151508 冻结 A/B 对照已完成：边界F1正向、全局ARI/NMI非正向（2026-11-10，最高优先级）

用户Windows运行 `scripts/cellcharter/mvp_fixed15_block_swap_151508.py`，终端明确 `MVP_FIXED15_COMPLETE`，输出目录 `D:\paper\CellCharter_reproduction\results\mvp_fixed15_block_swap_151508_gmm22911_v1`，**已实际执行**。同一151508 scVI seed22911 的25D缓存切出两组15D；Oracle K7，CPU GMM seed22911。A: ARI `0.46267065495944715`, NMI `0.6132171362713753`, boundaryF1 `0.10315575161180861`, TP152/FP1868/FN775，L5/L6 41/139；B: ARI `0.46059571688191825`, NMI `0.5691388933817928`, boundaryF1 `0.16513761467889906`, TP261/FP1973/FN666，L5/L6 49/139。B−A：ARI −0.002075，NMI −0.044078，边界F1 +0.061982，边界FP +105（负面需保留）。真实评估边12846，真界面边927。

对比151507开发切片：同seed B的ARI/NMI/F1均更好；**151508上整体聚类ARI略差且NMI明显差，不能宣称整体聚类跨切片稳定提升；仅两切片边界F1有探索性改善信号**。所有数值来自用户终端，不是假定已独立读取本地CSV。当前不做统计显著性声明；spot/边不等于生物独立样本，151508是曾经接触的样本，非严格未触碰盲测。完整终端归档：[151508 试验报告](experiments/cellcharter_dlpfc/MVP_FIXED15_151508_EXTENSION_PLAN_20261110.md)。

**下一步**：不追加151508随机种子挑好成绩、不更改已冻结A/B；预先确定下一阶段主要终点、容忍的ARI/NMI损失，盘点是否有未用于设计的其他切片；公平对照和创新性审查之后才评估发展方法论文的可行性。不要转STAGATE或重启历史GMM排错。

## 151508 scVI/25D 缓存完成，锁定跨切片 A/B 脚本待运行（2026-11-10，最新）

**用户终端已证实成功**：v2脚本输出 `151508_SCVI_TRAIN_FINISHED` 及 `151508_FEATURE_CACHE_COMPLETE`，scVI提前停止于epoch260；4384×5 latent，4384×25聚合，空间边12849，CUDA运行，peak_cuda_mib=106.73（仅Torch统计），聚合文件SHA256=`094f702ba7fae32fc69c6c8026acb5765bd7bcd39b2802fbe8091b26baba60ee`。缓存路径 `D:\paper\CellCharter_reproduction\results\cellcharter_151508_scvi22911_features_v2`。**尚未在151508运行GMM、未生成跨切片比较指标。**

**新脚本已上传GitHub（Windows尚未拉取）**：[151508冻结15D对比](scripts/cellcharter/mvp_fixed15_block_swap_151508.py)；A=L0+L1+L2，B=L0+L1+L4；CPU GMM seed22911 K7，标注只在预测之后读入，自动按真实151508标注及边数计算指标。完整记录：[151508实验档案](experiments/cellcharter_dlpfc/MVP_FIXED15_151508_EXTENSION_PLAN_20261110.md)。下一步**仅git pull**，随后单独运行GMM脚本，先不加其他组合、不更改种子，不称严格未接触的独立盲测。 

## v2 语法错误修复（2026-11-10；最新）

用户 Windows 尝试运行 `prepare_151508_scvi_aggregation_v2.py`，Python **编译解析阶段**第169行报 `SyntaxError: unexpected character after line continuation character`。原因是我此前通过GitHub写入脚本时把 `peak_cuda_mib` 条件表达式的换行误写为字面量 `\\n`。在程序运行前已失败，**未触发任何CUDA初始化、训练或输出目录创建**，故 v2 结果目录应尚未由这次命令创建（如存在则另行检查）。我已在同一 v2 脚本中将字面量替换为真实换行，未改实验配置、代码行为或输出目录。修复提交 `2b372dc`。下一步**只需手动git pull同步修复**，等待用户成功结果后再运行 v2。不得再让用户运行旧脚本版本或误判为GPU故障。

## 最新 GPU 诊断与 v2 准备（2026-11-10）

用户原环境实际输出：`TORCH_VERSION 2.1.2+cu121`、`TORCH_CUDA_VERSION 12.1`、`CUDA_AVAILABLE True`、`CUDA_DEVICE_COUNT 1`、`CUDA_ALLOCATION PASS`、`GPU_NAME NVIDIA GeForce RTX 4070 Laptop GPU`、`CUDA_MEMORY_STATS PASS`。此前151508 v1在 `reset_peak_memory_stats(0)` 报 Invalid device，**目前未证实是设备损坏或具体根因**，当次scVI训练未开始。

已在GitHub新建 [v2 特征准备脚本](scripts/cellcharter/prepare_151508_scvi_aggregation_v2.py)，独立结果目录 `cellcharter_151508_scvi22911_features_v2`；在创建目录/开始训练前显式 `torch.cuda.init()`、分配1元素测试张量并同步。统计API故障仅记录警告（不改变是否训练模型），禁止CPU静默回退；保留v1失败目录。**v2尚未同步到用户Windows，也尚未运行。当前唯一下一步：用户手动git pull，确认成功后再单独执行v2。**


## 151508 特征准备首次正式运行失败（2026-11-10）

用户实际运行 `prepare_151508_scvi_aggregation.py`（无 `--check-only`）。终端先输出 `151508_GRAPH_CHECK_PASS spots 4384 edges 12849`、`151508_PREPROCESS_PASS (4384, 5000)`、`Global seed set to 22911`；随后出现 `No GPU/TPU found, falling back to CPU.`，在**任何 `151508_SCVI_TRAIN_START` 之前**的 `torch.cuda.reset_peak_memory_stats(0)` 第127行报 `RuntimeError: Invalid device argument 0: did you call init?`。因此**scVI尚未训练，不存在新的latent/aggregated结果**。脚本已创建专属结果目录并通过except将status.json标为failed（代码预期；未直接读取本地文件，须通过用户后续输出确认）。原脚本禁止覆写，不能立即重试。

当前唯一下一步：用户在原CellCharter Python环境运行一个仅诊断的单条PowerShell命令，检查 torch.cuda.is_available、device_count、NVIDIA设备名、最小CUDA张量能否分配及显存统计 API 是否可用；异常按字符串输出。确认问题后再为失败结果目录设计安全的续跑方案（**新目录、保留失败记录**），不盲目重新安装依赖/换CPU/重训旧数据。

## 151508 六邻域图预检成功（2026-11-10）

用户Windows实际执行 `prepare_151508_scvi_aggregation.py --check-only`，终端输出：
```text
151508_GRAPH_CHECK_PASS spots 4384 edges 12849
151508_CHECK_ONLY_COMPLETE; NO_TRAINING; NO_FILES_WRITTEN
```
另见 `Global seed set to 0`（包导入阶段初始化信息）及 `pkg_resources`、基因名称重复的 UserWarning。正式脚本在拟合scVI前将设置 seed22911，预处理调用 `var_names_make_unique()`。

这只证明空间图几何/对称性等检查成功；**scVI尚未训练，5D/25D缓存尚未生成**。下一步用户仅运行正式 `prepare_151508_scvi_aggregation.py`（无 `--check-only`）来准备151508 5D latent及25D聚合，脚本拒绝覆盖已有结果、不执行GMM或人工标注评价。继续冻结开发阶段A/B组合；151508跨切片不能表述为先前从未探索的独立盲测。 

## 151508 表征缓存盘点与训练准备（2026-11-10，最新）

用户Windows只读搜索 `D:\paper\CellCharter_reproduction` 与 `D:\paper\ST_Benchmark_Planning\mvp` 下路径包含151508且文件名匹配 `latent|aggregat|embedding|scvi`、扩展名为 `.npy/.npz/.h5ad/.pt` 的文件，**终端无输出**。这表示在此匹配范围内未发现缓存，**不代表全盘绝对不存在，也不是训练已执行**。

根据已经核实的151507适配版原始脚本，GitHub新建 [151508 特征准备脚本](scripts/cellcharter/prepare_151508_scvi_aggregation.py)，采用相同5000 HVG/seurat_v3、5维scVI、AdamW/early-stop、4跳25维空间拼接、seed22911和基于Visium六邻域几何校验。仅生成 scVI 5维 latent / 25维聚合/条码顺序，不拟合GMM、不读取人工层标注、不更换已锁定A/B。新结果目录独立且拒绝覆盖。**脚本仅已提交GitHub，Windows尚未同步或运行**。

**唯一下一步：先 `git pull --ff-only` 同步新脚本；然后再单独运行 `--check-only` 核对空间图并确认不会训练写文件；成功后再正式开始scVI训练。** 来源151508曾用于项目其他任务，跨切片检验不称严格全新盲测。避免重复STAGATE与历史GMM排错。

## 151508 预检结果（2026-11-10，最新）

用户在Windows实际以 CellCharter 专用 Python 运行只读核查并输出 `151508_INPUT_PREFLIGHT_COMPLETE`。真实终端：`EXPRESSION_SHAPE: (4384, 33538)`；`POSITION_ROWS: 4384`；`BARCODE_UNIQUE: True`；`BARCODE_ORDER_MATCH: True`；`COORDINATES_VALID: True`；`ANNOTATED_SPOTS: 4381`；`ANNOTATION_CLASSES: 7`；`ANNOTATION_BARCODES_MATCH: True`。读10x H5时有两个基因变量名不唯一 UserWarning，属于预处理注意事项，原151507脚本使用 `var_names_make_unique()`，此轮未写文件。

**证据边界**：以上是用户真实终端转录，不是AI直接取得本地文件；这仅验证矩阵与坐标/标注匹配，不证明历史使用或已有latent缓存、也未运行151508 scVI/GMM。151508不是完全未知的盲测数据（项目早前已涉及该切片），后续应称跨切片验证/扩展开发验证并明确已有接触程度。

**当前唯一下一步**：在指定本地项目目录只读寻找151508可复用的 scVI 5维 latent 和25维聚合特征。若找不到，才准备匹配151507预处理的训练脚本；不重复训练，也不更换锁定 A/B（L0+L1+L2 vs L0+L1+L4）。

## 151508 跨切片准备：Windows 路径清点（2026-11-10）

用户在 Windows 手动执行三输入文件的 `Test-Path` 与结果目录筛查，真实输出表明 `D:\paper\ST_Benchmark_Planning\mvp\data\151508\` 下 `filtered_feature_bc_matrix.h5`、`spots_aligned.csv`、`manual_layer_annotations.csv` 均为 `True`；在 `D:\paper\CellCharter_reproduction\results` 下按目录名匹配 `151508` **未列出目录**。这不证明其他位置不存在缓存或151508未曾用于其他实验。

**下一步唯一动作**：对151508执行只读矩阵/空间坐标和标注表结构检查（数量、barcode唯一性及顺序、标注覆盖；不得拟合、不得写文件）。如无既有CellCharter latent，之后才规划最小scVI缓存生成，不能立即宣称已有跨片实验。候选固定为A=`L0+L1+L2` vs B=`L0+L1+L4`，均15维。151508历史上用于其他任务的情况应说明，不称未经探索的独立盲测。


## 最新分区一致性复核与下一步（2026-11-10，最高优先级）

用户在Windows只读检查两轮 `predictions.csv`，按 `barcode` 一对一合并各4226行，真实输出：对照 `L0+L1+L2` 的跨GMM seed分区ARI=`0.5049001187368433`，候选 `L0+L1+L4` 的跨GMM seed分区ARI=`1.0`。说明候选B在seed22911和101的这两次拟合中得到**相同分区（允许标签编号置换）**；**不是**与人工标签ARI=1，更不能代表跨切片验证。详细记录见 [MVP-1b档案](experiments/cellcharter_dlpfc/MVP_FIXED15_GMM_SEED101_151507_20261110.md)。

**决策**：不继续在151507刷seed/挑更多组合，候选B暂固定待跨片检验；首先**只读盘点151508已有数据及缓存，不开始大规模重训**。此前写的“下一步对比两份CSV”已完成，失效。不要开启STAGATE或历史GMM排错。

## 最新 MVP-1b 结果（2026-11-10；当前优先）

- 用户实际执行 `mvp_fixed15_block_swap_gmm101_151507.py` 成功，`MVP_FIXED15_COMPLETE`；结果在本地 `D:\paper\CellCharter_reproduction\results\mvp_fixed15_block_swap_151507_scvi22911_gmm101_v1`，当前仓库仅终端转录。
- 固定151507/scVI seed22911/15维特征，GMM seed101：A `L0+L1+L2` 的 ARI=`0.4177569883`、NMI=`0.6113343544`、boundary F1=`0.1694744782`、L5/L6=`3/145`；B `L0+L1+L4` 的 ARI=`0.5272652573`、NMI=`0.6175659085`、boundary F1=`0.2030360531`、L5/L6=`62/145`。对照先前seed22911：A的ARI=0.480019、F1=0.154412、L5/L6=64/145，B与本次全部指标完全相同。**B两次cluster_sizes互为排列，但尚未直接读取预测文件确认按barcode分区是否严格一致。**
- **判断**：候选B在这两个GMM初始化下的全局指标均优于A，但A对seed敏感，L5/L6在一个seed中反而是A更好。仅同切片单scVI表征双GMM seed，不能归纳为泛化优势或完整边界修复。实验明细：[MVP-1b真实终端归档](experiments/cellcharter_dlpfc/MVP_FIXED15_GMM_SEED101_151507_20261110.md)。
- **当前最小下一步**：只读比对两次候选B的预测CSV，按barcode计算分区一致性ARI，不训练、不更改原结果；其后考虑冻结方案并规划另一张切片的实际开发/验证协议。不主动重启已取消的历史 seed0 h4 问题或 STAGATE。


> 当前有效存档，2026-11-10。**先读此文件的当前状态，再按需看实验归档；历史诊断保留于日记和原始记录，不作为当前待办。**
> 新对话阅读顺序：[AGENTS.md](AGENTS.md) → 本文件 → [当日日记](RESEARCH_JOURNAL/2026-11-10.md) → [交接索引](CURRENT_RESEARCH_HANDOFF.md)。

## 最新 MVP-1 结果和唯一下一步（2026-11-10）

- 用户 Windows **已实际运行完成** `mvp_fixed15_block_swap_151507.py`，终端确认 `MVP_FIXED15_COMPLETE`；本地结果目录 `D:\paper\CellCharter_reproduction\results\mvp_fixed15_block_swap_151507_seed22911_v1`。本仓库目前是**用户终端转录**，并未直接读取本地结果文件。
- 同为15维、相同scVI表征和单次 GMM seed22911：A=`L0+L1+L2`，B=`L0+L1+L4`。A→B：ARI `0.480019→0.527265`，NMI `0.574796→0.617566`，全局边界F1 `0.154412→0.203036`，FP `2564→1891`；**负结果：L5/L6界面检出64/145→62/145**。GMM有100 max_epochs提示，不能将单次结果视作收敛/稳定性证明。详细 [实际运行档案](experiments/cellcharter_dlpfc/MVP_FIXED15_BLOCK_SWAP_151507_SEED22911_20261110.md)。
- **当前唯一下一步**：用户先同步 GitHub 最新脚本 `scripts/cellcharter/mvp_fixed15_block_swap_gmm101_151507.py`，随后单独运行该脚本，用不同的**GMM初始化seed=101**验证同一输入下对比方向是否保持。**scVI来源仍为seed22911，不是独立生物重复，不重新训练scVI；新脚本未运行。**
- 禁止反向把本次正结果称已证实创新或独立验证；STAGATE不在当前任务范围；历史seed0 GMM不一致不重启。

## 当前目标与采用的科研策略

- **目标**：争取符合毕业要求的普通 SCI 方法论文，以成熟可运行基线、低成本可解释的**小幅增量**为导向，不追求重大理论突破，也不承诺任何期刊录用。
- **流程**：成熟基线 → 可测弱点 → 1–2个最小候选 → 低成本开发集 MVP → 同预算必要对照、锁定方案并跨独立样本验证 → 随实验并行写稿。原创性审查优先最近3–5项最相似工作，避免无限审查。
- **诚信边界不变**：开发集可以探索但不能将幸运最佳成绩当独立盲测；保留所有失败、无提升和负结果；人工参考标签不用于所谓独立测试的调参/早停；不伪造引用/结果。Oracle K=7 是根据人工标注类别数设置。
- **暂停事项**：用户要求停止历史 seed0 L4 GMM 两组预测不一致原因排查，已有审计与不确定性保存于实验文档；**不要再让用户跑这两套历史诊断命令**。

## 已完成且可追溯的结果（不是最终论文结果）

- CellCharter **v0.3.2 适配版**，scVI 5D latent、Visium 六邻域、TorchGMM CPU；与作者 v0.2.0/PyCave/原预处理 h5ad 不同，不能宣称一模一样的作者复现。
- DLPFC 151507：4226 spots，4221 有有效人工层标签；12385 无向邻边、12381 有效评价边、950 跨层参考边界。**151507 已用于开发，不是独立测试片**。
- seed22911、Oracle K7、L0–L4 共用一份 scVI latent，特征维度依次 5/10/15/20/25，GMM各自拟合：
  - ARI：0.362131 / 0.444156 / 0.457461 / 0.469696 / 0.496146
  - NMI：0.441915 / 0.569587 / 0.604740 / 0.585078 / 0.675436
  - 全局边界F1：0.175802 / 0.162024 / 0.132590 / 0.136045 / 0.171509
  - L4 的 Layer5/Layer6 边界检出0/145、Layer4/Layer5约3/160；L0 在多个组织层内部错误分割率较高；L4也有部分界面召回反弹，不能声称全体单调下降或过度平滑因果成立。
- L3 初次预测完成但边界评价因 Layer5 标签字符串错误而失败，已从保存预测恢复指标并保留失败；统一五档边界与逐层审计已实际执行。
- 主要证据：[全局边界](experiments/cellcharter_dlpfc/snapshot_20261110/BOUNDARY_AUDIT_151507_SEED22911_20261110.md)、[逐层边界](experiments/cellcharter_dlpfc/snapshot_20261110/LAYERWISE_BOUNDARY_151507_SEED22911_20261110.md)、[L3恢复指标](experiments/cellcharter_dlpfc/snapshot_20261110/results/cellcharter_v032_151507_seed22911_L3_diagnostic/metrics_recovered.json)。
- 最近邻已有研究：[文献审查V1](experiments/cellcharter_dlpfc/NEAREST_PRIOR_ART_AUDIT_20261110_V1.md)。**简单邻域表达相似性权重、注意力或仅重命名模块不能自动声称原创性**；AugGCL 的训练代码存在每epoch ARI选最优的片段，但是否用于对应报告值仍待核实，不能断言原作者整篇泄漏。

## MVP-0 实际结果与下一步（2026-11-10 最新）

- **只读预检已实际运行成功**：源文件 SHA256 `15b1fd58d092277f81fa2a1513bb2fbf865eea71b1b7450a9a2f710c941a8f54`，4226×25 float32；L0–L4 RMS 分别为 `1.01395915, 0.77181948, 0.72375672, 0.69487204, 0.67063472`；同维对L0平均绝对相关分别为 `1.00000000, 0.64353317, 0.64636024, 0.63651649, 0.62608682`。未使用标签、未训练、未写文件。[完整终端转录和决策](experiments/cellcharter_dlpfc/MVP_MULTISCALE_SCREEN_151507_20261110.md)。
- **决策**：无远邻特征幅度异常放大，不把纯可逆分块缩放当新方法创新（full covariance GMM 基本可吸收这种重标度）。选择等维度（均15维）特征组合的**探索性筛查**，控制 `L0+L1+L2`，候选 `L0+L1+L4`，复用已保存25维输入、同一GMM超参数和seed，**两组都重新拟合GMM**以便同一次脚本下公平比较，标签只在预测后读取；执行后报告ARI/NMI与真实边界指标，不重新训练scVI。新脚本：[mvp_fixed15_block_swap_151507.py](scripts/cellcharter/mvp_fixed15_block_swap_151507.py)。**脚本尚未执行**。
- **下一条用户操作**：先 `git pull --ff-only` 同步新的GitHub脚本，等用户实际报告成功，再单独运行MVP脚本。本次没有启动GMM。

## 历史阶段：MVP-0，只读预检计划（已完成）

- [完整务实方案](experiments/cellcharter_dlpfc/MVP_INCREMENTAL_RESEARCH_PLAN_20261110.md) 已冻结**首项只读检查**，没有训练任何新方法；后续加权候选仅为待决定方案。
- 新建 [预检脚本](scripts/cellcharter/preflight_multiscale_blocks_151507.py)，读取已保存的 seed22911 L4 `cellcharter_aggregated.npy`（4226×25），按五个5维块报告绝对均值、RMS、列STD、自身块相关，**不加载标注、不运行GMM、不写文件**。
- **下一个唯一手动操作**：用户在 Windows 先从 GitHub 同步最新脚本（代理 git pull 的旧成功参数可复用），收到成功日志后再单独执行上述预检脚本。绝不要在用户同步前称本地已有新脚本。
- 预检结果返回后决定是否有理由预先锁定一个**固定25维**块尺度校准候选，以及原始 L4、最简单替代控制与同协议 GMM 的开发集实验。因为 full-covariance GMM 对可逆线性缩放理论上可吸收，任何差别可能来源于初始化/正则/数值，不能直接归因于生物学新机制。

## 仍需面对的局限与实施规则

- 当前仅开发切片单种子，深度与输入特征维度联动；跨独立切片/供体、重复种子、全套公平对照、最近邻完整机制审查、创新验证、论文结果均未完成。
- Windows: `D:\paper\CellCharter_reproduction`；本地 Git: `D:\paper\st-clustering-research`；Python: `D:\paper\CellCharter_reproduction\env_cellcharter\python.exe`。原始 H5、部分本地模型和 CSV 未上传；GitHub 终端转录不是原始文件字节校验。
- 用户本人执行 Windows 本地实验；AI 直接管理允许的 GitHub 文档/脚本。**一次只给一条可复制命令**，说明预期与报错处理。
- 本文件每次关键研究推进时保持简短、移除过期下一步；历史细节去日记和 `experiments/`，不能重复堆叠相互冲突的“下一步”。
