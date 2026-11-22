# 2026-11-22 Windows final audit archive provenance

**User-authorized GitHub evidence export.** The user exported six small original files from finished Windows audit directories using a PowerShell copy-only command. The ZIP `github_missing_derived_20261122.zip` contained exactly six files and one `SOURCE_SHA256.csv`. The ZIP source manifest was validated locally 6/6; **after writing to GitHub all seven files were fetched back and their exact original SHA256/byte lengths verified 7/7**. Names in the temporary export were prefixed E3D_, E5A_, E5B_ to prevent collision; archived files have original Windows basenames, unchanged contents (including UTF-8 BOM and CRLF).

[Original SHA256 + Windows OriginalPath provenance](SOURCE_SHA256.csv).

| Windows export basename | GitHub archived path | Original SHA256 |
|---|---|---|
| `E3D_all_48_autok_audit.csv` | [E3d all 48 audit rows](../E3D_20261122_RELEASE/derived/all_48_autok_audit.csv) | `f2560ec0cde25a9b09fcec8816ffac9e844faceb562756ec19f951cfe51fc821` |
| `E3D_audit_report.json` | [E3d original audit](../E3D_20261122_RELEASE/derived/audit_report.json) | `20bd782a1dc83021fb7b4badabb4d83cd7bf61537219cfa31feb62a1a1423b4d` |
| `E5A_all_288_prediction_checks.csv` | [E5a all 288 scores](../E5A_20261122_RELEASE/derived/all_288_prediction_checks.csv) | `a276d76905e0ada862574a0fc60b2824890381502c932cb149013f005f0d7892` |
| `E5A_method_regime_descriptives.csv` | [E5a 8 summaries](../E5A_20261122_RELEASE/derived/method_regime_descriptives.csv) | `f392c8a9ce231fec5ac393cfda08dd2929134b0802ab1eccd567674c51a5384e` |
| `E5A_e5a_phase_audit_report.json` | [E5a original audit](../E5A_20261122_RELEASE/derived/e5a_phase_audit_report.json) | `bec975d85c8801c8f9c550ea34a36967eb85bea4c174b3b016a949074c920cae` |
| `E5B_audit_report.json` | [E5b original audit](../E5B_20261122_RELEASE/derived/audit_report.json) | `af4061f5072f2b976aee7edbbb73dfeb7704b58eb363f927e1949871eb4f17fb` |

**Historical integrity**: source manifest file SHA256 `e6231d535a56778d1049392149db035f23b92a3ccee36ed803ca6477e26a1379`. E5b JSON contains SHA256 for the three previously archived metric files, matching its prior [release manifest](../E5B_20261122_RELEASE/manifest.json). No fresh model fitting, label selection, parameter tuning or modification of source files occurred during this copy-only operation. The ZIP was not committed as a redundant binary, only the underlying exact files.
