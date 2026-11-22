# E3b/E1E2 source-prediction publication (manual Windows step).
# Posthoc archival. Does not train, score, relabel, or modify original experiment files.
# Creates a NEW git checkout in results/. Stages and pushes 1200 byte-identical CSVs.
[CmdletBinding()]
param(
    [string]$Base = 'D:\paper\CellCharter_reproduction',
    [string]$ProxyUrl = ''
)
$ErrorActionPreference = 'Stop'
$repoUrl = 'https://github.com/Hisery123/st-clustering-research.git'
$repoName = 'Hisery123/st-clustering-research'
$zipFile = Join-Path $Base 'results\e3b_e1e2_1200_export_20261122.zip'
$expectedZip = 'cfad75dbc35723c72e52f8906b07e1b81048ff70fcf04df709d41ae42bc1302b'
$expectedLedger = 'e021ca75958c3d5539dda1987e5031d13ce4fe161d9f0db7f03b5dcfb40e065e'
$workDir = Join-Path $Base 'results\github_e3b_1200_push_20261122'
$repoDir = Join-Path $workDir 'st-clustering-research'
$releaseRel = 'experiments/cellcharter_dlpfc/E3B_E1E2_1200_PREDICTIONS_20261122'
$releaseDir = Join-Path $repoDir ($releaseRel -replace '/', '\')

function Assert-True([bool]$ok, [string]$message) {
    if (-not $ok) { throw $message }
}
function Sha256([string]$path) {
    return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
}
function Get-EntryText($entry) {
    $stream = $entry.Open()
    try {
        $reader = New-Object System.IO.StreamReader($stream, [System.Text.Encoding]::UTF8, $true)
        try { return $reader.ReadToEnd() } finally { $reader.Dispose() }
    } finally { $stream.Dispose() }
}
function Copy-Entry($entry, [string]$target) {
    $parent = Split-Path -Parent $target
    if (-not (Test-Path -LiteralPath $parent)) {
        [void](New-Item -ItemType Directory -Path $parent -Force)
    }
    Assert-True (-not (Test-Path -LiteralPath $target)) "NO_OVERWRITE_OUTPUT $target"
    $source = $entry.Open()
    try {
        $destination = [System.IO.File]::Create($target)
        try { $source.CopyTo($destination) } finally { $destination.Dispose() }
    } finally { $source.Dispose() }
}

Assert-True (Test-Path -LiteralPath $zipFile -PathType Leaf) "MISSING_ORIGINAL_ZIP $zipFile"
Assert-True ((Sha256 $zipFile) -eq $expectedZip) 'ORIGINAL_ZIP_SHA256_MISMATCH'
Assert-True (-not (Test-Path -LiteralPath $workDir)) "WORK_DIRECTORY_ALREADY_EXISTS $workDir"
$gitCommand = Get-Command git -ErrorAction SilentlyContinue
Assert-True ($null -ne $gitCommand) 'GIT_NOT_INSTALLED_OR_NOT_ON_PATH'

Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead($zipFile)
try {
    $fileEntries = @{}
    foreach ($entry in $zip.Entries) {
        $name = $entry.FullName.Replace('\', '/')
        if ($name.EndsWith('/')) { continue }
        Assert-True (-not $fileEntries.ContainsKey($name)) "ZIP_DUPLICATE_ENTRY $name"
        $fileEntries[$name] = $entry
    }
    Assert-True ($fileEntries.Count -eq 1202) "ZIP_UNEXPECTED_FILES count=$($fileEntries.Count)"
    Assert-True ($fileEntries.ContainsKey('SOURCE_SHA256.csv')) 'MISSING_SOURCE_SHA256'
    Assert-True ($fileEntries.ContainsKey('LEDGER_SHA256.txt')) 'MISSING_FROZEN_LEDGER_HASH'
    $ledgerSha = (Get-EntryText $fileEntries['LEDGER_SHA256.txt']).Trim().ToLowerInvariant()
    Assert-True ($ledgerSha -eq $expectedLedger) 'LEDGER_SHA256_UNEXPECTED'
    $manifestText = Get-EntryText $fileEntries['SOURCE_SHA256.csv']
    $manifest = @($manifestText | ConvertFrom-Csv)
    Assert-True ($manifest.Count -eq 1200) "MANIFEST_ROW_COUNT_BAD $($manifest.Count)"
    $seen = New-Object 'System.Collections.Generic.HashSet[string]' ([System.StringComparer]::OrdinalIgnoreCase)
    foreach ($row in $manifest) {
        $relative = ([string]$row.RelativePath).Replace('\', '/')
        Assert-True ($relative -match '^predictions/[0-9]{6}/[A-Za-z0-9_]+/seed_[0-9]+/predictions\.csv$') "INVALID_FILE_LAYOUT $relative"
        Assert-True ($seen.Add($relative)) "DUPLICATE_MANIFEST_PATH $relative"
        Assert-True ($fileEntries.ContainsKey($relative)) "ZIP_FILE_MISSING $relative"
        Assert-True (([string]$row.SHA256) -match '^[0-9a-fA-F]{64}$') "INVALID_SHA256 $relative"
    }
    Write-Host "E3B_SOURCE_PRECHECK_PASS predictions=$($manifest.Count) zip_sha256=$expectedZip"

    [void](New-Item -ItemType Directory -Path $workDir)
    $gitArgs = @()
    if ($ProxyUrl) { $gitArgs += @('-c', "http.proxy=$ProxyUrl") }
    $gitArgs += @('clone', '--quiet', '--branch', 'main', '--single-branch', $repoUrl, $repoDir)
    & git @gitArgs
    Assert-True ($LASTEXITCODE -eq 0) 'GIT_CLONE_FAILED_CHECK_NETWORK_OR_GITHUB_AUTH'
    $origin = (& git -C $repoDir remote get-url origin).Trim()
    Assert-True ($origin -eq $repoUrl) "UNEXPECTED_GIT_REMOTE $origin"
    Assert-True (-not (Test-Path -LiteralPath $releaseDir)) 'REMOTE_RELEASE_PATH_ALREADY_EXISTS_NO_OVERWRITE'

    [void](New-Item -ItemType Directory -Path $releaseDir -Force)
    $checked = 0
    foreach ($row in $manifest) {
        $relative = ([string]$row.RelativePath).Replace('\', '/')
        $destination = Join-Path $releaseDir ($relative -replace '/', '\')
        Copy-Entry $fileEntries[$relative] $destination
        Assert-True ((Sha256 $destination) -eq ([string]$row.SHA256).ToLowerInvariant()) "EXTRACTED_FILE_SHA256_MISMATCH $relative"
        $checked++
        if ($checked % 200 -eq 0) { Write-Host "E3B_SOURCE_VERIFIED $checked/1200" }
    }
    Copy-Entry $fileEntries['SOURCE_SHA256.csv'] (Join-Path $releaseDir 'SOURCE_SHA256.csv')
    Copy-Entry $fileEntries['LEDGER_SHA256.txt'] (Join-Path $releaseDir 'LEDGER_SHA256.txt')
    $readme = @"
# Exact 1200 original E1/E2 prediction CSVs (2026-11-22)

This is a BYTE-EXACT COPY of all 1,200 frozen clustering predictions
from the Windows export ZIP, organized by sample/condition/seed.
The experiment was previously conducted; this commit does not re-train
or re-score any predictions.

- Origin: D:\paper\CellCharter_reproduction\results\e3b_e1e2_1200_export_20261122.zip
- Original ZIP SHA256: $expectedZip
- Original 1200-task ledger SHA256: $expectedLedger
- Prediction SHA256 for EACH task: SOURCE_SHA256.csv
- Every 1200 source prediction CSV SHA256 was verified before git commit.
- Layout: predictions/<sample>/<condition>/seed_<seed>/predictions.csv
- Full posthoc boundary scores: ../E3B_E1E2_1200_POSTHOC_20261122_RELEASE/
- Biological independent unit: 3 donors; slices and seeds are nested.
- Boundary tolerance evaluation is posthoc, not retrospectively preregistered.
- Raw counts matrices and trained model checkpoints are not included.

The original ZIP is NOT uploaded here; its 1200 constituent prediction
CSVs, original export manifest, and original ledger checksum ARE uploaded.
"@
    [System.IO.File]::WriteAllText(
        (Join-Path $releaseDir 'README.md'),
        $readme + [Environment]::NewLine,
        (New-Object System.Text.UTF8Encoding($false))
    )
    & git -C $repoDir add -- $releaseRel
    Assert-True ($LASTEXITCODE -eq 0) 'GIT_STAGE_FAILED'
    $staged = @(& git -C $repoDir diff --cached --name-only -- $releaseRel)
    Assert-True ($staged.Count -eq 1203) "STAGED_COUNT_WRONG $($staged.Count) expected=1203"
    $userName = (& git -C $repoDir config user.name)
    $userEmail = (& git -C $repoDir config user.email)
    Assert-True (-not [string]::IsNullOrWhiteSpace($userName)) 'GIT_USER_NAME_NOT_CONFIGURED'
    Assert-True (-not [string]::IsNullOrWhiteSpace($userEmail)) 'GIT_USER_EMAIL_NOT_CONFIGURED'
    & git -C $repoDir commit -m 'data(cellcharter): publish all 1200 byte-verified E1E2 prediction CSVs for E3b audit'
    Assert-True ($LASTEXITCODE -eq 0) 'GIT_COMMIT_FAILED'
    $newCommit = (& git -C $repoDir rev-parse HEAD).Trim()

    $pushArgs = @()
    if ($ProxyUrl) { $pushArgs += @('-c', "http.proxy=$ProxyUrl") }
    $pushArgs += @('-C', $repoDir, 'push', 'origin', 'HEAD:refs/heads/main')
    & git @pushArgs
    Assert-True ($LASTEXITCODE -eq 0) 'GIT_PUSH_FAILED_NO_FORCE_ATTEMPTED'
    Write-Host "E3B_GITHUB_ORIGINALS_PUSH_PASS predictions=1200 files=1203"
    Write-Host "E3B_GITHUB_COMMIT=$newCommit"
    Write-Host "E3B_GITHUB_URL=https://github.com/$repoName/tree/main/$releaseRel"
    Write-Host "E3B_SOURCE_ZIP_SHA256=$expectedZip"
}
finally {
    $zip.Dispose()
}
