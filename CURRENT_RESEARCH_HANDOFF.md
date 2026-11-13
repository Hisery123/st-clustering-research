# CURRENT_RESEARCH_HANDOFF · 第三篇空间转录组聚类论文

## 【2026-11-13 E1首次同seed复现有差异：暂停大批量GMM】

用户Windows已真实执行E1首个151507同seed22911独立Python进程冒烟，终端显示`E1_PILOT_COMPLETE`、新目录`results/e1_same_seed_151507_gmm22911_rep01_v1`。对照历史seed22911预测，**A(L0/L1/L2)预测互比ARI=0.784965371、NMI=0.830379493、fit+predict=1.811s；B(L0/L1/L4)预测互比ARI=0.776070708、NMI=0.834877522、0.835s**。两配置同seed均未完全复现，原因**尚未确定**。GitHub历史151507代码及新运行代码都显式`np.random.seed(22911)`、`torch.manual_seed(22911)`，Cluster random_state=22911。不能拿之前B跨seed101/22911预测ARI1.0证明B普遍稳定；这不是相对参考标签的ARI/NMI。**不能现在启动1200批任务，需先做针对性的只读环境/线程诊断和受控独立进程验证**。详情见 [E0/E1延伸审计](experiments/cellcharter_dlpfc/E0_ASSET_LABEL_PREFLIGHT_20261112.md)。


## 【2026-11-13 E0第11步完成｜11片历史结果可复用，E1待启动】

用户Windows实际输出 `LEGACY_RESULT_AUDIT_PASS 11/11`：151508及151509–151676（共11片）既有固定15D A/B GMM seed22911结果，Manifest与25D源、15D切片特征SHA256、GMM参数、oracle-K和预测CSV条码顺序/类别全部通过核验。**无须重做这11片已完成的相同配置**，下一步切换E1同seed独立进程重复性冒烟，优先151507使用已有25D、两种15D特征与GMM seed22911；新运行必须使用新目录、不覆盖旧预测；按barcode比较新旧分区ARI/NMI，并记录环境版本与耗时。此11/11为Windows运行结果，未表示助手直接读取了本地CSV。E1、E2及新训练仍未开始；详情见 [E0资产审计](experiments/cellcharter_dlpfc/E0_ASSET_LABEL_PREFLIGHT_20261112.md)。


## 【2026-11-13 E0第10步更新：151507跨GMM seed分区稳定性新证据】

用户Windows实测，两组151507等维A/B预测CSV跨GMM种子101与22911、按4226条barcode对齐后，**对照A(L0+L1+L2)：预测互比ARI=0.504900119、NMI=0.637920634；候选B(L0+L1+L4)：预测互比ARI=1.0、NMI=1.0**。这仅表示单切片两seed的**预测分区相似度**；不是相对人工层标签的准确性，不能推出B多切片普遍更稳定、更准确或是新方法。旧两次seed0预测ARI≈0.713871是另一项记录，不能混淆；正式E1同seed独立重复未执行。详情见 [E0资产审计](experiments/cellcharter_dlpfc/E0_ASSET_LABEL_PREFLIGHT_20261112.md)。**下一步只读核查151508及后10片历史manifest/预测输出与缓存来源的一致性**；不训练、不改历史文件。


## 【2026-11-13 E0第9步更新：两组151507固定15D并非同seed重复】

用户Windows实际打印两份完整Manifest：`mvp_fixed15_block_swap_151507_scvi22911_gmm101_v1` 使用GMM seed101，`mvp_fixed15_block_swap_151507_seed22911_v1` 使用seed22911；两者状态completed、source 25D SHA256相同、A/B各自15D特征哈希相同，记录的GMM full/kmeans/CPU/100epoch等参数相同。候选B簇大小仅排列不同，但**不能据此断言两次分区一致**；需先按barcode对齐两目录的预测CSV，分别算A与B的分区互比ARI/NMI。**两者是跨seed对比，E1同seed重复仍未执行。** 完整字段与证据限制见 [E0审计档案](experiments/cellcharter_dlpfc/E0_ASSET_LABEL_PREFLIGHT_20261112.md)。下一步只读比较两组预测，不运行训练、不覆盖旧结果。


## 【2026-11-13 最新接手点｜建议1：E0只读核查到第8步，用户要求存档】

