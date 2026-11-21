# E5b独立外部数据集：事前来源核查（2026-11-21）

**状态：候选来源核查/预检计划；尚未冻结正式测试样本、未下载用户Windows文件、未训练E5b任何方法。** 不应因为本文出现“候选”就暗示用户已做实验。

## E5a上游关卡

用户Windows2026-11-21成功返回`E5A_PHASE_AUDIT_FINAL status=passed verified=288/288 errors=0`、`E5A_PHASE_AUDIT_EXIT_CODE=0`；完整本地审计JSON在`D:\paper\CellCharter_reproduction\results\e5a_phase_audit_v1\audit_20261121T035302Z_5292\e5a_phase_audit_report.json`。归档`E5A_FINAL_AUDIT_PASS_20261121.md`。只有E5a完整性已验收，不推断CellCharter效能优越。

## 优先候选：Wu et al. 2021 人乳腺癌6个Visium样本

- **论文**：Wu S.Z. et al., *A single-cell and spatially resolved atlas of human breast cancers*, *Nature Genetics* 2021, DOI `10.1038/s41588-021-00911-1`；论文开放全文 https://pmc.ncbi.nlm.nih.gov/articles/PMC9044823/ 。作者方法明确：“Spots were annotated by a specialist breast pathologist using the Loupe (v4.0.0) software (10X Genomics).” 对外部区域标注来源的可靠性优于仅有算法预测类别的标签。
- **原始公开资料归档**：https://zenodo.org/records/4739739 ，DOI `10.5281/zenodo.4739739`，Garvan Institute of Medical Research作者/资料上传单位，2021公开。Zenodo说明：6例独立原发乳腺癌Visium样本；`metadata.tar.gz` 包含tissue/spot临床亚型、逐spot病理标注；`filtered_count_matrices.tar.gz` 是过滤计数矩阵；`spatial.tar.gz` 包括位置、缩放因子和图像。文件页显示：metadata 217.5 kB（md5 `1d0b34ead70635c094ac74ac58a88d68`）；filtered counts 155.7 MB（md5 `ea1220f0606c4d4e9307468fb2d5427a`）；spatial 54.3 MB（md5 `29b02ae433d459d19dc52b75a529e8e9`）。正式许可证类型/复用条款需按Zenodo Rights细节在后续确认，不得先宣称CC-BY。
- **为什么适合考虑**：与原开发/评价DLPFC脑12切片是不同组织、患者/研究来源，并有公开真实病理空间区域标注；Visium平台相同，避免把测序平台/细胞分辨率差异与泛化效应混在一起；可考察DLPFC选尺度/选K/种子稳定性是否可迁移，不能预期同一最佳尺度或K。多个乳腺癌样本可能支持跨患者的定性重现；究竟采用1片、2片还是全部6片必须在查看文件结构/缺失率/样本独立性及预算后，**不基于模型分数事后挑选**。
- **E5b下一唯一准备步骤**：Windows手动只下载`metadata.tar.gz`小文件（约217.5kB），先核对作者给出的MD5，再只读列出tar内容，不下载大计数与图像，不查看任何新模型效能；输出 archive entry list 供后续选择sample、标签字段和匿名患者重复关系。预期要确认每个spot一个可用独立标签且能与counts/barcode和空间坐标精准对齐；不满足即记录原因再挑其他公开数据。
- **备选不等价**：10x Genomics human breast cancer Block A Section 1 的`SEDR_analyses/data/BRCA1/metadata.tsv` https://github.com/JinmiaoChenLab/SEDR_analyses/blob/master/data/BRCA1/metadata.tsv 。GitHub原表已实查：**3798 barcode，0重复/空值，4粗粒度`annot_type`类、20细粒度`fine_annot_type`类**；研究论文有的称此标注部分由病理学家基于H&E与marker共同制作、有的称silver reference，标签来源/人工证据等级有分歧。不得未经进一步源头审查将其等同Wu et al.专业病理医师逐spot标签，更不能把两套BRCA数据混为同一病人。

## 正式E5b执行前必须冻结

