# E5a成熟基线正式冻结协议 v1（2026-11-20，在首次E5a拟合前）

**状态：事前冻结计划，未取得任何E5a实际拟合结果。** 依据用户要求，按固定计划先执行，完成后汇总，交Claude做科研方法学总审。原E1/E2、E3c、E3d、E4均保留不覆盖；禁止观察结果后替换方法、挑有利种子/切片。用户Windows已真实完成Leiden/Scanpy/GMM、BANKSY1.3.5与BayesSpace1.20.2的**接口导入检查**，但正式数据运行尚未发生。脚本失败只按预先规定最小修复，不暗改预算或算法。

## 一、比较对象与同源性

- DLPFC原12切片：151507、151508、151509、151510、151669、151670、151671、151672、151673、151674、151675、151676；12切片嵌套于**3独立供体**，绝不将切片/spot/随机种子冒充生物重复。
- 基线固定4种，不加SpaGCN、GraphST、STAGATE作为本阶段新分支：
  1. **非空间GMM**：同一冻结scVI5D特征（从既存25D缓存取L0前5维），scikit-learn full covariance GaussianMixture，与CellCharter torchGMM为**不同实现**。比较表示与空间信息贡献，不把这个GMM当作与CellCharter完全相同求解器。
  2. **非空间Leiden**：同上scVI5D，经15NN Scanpy近邻图，Leiden原生`leidenalg`。
  3. **BANKSY 1.3.5**：10x原始counts、pxl spot coordinates（原样实际坐标比），独立预处理并使用`initialize_banksy`+原生邻域特征构造、Leiden聚类；固定`num_neighbours=15`、`max_m=1`、`lambda=0.2`、20PC；即方法自带数据表示与邻域模型，非同5D输入。
  4. **BayesSpace 1.20.2**：同一份原10x计数和Visium`array_row/array_col`，R SingleCellExperiment，`spatialPreprocess(platform="Visium",n.PCs=15,n.HVGs=2000,log.normalize=TRUE)`，`spatialCluster(q=...,d=15,platform="Visium",nrep=10000,burn.in=1000,init.method="mclust",model="t",save.chain=FALSE)`；BayesSpace本身属于CPU型R实现，不强行迁到GPU。**完整运行是否可行仍依用户Windows首批真实反馈，不假定已经训练成功**。
- **公平边界**：四方法使用同一切片、同一spot子集、同一人工层评价mask；不强迫原生空间方法共享5D特征，因为这改变算法定义；跨方法输入表示和计算开销不等价，报告原生基线+轻量同表示基线。CellCharter主比较固定A15D（`cum_L0_L1_L2`），B15D作为已完成补充，不得用现阶段新方法反向优化CellCharter。
- 原始RNA counts由`D:\paper\ST_Benchmark_Planning\mvp\data\<sample>\filtered_feature_bc_matrix.h5`只读，坐标来自同目录`spots_aligned.csv`，人工标签`manual_layer_annotations.csv`；既存25D特征从`D:\paper\CellCharter_reproduction\results\cellcharter*\cellcharter_aggregated.npy`与相应spot订单CSV，经**条码精确对齐**。数据缺损/条码错配是硬停止，禁止基于位置盲拼。
- 初期可视化展示不参与算法超参，参考标签仅用于事后ARI/NMI与参考层×聚类交叉表。标签类别总数Oracle-K：151669–151672=5，其余8张=7，属于已披露的**标签类别数知情**对照；K-blind全程不读`manual_layer_annotations.csv`进行任何训练、参数或K选择。

## 二、两个K策略（严格分表报告）