**真实Windows终端新证据**：12张DLPFC切片的25D聚合特征和5D latent文件均已定位，形状/float32/有限值检查通过；前2片spot行顺序与已有预测/spot_order一致；后10片源聚合/latent/坐标文件实际SHA256与历史status/config逐一MATCH（10/10）。12片按sample_name筛选并逐barcode匹配人工标签，`LABEL_ALIGNMENT_PASS 12/12`，本切片无重复标注或超出Spot条码；共352个Spot无有效参考层标签。151507参考CSV含来自151669的740行，筛选后有4221匹配、5无标签（has_label=False）；**不能据此断言其他历史评价脚本全部无污染或与上游官方数据逐barcode相符**。

**刚完成的E0第8步**：Windows只读列举结果目录（仅文件存在性、尚未读取其内容）：后10片各有1组固定15D A/B（manifest=1、results/metrics JSON=1、prediction CSV=2）；151508有一组；151507有两组命名不同的固定15D结果，每组同样有1 manifest、1 JSON、2预测CSV；151507另有L0–L4逐层诊断目录及其预测/指标。**不能将151507两组直接视为受控的同seed双运行**。详细证据与未核实项见 [E0核查档案](experiments/cellcharter_dlpfc/E0_ASSET_LABEL_PREFLIGHT_20261112.md)。

**实验状态**：本轮未做任何新增GMM/scVI训练、未运行E1、未冻结或执行1200拟议任务、未证实新创新；16页论文工作稿和原先A/B阴性结果不变。

**下一回合唯一优先操作**：用户Windows只读查看151507两个固定15D实验manifest及对照151508/后10片代表性manifest关键字段，核查完成状态/seed/K/GMM超参/输入特征哈希。待核对后再设计同seed重复性冒烟，不重复全缓存预检、不重跑scVI。只给一个PowerShell命令并等用户结果。**GitHub此处为远端存档，未自动同步Windows**。


## 【最新科研主计划｜2026-11-12：《第三篇完整实验建议1》】

**用户已明确要求汇总并正式归档两轮Claude建议及本助手修正，原则上全部实施、不因时间/算力估计而预先缩减。权威全文**：[`THIRD_PAPER_COMPLETE_RECOMMENDATION_1_20261112.md`](experiments/cellcharter_dlpfc/THIRD_PAPER_COMPLETE_RECOMMENDATION_1_20261112.md)。现有16页正文只是单seed A/B阶段稿，第三篇进入**全部12片系统消融＋同seed重复性/10seed稳定性＋25D置换对照＋K敏感性＋全空间图/混淆与标志基因＋Leiden/STAGATE/GraphST/SpaGCN/BayesSpace/SEDR公平基线＋第二数据集＋供体统计＋容差边界和无监督指标＋无标签自适应尺度候选＋论文重写**的正式研究计划。10唯一配置×12片×10seed理论上1200个GMM任务（额外K、基线另计），未经实测不能断言“一夜跑完”。

**必须区别证据**：151507三点hop数字和STAGATE ARI来自Claude报告，待原始CSV/日志核对；GitHub `GMM_L4_SEED0_MANIFEST_AUDIT_20261110.md`确实记录两次**同为seed0**、预测互比ARI≈0.713871，不能说“只改变seed导致不一致”；需区分同seed重复性和跨seed波动。151507混合标签文件及5个缺参考spot、下游评价join尚未彻查，正式批量评价前须完成适当数据质量门槛，旧结果不覆盖。**全部E1–E6新增实验尚未因本次存档而执行**，不预设规律、贡献或SCI录用。

**下次真正执行的第一步**：按用户需求只读核查GMM脚本、旧hop/固定25D、STAGATE/Leiden产物、25D缓存、标签评价代码，编制可复用清单，冻结预注册矩阵后做小规模冒烟与测时。用户Windows手动每回合最多一条PowerShell指令；GitHub档案未自动同步到其Windows。

## 【2026-11-12 最新正式科研决策｜全面扩充第三篇实验，优先于旧MVP收尾策略】

**用户明确要求：原则上全盘接受Claude提出的毕业论文+SCI实验补充建议，不因“实验数量多/尚无时间压力”而预先缩减，除非后续实际执行有实质困难或公平性/有效性约束。** 完整任务清单、科研红线、状态划分与执行路线已存档：[`THIRD_PAPER_FULL_EXPERIMENT_EXPANSION_DECISION_20261112.md`](experiments/cellcharter_dlpfc/THIRD_PAPER_FULL_EXPERIMENT_EXPANSION_DECISION_20261112.md)。

