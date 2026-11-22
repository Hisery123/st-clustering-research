# 毕业论文第三篇CellCharter章节：正文与来源对应（2026-11-22）

**当前首稿：** [chapter_04_results_rewrite_v1_20261122.tex](chapter_04_results_rewrite_v1_20261122.tex)。原 `chapter_04_results_integrated.tex` 是2026-11-12历史版本，**保留不覆盖**。首稿是可修改的完整实验结果章，不是全篇毕业论文已经完成，也未经过学校论文模板的全局LaTeX编译或导师审读。

## 写作路线（暂时不增加实验）

1. **已完成：第四章结果与分析v1**：按E1/E2→E3c→E3d→E3b→E5a→E5b组织真实数据，E4图件保留待核对插图位置。所有数值从下表真实归档读取。
2. **下一稿：方法章更新**：以已提交的`chapter_03_methods_integrated.tex`为基础，统一K-blind/Oracle-K、10/3/5技术种子区别、数据分割、原生BayesSpace选择K缺陷、无标签选择标签隔离、线图容差一对一匹配、独立生物单位。
3. **随后：背景/相关研究与讨论衔接**：利用`chapter_02_background_integrated.tex`，只保留可核实文献；不把CellCharter多层聚合或B15D等维替换冒充已证实的自创算法。
4. **最后：总论、摘要、结论、参考文献、学校格式、补充图表清单**，之后交Claude做独立逐项审稿，针对缺口修订。

## 第四章分节证据链

| 新稿小节 | 直接对应的GitHub来源 | 特别保留的限制 |
|---|---|---|
| 评价数据和指标 | E1/E2冻结协议、E3d/E3b评价代码、E5a/E5b冻结协议 | DLPFC n=3供体，外部n=6患者，标签mask，Oracle-K/K-blind独立 |
| 累计尺度和A/B特征 | [E1/E2完整120格分层](E1E2_20261119_RELEASE/derived/all_120_condition_stats.csv)、[12切片A/B差值](E1E2_20261119_RELEASE/derived/B_vs_A_12slices.csv) | 1200条件任务、10个seed不是独立n；A/B差异很小且存在负结果 |
| 固定K敏感性 | [E3c完整K×维度结果](E3C_20261120_RELEASE/e3c_macro_K_depth_20groups.csv) | K是预设网格；Oracle-K旧480格复用，不是新跑2400 |
| AutoK | [E3d无标签审计](E3D_20261122_RELEASE/derived/all_48_autok_audit.csv)、[事后48条ARI/NMI](E3D_POSTHOC_20261122_RELEASE/derived/all_48_posthoc_ari_nmi.csv) | 10/48达到K边界；后验评分，不更改选K规则 |
| 边界定位 | [E3b全1200配置的30行宏均值](E3B_E1E2_1200_POSTHOC_20261122_RELEASE/derived/macro_mean_30.csv)、[3600条完整边界指标](E3B_E1E2_1200_POSTHOC_20261122_RELEASE/derived/all_3600_boundary_metric_rows.csv) | E1/E2 Oracle-K与E3d K-blind分开；严格F1下降、容差F1上升；事后评价 |
| 四成熟基线 | [E5a方法和K模式8组汇总](E5A_20261122_RELEASE/derived/method_regime_descriptives.csv)、[全部288项](E5A_20261122_RELEASE/derived/all_288_prediction_checks.csv) | BayesSpace K-blind q10上限28/36；各方法原生数据不完全一致 |
| 六患者外部验证 | [E5b患者120组汇总](E5B_20261122_RELEASE/derived/patient_three_seed_summary.csv)、[144条患者配对](E5B_20261122_RELEASE/derived/patient_paired_effects.csv)、[全部360项](E5B_20261122_RELEASE/derived/all_360_prediction_metrics.csv) | A15D对BayesSpace NMI宏均值负向，3/6患者A15D ARI低于0.05，Kblind q10上界18/18 |
| E4空间示例 | [E4审计](E4_FINAL_AUDIT_PASS_20261120.md)、[E4生成脚本](e4_spatial_visualization_batch_v1.py) | 未在GitHub逐图核对原12切片SVG，不编造图中形态/marker机制 |

## 数值和论证检查点

- E1/E2 5/10/15/20/25D Oracle-K ARI: `0.3051/0.4081/0.4299/0.4383/0.4418`，NMI `0.4133/0.5422/0.5780/0.5891/0.5982`。先平均每片10 seed，再平均12切片。
- E3d K-blind 10/15/20/25D ARI: `0.3793/0.3861/0.4311/0.3890`，边界次数 `4/2/1/3`；均值12切片，生物学n=3。
- E3b全量Oracle-K严格边界F1: `0.1441/0.1446/0.1361/0.1344/0.1179`；2-hop: `0.2863/0.4116/0.4838/0.5223/0.5333`，不写成平滑机制因果证明。
- E5a成熟基线K-blind/Oracle-K ARI: GMM `0.2563/0.3101`、Leiden `0.1702/0.3265`、BANKSY `0.2614/0.2974`、BayesSpace `0.3442/0.4225`。
- E5b六患者A15D K-blind ARI `0.2004` NMI `0.2831`；相较L0 ARI `+0.0458` NMI `+0.0583`，两指标均6/6正向；相较BayesSpace ARI差`+0.0404`只有4/6正向、NMI差`-0.0139`，不能断言完全优越。外部患者CID4290 ARI为`0.04114`，所以严格说是**3/6患者ARI低于0.05**，不是3/6低于0.04。
- 不报告从n=3供体得到的独立切片显著性，不把后验bootstrap称为预注册，不把外部6例当临床验证。

## 拟插的真实图（不得用生成式示意图顶替）

- E1/E2：`E1E2_20261119_RELEASE/derived/B_vs_A_ARI_12slices.svg`、`B_vs_A_donor_ARI.svg`。
- E3c：`E3C_20261120_RELEASE/e3c_Fig1_K_depth_macro_ARI_NMI.svg`、`e3c_Fig3_scale_effect_slice_K_heatmap.svg`。
- E3d：优先从48条原指标新作可编辑尺度-ARI/NMI描述图，不再未经确认插旧E4图件。
- E3b：`E3B_E1E2_1200_POSTHOC_20261122_RELEASE/derived/E3B_E1E2_1200_all_config_0_1_2hop.svg`，注意主文0-hop，容差为敏感性。
- E5b：`E5B_20261122_RELEASE/derived/E5b_Kblind_PatientPaired_ARI.svg`与`E5b_Kblind_PatientPaired_NMI.svg`。
- E4：用户Windows端真实SVG完成逐张验收之后才能插。

## 待人工确认（不阻碍开始写作）

- 正式学位论文全文题目、学校模板章节层级和整篇论文其他两项工作的衔接，需要以用户/导师的最新版要求确定。
- 原DLPFC供体映射目前是公开附录推定，需要再次与源metadata交叉核对；不因n=3而虚构具体供体身份。
- CellCharter原论文与Supplement的逐项重叠/引用应在最终定稿前核实，当前不以“新算法”作为研究贡献。
- LaTeX正文需在目标学校主模板环境中编译，图路径根据实际文件布局调整；此前未做全论文编译验证。