| 基线 | Oracle-K（使用参考层数的受监督外部K先验） | K-blind（不使用人工层标签） |
|---|---|---|
| GMM | 固定`n_components=5/7`；full covariance, tol 0.001, reg_covar1e-6, max_iter100, n_init1 | 预先候选K=2..10，按最小sklearn BIC选择，分数与各K结果全部保存；相同其余参数 |
| Leiden | 固定近邻图15NN；按固定分辨率表搜索最接近目标K，出现并列选更小resolution；**若未恰得目标K，真实报告差距，不是假装等于Oracle-K** | 固定res=1.0的无标签预定参数，不读取人工层标签或人工选K |
| BANKSY | 固定lambda0.2、15个空间邻居、20PC；按固定Leiden resolution表选与目标K绝对差最小项；不根据ARI选 | 固定Leiden res=1.0，不读人工层标签；两臂共享原生BANKSY变换 |
| BayesSpace | 固定q=5或7；每个随机seed独立运行10000次MCMC | `qTune(qs=2:10,burn.in=100,nrep=1000)`，**事前确定最小平均负对数似然对应q（即最大平均q.logliks）并列取更小q**，保存全部曲线；随后q固定10000次正式MCMC；官方vignette常建议人工看elbow，本方案明确使用一种预定自动判据，**不宣称该自动判据就是作者推荐的默认** |

- 预定固定resolution表（Leiden和BANKSY共用）：`[0.1,0.15,0.2,0.25,0.3,0.4,0.5,0.65,0.8,1.0,1.25,1.5,2.0,2.5,3.0,4.0]`。Oracle-K每种子在全部表内搜索，选`abs(actual_K-Oracle_K)`最小，平局选更低resolution；K-blind只用res1.0不作后验调参。
- 固定技术seed **22911、7449、25842**（与历史E1/E2前3个seed匹配）。同方法、切片、K臂每seed完整保存原始预测（每方法12×2×3=72份；四方法共288拟议正式预测任务），超参搜索轨迹单列、计算预算/设备记录。3个seed是**技术重复**，与E1/E2以前10seed的完整分布不可误称同预算；若比较CellCharter随机波动，取E1/E2前3seed作为配对敏感性，其他7seed历史结果完整保留另行报告。
- GMM和Leiden使用现有Windows Python venv；BANKSY隔离`third_party/e5a_banksy_libs`，必要时环境变量仅本进程；BayesSpace采用R4.5.1 `D:\R\R-4.5.1\bin\Rscript.exe`且通过`.libPaths`优先`third_party/e5a_r_libs`。当前GPU RTX4070 8GB、CUDA可用，但**不把CPU sklearn/Leiden/BANKSY默认CPU强行宣称为GPU**；BayesSpace仅CPU。记录真实运行时间和依赖版本，不预先捏造GPU加速。
- E5a结果最低限度：12片×4法×2 K臂×3 seed原始文件、全样本失败记录、ARI/NMI仅在保存预测后使用同一人工层mask、真实K与Oracle目标差、K盲决策全轨迹（无监督）、各原始文件SHA256、每片spot顺序、算法版本、运行耗时；汇总以3名供体为独立单位做描述性统计，不凭72预测/种子冒充显著性。
- 计算顺序固定：**第一子批非空间GMM+Leiden → 第二子批BANKSY → 第三子批BayesSpace**。这是E5a**统一冻结计划内的三次批处理**，不是看到中间ARI后添加/删减方法。每子批完整12片×2臂×3seed自动连续运行，等全E5a结束再汇总与Claude论文方法审查。若训练脚本或真实算法API出现阻断性故障，保留失败日志、仅修复执行错误且不更改设计规则；不得因结果差而换方法/改超参。

## 三、API依据与注意事项
- 用户Windows2026-11-20真实`E5A_PY_API_PASS`,`E5A_R_API_PASS`,`E5A_METHOD_INTERFACE_CHECK_COMPLETE`，已核对函数signature，但**不是完整算法运行证明**。
- 官方BANKSY Python README： https://github.com/prabhakarlab/Banksy_py ; default Leiden不要求rpy2，后者仅mclust可选；原作者Python函数的annotation_key默认非空，会在有标签输入时计算ARI，**正式实验必须将annotation_key=None、match_labels=False，严防训练时引用真值**。
- BayesSpace3.22 vignette： https://bioconductor.posit.co/packages/3.22/bioc/vignettes/BayesSpace/inst/doc/BayesSpace.html ，推荐正式MCMC至少10000次、`qTune`展示pseudo-log-likelihood vs q，`qTune`输出`attr(sce,"q.logliks")`。
- `E3_E6_Q4_EMPIRICAL_RESEARCH_GATE_20261119.md`与用户`EXECUTION_FIRST_CLAUDE_FINAL_REVIEW_DECISION_20261120.md`是本阶段顺序和审查纪律依据。