**全部纳入计划（未执行≠已完成）**：5类逐层累加＋固定15D的6类组合（共10个不同配置）；12片、GMM多种子5–10；ARI/NMI/边界F1热图/箱线与12片空间图、监督后处理颜色对齐；逐片混淆矩阵/层标志基因；K5–9与AutoK；Leiden/BayesSpace/SpaGCN/STAGATE/GraphST/SEDR等公平基线；至少第二个外部数据集；供体层面统计（仅3生物供体）；容差边界F1及无标签空间指标；探索不依赖参考标签的自适应尺度选择候选；按真实结果扩充并重写论文。**目标为SCI级别实验完整性，硕士论文可提交研究为基础，创新须另证。** Claude提到本地runs/存在151507 hop消融和置换对照、figures/存在图：这是Claude报告，**本助手尚未核查原始本地文件**。

**当前状态**：16页第二/三/四章工作稿已实际编译并上传审查，不能当最终定稿；原单一A/B结论B未稳定胜出。新扩充试验均为计划，不宣称已运行。此前151507跨切片参考CSV异样仍未消除；按此前用户决定，不无端继续历史排障，但正式批量评估前必须核实实际标签匹配与评价代码，防止污染。**下次唯一优先方向：先只读审查现有GMM与旧消融源码/缓存、盘点可复用成果和预算，冻结实验协议后再启动。** 绝不擅自批量跑；Windows一回合一条命令。GitHub新增记录需要用户以后同步本地。


## 最新权威接手点｜2026-11-12（用户要求存档并暂停标签排查）

完整存档见 experiments/cellcharter_dlpfc/THIRD_PAPER_PAUSE_CHECKPOINT_20261112.md。第三篇核心第二、三、四章16页整合PDF已由Windows两轮XeLaTeX成功编译、上传并审查，3张图4张表6篇文献齐全；尚未写绪论、总结、摘要，也未适配学校模板。不要误用下方旧条目的过期指令（例如继续编译第二章）。
151507最新真实审计：metadata.tsv里3661行第三字段全部是151669，原文件表头73/数据74列；manual_layer_annotations.csv含151507的4221行和151669的740行；spots_aligned.csv共4226行，对151507自身4221条标签逐barcode匹配一致数4221、标签不一致0、无参考5。5个未匹配spot的标记及下游评价代码尚未检查，不得断言评价已污染或完全无污染。用户已明确暂时不追查此事；后续以写作及用户主动决定为优先，不启动训练。GitHub本次修改尚未同步Windows。


## 2026-11-12 追加：DLPFC参考层标签源头得到官方资料支持（待本地逐barcode复核）

公开SEDR_analyses仓库README证实其DLPFC数据源为SpatialLIBD、metadata.tsv与BayesSpace数据一致，源码DLPFC_Seurat.R直接读取layer_guess作为参考标签；SpatialLIBD官方fetch_data文档列出layer_guess字段。完整证据与原网址见 `experiments/cellcharter_dlpfc/DLPFC_LABEL_ORIGIN_AUDIT_20261112.md`。可说后10片沿用公开数据链中的既有参考标签，而非SEDR模型输出或本研究新人工标注；**尚未证实本地CSV与公开上游每行一致、也未核实旧2片与新10片完全同源**。下一步用户Windows只读列出12个目录里metadata_source.tsv与manual_layer_annotations.csv的实际存在性，收到输出再设计逐barcode核对；不训练，不改旧结果。本次新增GitHub证据档案，尚未同步用户Windows。

## 2026-11-12 16页整合PDF用户实测通过、逐页视觉审查（最新）

用户Windows第二轮XeLaTeX成功生成`THESIS_CHAPTERS_2_4_INTEGRATED_20261112.pdf`(16页)并上传，已直接审查PDF：第2章页1–3、第3章页4–8、第4章页9–15、参考文献页16；方法TikZ图1页7、12片Δ三面板图2页10、两例六面板真实空间图3页14，4张表全在，6篇参考文献文末出现，未出现缺图占位框。公式跨章连续到(11)，图表编号已统一。**整合版技术结构初步通过，但有实际页面问题**：第6页3.6标题/引导文字留在页尾而图1在第7页；第13页表4单独位于空白较多的页面；第14页六面板原图图例偏小。另用户终端只有`caption hypcap=true ignored`非致命警告。不要断言达到学校学位模板要求。