1. **选择偏差/独立性**：确认该六例数据此前未在本项目scVI/CellCharter/基线调参使用，并且原始CellCharter paper是否对该数据已有benchmark；若已用仅能明确称“本研究开发阶段独立于DLPFC”，不能夸口“方法发表后首次外部验证”。
2. **标签与指标**：指定spot barcode、有效标签、含糊/不确定label的处理（事前规则），K-blind绝不读病理标签确定K；Oracle-K仅用真实类别总数作为外部知情上界。跨组织的病理区域和脑皮层分层**语义不一致**，只比较同一外部数据中算法与对照性能，不以跨组织ARI绝对差证明泛化。
3. **算法与算力**：先选数据与方法集再冻结；CellCharter表示缓存不可偷用DLPFC模型，必须重新根据原始外部数据走同等预处理/表达表示训练与空间邻域聚合；对照保持既定原生定义。BayesSpace若保留全qTune+正式10k MCMC，需以E5a首片约2405s的真实时间评估预算；一切改少seed/K/样本的决定**在首次外部拟合前**公开写清、避免与E5a混为严格同计算预算/同重复。
4. **文献和科研伦理**：归档原DOI、公开许可、文件checksum、下载时间、匿名样本、标签来源及作者使用声明，报告所有选样及负结果。术语E5b为“external dataset validation”，不是临床外部诊断验证，也不是独立样本泛化的因果证明。
5. **流程纪律**：只做必要预冻核查→连续执行所冻结E5b任务→末尾一次审计→若符合GO条件考虑E6→整阶段交Claude做方法/SCI论文总审；中途不得因ARI/K值多加实验。

## Windows首次公开元数据归档完整性检验（2026-11-21）

**来自用户当次Windows终端原始记录，已执行**：
```text
E5B_METADATA_INTEGRITY_PASS md5=1d0b34ead70635c094ac74ac58a88d68
metadata/
metadata/1142243F_metadata.csv
metadata/1160920F_metadata.csv
metadata/CID4290_metadata.csv
metadata/CID4465_metadata.csv
metadata/CID44971_metadata.csv
metadata/CID4535_metadata.csv
E5B_METADATA_ARCHIVE_LIST_PASS
```
这说明公开的metadata.tar.gz包哈希与预检记录一致，归档目录中有六份不同名字的样本CSV。**不能仅凭文件名或压缩包目录断言每个CSV具备可靠病理标签、barcode唯一性、坐标一一对应或6个患者独立**，更不代表已经开始E5b训练。下一步用Python标准库对tar.gz内六个CSV做只读列名/样本行数/字段缺失率/潜在标签类别计数，保留明细并先判断方法学有效性；不提取至原始数据目录、不看任何算法表现、不调参。按E5b预冻纪律在了解元数据与表达矩阵真实结构后再锁定样本与预算。

## 第二次Windows只读CSV结构检查真实通过（2026-11-21）

用户Windows终端完整回报`E5B_METADATA_STRUCTURE_PASS files=6`、`NO_TRAINING_NO_EXTRACTION`，压缩包内六个CSV的行数与列名实查如下（**不是训练结果**）：

| CSV | 元数据CSV行数 | 实际列名 |
|---|---:|---|
| 1142243F_metadata.csv | 4784 | 空标题索引列、nCount_RNA、nFeature_RNA、patientid、subtype、Classification |
| 1160920F_metadata.csv | 4895 | 同字段 |
| CID4290_metadata.csv | 2432 | 空标题索引列、nCount_RNA、nFeature_RNA、subtype、patientid、Classification |
| CID4465_metadata.csv | 1211 | 同字段 |
| CID44971_metadata.csv | 1162 | 同字段 |
| CID4535_metadata.csv | 1127 | 同字段 |

合计`15611`行原始元数据（仅原始行数，尚不能称有效标注spot数）。此前字段自动筛选仅匹配`subtype`，逐文件`subtype`均非空但只1个唯一值，是样本属性，**不能将其当空间域真值**；本次脚本遗漏了未含关键词的`Classification`列。最左列CSV表头为空，**推测**可能承载barcode但尚未验证。下一次只读核查应枚举6文件`Classification`的类别频数和缺失占比、最左列非空/重复情况、`patientid`一致性/跨文件独立性线索、核对样本级`subtype`。注意未核实`Classification`是否确为病理学家原始区域标签、是否包含unknown或排除类别，不能在实验前凭预测分数筛标签或样本。此后需下载原始count/spatial对应条码/坐标并核验；目前E5b无模型训练，样本与实验预算未冻结。