## 四、本阶段不可交付或承诺
- **E5a尚未训练**；不能因安装/接口PASS宣称基线已经达到可发表效果。
- 这不是无偏“独立新数据测试”，DLPFC 12片已有历史探索；独立外部验证在E5b单独冻结。
- 不因本阶段方法K-blind选K值（含边界K）而重设已有E3d冻结K2..10，也不把E3d5次AutoK重复和E5a3seed种子当成同一配对重复。
- 论文方法贡献/创新性、增益与显著性要等真实结果和最终Claude审稿。

## 五、BANKSY子批事前实现参数补充（子批首个拟合前冻结）

第一子批非空间GMM+Leiden的144/144拟合已由用户Windows真实完成，`E5A_NONSPATIAL_FINAL status=completed completed=144/144 failed=0`、`E5A_NONSPATIAL_EXIT_CODE=0`，批次`D:\paper\CellCharter_reproduction\results\e5a_baselines_v1\nonspatial_20261120T095303Z_15120\batch_status.json`。末尾Leiden固定无标签resolution=1.0实际K=17：**不是错误，不得后验改分辨率。** 任务文件目前仅Windows保存，未做全E5a阶段末审计。

BANKSY尚未开始运行；经查官方BANKSY Python `src/banksy/`代码（https://github.com/prabhakarlab/Banksy_py）进一步事前固定：
1. 独立使用10x`filtered_feature_bc_matrix.h5`的真实raw counts，按`barcode`匹配所有spots，`scanpy.pp.normalize_total(target_sum=10000)`→`log1p`→`scanpy.pp.highly_variable_genes(flavor="seurat",n_top_genes=2000)`，不因marker位置/人工层改变HVG；所有源spot保留，使用相同像素坐标`(pxl_col_in_fullres,pxl_row_in_fullres)`。
2. `initialize_banksy(num_neighbours=15,nbr_weight_decay="scaled_gaussian",max_m=1)`，关闭仅QC用途的绘图；`generate_banksy_matrix(lambda_list=[0.2],max_m=1,variance_balance=False)`→`pca_umap(pca_dims=[20],add_umap=False,plt_remaining_var=False)`，再`run_Leiden_partition(num_nn=50,match_labels=False,annotations=None, max_labels=None, partition_seed=<fixed seed>)`直接生成Leiden原生结果，替代默认`run_banksy_multiparam`额外逐参数自动绘制PNG散点的**包装层**；空间加权、PCA、Leiden均使用同一个BANKSY官方Python包核心函数，算法没改，节省数百张重复无用临时图。禁止调用`match_labels=True`或加载参考层作为annotation。
3. 预冻Leiden resolution grid 16个候选；每个切片×seed只生成一次16候选，Oracle-K臂按聚类个数距离K5/7最小并列取更低resolution；Kblind仅选固定1.0，一律不看ARI/NMI选择。共享相同候选分区是**同计算预算透明复用**，两个臂不构成彼此独立重复；每个seed输出候选K全轨迹及预测结果两套，各自参考层指标只在保存预测之后计算。
4. PCA表示阶段固定`np.random.seed(22911)`用于基线可复现特征生成，与Leiden聚类的三技术seed22911/7449/25842区分。实际CPU/GPU、库版本、矩阵输入SHA、候选K和最终K以及执行耗时全部保存；默认BANKSY的Leiden/矩阵构造是CPU，不强行宣称使用GPU。12×3×2=72份输出，输出隔离`results/e5a_baselines_v1/banksy_<UTC>_<PID>`。
5. 上述补充在BANKSY首次运行前确定，不更改已运行的第一子批结果及最初四基线/K/seed/空间邻域设计。