科研边界仍是12片/3供体、固定单seed、Oracle-K，B无稳定改善；文献正文是初步核查而非系统综述/全部全文精读。**下一步优先是整合稿的实质性内容质量审查、SEDR标签源头核实和格式改善的优先级规划**，不要机械重训；如果只修复分页，修改整合正文快照片段而非覆盖原始独立版本，修复后必须先Git同步再由用户Windows重新编译验收。此次PDF上传不等于GitHub已备份用户本地PDF与实验图字节。

## 2026-11-12 更新：第二章PDF已核查，通过；2–4章整合TeX已提交，待Windows验证（当前最新）

**用户实际PDF证据：** 最新上传的第二章《研究背景与相关工作》PDF（3页）经逐页检查：页眉误显示“参考文献”的问题已消除，m2ST参考文献间距正常，6条参考文献完整。这只是格式审查通过，不代表已经核查全部付费论文全文或符合学校学位模板。

**GitHub新增：** 保留三个原始独立TeX不变，新建 `experiments/cellcharter_dlpfc/THESIS_CHAPTERS_2_4_INTEGRATED_20261112.tex` 主文件和 `chapter_02_background_integrated.tex`、`chapter_03_methods_integrated.tex`、`chapter_04_results_integrated.tex` 三份正文快照。统一ctexart导言、2/3/4节次序和文末6篇参考文献；从整合版第4节移除“定稿前核查提示”。两张实验图仍只引用用户Windows已有的真实PDF文件，源TeX里有找不到文件时的明确占位提示。**这些新增文件尚未在用户Windows同步，也未经过Windows实际XeLaTeX编译或视觉验收，不可称整合已成功。** 原TeX与真实本地结果均未被覆盖；整合片段是快照，后续更改单章要同步片段。

**当前下一步唯一Windows操作**：运行此前成功的 `git -c http.proxy=http://127.0.0.1:7897 -c https.proxy=http://127.0.0.1:7897 -C "D:\paper\st-clustering-research" pull --ff-only`。确认Fast-forward和四个新文件到位，之后另一回合单独编译主TeX，核查总图/表/公式编号、文末参考文献、横向六联图及缺图占位。禁止重训，禁止把12切片当12独立供体、把B称为已验证创新。


## 最新接手点｜2026-11-12：第二章已同步Windows，等待第一次XeLaTeX

用户实际Windows `git pull --ff-only` 输出：`0792652..73bbc05 Fast-forward`，确认第二章TeX `experiments/cellcharter_dlpfc/THESIS_BACKGROUND_RELATED_WORK_20261111.tex` 和文献证据矩阵均已下载。**不要再让用户重复这一步**。用户要求“先存个档”，本轮仅归档，无训练/编译。

**章节状态：** 第二章TeX已写、已本地同步、尚未编译；第三章5页、第四章7页独立PDF已真实编译并上传核查，尚未合并。第三章后续二次编译已消除“图??”、图位置正常；第四章两张科研图已嵌入。12片3供体、单种子冻结15D A/B结论不变：B无稳定改进；仅3位生物学独立供体；Oracle-K及开发/扩展标注差异务必披露；不把多尺度特征称新算法。

**唯一下一步：** 让用户在PowerShell手动XeLaTeX编译第二章TeX（输出到既有结果目录）；等完整成功/失败日志再决定是否二次编译或修正，然后上传第二章PDF进行实际逐页审查。**现在不提供新的git pull，不重训任何模型，也不要声称第二章PDF已生成**。

**读档路径：** `AGENTS.md` → `PROJECT_STATE.md` → 本文件 → `RESEARCH_JOURNAL/2026-11-12.md` → 需要时读`LITERATURE_EVIDENCE_AND_NOVELTY_20261111.md`与相关TeX/实际脚本。此前旧“下一步”只能作为历史。

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

## 151508 输入文件存在（2026-11-10；当前最优先）

用户Windows检查：151508 的表达H5、spots_aligned.csv、manual_layer_annotations.csv 三文件均存在；指定 `CellCharter_reproduction\results` 下没有列出匹配151508的目录。**未检查文件结构/条码匹配、也未确证所有位置没有scVI缓存**。下一步仅只读检验151508矩阵与坐标行顺序及标注覆盖；随后决定最小跨片实验。方案A L0+L1+L2、B L0+L1+L4不变。暂不重训、不查STAGATE。


## 最新结果（2026-11-10）：已完成 Barcode 分区一致性复核

