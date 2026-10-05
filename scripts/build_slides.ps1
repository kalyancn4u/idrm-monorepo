# Build a Marp slide deck from a folder of Markdown chapters. GENERIC over -SrcDir.
# Windows/PowerShell mirror of build_slides.sh. Keep this file ASCII-only (PS 5.1 reads
# BOM-less files as ANSI); it reads Markdown sources as UTF-8 and writes UTF-8 (no BOM).
[CmdletBinding()]
param(
  [string]$SrcDir   = "docs/walkthrough",              # folder of NN-*.md chapters
  [string]$OutDir   = "",                              # default: <SrcDir>/slides
  [string]$Footer   = "IDRM MVP - Code Walk-Through",  # slide footer text
  [string]$Combined = "walkthrough-full",              # basename of the all-chapters deck
  [string]$Theme    = "",                              # default: <SrcDir>/assets/marp-theme.css
  [string]$Config   = "",                              # default: <repo-root>/.marprc.yml
  [string]$MarpCmd  = "npx --yes @marp-team/marp-cli@latest",
  [switch]$Pdf
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

function Resolve-Under($path) {
  if ([System.IO.Path]::IsPathRooted($path)) { return $path }
  return (Join-Path $repoRoot $path)
}

$SrcDir = Resolve-Under $SrcDir
if (-not (Test-Path -LiteralPath $SrcDir)) { Write-Error "Source folder not found: $SrcDir" }
if (-not $OutDir) { $OutDir = Join-Path $SrcDir "slides" } else { $OutDir = Resolve-Under $OutDir }
if (-not $Theme)  { $Theme  = Join-Path $SrcDir "assets/marp-theme.css" }
if (-not $Config) { $Config = Join-Path $repoRoot ".marprc.yml" }

# Split "npx --yes pkg" into command + leading args.
$marpParts = $MarpCmd.Split(" ", [System.StringSplitOptions]::RemoveEmptyEntries)
$marpBin   = $marpParts[0]
$marpLead  = @(); if ($marpParts.Length -gt 1) { $marpLead = $marpParts[1..($marpParts.Length-1)] }
if (-not (Get-Command $marpBin -ErrorAction SilentlyContinue)) {
  Write-Error "Install Node.js, or pass -MarpCmd marp"
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
# Marp keeps relative <img> paths (it does NOT inline them) -> copy assets next to the decks.
$assetsSrc = Join-Path $SrcDir "assets"
if (Test-Path -LiteralPath $assetsSrc) {
  $svgs = Get-ChildItem -LiteralPath $assetsSrc -Filter *.svg -ErrorAction SilentlyContinue
  if ($svgs) {
    $assetsOut = Join-Path $OutDir "assets"
    New-Item -ItemType Directory -Force -Path $assetsOut | Out-Null
    $svgs | ForEach-Object { Copy-Item $_.FullName -Destination $assetsOut -Force }
  }
}

$utf8 = New-Object System.Text.UTF8Encoding($false)  # UTF-8 without BOM
$frontMatter = "---`nmarp: true`ntheme: walkthrough`npaginate: true`nfooter: '$Footer'`n---`n`n"

$chapters = Get-ChildItem -LiteralPath $SrcDir -Filter *.md |
  Where-Object { $_.Name -match '^[0-9][0-9]-' } | Sort-Object Name
if (-not $chapters) { Write-Error "No chapters (NN-*.md) in $SrcDir" }

$temp = New-Object System.Collections.Generic.List[string]
function Invoke-Marp($inFile, $outFile, [switch]$AsPdf) {
  $args = @($inFile, "-o", $outFile, "-c", $Config, "--no-stdin", "--allow-local-files", "--theme", $Theme)
  if ($AsPdf) { $args += "--pdf" }
  & $marpBin @marpLead @args | Out-Host
  if ($LASTEXITCODE -ne 0) { throw "Marp failed (exit $LASTEXITCODE) on $inFile" }  # judge by exit code
}

try {
  # one deck per chapter
  foreach ($ch in $chapters) {
    $base = [System.IO.Path]::GetFileNameWithoutExtension($ch.Name)
    $tmp  = Join-Path $SrcDir "_build_$base.md"; $temp.Add($tmp)
    $body = Get-Content -LiteralPath $ch.FullName -Raw -Encoding UTF8
    [System.IO.File]::WriteAllText($tmp, $frontMatter + $body, $utf8)
    Write-Host "Building $($ch.Name)"
    Invoke-Marp $tmp (Join-Path $OutDir "$base.html")
    if ($Pdf) { Invoke-Marp $tmp (Join-Path $OutDir "$base.pdf") -AsPdf }
  }

  # one combined deck
  $combinedTmp = Join-Path $SrcDir "_build_$Combined.md"; $temp.Add($combinedTmp)
  $sb = New-Object System.Text.StringBuilder
  [void]$sb.Append($frontMatter); $first = $true
  foreach ($ch in $chapters) {
    if (-not $first) { [void]$sb.Append("`n`n---`n`n") }
    [void]$sb.Append((Get-Content -LiteralPath $ch.FullName -Raw -Encoding UTF8)); $first = $false
  }
  [System.IO.File]::WriteAllText($combinedTmp, $sb.ToString(), $utf8)
  Invoke-Marp $combinedTmp (Join-Path $OutDir "$Combined.html")
  if ($Pdf) { Invoke-Marp $combinedTmp (Join-Path $OutDir "$Combined.pdf") -AsPdf }
  Write-Host "Done -> $OutDir (open $Combined.html)"
}
finally {
  foreach ($t in $temp) { if (Test-Path -LiteralPath $t) { Remove-Item -LiteralPath $t -Force } }
}
