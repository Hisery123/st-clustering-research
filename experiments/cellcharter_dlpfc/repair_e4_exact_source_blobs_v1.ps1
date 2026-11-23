# One-time correction: Git on Windows normalized CRLF while committing E4 SVG/CSV/JSON.
# Rebuild the Git INDEX with exact ORIGINAL experiment bytes, bypassing all text filters.
# Does NOT modify original Windows experiment source or model predictions.
# Requires E4_SOURCE_FIGURES_20261122_RELEASE/.gitattributes ("* -text") on main.
[CmdletBinding()]
param(
    [string]$Base = 'D:\paper\CellCharter_reproduction',
    [string]$ProxyUrl = ''
)
$ErrorActionPreference = 'Stop'
function Need([bool]$ok, [string]$msg) {
    if (-not $ok) { throw $msg }
}
function H([string]$path) {
    return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
}
$repoUrl = 'https://github.com/Hisery123/st-clustering-research.git'
$relativeRoot = 'experiments/cellcharter_dlpfc/E4_SOURCE_FIGURES_20261122_RELEASE'
$batchBase = Join-Path $Base 'results\e4_spatial_visualization_v1'
$out = Join-Path $Base 'results\github_e4_exact_source_blob_repair_20261123'
$checkout = Join-Path $out 'st-clustering-research'
$sub = Join-Path $checkout ($relativeRoot -replace '/', '\')
$validSamples = @('151507','151508','151509','151510','151669','151670',
                  '151671','151672','151673','151674','151675','151676')

Need ($null -ne (Get-Command git -ErrorAction SilentlyContinue)) 'E4_GIT_COMMAND_NOT_FOUND'
Need (-not (Test-Path -LiteralPath $out)) "E4_REPAIR_WORKSPACE_ALREADY_EXISTS $out"
Need (Test-Path -LiteralPath $batchBase -PathType Container) "E4_SOURCE_BATCH_BASE_MISSING $batchBase"

[void](New-Item -ItemType Directory -Path $out)
$cloneArgs = @()
if ($ProxyUrl) { $cloneArgs += @('-c', "http.proxy=$ProxyUrl") }
$cloneArgs += @('clone','--quiet','--branch','main','--single-branch',$repoUrl,$checkout)
& git @cloneArgs
Need ($LASTEXITCODE -eq 0) 'E4_REPAIR_CLONE_FAILED'
Need ((& git -C $checkout remote get-url origin).Trim() -eq $repoUrl) 'E4_REPAIR_REMOTE_MISMATCH'
Need (Test-Path -LiteralPath (Join-Path $sub '.gitattributes') -PathType Leaf) 'E4_EXACT_BYTES_GITATTRIBUTES_MISSING'

$attrResult = (& git -C $checkout check-attr text -- "$relativeRoot/figures/151507/151507_reference_A_B_spatial.svg") -join ''
Need ($LASTEXITCODE -eq 0 -and $attrResult -match 'text:\s+unset') "E4_EXACT_BYTES_ATTR_NOT_EFFECTIVE $attrResult"

$manifestFile = Join-Path $sub 'SOURCE_SHA256.csv'
Need (Test-Path -LiteralPath $manifestFile -PathType Leaf) 'E4_SOURCE_SHA256_MANIFEST_MISSING'
$rows = @(Import-Csv -LiteralPath $manifestFile)
Need ($rows.Count -eq 86) "E4_SOURCE_MANIFEST_COUNT_BAD $($rows.Count)"
$seen = New-Object 'System.Collections.Generic.HashSet[string]' ([System.StringComparer]::OrdinalIgnoreCase)
$jobs = New-Object 'System.Collections.Generic.List[object]'
$batchPathPrefix = [IO.Path]::GetFullPath($batchBase)
if (-not $batchPathPrefix.EndsWith('\')) { $batchPathPrefix += '\' }

foreach ($r in $rows) {
    $rel = ([string]$r.RelativePath).Replace('\','/')
    $parts = $rel.Split('/')
    $allowed = $false
    if ($parts.Length -eq 3 -and $parts[0] -eq 'figures' -and ($parts[1] -in $validSamples)) {
        $allowed = $parts[2] -match '^[A-Za-z0-9_]+\.(svg|csv|json)$'
    } elseif ($parts.Length -eq 1) {
        $allowed = $rel -in @('e4_batch_status.json','e4_phase_audit_report.json')
    }
    Need $allowed "E4_MANIFEST_PATH_INVALID $rel"
    Need ($seen.Add($rel)) "E4_MANIFEST_PATH_DUPLICATE $rel"
    $source = [IO.Path]::GetFullPath([string]$r.OriginalPath)
    Need ($source.StartsWith($batchPathPrefix, [StringComparison]::OrdinalIgnoreCase)) "E4_SOURCE_ESCAPES_BATCH_DIR $source"
    Need (Test-Path -LiteralPath $source -PathType Leaf) "E4_ORIGINAL_NOT_FOUND $source"
    $expected = ([string]$r.SHA256).ToLowerInvariant()
    Need ($expected -match '^[0-9a-f]{64}$') "E4_EXPECTED_SHA_INVALID $rel"
    $actual = H $source
    Need ($actual -eq $expected) "E4_ORIGINAL_SHA_MISMATCH $rel"

    $gitPath = "$relativeRoot/$rel"
    $old = (& git -C $checkout rev-parse "HEAD:$gitPath").Trim()
    Need ($LASTEXITCODE -eq 0 -and $old -match '^[0-9a-f]{40}$') "E4_EXISTING_GIT_BLOB_MISSING $gitPath"

    # Git hash-object --no-filters records the exact Windows original bytes.
    $new = (& git -C $checkout hash-object -w --no-filters -- $source).Trim()
    Need ($LASTEXITCODE -eq 0 -and $new -match '^[0-9a-f]{40}$') "E4_ORIGINAL_GIT_HASH_FAILED $rel"

    # Direct index update bypasses both autocrlf and any working-tree translation.
    & git -C $checkout update-index --add --cacheinfo "100644,$new,$gitPath"
    Need ($LASTEXITCODE -eq 0) "E4_GIT_INDEX_STAGE_FAILED $rel"

    $jobs.Add([PSCustomObject]@{
        RelativePath=$rel
        OriginalSHA256=$expected
        OldGitBlob=$old
        ExactGitBlob=$new
        ChangedInGit=($old -ne $new)
    })
}
Need ($jobs.Count -eq 86) 'E4_SOURCE_BLOB_MATRIX_NOT_86'
$countChanged = @($jobs | Where-Object { $_.ChangedInGit }).Count
Need ($countChanged -gt 0) 'E4_NO_NORMALIZED_SOURCE_BLOBS_FOUND'
Write-Host "E4_EXACT_SOURCE_BLOB_PRECHECK_PASS sources=86 sha256=86 normalized_to_repair=$countChanged"

# Record the provenance of the correction as a new derived audit CSV.
$report = Join-Path $sub 'EXACT_SOURCE_BLOB_REPAIR_AUDIT_20261123.csv'
Need (-not (Test-Path -LiteralPath $report)) 'E4_REPAIR_AUDIT_ALREADY_EXISTS'
$jobs | Export-Csv -LiteralPath $report -NoTypeInformation -Encoding UTF8
& git -C $checkout add -- "$relativeRoot/EXACT_SOURCE_BLOB_REPAIR_AUDIT_20261123.csv"
Need ($LASTEXITCODE -eq 0) 'E4_REPAIR_AUDIT_STAGE_FAILED'

$changedStaged = @(& git -C $checkout diff --cached --name-only)
Need ($changedStaged.Count -eq ($countChanged + 1)) "E4_REPAIR_STAGED_WRONG count=$($changedStaged.Count) expected=$($countChanged + 1)"
Need (-not [string]::IsNullOrWhiteSpace((& git -C $checkout config user.name))) 'E4_GIT_USERNAME_MISSING'
Need (-not [string]::IsNullOrWhiteSpace((& git -C $checkout config user.email))) 'E4_GIT_USEREMAIL_MISSING'
& git -C $checkout commit -m 'fix(data): restore exact 86 original E4 experiment source blobs after Windows EOL normalization'
Need ($LASTEXITCODE -eq 0) 'E4_REPAIR_COMMIT_FAILED'
$commit = (& git -C $checkout rev-parse HEAD).Trim()

# Verify that the committed Git TREE (not merely the local working copy)
# points to the exact hash-object --no-filters result of EVERY original.
foreach ($j in $jobs) {
    $gitPath = "$relativeRoot/$($j.RelativePath)"
    $committed = (& git -C $checkout rev-parse "HEAD:$gitPath").Trim()
    Need ($LASTEXITCODE -eq 0 -and $committed -eq $j.ExactGitBlob) "E4_COMMITTED_BLOB_SHA_MISMATCH $gitPath"
}
Write-Host 'E4_COMMITTED_EXACT_SOURCE_BLOB_PASS sources=86/86'

$pushArgs = @()
if ($ProxyUrl) { $pushArgs += @('-c', "http.proxy=$ProxyUrl") }
$pushArgs += @('-C',$checkout,'push','origin','HEAD:refs/heads/main')
& git @pushArgs
Need ($LASTEXITCODE -eq 0) 'E4_REPAIR_PUSH_FAILED_NO_FORCE'
Write-Host "E4_EXACT_SOURCE_BYTES_PUSH_PASS sources=86 changed=$countChanged"
Write-Host "E4_EXACT_SOURCE_BYTES_COMMIT=$commit"
Write-Host 'E4_EXACT_SOURCE_BYTES_URL=https://github.com/Hisery123/st-clustering-research/tree/main/experiments/cellcharter_dlpfc/E4_SOURCE_FIGURES_20261122_RELEASE'