用户实际只读合并两轮各4226行 predictions.csv，结果：对照 A 的跨 GMM seed 分区 ARI=`0.5049001187368433`，候选 B 的分区 ARI=`1.0`。因此 B 在这两个 GMM seed 下为同一分区（簇编号可置换），不是对人工标签 ARI=1.0、不是不同切片验证。原本本文件旧段落“尚未直接读取预测文件”已过期；详细档案见 [MVP-1b](experiments/cellcharter_dlpfc/MVP_FIXED15_GMM_SEED101_151507_20261110.md)。**接下来仅只读检查151508已有数据及特征缓存；不继续刷151507、不恢复STAGATE和历史GMM排查。**


## 最新 MVP-1b 结果（2026-11-10；当前优先）

- 用户实际执行 `mvp_fixed15_block_swap_gmm101_151507.py` 成功，`MVP_FIXED15_COMPLETE`；结果在本地 `D:\paper\CellCharter_reproduction\results\mvp_fixed15_block_swap_151507_scvi22911_gmm101_v1`，当前仓库仅终端转录。
- 固定151507/scVI seed22911/15维特征，GMM seed101：A `L0+L1+L2` 的 ARI=`0.4177569883`、NMI=`0.6113343544`、boundary F1=`0.1694744782`、L5/L6=`3/145`；B `L0+L1+L4` 的 ARI=`0.5272652573`、NMI=`0.6175659085`、boundary F1=`0.2030360531`、L5/L6=`62/145`。对照先前seed22911：A的ARI=0.480019、F1=0.154412、L5/L6=64/145，B与本次全部指标完全相同。**B两次cluster_sizes互为排列，但尚未直接读取预测文件确认按barcode分区是否严格一致。**
- **判断**：候选B在这两个GMM初始化下的全局指标均优于A，但A对seed敏感，L5/L6在一个seed中反而是A更好。仅同切片单scVI表征双GMM seed，不能归纳为泛化优势或完整边界修复。实验明细：[MVP-1b真实终端归档](experiments/cellcharter_dlpfc/MVP_FIXED15_GMM_SEED101_151507_20261110.md)。
- **当前最小下一步**：只读比对两次候选B的预测CSV，按barcode计算分区一致性ARI，不训练、不更改原结果；其后考虑冻结方案并规划另一张切片的实际开发/验证协议。不主动重启已取消的历史 seed0 h4 问题或 STAGATE。


> **2026-11-10 文献核查新进展**：已核实 CellCharter 原文/官方邻域拼接 API、AugGCL 2026 PLOS 原文 NIA 表达-邻域相似度加权、CodaST 出版方摘要 LSWC、HarveST PMC 全文及 GATCL/TRACER 的摘要；详见 [第一轮最近邻审计](experiments/cellcharter_dlpfc/NEAREST_PRIOR_ART_AUDIT_20261110_V1.md)。**STOP：**不得将单纯表达相似性加权邻接或 GAT 注意力包装成独创。**条件 GO：**先审查多尺度特征块与 GMM 可分性影响的最小、可证伪机制对照（非新算法）。AugGCL GitHub 代码含根据每epoch ARI选择最佳结果的片段，但尚未证实其用于论文151507的报告值。当前无需 Windows 操作，不自动恢复已暂停的历史 GMM 排查。下方早期“下一步查 GMM”均为旧记录。


> **2026-11-10 用户最新科研决策（优先于下文旧待办）**：停止追查历史两份 seed0 L4 GMM 不一致，根因未明，暂存为局限；**禁止自动继续预测对齐、RNG、重复拟合诊断**。转入 S2/S3：对 CellCharter 边界/连续性权衡作最近邻论文原创性审查，再决定单一最小机制。初步检索与源链接：[研究转向记录](experiments/cellcharter_dlpfc/RESEARCH_PIVOT_AND_PRIOR_ART_SCREEN_20261110.md)。后文涉及“下一步继续查 GMM”的句子是先前历史状态，现已失效。


> 最后整理：2026-11-10。**跨对话读档顺序：** [AGENTS.md](AGENTS.md) → [PROJECT_STATE.md](PROJECT_STATE.md) → [最近科研日记](RESEARCH_JOURNAL/2026-11-10.md) → 按需审查本文件和对应实际实验代码/结果。此文件是交接索引，不是原始证据。历史实验完整记录在 `experiments/`。

## MVP-0 实际结果与下一步（2026-11-10 最新）

