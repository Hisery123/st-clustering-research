# DLPFC参考层标签源头审查（2026-11-12，外部来源核查，不等于逐barcode独立审计）

## 本轮直接核查证据
- SEDR官方分析仓库 README: https://github.com/JinmiaoChenLab/SEDR_analyses ，其DLPFC 12切片数据下载说明明确指向**SpatialLIBD**，并声明自带的metadata.tsv与BayesSpace使用的元数据一致。该仓库列出完整12片与聚类K5/K7，与现有实验协议一致。
- SEDR源码 https://github.com/JinmiaoChenLab/SEDR_analyses/blob/master/DLPFC_Seurat.R ：读取同目录metadata.tsv的layer_guess列，并用该列参与ARI比较；不是SEDR聚类后写回预测标签。
- SEDR官方教程 https://sedr.readthedocs.io/en/latest/Tutorial1_Clustering.html ：加载DLPFC metadata.tsv 的 layer_guess 到adata.obs以进行评价。
- spatialLIBD官方文档 https://research.libd.org/spatialLIBD/reference/fetch_data.html ：官方layer-level对象colData中有layer_guess及layer_guess_reordered_short字段。这是字段名称与原数据链的依据，尚不能替代spot级逐行比对。
- SEDR公开151507源metadata.tsv: https://github.com/JinmiaoChenLab/SEDR_analyses/blob/master/data/DLPFC/151507/metadata.tsv ，151676: https://github.com/JinmiaoChenLab/SEDR_analyses/blob/master/data/DLPFC/151676/metadata.tsv 。公开文件存在，但本轮未做全行byte/hash核验。
- 用户现有本地转换脚本 scripts/cellcharter/prepare_dlpfc_10_sources.py 读取metadata_source.tsv的layer_guess，经barcode与H5、坐标对齐后生成manual_layer_annotations.csv，并检查layer_guess_reordered与layer_guess一致，见脚本第44、66、84–112、125–132行。

## 目前允许的表述
后续10片使用基于公开DLPFC基准数据链的既有参考层标签，源数据由SEDR分析仓库存放并沿用SpatialLIBD，非本研究新判读标签，也无证据称SEDR模型输出了layer_guess。这是**来源的文档链验证**，尚不是从用户本地文件到公开官方文件的逐barcode等价审计。

## 尚不能确认
1. 用户本地metadata_source.tsv是否与SEDR GitHub公开文件（以及SpatialLIBD原始对象）的内容完全相同；源文件可能存在版本变化、额外列或重排。
2. 两张旧开发切片151507/151508的manual_layer_annotations.csv具体生成链与新10片是否完全一致；仅知道旧脚本读取该文件。
3. 不同供体参考类别K5/K7的标签粒度差异仍存在，即使属于同一上游数据库也不能据此消除混杂。

## 下一步（用户Windows一步只读检查）
先检查12个本地DLPFC数据目录里 metadata_source.tsv 和 manual_layer_annotations.csv 是否实际存在，且旧2片是否有源metadata。此步骤不做结果修改或训练；拿到文件清单后进一步制定按barcode对照的最小审计。不得未经用户实际反馈宣称检查通过。
