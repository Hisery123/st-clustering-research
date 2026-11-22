# Publish ORIGINAL E4 SVG+CSV outputs without re-running plotting or training.
# Uses the 2026-11-20 completed batch, its original manifests, and independent audit.
# No source model/label/CSV is modified; clone is new and push is non-force.
[CmdletBinding()]
param(
  [string]$Base = 'D:\paper\CellCharter_reproduction',
  [string]$ProxyUrl = ''
)
$ErrorActionPreference = 'Stop'
function Assert-True([bool]$Condition, [string]$ErrorCode) {
  if (-not $Condition) { throw $ErrorCode }
}
function SHA256([string]$Path) {
  return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}
function LoadJson([string]$Path) {
  return (Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json)
}

$repoUrl = 'https://github.com/Hisery123/st-clustering-research.git'
$batchDir = Join-Path $Base 'results\e4_spatial_visualization_v1\batch_20261120T080609Z_4732'
$auditFile = Join-Path $Base 'results\e4_spatial_visualization_v1\phase_audit_v1\20261120T082135Z_29612\e4_phase_audit_report.json'
$workDir = Join-Path $Base 'results\github_e4_original_push_20261122'
$cloneDir = Join-Path $workDir 'st-clustering-research'
$releaseRel = 'experiments/cellcharter_dlpfc/E4_SOURCE_FIGURES_20261122_RELEASE'
$releaseDir = Join-Path $cloneDir ($releaseRel -replace '/', '\')
$samples = @('151507','151508','151509','151510','151669','151670','151671','151672','151673','151674','151675','151676')
$requiredNames = @(
  '{sid}_reference_A_B_spatial.svg',
  '{sid}_MOBP_PCP4_SNAP25_expression.svg',
  '{sid}_reference_A_B_confusion.svg',
  '{sid}_marker_expression_raw_and_log1p10k.csv',
  '{sid}_reference_vs_A_confusion_counts.csv',
  '{sid}_reference_vs_B_confusion_counts.csv'
)

Assert-True (-not (Test-Path -LiteralPath $workDir)) "E4_WORKDIR_ALREADY_EXISTS $workDir"
Assert-True ($null -ne (Get-Command git -ErrorAction SilentlyContinue)) 'E4_GIT_NOT_INSTALLED'
Assert-True (Test-Path -LiteralPath $auditFile -PathType Leaf) "E4_AUDIT_MISSING $auditFile"
$batchFile = Join-Path $batchDir 'e4_batch_status.json'
Assert-True (Test-Path -LiteralPath $batchFile -PathType Leaf) "E4_BATCH_MISSING $batchFile"
$batch = LoadJson $batchFile
$audit = LoadJson $auditFile
Assert-True ($batch.protocol -eq 'E4_SPATIAL_MARKER_REAL_DATA_BATCH_V1') 'E4_BATCH_PROTOCOL_WRONG'
Assert-True ($batch.status -eq 'completed' -and [int]$batch.pass_count -eq 12 -and @($batch.failure_samples).Count -eq 0) 'E4_BATCH_NOT_PASSED'
Assert-True ($audit.status -eq 'passed' -and [int]$audit.checked_samples -eq 12 -and [int]$audit.svg_checked -eq 36 -and [int]$audit.csv_checked -eq 36 -and @($audit.issues).Count -eq 0) 'E4_FINAL_AUDIT_NOT_PASSED'

$manifestRows = New-Object 'System.Collections.Generic.List[object]'
$copyJobs = New-Object 'System.Collections.Generic.List[object]'
foreach ($sid in $samples) {
  $sourceFolder = Join-Path $batchDir $sid
  $sourceManifest = Join-Path $sourceFolder 'e4_sample_manifest.json'
  Assert-True (Test-Path -LiteralPath $sourceManifest -PathType Leaf) "E4_MANIFEST_MISSING $sid"
  $saved = LoadJson $sourceManifest
  $recordProp = $batch.samples.PSObject.Properties[$sid]
  Assert-True ($null -ne $recordProp) "E4_BATCH_SAMPLE_NOT_FOUND $sid"
  $status = $recordProp.Value
  Assert-True ($saved.sample -eq $sid -and $saved.status -eq 'completed') "E4_SAMPLE_NOT_COMPLETED $sid"
  Assert-True (([int]$saved.spots) -eq ([int]$status.spots) -and ([int]$saved.labeled) -eq ([int]$status.labeled)) "E4_SAMPLE_BATCH_MISMATCH $sid"
  $names = @($requiredNames | ForEach-Object { $_.Replace('{sid}',$sid) })
  $actualNameList = @($saved.output_sha256.PSObject.Properties.Name)
  Assert-True (@(Compare-Object $names $actualNameList).Count -eq 0) "E4_OUTPUT_NAME_SET_WRONG $sid"
  foreach ($name in $names) {
    $original = Join-Path $sourceFolder $name
    Assert-True (Test-Path -LiteralPath $original -PathType Leaf) "E4_OUTPUT_MISSING $original"
    $originalHash = SHA256 $original
    $hashProperty = $saved.output_sha256.PSObject.Properties[$name]
    $statusHashProp = $status.output_sha256.PSObject.Properties[$name]
    Assert-True ($null -ne $hashProperty -and $null -ne $statusHashProp) "E4_MANIFEST_HASH_FIELD_MISSING $sid $name"
    Assert-True ($originalHash -eq ([string]$hashProperty.Value).ToLowerInvariant()) "E4_OUTPUT_SHA_MISMATCH $original"
    Assert-True ($originalHash -eq ([string]$statusHashProp.Value).ToLowerInvariant()) "E4_BATCH_SHA_MISMATCH $original"
    $relative = "figures/$sid/$name"
    $copyJobs.Add([PSCustomObject]@{ Source=$original; Relative=$relative; SHA256=$originalHash })
  }
  $copyJobs.Add([PSCustomObject]@{
    Source=$sourceManifest
    Relative="figures/$sid/e4_sample_manifest.json"
    SHA256=(SHA256 $sourceManifest)
  })
}
Assert-True ($copyJobs.Count -eq 84) "E4_SOURCE_JOB_COUNT_BAD $($copyJobs.Count)"
$copyJobs.Add([PSCustomObject]@{ Source=$batchFile; Relative='e4_batch_status.json'; SHA256=(SHA256 $batchFile) })
$copyJobs.Add([PSCustomObject]@{ Source=$auditFile; Relative='e4_phase_audit_report.json'; SHA256=(SHA256 $auditFile) })
Assert-True ($copyJobs.Count -eq 86) 'E4_ALL_SOURCE_JOB_COUNT_BAD'
Write-Host 'E4_SOURCE_PRECHECK_PASS samples=12 svg=36 csv=36 manifests=12 audit=passed'

[void](New-Item -ItemType Directory -Path $workDir)
$cloneArgs = @()
if ($ProxyUrl) { $cloneArgs += @('-c',"http.proxy=$ProxyUrl") }
$cloneArgs += @('clone','--quiet','--branch','main','--single-branch',$repoUrl,$cloneDir)
& git @cloneArgs
Assert-True ($LASTEXITCODE -eq 0) 'E4_GIT_CLONE_FAILED'
$remote = (& git -C $cloneDir remote get-url origin).Trim()
Assert-True ($remote -eq $repoUrl) "E4_REMOTE_MISMATCH $remote"
Assert-True (-not (Test-Path -LiteralPath $releaseDir)) "E4_RELEASE_ALREADY_PRESENT $releaseDir"

[void](New-Item -ItemType Directory -Path $releaseDir)
$verified = 0
foreach ($job in $copyJobs) {
  $dest = Join-Path $releaseDir ($job.Relative -replace '/', '\')
  $parent = Split-Path -Parent $dest
  if (-not (Test-Path -LiteralPath $parent)) {
    [void](New-Item -ItemType Directory -Path $parent -Force)
  }
  Assert-True (-not (Test-Path -LiteralPath $dest)) "E4_TARGET_EXISTS $dest"
  Copy-Item -LiteralPath $job.Source -Destination $dest
  Assert-True ((SHA256 $dest) -eq $job.SHA256) "E4_COPY_SHA_MISMATCH $($job.Relative)"
  $manifestRows.Add([PSCustomObject]@{
    RelativePath = $job.Relative
    OriginalPath = $job.Source
    SHA256 = $job.SHA256
  })
  $verified++
}
$manifestRows | Export-Csv -LiteralPath (Join-Path $releaseDir 'SOURCE_SHA256.csv') -NoTypeInformation -Encoding UTF8

$readme = @'
# E4 full original SVG and CSV publication (2026-11-22)
Source: Windows batch_20261120T080609Z_4732, audited 20261120T082135Z_29612.
This directory holds byte-identical copies of 36 genuine SVGs, 36 genuine CSVs,
12 original e4_sample_manifest.json files, the original batch status and final
audit report, and an export-time SOURCE_SHA256.csv manifest.
NO model fitting, image synthesis, post-hoc cluster relabeling, or re-plotting.

figures/<sample>/: three original vector plots, three raw/derived CSV files,
and the manifest with source and prediction SHAs.
The main-text representatives were frozen in the original plot script:
151507 (D1 positive B-A ARI), 151671 (D2 near zero), 151675 (D3 negative).
These are result-informed illustrative samples, not blind test selection.
All twelve are provided, including unfavorable cases.
CellCharter A/B source is seed22911 Oracle-K; other result stages have
different seed/K settings. Never silently mix them.
Independent biological n=3 donors, not n=12 slices or ~43k spots.

Original editable SVGs live in figures/. For XeLaTeX using graphicx,
a separate, exactly derived vector-PDF export may be made later under
figures_pdf/; it is not part of the original E4 Windows plot run.
'@
[System.IO.File]::WriteAllText(
  (Join-Path $releaseDir 'README.md'),
  $readme + [Environment]::NewLine,
  (New-Object System.Text.UTF8Encoding($false))
)

& git -C $cloneDir add -- $releaseRel
Assert-True ($LASTEXITCODE -eq 0) 'E4_GIT_ADD_FAILED'
$files = @(& git -C $cloneDir diff --cached --name-only -- $releaseRel)
Assert-True ($files.Count -eq 88) "E4_GIT_STAGED_COUNT_BAD found=$($files.Count) expected=88"
Assert-True (-not [string]::IsNullOrWhiteSpace((& git -C $cloneDir config user.name))) 'E4_GIT_USERNAME_NOT_CONFIGURED'
Assert-True (-not [string]::IsNullOrWhiteSpace((& git -C $cloneDir config user.email))) 'E4_GIT_EMAIL_NOT_CONFIGURED'
& git -C $cloneDir commit -m 'data(cellcharter): publish 36 original E4 SVGs, 36 CSVs and 12 audit manifests'
Assert-True ($LASTEXITCODE -eq 0) 'E4_GIT_COMMIT_FAILED'
$newCommit = (& git -C $cloneDir rev-parse HEAD).Trim()
$pushArgs = @()
if ($ProxyUrl) { $pushArgs += @('-c',"http.proxy=$ProxyUrl") }
$pushArgs += @('-C',$cloneDir,'push','origin','HEAD:refs/heads/main')
& git @pushArgs
Assert-True ($LASTEXITCODE -eq 0) 'E4_GIT_PUSH_FAILED_NO_FORCE'
Write-Host 'E4_GITHUB_ORIGINALS_PUSH_PASS svg=36 csv=36 manifests=12 total_files=88'
Write-Host "E4_GITHUB_COMMIT=$newCommit"
Write-Host 'E4_GITHUB_URL=https://github.com/Hisery123/st-clustering-research/tree/main/experiments/cellcharter_dlpfc/E4_SOURCE_FIGURES_20261122_RELEASE'