## 六、BayesSpace子批前冻结执行补充（2026-11-20）

- 用户Windows真实报告`E5A_BANKSY_FINAL status=completed completed=72/72 failed=0 summary=D:\paper\CellCharter_reproduction\results\e5a_baselines_v1\banksy_20261120T101256Z_26540\batch_status.json`以及`E5A_BANKSY_EXIT_CODE=0`。BANKSY非全部K准确命中Oracle的单项是已冻结16项resolution网格允许结果，不能据此改协议。E5a已真实做完第一非空间144+第二BANKSY72=216/288项，剩余第三BayesSpace72项；未做全阶段独立审计。
- BayesSpace第三子批R脚本在**首次BayesSpace正式拟合前**冻结于`experiments/cellcharter_dlpfc/e5a_bayesspace_baselines_batch_v1.R`。软件R4.5.1、BayesSpace1.20.2、Bioconductor3.22，读取真实`filtered_feature_bc_matrix.h5` CSC原计数、以`barcode`对齐真实`spots_aligned.csv`。使用`array_row,array_col` Visium六角网格坐标而不是像素；官方`spatialPreprocess(platform='Visium',n.PCs=15,n.HVGs=2000,log.normalize=TRUE)`；固定PCA前`set.seed(22911)`，可复现。每个切片×3 seed=36个无标签`qTune(qs=2:10,burn.in=100,nrep=1000,cores=1)`，**最大`attr(sce,'q.logliks')$loglik`，并列选最小q**，独立保存全K曲线。Oracle-K固定参考类别数5或7；两臂均`spatialCluster(platform='Visium',q=选定K,d=15,init.method='mclust',model='t',precision='equal',nrep=10000,burn.in=1000,thin=100,save.chain=FALSE)`，两臂全部`predictions.csv`先落盘，后才读取参考层计算同mask ARI（R mclust调整Rand）及NMI（与sklearn arithmetic mean entropy相同的公式）。原始各输入和预测SHA256与决策轨迹写入JSON，**本实现纯CPU**。从未在标签上拟合或根据ARI挑K；12片×3seed×2臂=72份预测，存放在独立`results/e5a_baselines_v1/bayesspace_<UTC>_<PID>`。qTune候选K全部保留。
- **运行前真实性边界**：仅官方当前函数签名在用户R中预检通过；GitHub R脚本未在Windows完整执行、此环境无Rscript静态运行器；如真实算法API/本机HDF5发生阻断，请停止并保持原会话文件，不重复启动或修改先前完成两子批、仅修复程序问题而非方法规则。按既定顺序先完成第三子批，再统一E5a全量文件验收，最终Claude审稿于计划末。
- 来源：BayesSpace3.22 vignette https://bioconductor.posit.co/packages/3.22/bioc/vignettes/BayesSpace/inst/doc/BayesSpace.html 说明Visium的array_row/array_col、qTune返回q.logliks和建议正式至少1万MCMC迭代；实际版本R API已由用户真实反馈。

## 七、BayesSpace首次运行0/72阻断的最小代码修复（2026-11-20）

**真实Windows失败日志：** 原v1脚本SHA与GitHub匹配，`E5A_BAYESSPACE_SAMPLE_START sample=151507 expected=6`后立即`E5A_BAYESSPACE_HALTED completed=0/72 error=类别为"dgCMatrix"的对象无效: 'i' slot is not increasing within columns`，exit2，保留只读输入与原失败会话`D:/paper/CellCharter_reproduction/results/e5a_baselines_v1/bayesspace_20261120T102925Z_30592/batch_status.json`。本错误发生于**拟合前的10x CSC稀疏矩阵导入**，没有任何BayesSpace拟合/选择K结果可用；不应误判BayesSpace算法失败或数据损坏。

