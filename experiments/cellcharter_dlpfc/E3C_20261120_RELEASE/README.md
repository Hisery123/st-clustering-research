# CellCharter DLPFC E3c — 2026-11-20 data-and-figures release

研究范围：仅第三篇CellCharter DLPFC实验，**E3c固定K敏感性**。真实实验已经在用户Windows上完成2400格全网格只读审计（旧Oracle-K复用480格，新K拟合1920格）：`E3C_GRID_PREFLIGHT_PASS total=2400 REUSED_AUDITED=480 EXISTING_AUDITED=1920 NEW_TASK=0`。

## 实际公开的文件与证据等级

- **用户上传的真实原始指标（非完整预测）**：`e3c_newK_metrics_1920.csv`，1920行，原始SHA256 `50c624a9133d0ad885cd69d53929047f6398729699498771b20c86537bff92f2`。已对上传和GitHub文件验证Git blob SHA完全相同。
- **从新1920行和旧480 Oracle-K归档计算的描述性CSV**：
  - `e3c_slice_K_depth_240groups.csv`、`e3c_macro_K_depth_20groups.csv`、`e3c_donor_K_depth_60groups.csv`
  - `e3c_paired_scale_differences_300.csv`、`e3c_posthoc_oracle_comparison_48.csv`
  - `e3c_oracle_48group_archived_mean_sd.csv`
- **实际统计图**：`e3c_Fig1_K_depth_macro_ARI_NMI.svg`、`e3c_Fig2_depth_increment_effects.svg`、`e3c_Fig3_scale_effect_slice_K_heatmap.svg`，可编辑SVG、从真实指标生成。
- **复现代码**：`build_e3c_review.py`和`e3c_oracle_summary_packed.txt`、`e3c_oracle_sha_prefix_reference.txt`，均与2026-11-20原打包分析版本的Git blob字节一致；旧480行完整逐任务原记录来自相邻的[E1/E2 release](../E1E2_20261119_RELEASE/derived/all_1200_tasks.csv)（不能用打包后的6位精度摘要冒充480行原始记录）。
- **方法和限制**：`E3c_分析说明_20261120.md`。此前聊天里的15文件ZIP包还包含`e3c_summary_audit.txt`文本汇总，**ZIP二进制及该文本尚未在本目录发布**，本README不宣称发布了整份原ZIP。

### 在另一个Python环境重算

将同目录全部文件放在可写目录中，安装`numpy`、`matplotlib`（使用独立分析环境，**无需重新拟合**）：

```powershell
python build_e3c_review.py
```

脚本会检查原始上传CSV的SHA256、索引键与旧Oracle-K派生参照，然后计算描述性CSV、生成SVG和离线ZIP。该脚本使用相同的48组6位数值摘要；精确完整的2400行任务合并需要另外直接读取E1/E2旧480条原行，不能由6位摘要逆向还原。

## 严格局限

12切片来自3位供体；10seed不代表10个生物学重复。K网格不是无标签选K（E3d尚未完成）；旧Oracle-K由人工层标签类别数确定；未使用真实人工标签参与每次GMM拟合不等于Oracle-K不知情。增加hop同时增加维数，不能仅凭ARI均值作因果解释。151507本地误放的metadata.tsv问题不能仅凭本次输出合法性判定已经彻底解决。未经再次收集，不要声称GitHub已备份Windows全部1920份原始逐spot预测CSV、session日志、manifest或模型权重。

详情：[E3c审查说明](../E3C_K_SENSITIVITY_ANALYSIS_20261120.md)。