- **只读预检已实际运行成功**：源文件 SHA256 `15b1fd58d092277f81fa2a1513bb2fbf865eea71b1b7450a9a2f710c941a8f54`，4226×25 float32；L0–L4 RMS 分别为 `1.01395915, 0.77181948, 0.72375672, 0.69487204, 0.67063472`；同维对L0平均绝对相关分别为 `1.00000000, 0.64353317, 0.64636024, 0.63651649, 0.62608682`。未使用标签、未训练、未写文件。[完整终端转录和决策](experiments/cellcharter_dlpfc/MVP_MULTISCALE_SCREEN_151507_20261110.md)。
- **决策**：无远邻特征幅度异常放大，不把纯可逆分块缩放当新方法创新（full covariance GMM 基本可吸收这种重标度）。选择等维度（均15维）特征组合的**探索性筛查**，控制 `L0+L1+L2`，候选 `L0+L1+L4`，复用已保存25维输入、同一GMM超参数和seed，**两组都重新拟合GMM**以便同一次脚本下公平比较，标签只在预测后读取；执行后报告ARI/NMI与真实边界指标，不重新训练scVI。新脚本：[mvp_fixed15_block_swap_151507.py](scripts/cellcharter/mvp_fixed15_block_swap_151507.py)。**脚本尚未执行**。
- **下一条用户操作**：先 `git pull --ff-only` 同步新的GitHub脚本，等用户实际报告成功，再单独运行MVP脚本。本次没有启动GMM。

## 当前路线的历史摘要

**用户确定将论文策略调整为普通SCI毕业目标下的成熟基线、小幅增量、低成本MVP**：已完成 CellCharter adapted 151507 seed22911 L0–L4 与边界审计；立即进入**多尺度块的只读预检**，随后由数据决定是否开展一项最小固定25维校准对照。停止追查历史 seed0 GMM 不一致，停止无限期文献排查；最近邻文献以3–5篇最相似为先。当前所有加权/校准方案均未执行、不是创新成果；151507只能当开发切片，不能把大范围尝试后的幸运值当独立测试。

- 最新研究策略：[MVP 增量计划](experiments/cellcharter_dlpfc/MVP_INCREMENTAL_RESEARCH_PLAN_20261110.md)
- 新预检脚本：[多尺度块只读预检](scripts/cellcharter/preflight_multiscale_blocks_151507.py)
- **下一个唯一操作：** Windows 本地 `git pull --ff-only` 同步 GitHub（已有 Clash 7897 代理成功方案）；用户汇报成功后，单独运行预检，不要同一回合给两条命令。
- 实验终端还没有运行新预检，不能填预检结果。下方任何“继续查历史 GMM”的旧表述是历史记录，不是当前任务。更简明准确的现状以 [PROJECT_STATE.md](PROJECT_STATE.md) 为准。

## 一句话状态

当前母体为 **CellCharter v0.3.2 适配版**。DLPFC **151507、seed22911、Oracle-K=7** 的基线及 L0–L4 五档空间邻域深度诊断均已完成；统一边界审计及逐层边界分析也已运行。**当前优先执行多尺度特征块的只读预检**，不重复 L3，也不再主动排查历史 GMM。

## 研究者与助手分工

- 用户使用 Windows 11 / PowerShell **手动执行本地实验**。助手负责方法审查、代码设计、文献、统计、可编辑绘图、科研写作，并经授权直接维护本私人 GitHub 仓库。
- 本地操作一次仅给一条命令或一个短操作，交代目的、成功标记、失败处理，等待终端真实结果；不默认使用 Codex 或远程操作用户电脑。
- GitHub 可直接编辑不等于助手能访问 Windows 本地任何文件；**不得假称本地未上传的文件已核验或已备份**。GitHub 更新后用户本地 checkout 需另行同步。

## 原始文件与实验环境

