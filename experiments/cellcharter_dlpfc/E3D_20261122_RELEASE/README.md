# E3d · DLPFC 12切片无标签AutoK独立审计原件 (2026-11-22归档)
**真实完成：** 原始Windows审计脚本记录 `status=passed`，48/48项配置、2640个K种子标签运行归档、528/528个被选择最佳模型检查标记收敛；48项中10项达到冻结的K2–10搜索边界（K=2九项，K=10一项）。详见本目录 [all_48_autok_audit.csv](derived/all_48_autok_audit.csv) 和 [audit_report.json](derived/audit_report.json)，所有48行未筛选。
**不能夸大：** 该阶段AutoK只做无标签选K/预测文件验收，不含ARI/NMI；读到的不是E3d对人工标注的独立聚类质量评分。DLPFC 12张切片嵌套于3位供体，只有供体n=3属于独立生物重复。不能把48配置、2640拟合或spot作为独立生物重复。
**来源：** 用户Windows目录 `D:\paper\CellCharter_reproduction\results\e3d_autok_phase_audit_v1\20261120T072220Z_24992`。用户导出后的文件名增加了前缀E3D_，归档时仅恢复易读basename，**文件内容包括BOM/CRLF保持逐字节一致**。详细SHA256见 [manifest.json](manifest.json) 与 [跨阶段Windows导出清单](../AUDIT_EXPORT_20261122/SOURCE_SHA256.csv)，GitHub上传后远端重读验证SHA256 PASS。
**待做：** 若希望得到E3d真实ARI/NMI，须从冻结的48份原预测与标签进行独立后验评价并单独标注完成日期；不可凭此审计报告直接写E3d性能结论，也不能事后修改AutoK结果。
