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
