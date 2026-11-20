# E5a成熟基线启动准备：环境结果、基线候选与公平性边界（2026-11-20）

> **状态：事前安装/协议设计，未运行任何E5a基线；以下方法是事前待冻结选择，不代表已经得到结果。** 按用户“阶段开始前审核，一旦开始连续完成，计划结束后Claude集中审核”的新约定执行。E4已12/12和36SVG/36CSV通过最终只读审计。

## Windows当前真实预检（用户PowerShell原样报告）
- Python 3.10.22；`leidenalg 0.12.0`、`igraph 1.0.0`，Scanpy、anndata、torch、scvi、cellcharter可导入；部分旧版distribution映射不出版本，不能臆造。
- PyTorch `2.1.2+cu121`；`torch.cuda.is_available()=True`；GPU `NVIDIA GeForce RTX 4070 Laptop GPU` 8.0GB。
- `banksy`, `GraphST`, `graphst`, `torch_geometric`, `rpy2` **尚未安装**，`Rscript` 未在PATH。不可认定BayesSpace当前可运行或E5a已完成。

## 基线预选及明确兼容性门槛
**主路径**：先把无空间`Leiden`、scVI 5D输入`GMM`作为廉价对照；空间成熟方法`BANKSY`与`SpaGCN`作为计划内强对照。目标4种基线（其中2项空间方法）；如果SpaGCN实际依赖无法兼容，则**事前预列GraphST/STAGATE作为空间替代**，不得悄悄将失败者从报告里抹去或只留下高分方法。GraphST官方文档当前要求旧Python 3.8和R/rpy2、且特别注明以Linux完整支持为主，因此在现有Windows+Python3.10无R环境下不能承诺可直接GPU运行。BayesSpace官方是R/Bioconductor包，当前R不可执行，属于本机阻断候选而非已完成基线。所有替代需在真正训练E5a之前**一次性冻结确定**，不得看到聚类ARI/NMI后换方法。
- BANKSY官方Python包`pybanksy==1.3.5`，支持Python3.10、`pip install pybanksy`；推荐依照原方法以scRNA/Visium raw counts/表达矩阵+空间坐标输入，native kernel/feature augmentation与Leiden聚类；不把其官方“R/mclust”可选部分误当依赖必需。安装于独立第三方`--target`目录，`--no-deps`以免修改任何已审计CellCharter环境；若缺依赖再依本机真实结果修复，不原地升级Torch/Scanpy/PyTorch。
- SpaGCN官方提供`pip install SpaGCN`但已发布教程多为Python3.7/3.8旧环境；选它是**候选兼容性尝试**，不能保证Python3.10+torch2.1.2直接兼容。如不行，在正式批量训练前替代并记录。
- GPU只用于方法确实支持且与官方实现兼容的独立基线训练，公平性不要求所有模型物理设备相同；必须记录设备/seed/budget。

## 正式E5a计划冻结前必须确定的比较共同条件
- **样本/数据**：同12张DLPFC切片；同份原始10x counts/坐标、完全相同barcode与有标签评价mask。仅逐片独立拟合，其他切片真值层不能参与K/超参数选择；历史12张DLPFC不是新独立验证数据。
- **可比性**：非空间Leiden/GMM共享已经预存的scVI 5D表示，比较CellCharter空间特征聚合的增益；空间方法BANKSY/SpaGCN遵守其**原生输入与预处理**，不是假装它们也共享同一scVI 5D；这意味着“相同原始数据/评价条件”可比而算法表示/资源并非严格相同，需要明确写出，必要时额外同输入敏感性小对照但不在已冻结批次中临时新增。
- **K协议两套独立**：Oracle-K={5/7}用参考类别数作为公开的外部K先验；不能称无监督选K；K-blind不读人工标签选K，候选K与随机性/预算在正式训练前冻结并保存每方法完整搜索轨迹。真实标签只用于预测后ARI/NMI评价、边界指标同mask。
- **seed**：明确是否每方法可重启训练及5–10个技术seed，随机多次不是生物重复；在预冻计划写清方法特定随机参数、early stopping、超参和失败处理。
- **报表**：每一方法12片全部结果、完整失败列表、同mask ARI/NMI/K、训练时间硬件+版本、种子方差、供体内切片/3名独立供体的描述统计；保留负结果，不挑最佳slice/seed/模型。
- **输出**：隔离`results/e5a_baselines_v1/`，原E1/E2/E3c/E3d/E4不可覆盖。