## 第三次Windows只读Classification与患者ID检查真实通过（2026-11-21）

**用户Windows实测终端（非训练）**：`E5B_CLASSIFICATION_PREFLIGHT_PASS files=6`、`NO_TRAINING_NO_DATA_MODIFICATION`；六CSV最左索引列非空且每份内无重复；每CSV `patientid`各1唯一值，跨六CSV共6种不同ID，0个跨CSV共享。注意ID互异是元数据内部的患者独立性支持，**不等价于我们已经核实了临床真实独立受试者身份或技术重复关系**。`Classification`确实存在逐spot类别，且每片分布极不均衡：本阶段应保留全样本，不能根据后验模型成绩筛选。

| 样本 | 行数 | Classification真实观察 |
|---|---:|---|
| 1142243F | 4784 | 6类：Invasive cancer + stroma + lymphocytes 3627; Necrosis 568; Stroma 445; Artefact 119; Lymphocytes 15; TLS 10 |
| 1160920F | 4895 | 9值：Invasive cancer + stroma + lymphocytes 3146; Stroma 1132; Normal glands + lymphocytes 278; Lymphocytes 186; Adipose tissue 83; Artefact 48; DCIS 12; Cancer trapped in lymphocyte aggregation 9; 空字符串 1 |
| CID4290 | 2432 | 5值：Invasive cancer + stroma 2082; Invasive cancer + stroma + lymphocytes 215; Stroma 122; Artefact 7; 字面NA 6 |
| CID4465 | 1211 | 4值：Invasive cancer + stroma + lymphocytes 1131; Stroma 73; Artefact 4; Normal duct 3 |
| CID44971 | 1162 | 8值：Invasive cancer + lymphocytes 317; DCIS 273; Normal + stroma + lymphocytes 240; Stroma 134; Stroma + adipose tissue 114; Lymphocytes 81; 字面NA 2; Artefact 1 |
| CID4535 | 1127 | 10值：Invasive cancer 418; Invasive cancer + lymphocytes 361; Stroma 169; Uncertain 73; Lymphocytes 69; Artefact 23; Adipose tissue 8; Invasive cancer + adipose tissue + lymphocytes 3; 字面NA 2; 空字符串 1 |

六CSV共有**15611行**。原生病理区域标签为组合型类别（如`Invasive cancer + stroma + lymphocytes`），不应当作单一细胞类型或与DLPFC层级同语义真值。候选主评价mask应事前排除`Artefact`、`NA`、空字符串、`Uncertain`；是否排除这些类别、缺失/定位处置和各方法输入spot处理须在首次外部拟合**之前**公开冻结，且不能据任何ARI/NMI或方法排名修改。切勿把`Uncertain`合并成任意有利类别。极少类别及严重失衡需完整披露，统计单位为样本患者而非15611个独立生物观测。

**仍未完成**：raw counts与spatial对应元数据的文件结构和barcode精准交集检查、病理标签真实来源核验、独立患者/原论文是否预先训练使用的边界核对、主配置与K策略+预算及外部协议冻结。下一只读步骤下载原始`spatial.tar.gz`（来源Zenodo，约54.3MB，预记录MD5 `29b02ae433d459d19dc52b75a529e8e9`）校验后仅列目录，不解压覆盖/不训练；之后核查raw count压缩包，避免无来源匹配就拟合。

## 第四次Windows只读spatial原始归档完整性检查真实通过（2026-11-21）

**用户Windows原始终端**：
```text
E5B_SPATIAL_INTEGRITY_PASS md5=29b02ae433d459d19dc52b75a529e8e9
E5B_SPATIAL_ARCHIVE_LIST_PASS entries=43
NO_TRAINING_NO_EXTRACTION
```
原公开Zenodo空间归档经MD5校验与预检资料一致，内含六个与metadata匹配**名称**的样本目录（1142243F、1160920F、CID4290、CID4465、CID44971、CID4535）。每样本目录可见`tissue_positions_list.csv`、`scalefactors_json.json`及组织图像文件（tissue_hires_image.png、tissue_lowres_image.png、detected_tissue_image.jpg、aligned_fiducials.jpg）；43项包含目录项。**仅文件存在与压缩包校验成功，不代表已经检查内部坐标值、barcode交集或in_tissue标志、完整文件内容**，更不代表训练完成。

