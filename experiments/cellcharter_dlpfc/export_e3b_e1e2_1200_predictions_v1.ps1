# Export only the 1200 pre-existing E1/E2 prediction files for E3b follow-up.
# Does NOT train, evaluate, modify, overwrite, or delete original experiments.
# Uses the frozen GitHub all_1200_tasks.csv ledger as a source of expected SHA256.
# The ZIP will contain source predictions and an auditable manifest; the
# 12 frozen positions/reference CSVs are in the already supplied E3d ZIP.

param(
    [Parameter(Mandatory=$true)][string]$Ledger,
    [string]$Base = 'D:\paper\CellCharter_reproduction'
)
$ErrorActionPreference = 'Stop'
$root = Join-Path $Base 'results\e3b_e1e2_1200_export_20261122'
$archive = "$root.zip"

if (-not (Test-Path -LiteralPath $Ledger -PathType Leaf)) {
    throw "E3B_LEDGER_MISSING: $Ledger"
}
if ((Test-Path -LiteralPath $root) -or (Test-Path -LiteralPath $archive)) {
    throw "E3B_EXPORT_ALREADY_EXISTS: $root"
}
$records = @(Import-Csv -LiteralPath $Ledger)
if ($records.Count -ne 1200) {
    throw "E3B_EXPECTED_1200_ROWS actual=$($records.Count)"
}
$sampleIds = @($records | Select-Object -ExpandProperty sample -Unique)
$conditions = @($records | Select-Object -ExpandProperty condition -Unique)
$seeds = @($records | Select-Object -ExpandProperty gmm_seed -Unique)
if ($sampleIds.Count -ne 12 -or $conditions.Count -ne 10 -or $seeds.Count -ne 10) {
    throw "E3B_TASK_GRID_DIMENSIONS_BAD samples=$($sampleIds.Count) conditions=$($conditions.Count) seeds=$($seeds.Count)"
}
$keys = @($records | ForEach-Object { "$($_.sample)|$($_.condition)|$($_.gmm_seed)" } | Sort-Object -Unique)
if ($keys.Count -ne 1200) {
    throw 'E3B_DUPLICATE_TASKS'
}

# Check every original first; no partial export folder is created until
# ALL 1200 files and their frozen SHA256 hashes pass.
$items = New-Object 'System.Collections.Generic.List[object]'
foreach ($r in $records) {
    $src = [System.IO.Path]::GetFullPath([string]$r.prediction_file)
    $srcRoot = [System.IO.Path]::GetFullPath($Base).TrimEnd('\') + '\'
    if (-not $src.StartsWith($srcRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "E3B_SOURCE_PATH_OUTSIDE_PROJECT: $src"
    }
    if (-not (Test-Path -LiteralPath $src -PathType Leaf)) {
        throw "E3B_ORIGINAL_PREDICTION_MISSING: $src"
    }
    if ([string]$r.prediction_sha256 -notmatch '^[0-9a-fA-F]{64}$') {
        throw "E3B_LEDGER_PRED_SHA_BAD: $src"
    }
    $got = (Get-FileHash -LiteralPath $src -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($got -ne ([string]$r.prediction_sha256).ToLowerInvariant()) {
        throw "E3B_ORIGINAL_PREDICTION_SHA_MISMATCH: $src"
    }
    $rel = "predictions\$($r.sample)\$($r.condition)\seed_$($r.gmm_seed)\predictions.csv"
    $items.Add([PSCustomObject]@{
        Sample = [string]$r.sample
        Condition = [string]$r.condition
        Seed = [string]$r.gmm_seed
        RelativePath = $rel
        OriginalPath = $src
        SHA256 = $got
    })
}

New-Item -Path $root -ItemType Directory | Out-Null
foreach ($item in $items) {
    $dest = Join-Path $root $item.RelativePath
    New-Item -Path (Split-Path $dest -Parent) -ItemType Directory -Force | Out-Null
    Copy-Item -LiteralPath $item.OriginalPath -Destination $dest -ErrorAction Stop
}
$items | Export-Csv (Join-Path $root 'SOURCE_SHA256.csv') -NoTypeInformation -Encoding UTF8
$ledgerHash = (Get-FileHash -LiteralPath $Ledger -Algorithm SHA256).Hash.ToLowerInvariant()
$ledgerHash | Set-Content (Join-Path $root 'LEDGER_SHA256.txt') -Encoding ASCII
Compress-Archive -Path (Join-Path $root '*') -DestinationPath $archive -CompressionLevel Optimal
$zipHash = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant()
Write-Host "E3B_E1E2_EXPORT_PASS predictions=1200 audit_sha_pass=1200 missing=0"
Write-Host "E3B_E1E2_ZIP=$archive"
Write-Host "E3B_E1E2_ZIP_SHA256=$zipHash"