## 官方来源（事前查证）
- BANKSY Python: https://github.com/prabhakarlab/Banksy_py （`pyproject.toml`版本1.3.5、Python3.8–3.13、无R基本安装）
- SpaGCN Python: https://github.com/jianhuupenn/SpaGCN
- GraphST tutorial: https://github.com/JinmiaoChenLab/GraphST_Tutorials/blob/main/docs/source/Installation.rst （特别说明Linux、Py3.8与R背景）
- BayesSpace: https://bioconductor.org/packages/release/bioc/html/BayesSpace.html
- E5a正式原计划：`E3_E6_Q4_EMPIRICAL_RESEARCH_GATE_20261119.md`、`THIRD_PAPER_FULL_EXPERIMENT_EXPANSION_DECISION_20261112.md`。

## 唯一下一步
**先仅安装、导入测试官方Python BANKSY包`pybanksy==1.3.5`到一个新独立`third_party/e5a_banksy_libs`目录（`pip --target ... --no-deps`），不改原env，未训练、未改E1–E4。** 此后安装/验证另一个空间基线，再冻结完整批量参数与脚本并一口气执行E5a，阶段末统一审计；最终Claude在全部预定研究计划结束后审查。

## 补充：2026-11-20 用户证实BANKSY安装成功、提供R和Clash路径

> 以下为**用户真实Windows终端和两张截图**，发生在E5a正式基线实验训练之前，覆盖本文早先“Rscript未在PATH因此R可能不可用”的推断。具体Rscript.exe路径与BayesSpace是否安装仍**未独立验证**。

- BANKSY 通过`pip --no-deps --target D:\paper\CellCharter_reproduction\third_party\e5a_banksy_libs pybanksy==1.3.5`安装成功，用户实际`E5A_BANKSY_IMPORT_PASS version=1.3.5`、`E5A_TORCH_VERSION 2.1.2+cu121`、`E5A_CUDA_AVAILABLE True`、`E5A_BANKSY_SETUP_COMPLETE`。提示没有`rpy2`，明确警告只影响`mclust`、不妨碍默认`leiden`聚类；后续禁止错误称BANKSY失败或必须安装rpy2。
- **用户R路径截图**：`D:\R\R-4.5.1`目录真实存在，截图中未直接显示`Rscript.exe`文件，必须在Windows下一步检查`D:\R\R-4.5.1\bin\Rscript.exe`或`bin\x64\Rscript.exe`。此前`Get-Command Rscript`没找到只是PATH不可访问，不能推断R不存在。BayesSpace真实安装状态未知，不能声称已就绪。
- **Clash Verge截图**：Windows本地**混合代理端口7897**、系统代理`127.0.0.1:7897`；未来从R/Bioconductor、pip/GitHub下载安装依赖时可在**单次PowerShell进程/调用期间**显式设`HTTP_PROXY=http://127.0.0.1:7897`和`HTTPS_PROXY=http://127.0.0.1:7897`并恢复原环境，**不要永久改系统设置**。代理设置是连接配置，真实可用性必须以实际网络输出为准。
- 接下来仅一条Windows**只读验证Rscript路径、R自身版本、BayesSpace/BiocManager命名空间**的PowerShell指令；之后在正式冻结E5a前一次性决定使用哪些成熟空间基线，不因中途ARI/NMI换方法。