下一Windows唯一步骤：使用Python标准库直接读取两个现有归档内的metadata CSV和每份`tissue_positions_list.csv`，按对应barcode原样做set交叉，报告每样本metadata条码总数、空间条码数、匹配数/差集数、位置重复数、in_tissue值分布、是否具备合法Visium阵列/像素坐标；不解压、下载或拟合。必须明确是否位置CSV带头、顺序是否一致。若交集不足则停止在预检，找原因且不可按行盲拼。下一阶段对counts和barcode继续审查，所有6样本仍是前期候选。

## 第五次Windows条码与Visium空间坐标精确一致性检查（2026-11-21）

**用户Windows原始终端报告**：`E5B_SPATIAL_BARCODE_ALIGNMENT_PASS samples=6`和`NO_TRAINING_NO_EXTRACTION`。已从两个原始.tar.gz里直接只读提取CSV流并按barcode查交集，全部6张样本的metadata各spot都在对应空间tissue_positions_list.csv中发现，且重复条码0、坏坐标0，原始空间CSV均无header。原脚本的`PASS`条件是每个metadata barcode均在spatial出现、无重复/坏坐标；**不强制metadata in_tissue全为1**，需分开披露这项。

| sample | metadata | spatial full grid | matched | spatial not in metadata | matched in_tissue=0 |
|---|---:|---:|---:|---:|---:|
| 1142243F | 4784 | 4992 | 4784 | 208 | 0 |
| 1160920F | 4895 | 4992 | 4895 | 97 | 0 |
| CID4290 | 2432 | 4992 | 2432 | 2560 | 6 |
| CID4465 | 1211 | 4992 | 1211 | 3781 | 0 |
| CID44971 | 1162 | 4992 | 1162 | 3830 | 2 |
| CID4535 | 1127 | 4992 | 1127 | 3865 | 2 |

合计metadata=15611、精确matched=15611、metadata中有**10个标记为组织外**：CID4290 6、CID44971 2、CID4535 2；其他3例0。原空间文件每片4992个阵列位置，未列入metadata的位置不是CSV丢失；组织外标志须在方法学文稿中单独说明。**后续正式拟合前预先统一固定处理**：优先考虑在所有方法拟合及评价中统一排除`in_tissue=0`的spot，再与分类为Artefact/NA/Uncertain/空标签的评价mask区分；不能悄悄把标签为unknown的spot硬转成人工真值或按ARI决定阈值。

当前还未读取raw expression archive。接下来只做公开`filtered_count_matrices.tar.gz`下载、MD5与archive路径列表，核实6份count矩阵文件存在；再做counts<->metadata/barcode/spatial对齐，**之后**才冻结E5b最终样本、label mask和预算。E5a原件封存无改动。

## 第六次Windows raw count压缩包完整性检查真实通过（2026-11-21）

用户Windows终端真实输出：`E5B_COUNTS_INTEGRITY_PASS md5=ea1220f0606c4d4e9307468fb2d5427a`及`E5B_COUNTS_ARCHIVE_LIST_PASS entries=25`、`NO_TRAINING_NO_EXTRACTION`。这是公开Zenodo原始`filtered_count_matrices.tar.gz`，MD5与此前来源记录一致，25项含1根目录、6个样本目录以及每样本3个核心计数成员：`matrix.mtx.gz`、`features.tsv.gz`、`barcodes.tsv.gz`；样本分别为1142243F、1160920F、CID4290、CID4465、CID44971、CID4535。**目前没有读取任何内部矩阵/条码，不能推断维度和一一对齐，也尚未训练。**

下一Windows唯一只读步骤：直接用Python标准库读取归档中的6份`barcodes.tsv.gz`和`matrix.mtx.gz`的MatrixMarket尺寸头（不加载全矩阵），和已校验`metadata.tar.gz`的最左列spot条码逐样本精确做集合交叉，核对6样本matrix列数等于barcodes行数、记录metadata完全匹配情况及额外barcodes、重复/空条码、MatrixMarket banner和features行数（不修改原数据）。**不做模糊条码修正、不按行盲拼**。成功后仍需数据工程/最终标签mask与样本K方案预先冻结，才可称E5b可正式拟合。