- 私人仓库：https://github.com/Hisery123/st-clustering-research
- Windows 训练根目录：`D:\paper\CellCharter_reproduction`
- Git checkout：`D:\paper\st-clustering-research`
- 数据目录：`D:\paper\ST_Benchmark_Planning\mvp\data\151507`
- Python：`D:\paper\CellCharter_reproduction\env_cellcharter\python.exe`
- 正式 L4 基线：[代码](scripts/cellcharter/cellcharter_151507_baseline_v032.py)、[配置](experiments/cellcharter_dlpfc/snapshot_20261110/results/cellcharter_v032_151507_seed22911_oracleK7/config.json)、[指标](experiments/cellcharter_dlpfc/snapshot_20261110/results/cellcharter_v032_151507_seed22911_oracleK7/metrics.json)
- L3 后补：[运行代码](scripts/cellcharter/cellcharter_151507_L3_diagnostic.py)、[非重训结果恢复代码](scripts/cellcharter/recover_151507_L3_metrics.py)、[真实终端转录指标](experiments/cellcharter_dlpfc/snapshot_20261110/results/cellcharter_v032_151507_seed22911_L3_diagnostic/metrics_recovered.json)
- 五档统一边界审计：[代码](scripts/cellcharter/audit_151507_all_depth_boundaries.py)、[完成记录](experiments/cellcharter_dlpfc/snapshot_20261110/BOUNDARY_AUDIT_151507_SEED22911_20261110.md)、[逐层结果](experiments/cellcharter_dlpfc/snapshot_20261110/LAYERWISE_BOUNDARY_151507_SEED22911_20261110.md)
- 历史 2026-11-09 seed0：[跳数消融](experiments/cellcharter_dlpfc/HOP_ABLATION_151507_SEED0_20261109.md)、[固定25维置换](experiments/cellcharter_dlpfc/FIXED25_PERMUTATION_151507_SEED0_20261109.md)。**不可将历史 seed0 当成 22911 的重复**。

原始10x H5、scVI 模型、latent.npy、聚合矩阵及部分本地 CSV 尚未备份到仓库；需要实际文件时再由用户提供，不应擅自宣称已读取。

## 2026-11-10 已完成结果（仅单切片单种子）

- 151507 原始 4226 spots；4221 带人工组织层标注。跨切片 barcode 可能重复：必须先按 `sample_name=="151507"` 筛标签，再对齐 barcode。
- Visium 12385 条无向空间邻边，12381 条两端都具有标签，可评价真实层间边界共 950 条。
- scVI（5000 HVG、latent5、GPU）→ 同一 scVI latent 的 CellCharter L0/L1/L2/L3/L4 聚合，特征维度依次 5/10/15/20/25 → 每档独立 TorchGMM CPU 拟合，Oracle K7（人工类别数）并用固定 seed22911。
- L4：ARI=0.4961464421378273，NMI=0.6754358219165002。协议是 v0.3.2 TorchGMM 与本地重建图的**适配基线**，不是作者 v0.2.0 + PyCave + 预处理 h5ad 的完整同版本复现。

| Depth | ARI | NMI | Boundary F1 | L5/L6 Boundary Recall |
|---|---:|---:|---:|---:|
| L0 | 0.362131 | 0.441915 | 0.175802 | 0.6000 |
| L1 | 0.444156 | 0.569587 | 0.162024 | 0.5448 |
| L2 | 0.457461 | 0.604740 | 0.132590 | 0.4414 |
| L3 | 0.469696 | 0.585078 | 0.136045 | 0.3310 |
| L4 | 0.496146 | 0.675436 | 0.171509 | 0.0000 |

L3 首次运行聚合及 GMM 预测已完成，但边界代码误把 `Layer 5/Layer 6` 写成 `L5/L6` 导致失败；随后直接从保存的预测恢复指标并保留失败状态，不重训。其恢复指标 ARI=0.4696960562716283，NMI=0.5850783791093968，边界 TP/FP/FN=194/1708/756。

逐层结果：L4 下 L5/L6 为 0/145，L4/L5 约为 3/160；但是 L1/L2、L2/L3 在 L4 比 L3 回升。L0 高边界召回伴随大量同层错误分割；全局 F1 亦非单调。**仅可声称单切片探索性权衡，不可声称因果过度平滑、普遍规律或已验证创新。**

## 最新核查补记（2026-11-10）

用户已经提供两份历史 seed0 L4 原始 `manifest.json` 的完整终端内容；见 [GMM manifest 对照归档](experiments/cellcharter_dlpfc/GMM_L4_SEED0_MANIFEST_AUDIT_20261110.md)。来源聚合与 latent 的 SHA256 一致、显式 GMM 超参一致，但旧 manifest 缺少最终输入矩阵 SHA256，脚本 hash 不同，训练实际收敛迭代 24 vs 29，NLL 4.614036 vs 4.721235；此不一致原因仍未定位。**下一步只读比较实际脚本中的矩阵构造、随机种子调用与 GMM fit 位置，不重复已完成的 manifest 检查或训练。**

## 当前阻碍及下一步