**根因：** 十倍空间H5的CSC`indices`每列未必按升序排列，而R `Matrix::dgCMatrix` S4对象构造时要求每列内行索引严格递增。原脚本直接通过`methods::new("dgCMatrix", i=ind,p=ptr,x=val,Dim=dims)`，未规范排序。**修复仅限读取层**：新文件`experiments/cellcharter_dlpfc/e5a_bayesspace_baselines_batch_v1_1.R`利用CSC`indptr`向量恢复列序列，采用`Matrix::sparseMatrix(i=ind+1L,j=rep.int(seq_len(dims[2]),diff(ptr)),x=val,dims=dims,index1=TRUE,giveCsparse=TRUE)`，R Matrix据此按列规范排序（若极少数重复坐标则求和）；加强指针与行索引合法性断言。**未更改**10x源文件、barcode对齐、HVG/PCA、seed表、qTune K2..10判据、正式1万次MCMC、双臂、输出策略或评价mask。原v1保留原样，新v1.1新文件；SHA256=`fed1f66c87a186104c60727d1bd27791a6dd9d389096b06305aac40fc97ccfbe`。尚未在用户Windows运行修复版；GitHub新文件已提交，不能称修复成功。依已冻阶段执行纪律只解决硬阻断，不中途审查分数。

**下一Windows唯一任务**：下载v1.1新文件、核SHA并执行`Rscript.exe --vanilla ...v1_1.R --run`。新会话必须与失败的0/72老目录隔离。若再阻断，原样报告末尾错误与会话路径；绝不盲目重启或修改方法学协议。

## 八、阶段末独立只读验收方案（2026-11-21，288项训练完成后）

当前三子批Windows真实日志均为PASS：nonspatial 144/144 `20261120T095303Z_15120`、BANKSY72/72 `20261120T101256Z_26540`、BayesSpace v1.1 72/72 `20261120T103557Z_11440`，无失败任务。**成功日志不是审计**，必须对真实产物进行统一复查。

已经在GitHub提交只读审计脚本`experiments/cellcharter_dlpfc/e5a_phase_audit_v1.py`，SHA256=`715922fc8a7ffe4757176396ef5e5d5e22330182e7e06db187b4d6778eb80278`，Git blob=`0b2fbaf5caa9c47aa5bc2faf61901c9ff5baf99d`。使用原Windows Python环境，明确三历史会话目录及版本SHA，无模型训练、不执行环境安装、不覆盖任何原任务。冻结审计：
- 三批`batch_status.json`全部状态completed且144/72/72，实物CSV数量144/72/72，任务4法×12片×双K×3seed精确288种唯一组合，任务元数据一致。
- 逐项读取`manifest.json`、`predictions.csv`，按对应SHA256与原始源文件复核，要求文件行数、barcode顺序、标签非空与固定`spots_aligned.csv`一一对应；12片相同人工标注mask（label count）与Oracle-K先验，按原raw标签重算全部288个ARI/NMI并和原记录数值对照（容差1e-7）；BIC K2..10最小值，Leiden固定16候选分辨率或盲1.0，BANKSY官方16候选原始标签NPZ和双臂选定分区一致，BayesSpace每种子qTune2..10曲线和K最大平均伪对数似然+小K并列规则；原批脚本在用户Windows本机的SHA固定且未改变。
- 非空间批原25D文件和spot订单SHA；BANKSY/BayesSpace raw10x及坐标各自SHA、且两者同一原始H5/坐标；BANKSY20D嵌入SHA、BayesSpace全九K轨迹SHA。阶段末脚本只向独立`results/e5a_phase_audit_v1/audit_<UTC>_<PID>/`写审计JSON与3张可复算CSV，**不把观察到的分数用于重新调参**。
- BayesSpace Kblind有K10边界的任务数，仅作事先列出的限制提示（不得事后扩K）；不把3seed当独立供体、不把原生空间方法与非空间5D方法宣称相同特征输入。除审计确认的结果外不虚构数值/性能优势。
- 若首次运行审计代码因方法输出版本差异或脚本自身错误停在`status=failed`，保留全部失败轨迹，仅审计工具最小代码修复**不重新训练任何方法**。只有用户Windows真实看到`E5A_PHASE_AUDIT_FINAL status=passed verified=288/288 errors=0`和退出0才标记阶段通过；之后进入E5b方案冻结。