1. **立即下一步只读审查历史 GMM 重拟合一致性：** 2026-11-09 两次 seed0、名义上同源 L4 输入和同名超参数的预测分区 ARI=0.713871，而不是 1，原因不明。用户最近已列示两次本地运行目录有 `manifest.json`、`predictions.csv`、`script_snapshot.py`、`gmm_weights.pt` 等。**还未收到新一轮完整 manifest JSON 输出**；不能声称已经核查完该对比。
2. 机制混杂：聚合深度同时改变 GMM 输入维度；旧固定25维置换将不使用的邻域特征行错配，并不等于仅改变传播深度。须先解决模型稳定性与同维控制，再提出候选边界感知模块。
3. 归档/复现：用户终端已展示逐层四位小数，但本地五档新审计原始 CSV、L3 predictions.csv 和失败状态尚未直接读取/上传，不能误当 GitHub 已有。审计代码是事后补写，不可称当时历史实验曾运行该文件。
4. 之后才是预先冻结对照的跨 seed、跨切片/独立供体测试，以及最近邻已有方法、机制创新、论文叙事等审查。151507已被频繁探索，不是独立盲测。

## 最新代码核查（2026-11-10）

用户已运行两份 `script_snapshot.py` 的关键字与上下文检查：旧 h4 在创建 AnnData 之后设 seed，固定25维 h4 在创建 AnnData 之前设 seed；均在 Cluster 构造前设 seed。尚无法断定该顺序影响随机数。旧 h4 从聚合特征取前25列，新 h4 在 hop4 无置换并返回 C-contiguous float32。**下一个唯一动作：只读计算两者的最终输入数组 SHA256，与新 h4 manifest 的哈希比较**。详情见 [历史 GMM 审计](experiments/cellcharter_dlpfc/GMM_L4_SEED0_MANIFEST_AUDIT_20261110.md)。

## 最新输入哈希复核（2026-11-10）

用户实际运行只读 SHA256 检查：共同来源 `aggregated.npz` 中 `X_cellcharter (4226,25) float32`，按旧脚本 `np.ascontiguousarray(..., dtype=np.float32)` 重建后得到 `f653234c166ce80b80e1971b387439779ebe92745087d742c5821beedf1c9463`，与新固定25维 h4 manifest 中的输入矩阵 hash **一致**。这是重建一致性证据，旧运行时最终输入 hash 未被原始日志独立记录。下一步只读检查 AnnData 建立前后 NumPy/Torch RNG 状态是否被消耗，再决定是否需最小训练重复性实验；不可直接声称非确定性已证实。详见 [GMM 审计](experiments/cellcharter_dlpfc/GMM_L4_SEED0_MANIFEST_AUDIT_20261110.md)。

## 最新 RNG 诊断（2026-11-10）

用户完成 AnnData 构造 RNG 状态检测：`old` 与 `fixed25` 均显示 `TORCH_RNG_CHANGED=False`、`NUMPY_RNG_CHANGED=False`。第一次助手给出的测试代码误用 `torch.Generator.get_rng_state()` 导致 `AttributeError`，后修正成功；未重新训练。说明所测模拟 AnnData 创建过程没有消耗 CPU Torch/NumPy 全局 RNG，**不等于 TorchGMM 内部随机性已排除**。下一步只读核查脚本中完整 `cc.tl.Cluster(...)` 构造及特征装载差异。详见 [审计追加记录](experiments/cellcharter_dlpfc/GMM_L4_SEED0_MANIFEST_AUDIT_20261110.md)。

## 最新完整 GMM 调用核查（2026-11-10）

用户回传旧 L4 和固定25维 L4 的脚本原始行号片段；两份 `cc.tl.Cluster` 的 n_clusters、random_state、covariance_type、init_strategy、convergence_tolerance、covariance_regularization、trainer_params 全部一致，且新 h4 的特征置换循环为空。当前尚未发现显式参数差异。**唯一下一步：只读审查两份脚本中的原始 barcode/feature 加载、顺序与此前 ARI 比对对齐口径；不先重复训练**。参见 [GMM 审计](experiments/cellcharter_dlpfc/GMM_L4_SEED0_MANIFEST_AUDIT_20261110.md)。

## 下一次新对话如何接手

先按顶部顺序读取三个记忆文件。若 `PROJECT_STATE.md` 与本文件不一致，以**最新可核实的原始证据**为准并报告冲突；不要从旧 README 中取代当前状态。读取任务相关的 `manifest.json`、脚本、日志与指标，再给用户一条 Windows 手动操作；目前不需重建环境、重跑 L3、L0–L4、跨深度边界审计。

每次归档都同步更新 `PROJECT_STATE.md`、本文件与当天 `RESEARCH_JOURNAL/YYYY-MM-DD.md`，区分已执行、转录日志、待验证假设和计划。
